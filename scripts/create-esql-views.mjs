#!/usr/bin/env node
/**
 * Creates ES|QL virtual views for DMR base filters (Kibana 9.4 / Elasticsearch 9.4+).
 *
 * Views:
 *   dmr-cars         → base filter only (registered Personbil)
 *   dmr-vehicles     → base filter only (all registered vehicles)
 *   dmr-cars-flat    → registered Personbil with readable column names + data quality guards baked in
 *   dmr-vehicles-flat → all registered vehicles with readable column names
 *
 * The flat views are the key enabler for free-form ES|QL generation:
 *   FROM dmr-cars-flat | WHERE fuel == "El" | STATS COUNT(*) BY brand
 * instead of:
 *   FROM dmr-raw-000002 | WHERE ... AND _drivkraft_primaer == "El" | STATS COUNT(*) BY Koeretoej...keyword
 *
 * Run once:
 *   node scripts/create-esql-views.mjs
 *
 * Dry-run (preview without executing):
 *   node scripts/create-esql-views.mjs --dry-run
 *
 * Flat views only:
 *   node scripts/create-esql-views.mjs --flat-only
 */

import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

try {
  process.loadEnvFile();
} catch {}

const esUrl = process.env.ELASTICSEARCH_URL?.replace(/\/$/, "");
const esKey = process.env.ELASTICSEARCH_API_KEY;
const isDryRun = process.argv.includes("--dry-run");
const flatOnly = process.argv.includes("--flat-only");

if (!esUrl) {
  console.error("ELASTICSEARCH_URL is required.");
  process.exit(1);
}
if (!esKey && !isDryRun) {
  console.error("ELASTICSEARCH_API_KEY is required (or use --dry-run to preview).");
  process.exit(1);
}

// Base filter views — simple, no renaming
const baseViews = [
  {
    name: "dmr-cars",
    description: "Registered passenger cars (Personbil). Shorthand base for all Personbil analytics tools.",
    query: `FROM dmr-raw-000002
| WHERE KoeretoejRegistreringStatus.keyword == "Registreret"
  AND KoeretoejArtNavn.keyword == "Personbil"`,
  },
  {
    name: "dmr-vehicles",
    description: "All registered vehicles (all KoeretoejArtNavn types). Use when scope is not limited to passenger cars.",
    query: `FROM dmr-raw-000002
| WHERE KoeretoejRegistreringStatus.keyword == "Registreret"`,
  },
];

// Flat views — readable column names + data quality guards baked in
// These are the key enabler for free-form ES|QL generation by small models.
// Note: EVAL+KEEP in view definitions is Tech Preview in 9.4 — validate in DevTools first if unsure.
const FLAT_PASSENGER_EVALS = `
| EVAL
    vehicle_id  = KoeretoejIdent,
    vin         = KoeretoejOplysningGrundStruktur.KoeretoejOplysningStelNummer.keyword,
    vehicle_category = KoeretoejArtNavn.keyword,
    registration_status = KoeretoejRegistreringStatus.keyword,
    brand       = KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.KoeretoejMaerkeTypeNavn.keyword,
    model       = KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.Model.KoeretoejModelTypeNavn.keyword,
    vehicle_type = KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.Type.KoeretoejTypeTypeNavn.keyword,
    variant     = KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.Variant.KoeretoejVariantTypeNavn.keyword,
    manufacturer = KoeretoejOplysningGrundStruktur.KoeretoejOplysningFabrikant.keyword,
    fuel        = _drivkraft_primaer,
    color       = KoeretoejOplysningGrundStruktur.KoeretoejFarveStruktur.FarveTypeStruktur.FarveTypeNavn.keyword,
    year        = _foerste_registrering_aar,
    power_kw    = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStoersteEffekt >= 1
                    AND KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStoersteEffekt <= 750,
                    KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStoersteEffekt, NULL),
    kerb_kg     = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningKoereklarVaegtMinimum >= 300
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningKoereklarVaegtMinimum <= 5000,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningKoereklarVaegtMinimum, NULL),
    gross_kg    = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTotalVaegt >= 300
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningTotalVaegt <= 10000,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTotalVaegt, NULL),
    max_kerb_kg = KoeretoejOplysningGrundStruktur.KoeretoejOplysningKoereklarVaegtMaksimum,
    own_kg      = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningEgenVaegt >= 300
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningEgenVaegt <= 5000,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningEgenVaegt, NULL),
    technical_gross_kg = KoeretoejOplysningGrundStruktur.KoeretoejOplysningTekniskTotalVaegt,
    gross_combination_kg = KoeretoejOplysningGrundStruktur.KoeretoejOplysningVogntogVaegt,
    towing_kg   = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtMedBremser >= 1
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtMedBremser <= 5000,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtMedBremser, NULL),
    unbraked_towing_kg = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtUdenBremser >= 1
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtUdenBremser <= 5000,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtUdenBremser, NULL),
    towing_capable = KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingMulighed,
    speed_kmh   = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningMaksimumHastighed >= 50
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningMaksimumHastighed <= 400,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningMaksimumHastighed, NULL),
    doors       = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalDoere >= 2
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalDoere <= 6,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalDoere, NULL),
    seats       = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningSiddepladserMinimum >= 1
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningSiddepladserMinimum <= 9,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningSiddepladserMinimum, NULL),
    max_seats   = KoeretoejOplysningGrundStruktur.KoeretoejOplysningSiddepladserMaksimum,
    axles       = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAntal >= 1
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAntal <= 10,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAntal, NULL),
    gears       = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalGear >= 1
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalGear <= 12,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalGear, NULL),
    wheelbase_mm = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAfstand >= 1500
                    AND KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAfstand <= 4500,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAfstand, NULL),
    front_track_mm = KoeretoejOplysningGrundStruktur.KoeretoejOplysningSporviddenForrest,
    rear_track_mm = KoeretoejOplysningGrundStruktur.KoeretoejOplysningSporviddenBagest,
    cylinders   = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorCylinderAntal,
    displacement_cc = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorSlagVolumen,
    co2_gkm     = _co2_g_per_km_primaer,
    specific_co2_gkm = KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningSpecifikCO2Emission,
    nox_emission = KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningEmissionNOX,
    co_emission = KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningEmissionCO,
    hc_plus_nox_emission = KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningEmissionHCPlusNOX,
    pm_emission = KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningPartikler,
    measurement_norm = _maale_norm_primaer,
    emission_norm = _maale_norm_primaer,
    euro_norm = KoeretoejOplysningGrundStruktur.KoeretoejNormStruktur.NormTypeStruktur.NormTypeNavn.keyword,
    particle_filter = KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningPartikelFilter,
    km_per_liter = CASE(
                    _km_per_liter_primaer > 1 AND _km_per_liter_primaer <= 30,
                    _km_per_liter_primaer, NULL),
    km_per_liter_ev = CASE(
                    _km_per_liter_primaer > 10 AND _km_per_liter_primaer <= 200,
                    _km_per_liter_primaer, NULL),
    awd         = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTraekkendeAkslerListe == 1
                    OR KoeretoejOplysningGrundStruktur.KoeretoejOplysningTraekkendeAkslerListe == 2,
                    KoeretoejOplysningGrundStruktur.KoeretoejOplysningTraekkendeAkslerListe, NULL),
    model_year  = KoeretoejOplysningGrundStruktur.KoeretoejOplysningModelAar,
    first_reg_date = KoeretoejOplysningGrundStruktur.KoeretoejOplysningFoersteRegistreringDato,
    registration_status_date = KoeretoejRegistreringStatusDato,
    body_style  = KoeretoejOplysningGrundStruktur.KarrosseriTypeStruktur.KarrosseriTypeNavn.keyword,
    usage       = KoeretoejAnvendelseStruktur.KoeretoejAnvendelseNavn.keyword,
    inspection_result = SynResultatStruktur.SynResultatSynsResultat.keyword,
    inspection_date   = SynResultatStruktur.SynResultatSynsDato,
    inspection_type   = SynResultatStruktur.SynResultatSynsType.keyword,
    inspection_status = SynResultatStruktur.SynResultatSynStatus.keyword,
    inspection_status_date = SynResultatStruktur.SynResultatSynStatusDato,
    odometer_km_raw = SynResultatStruktur.KoeretoejMotorKilometerstand,
    inspection_odometer_km_sane = CASE(
                    SynResultatStruktur.KoeretoejMotorKilometerstand >= 0
                    AND SynResultatStruktur.KoeretoejMotorKilometerstand <= 1000000,
                    SynResultatStruktur.KoeretoejMotorKilometerstand, NULL),
    engine_odometer_km_raw = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKilometerstand,
    engine_odometer_km_sane = CASE(
                    KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKilometerstand >= 0
                    AND KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKilometerstand <= 1000000,
                    KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKilometerstand, NULL),
    engine_odometer_documented = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKilometerstandDokumentation,
    engine_odometer_unavailable = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKilometerstandIkkeTilgaengelig,
    permit_type = TilladelseSamling.Tilladelse.TilladelseStruktur.TilladelseTypeStruktur.TilladelseTypeNavn.keyword,
    permit_start_date = TilladelseSamling.Tilladelse.TilladelseStruktur.TilladelseGyldigFra,
    permit_end_date = TilladelseSamling.Tilladelse.TilladelseStruktur.TilladelseGyldigTil,
    permit_comment = TilladelseSamling.Tilladelse.TilladelseStruktur.TilladelseKommentar.keyword,
    blocking_reason = KoeretoejOplysningGrundStruktur.KoeretoejBlokeringAarsagListeStruktur.KoeretoejBlokeringAarsagListe.KoeretoejBlokeringAarsag.KoeretoejBlokeringAarsagTypeNavn.keyword,
    vehicle_condition = KoeretoejOplysningGrundStruktur.KoeretoejOplysningKoeretoejstand.keyword,
    record_created_from = KoeretoejOplysningGrundStruktur.KoeretoejOplysningOprettetUdFra.keyword,
    tyres_rims = KoeretoejOplysningGrundStruktur.KoeretoejOplysningFaelgDaek.keyword,
    other_equipment = KoeretoejOplysningGrundStruktur.KoeretoejOplysningOevrigtUdstyr.keyword,
    standing_noise_db = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStandStoej,
    driving_noise_db = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKoerselStoej,
    standing_noise_rpm = KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStandStoejOmdrejningstal,
    is_leased   = CASE(LeasingGyldigFra IS NOT NULL, TRUE, FALSE),
    lease_start_date = LeasingGyldigFra,
    lease_end_date = LeasingGyldigTil,
    is_veteran  = CASE(KoeretoejOplysningGrundStruktur.KoeretoejOplysningVeteranKoeretoejOriginal == TRUE, TRUE, FALSE),
    is_accident_damaged = CASE(KoeretoejOplysningGrundStruktur.KoeretoejOplysningTrafikskade == TRUE, TRUE, FALSE),
    taxi_suitable = CASE(KoeretoejOplysningGrundStruktur.KoeretoejOplysningEgnetTilTaxi == TRUE, TRUE, FALSE),
    ncap_tested = CASE(KoeretoejOplysningGrundStruktur.KoeretoejOplysningNCAPTest == TRUE, TRUE, FALSE),
    plate       = RegistreringNummerNummer
| KEEP vehicle_id, vin, vehicle_category, registration_status, brand, model, vehicle_type, variant, manufacturer,
        fuel, color, year, first_reg_date, model_year, registration_status_date,
        power_kw, kerb_kg, gross_kg, max_kerb_kg, own_kg, technical_gross_kg,
        gross_combination_kg, towing_kg, unbraked_towing_kg, towing_capable,
        speed_kmh, doors, seats, max_seats, axles, gears, wheelbase_mm,
        front_track_mm, rear_track_mm, cylinders, displacement_cc,
        co2_gkm, specific_co2_gkm, nox_emission, co_emission, hc_plus_nox_emission,
        pm_emission, measurement_norm, emission_norm, euro_norm, particle_filter,
        km_per_liter, km_per_liter_ev, awd,
        body_style, usage, inspection_result, inspection_date, inspection_type,
        inspection_status, inspection_status_date, odometer_km_raw,
        inspection_odometer_km_sane, engine_odometer_km_raw, engine_odometer_km_sane,
        engine_odometer_documented, engine_odometer_unavailable, permit_type,
        permit_start_date, permit_end_date, permit_comment, blocking_reason,
        vehicle_condition, record_created_from,
        tyres_rims, other_equipment, standing_noise_db, driving_noise_db,
        standing_noise_rpm, is_leased,
        lease_start_date, lease_end_date, is_veteran, is_accident_damaged,
        taxi_suitable, ncap_tested, plate`.trim();

const flatViews = [
  {
    name: "dmr-cars-flat",
    description: "Registered passenger cars with readable column names and data quality guards baked in. Use for free-form ES|QL generation — no nested paths needed.",
    query: `FROM dmr-raw-000002
| WHERE KoeretoejRegistreringStatus.keyword == "Registreret"
  AND KoeretoejArtNavn.keyword == "Personbil"
${FLAT_PASSENGER_EVALS}`,
  },
  {
    name: "dmr-vehicles-flat",
    description: "All registered vehicles with readable column names. Use when scope includes vans, trucks, and motorcycles.",
    query: `FROM dmr-raw-000002
| WHERE KoeretoejRegistreringStatus.keyword == "Registreret"
${FLAT_PASSENGER_EVALS}`,
  },
  {
    name: "dmr-cars-all-flat",
    description: "ALL passenger cars regardless of registration status (Registreret + Afmeldt + UnderUdarbejdelse + null). Use for lifecycle, write-off, salvage, deregistration, and historical-stock questions where filtering to Registreret would hide the answer. The flat columns and data-quality guards match dmr-cars-flat.",
    query: `FROM dmr-raw-000002
| WHERE KoeretoejArtNavn.keyword == "Personbil"
${FLAT_PASSENGER_EVALS}`,
  },
];

const views = flatOnly ? flatViews : [...baseViews, ...flatViews];

function compactEsql(query) {
  return query.trim().replace(/\s+/g, " ");
}

// Correct ES|QL View API: PUT /_query/view/{name} with { "query": "..." }
// Reference: https://www.elastic.co/docs (Elasticsearch 9.4, ES|QL Views, Tech Preview)
async function viewPut(name, query) {
  const response = await fetch(`${esUrl}/_query/view/${encodeURIComponent(name)}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `ApiKey ${esKey}`,
    },
    body: JSON.stringify({ query: compactEsql(query) }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }
  return response.json();
}

function devToolsCommand(view) {
  return `PUT /_query/view/${view.name}\n{\n  "query": """\n${compactEsql(view.query)}\n  """\n}`;
}

async function createView(view) {
  if (isDryRun) {
    console.log(`\n# Kibana Dev Tools — paste as-is:`);
    console.log(devToolsCommand(view));
    console.log();
    return;
  }

  try {
    await viewPut(view.name, view.query);
    console.log(`created/updated view ${view.name}`);
  } catch (err) {
    if (err.message.includes("already exists") || err.message.includes("resource_already_exists")) {
      console.log(`view ${view.name} already exists — run DELETE /_query/view/${view.name} first to recreate`);
    } else {
      console.error(`view ${view.name} FAILED: ${err.message}`);
      console.log(`\nFallback — paste in Kibana Dev Tools:`);
      console.log(devToolsCommand(view));
      console.log();
    }
  }
}

async function checkVersion() {
  const response = await fetch(`${esUrl}/`, {
    headers: { "Authorization": `ApiKey ${esKey}` },
  });
  const data = await response.json();
  const version = data.version?.number || "unknown";
  console.log(`Elasticsearch version: ${version}`);
  return version;
}

async function listViews() {
  const response = await fetch(`${esUrl}/_query/view`, {
    headers: { "Authorization": `ApiKey ${esKey}` },
  });
  if (!response.ok) return null;
  return response.json();
}

console.log(isDryRun ? "Dry run — no changes will be made." : "Creating ES|QL views...");

if (!isDryRun) {
  await checkVersion();
}

for (const view of views) {
  await createView(view);
}

if (!isDryRun) {
  console.log("\nDone. Verifying deployed views...");
  const existing = await listViews();
  if (existing) {
    const names = (existing.views || existing).map(v => v.name || v).join(", ");
    console.log("Live views:", names || "(none)");
  }
  console.log("\nTest with:");
  console.log('  POST /_query { "query": "FROM dmr-cars | LIMIT 1" }');
  console.log('  POST /_query { "query": "FROM dmr-cars-flat | WHERE fuel == \\"El\\" | STATS COUNT(*) BY brand | LIMIT 5" }');
}
