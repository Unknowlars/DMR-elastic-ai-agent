#!/usr/bin/env python3
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "grafana" / "dashboards"
DS = {"type": "elasticsearch", "uid": "dmr-elasticsearch"}
TIME = {"from": "1900-01-01T00:00:00Z", "to": "now"}

BRAND = "KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.KoeretoejMaerkeTypeNavn.keyword"
MODEL = "KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.Model.KoeretoejModelTypeNavn.keyword"
BODY = "KoeretoejOplysningGrundStruktur.KarrosseriTypeStruktur.KarrosseriTypeNavn.keyword"
COLOR = "KoeretoejOplysningGrundStruktur.KoeretoejFarveStruktur.FarveTypeStruktur.FarveTypeNavn.keyword"
YEAR = "_foerste_registrering_aar"
FUEL = "_drivkraft_primaer"
STATUS = "KoeretoejRegistreringStatus.keyword"
ART = "KoeretoejArtNavn.keyword"
LEASE = "LeasingGyldigFra"
KW = "KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStoersteEffekt"
SPEED = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningMaksimumHastighed"
TOTAL_WEIGHT = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningTotalVaegt"
KERB_WEIGHT = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningKoereklarVaegtMinimum"
TOW_BRAKED = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtMedBremser"
SEATS = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningSiddepladserMinimum"
DRIVEN_AXLES = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningTraekkendeAkslerListe"
INSPECTION_RESULT = "SynResultatStruktur.SynResultatSynsResultat.keyword"
INSPECTION_DATE = "SynResultatStruktur.SynResultatSynsDato"
EMISSION_NORM = "KoeretoejOplysningGrundStruktur.KoeretoejNormStruktur.NormTypeStruktur.NormTypeNavn.keyword"
PARTICLE_FILTER = "KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningPartikelFilter"
VETERAN = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningVeteranKoeretoejOriginal"
NCAP = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningNCAPTest"
CO2 = "_co2_g_per_km_primaer"
KM_PER_LITER = "_km_per_liter_primaer"
MAALE_NORM = "_maale_norm_primaer"
USAGE = "KoeretoejAnvendelseStruktur.KoeretoejAnvendelseNavn.keyword"
DOORS = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningAntalDoere"
CYLINDERS = "KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorCylinderAntal"
DRIVE_NOISE = "KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorKoerselStoej"
STAND_NOISE = "KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStandStoej"
FRONT_TRACK = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningSporviddenForrest"
REAR_TRACK = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningSporviddenBagest"
NOX = "KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningEmissionNOX"
CO_EMIT = "KoeretoejOplysningGrundStruktur.KoeretoejMiljoeOplysningStruktur.KoeretoejMiljoeOplysningEmissionCO"
INSP_KM = "SynResultatStruktur.KoeretoejMotorKilometerstand"
PERMIT_TYPE = "TilladelseSamling.Tilladelse.TilladelseStruktur.TilladelseTypeStruktur.TilladelseTypeNavn.keyword"
TOW_BRAKED_RATIO_THRESH = 1.0
MAX_SPEED = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningMaksimumHastighed"
MODEL_YEAR = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningModelAar"
DISPLACEMENT = "KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorSlagVolumen"
TRAFIKSKADE = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningTrafikskade"
WHEELBASE = "KoeretoejOplysningGrundStruktur.KoeretoejOplysningAkselAfstand"
BLOCK_REASON = "KoeretoejOplysningGrundStruktur.KoeretoejBlokeringAarsagListeStruktur.KoeretoejBlokeringAarsag.KoeretoejBlokeringAarsagTypeNavn.keyword"

CURRENT_SCOPE = f'{STATUS} == "Registreret" AND {ART} == "Personbil"'
PASSENGER_SCOPE = f'{ART} == "Personbil"'
YEAR_FILTER = f"{YEAR} IS NOT NULL AND {YEAR} >= ${{year_from}} AND {YEAR} <= ${{year_to}}"
FUEL_FILTER = f'("${{fuel}}" == "All" OR {FUEL} == "${{fuel}}")'


def q(body):
    return f"FROM $__index | {body}"


def target(query, ref_id="A"):
    return {"query": query, "queryType": "esql", "refId": ref_id}


def field_config(unit="short", decimals=0, color_mode="palette-classic"):
    return {
        "defaults": {
            "color": {"mode": color_mode},
            "decimals": decimals,
            "unit": unit,
        },
        "overrides": [],
    }


def stat_options(color_mode="background"):
    return {
        "colorMode": color_mode,
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
        "textMode": "auto",
        "wideLayout": True,
    }


def bar_options(show_legend=False, stacking="none"):
    return {
        "legend": {"displayMode": "list", "placement": "bottom", "showLegend": show_legend},
        "orientation": "auto",
        "showValue": "auto",
        "stacking": stacking,
        "xTickLabelRotation": 0,
        "xTickLabelSpacing": 0,
    }


def timeseries_options(show_legend=True):
    return {
        "legend": {"displayMode": "list", "placement": "bottom", "showLegend": show_legend},
        "tooltip": {"mode": "single", "sort": "none"},
    }


def table_options():
    return {"cellHeight": "sm", "footer": {"countRows": False, "fields": "", "reducer": ["sum"], "show": False}, "showHeader": True}


def panel(panel_id, title, panel_type, x, y, w, h, query, unit="short", decimals=0, color_mode="palette-classic", stacking="none"):
    p = {
        "datasource": copy.deepcopy(DS),
        "fieldConfig": field_config(unit, decimals, "thresholds" if panel_type == "stat" else color_mode),
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "id": panel_id,
        "targets": [target(query)],
        "title": title,
        "type": panel_type,
    }
    if panel_type == "stat":
        p["options"] = stat_options()
    elif panel_type == "barchart":
        p["options"] = bar_options(stacking=stacking, show_legend=(stacking != "none"))
    elif panel_type == "timeseries":
        p["options"] = timeseries_options()
    elif panel_type == "table":
        p["options"] = table_options()
    return p


def dashboard(title, uid, description, panels, variables=None):
    for p in panels:
        gp = p["gridPos"]
        if gp["x"] + gp["w"] > 24:
            raise ValueError(f"Panel overflows grid: {title} / {p['title']}")
    return {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "description": description,
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": None,
        "links": [{"asDropdown": True, "includeVars": True, "keepTime": True, "tags": ["dmr"], "targetBlank": False, "title": "DMR dashboard suite", "type": "dashboards"}],
        "liveNow": False,
        "panels": panels,
        "refresh": "",
        "schemaVersion": 41,
        "style": "dark",
        "tags": ["dmr", "elasticsearch"],
        "templating": {"list": variables or []},
        "time": copy.deepcopy(TIME),
        "timepicker": {},
        "timezone": "browser",
        "title": title,
        "uid": uid,
        "version": 1,
        "weekStart": "",
    }


def custom_var(name, label, query_text, current, include_all=False, all_value=None):
    var = {
        "current": {"selected": True, "text": current, "value": current},
        "hide": 0,
        "label": label,
        "name": name,
        "options": [{"selected": value == current, "text": value, "value": value} for value in query_text.split(",")],
        "query": query_text,
        "type": "custom",
    }
    if include_all:
        var["includeAll"] = True
        var["allValue"] = all_value
    return var


def textbox_var(name, label, value):
    return {
        "current": {"selected": False, "text": value, "value": value},
        "hide": 0,
        "label": label,
        "name": name,
        "options": [{"selected": True, "text": value, "value": value}],
        "query": value,
        "type": "textbox",
    }


def fuel_year_vars():
    return [
        custom_var("fuel", "Fuel", "All,El,Benzin,Diesel,Plugin hybrid,Hybrid", "All"),
        textbox_var("year_from", "First registration from", "1900"),
        textbox_var("year_to", "First registration to", "2026"),
    ]


def year_vars():
    return [
        textbox_var("year_from", "First registration from", "1900"),
        textbox_var("year_to", "First registration to", "2026"),
    ]


def electrification():
    panels = [
        panel(1, "Registered Passenger Cars", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS registered_cars = COUNT(*)")),
        panel(2, "Electric Registered Passenger Cars", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS electric_cars = COUNT(*) WHERE {FUEL} == "El"')),
        panel(3, "EV Share of Registered Passenger Cars", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS total_cars = COUNT(*), electric_cars = COUNT(*) WHERE {FUEL} == "El" | EVAL ev_share = 1.0 * electric_cars / total_cars | KEEP ev_share'), "percentunit", 1),
        panel(4, "Diesel Registered Passenger Cars", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS diesel_cars = COUNT(*) WHERE {FUEL} == "Diesel"')),
        panel(5, "EV Leasing Rate (% of EVs Leased)", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "El" | STATS total_evs = COUNT(*), leased_evs = COUNT(*) WHERE {LEASE} IS NOT NULL | EVAL leased_ev_share = 1.0 * leased_evs / total_evs | KEEP leased_ev_share'), "percentunit", 1),
        panel(6, "EV Registrations by First Registration Year", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "El" AND {YEAR_FILTER} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS electric_cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(7, "Fuel Mix by First Registration Decade", "barchart", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL | EVAL decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*) BY decade, fuel = {FUEL} | SORT decade ASC, cars DESC | LIMIT 80'), stacking="normal"),
        panel(8, "EV and Diesel Share by Year", "timeseries", 0, 14, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), evs = COUNT(*) WHERE {FUEL} == "El", diesels = COUNT(*) WHERE {FUEL} == "Diesel" BY year_date | EVAL ev_share_pct = ROUND(evs * 100.0 / total, 1), diesel_share_pct = ROUND(diesels * 100.0 / total, 1) | KEEP year_date, ev_share_pct, diesel_share_pct | SORT year_date ASC'), "percent", 1),
        panel(9, "EV Share by Body Style", "barchart", 12, 14, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {BODY} IS NOT NULL | STATS total = COUNT(*), electric = COUNT(*) WHERE {FUEL} == "El" BY body_style = {BODY} | EVAL ev_share_pct = ROUND(electric * 100.0 / total, 1) | WHERE total >= 1000 | SORT ev_share_pct DESC | LIMIT 15'), "percent", 1),
        panel(10, "EV Brand Leaders", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} | STATS total_cars = COUNT(*), ev_cars = COUNT(*) WHERE {FUEL} == "El" BY brand = {BRAND} | WHERE total_cars >= 500 AND ev_cars >= 50 AND brand IS NOT NULL | EVAL ev_share_pct = ROUND(ev_cars * 100.0 / total_cars, 1) | SORT ev_cars DESC | LIMIT 25')),
        panel(11, "EV Model Leaders", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "El" AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS electric_cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | SORT electric_cars DESC | LIMIT 25')),
        panel(12, "EV Leasing by Brand", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "El" AND {BRAND} IS NOT NULL | STATS ev_cars = COUNT(*), leased_evs = COUNT(*) WHERE {LEASE} IS NOT NULL BY brand = {BRAND} | WHERE ev_cars >= 100 | EVAL leased_ev_share_pct = ROUND(leased_evs * 100.0 / ev_cars, 1) | SORT leased_evs DESC | LIMIT 25'), "percent", 1),
    ]
    return dashboard("DMR Electrification & Fuel Transition", "dmr-electrification-fuel-transition", "EV growth, diesel decline, fuel mix, EV leasing, and electric brand/model leaders for registered Danish passenger cars.", panels, year_vars())


def market():
    panels = [
        panel(1, "Registered Passenger Cars", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS registered_cars = COUNT(*)")),
        panel(2, "Leased Registered Passenger Cars", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS leased_cars = COUNT(*) WHERE {LEASE} IS NOT NULL")),
        panel(3, "Leased Share of Registered Passenger Cars", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS total_cars = COUNT(*), leased_cars = COUNT(*) WHERE {LEASE} IS NOT NULL | EVAL leased_share = 1.0 * leased_cars / total_cars | KEEP leased_share"), "percentunit", 1),
        panel(4, "Top 10 Brand Fleet Share", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | INLINE STATS fleet_cars = SUM(cars) | SORT cars DESC | LIMIT 10 | STATS top_10_cars = SUM(cars), fleet_cars = MAX(fleet_cars) | EVAL top_10_share = 1.0 * top_10_cars / fleet_cars | KEEP top_10_share"), "percentunit", 1),
        panel(5, "Ultra-Rare Brands (≤10 cars)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | WHERE cars <= 10 | STATS rare_brands = COUNT(*)")),
        panel(6, "Top Registered Passenger-Car Brands", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 15")),
        panel(7, "Top Registered Passenger-Car Models", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {MODEL} IS NOT NULL | STATS cars = COUNT(*) BY model = {MODEL} | SORT cars DESC | LIMIT 15")),
        panel(8, "Leasing Share by Fuel", "barchart", 0, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL} IS NOT NULL | STATS total = COUNT(*), leased = COUNT(*) WHERE {LEASE} IS NOT NULL BY fuel = {FUEL} | EVAL leased_share_pct = ROUND(leased * 100.0 / total, 1) | SORT total DESC | LIMIT 10"), "percent", 1),
        panel(9, "Vehicle Usage Mix", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {USAGE} IS NOT NULL | STATS cars = COUNT(*) BY usage = {USAGE} | SORT cars DESC | LIMIT 15")),
        panel(10, "Brand Concentration Curve", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 25")),
        panel(11, "Leasing by Brand", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS total_cars = COUNT(*), leased_cars = COUNT(*) WHERE {LEASE} IS NOT NULL BY brand = {BRAND} | WHERE total_cars >= 500 | EVAL leased_share_pct = ROUND(leased_cars * 100.0 / total_cars, 1) | SORT leased_cars DESC | LIMIT 30")),
        panel(12, "Niche Brands (≤25 registered cars)", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | WHERE cars <= 25 | SORT cars ASC, brand ASC | LIMIT 50")),
        panel(13, "Top Brand and Model Combinations", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | SORT cars DESC | LIMIT 40")),
    ]
    return dashboard("DMR Market, Leasing & Brands", "dmr-market-leasing-brands", "Market shape, leasing penetration, brand concentration, vehicle usage mix, and top brand/model views for registered Danish passenger cars.", panels, fuel_year_vars())


def performance():
    panels = [
        panel(1, "Cars With Valid Power", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL kw_clean = CLAMP({KW}, 1, 750) | STATS cars_with_power = COUNT(kw_clean)")),
        panel(2, "Average Power of Registered Passenger Cars", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL kw_clean = CLAMP({KW}, 1, 750) | STATS avg_power_kw = AVG(kw_clean)"), "kwatth", 0),
        panel(3, "AWD/4WD Registered Passenger Cars", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS awd_4wd_cars = COUNT(*) WHERE {DRIVEN_AXLES} == 2")),
        panel(4, "Tow-Capable Registered Passenger Cars", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL tow = CASE({TOW_BRAKED} > 0 AND {TOW_BRAKED} <= 5000, {TOW_BRAKED}, NULL) | STATS tow_capable_cars = COUNT(tow)")),
        panel(5, "High-Power Cars (≥220 kW)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL kw_clean = CLAMP({KW}, 1, 750) | STATS high_power_cars = COUNT(*) WHERE kw_clean >= 220")),
        panel(6, "Power Tiers of Registered Passenger Cars", "barchart", 0, 5, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL kw_clean = CLAMP({KW}, 1, 750), power_tier = CASE(kw_clean < 75, "<75 kW", kw_clean < 110, "75-109 kW", kw_clean < 150, "110-149 kW", kw_clean < 220, "150-219 kW", "220+ kW") | STATS cars = COUNT(*) BY power_tier | SORT cars DESC')),
        panel(7, "Average Power by Fuel", "barchart", 8, 5, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL | EVAL kw_clean = CLAMP({KW}, 1, 750) | STATS cars = COUNT(kw_clean), avg_power_kw = AVG(kw_clean), p90_power_kw = PERCENTILE(kw_clean, 90) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_power_kw DESC"), "kwatth", 0),
        panel(8, "Average Weight by First Registration Year", "timeseries", 16, 5, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), total_weight = CASE({TOTAL_WEIGHT} >= 300 AND {TOTAL_WEIGHT} <= 10000, {TOTAL_WEIGHT}, NULL) | STATS avg_total_weight_kg = AVG(total_weight) BY year_date | SORT year_date ASC'), "kg", 0),
        panel(9, "Body Styles", "barchart", 0, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY body_style = {BODY} | SORT cars DESC | LIMIT 15")),
        panel(10, "Seat Count Distribution", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} | EVAL seats = {SEATS}, seat_bucket = CASE(seats IS NULL, "Missing", seats < 1 OR seats > 9, "Invalid", TO_STRING(ROUND(seats, 0))) | STATS cars = COUNT(*) BY seat_bucket | SORT cars DESC | LIMIT 15')),
        panel(11, "AWD/4WD Share by Fuel", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL | STATS total = COUNT(*), awd_4wd = COUNT(*) WHERE {DRIVEN_AXLES} == 2 BY fuel = {FUEL} | EVAL awd_share_pct = ROUND(awd_4wd * 100.0 / total, 1) | SORT total DESC | LIMIT 10"), "percent", 1),
        panel(12, "Best Towing Brands", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL | EVAL braked_towing_weight = CLAMP({TOW_BRAKED}, 0, 5000) | WHERE braked_towing_weight > 0 | STATS tow_capable_cars = COUNT(*), avg_braked_towing_weight = AVG(braked_towing_weight), p90_braked_towing_weight = PERCENTILE(braked_towing_weight, 90) BY brand = {BRAND} | WHERE tow_capable_cars >= 100 | SORT avg_braked_towing_weight DESC | LIMIT 30")),
        panel(13, "High-Power Brands", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL | EVAL kw_clean = CLAMP({KW}, 1, 750) | STATS cars_with_power = COUNT(kw_clean), avg_power_kw = AVG(kw_clean), p90_power_kw = PERCENTILE(kw_clean, 90) BY brand = {BRAND} | WHERE cars_with_power >= 100 | SORT avg_power_kw DESC | LIMIT 30")),
        panel(14, "AWD/4WD Brands", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL | STATS total_cars = COUNT(*), awd_4wd_cars = COUNT(*) WHERE {DRIVEN_AXLES} == 2 BY brand = {BRAND} | WHERE total_cars >= 500 | EVAL awd_share_pct = ROUND(awd_4wd_cars * 100.0 / total_cars, 1) | SORT awd_4wd_cars DESC | LIMIT 30")),
    ]
    return dashboard("DMR Performance & Practicality", "dmr-performance-practicality", "Power, weight, drivetrain, towing, seats, and body-style practicality for registered Danish passenger cars.", panels, fuel_year_vars())


def inspection():
    panels = [
        panel(1, "Inspection Outcome Records", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {INSPECTION_RESULT} IS NOT NULL | STATS inspection_outcome_records = COUNT(*)")),
        panel(2, "Approved Inspection Results", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {INSPECTION_RESULT} IS NOT NULL | STATS approved_results = COUNT(*) WHERE {INSPECTION_RESULT} == "Godkendt"')),
        panel(3, "Known Emission Norm Cars", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {EMISSION_NORM} IS NOT NULL | STATS known_emission_norm_cars = COUNT(*)")),
        panel(4, "Diesels With Particle Filter Flag", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {PARTICLE_FILTER} IS NOT NULL | STATS diesel_particle_filter_records = COUNT(*) WHERE {PARTICLE_FILTER} == true')),
        panel(5, "NCAP-Tested Registered Passenger Cars", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} | STATS ncap_tested_cars = COUNT(*) WHERE {NCAP} == true")),
        panel(6, "Inspection Outcome Mix", "barchart", 0, 5, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {INSPECTION_RESULT} IS NOT NULL | STATS cars = COUNT(*) BY inspection_result = {INSPECTION_RESULT} | SORT cars DESC | LIMIT 10")),
        panel(7, "Inspection Outcome by Age Band", "barchart", 8, 5, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {INSPECTION_RESULT} IS NOT NULL | EVAL age_band = CASE({YEAR} >= 2020, "2020s", {YEAR} >= 2010, "2010s", {YEAR} >= 2000, "2000s", {YEAR} >= 1990, "1990s", "Before 1990") | STATS cars = COUNT(*) BY age_band, inspection_result = {INSPECTION_RESULT} | SORT age_band ASC, cars DESC | LIMIT 80')),
        panel(8, "Inspection Records by Inspection Year", "timeseries", 16, 5, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {INSPECTION_DATE} IS NOT NULL | EVAL inspection_year = DATE_EXTRACT("year", {INSPECTION_DATE}) | WHERE inspection_year >= 1990 AND inspection_year <= 2030 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING(inspection_year), "-01-01")) | STATS inspection_records = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(9, "Emission Norm Mix", "barchart", 0, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {EMISSION_NORM} IS NOT NULL | STATS cars = COUNT(*) BY emission_norm = {EMISSION_NORM} | SORT cars DESC | LIMIT 20")),
        panel(10, "Diesel Particle Filter Adoption by Year", "timeseries", 8, 14, 8, 9, q(f'WHERE {PASSENGER_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} IS NOT NULL AND {YEAR} >= 1995 AND {YEAR} <= 2026 AND {PARTICLE_FILTER} IS NOT NULL | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), with_particle_filter = COUNT(*) WHERE {PARTICLE_FILTER} == true BY year_date | EVAL filter_pct = ROUND(with_particle_filter * 100.0 / total, 1) | KEEP year_date, filter_pct | SORT year_date ASC'), "percent", 1),
        panel(11, "Inspection Coverage by Fuel", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL | STATS total = COUNT(*), with_inspection_result = COUNT(*) WHERE {INSPECTION_RESULT} IS NOT NULL BY fuel = {FUEL} | EVAL inspection_coverage_pct = ROUND(with_inspection_result * 100.0 / total, 1) | SORT total DESC | LIMIT 10"), "percent", 1),
        panel(12, "Inspection Pass Rate by Brand", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {INSPECTION_RESULT} IS NOT NULL | STATS inspected_cars = COUNT(*), approved = COUNT(*) WHERE {INSPECTION_RESULT} == "Godkendt" BY brand = {BRAND} | WHERE inspected_cars >= 500 | EVAL approved_share_pct = ROUND(approved * 100.0 / inspected_cars, 1) | SORT approved_share_pct DESC | LIMIT 30')),
        panel(13, "Emission Norm by Fuel", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {EMISSION_NORM} IS NOT NULL AND {FUEL} IS NOT NULL | STATS cars = COUNT(*) BY fuel = {FUEL}, emission_norm = {EMISSION_NORM} | SORT fuel ASC, cars DESC | LIMIT 80")),
        panel(14, "Brands Missing Inspection Result", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS total_cars = COUNT(*), missing_inspection = COUNT(*) WHERE {INSPECTION_RESULT} IS NULL BY brand = {BRAND} | WHERE total_cars >= 500 | EVAL missing_inspection_pct = ROUND(missing_inspection * 100.0 / total_cars, 1) | SORT missing_inspection DESC | LIMIT 30")),
    ]
    return dashboard("DMR Inspection & Compliance", "dmr-inspection-compliance", "Inspection outcomes, inspection coverage, emission norms, particle-filter adoption, and compliance-oriented data quality for registered Danish passenger cars.", panels, fuel_year_vars())


def history():
    panels = [
        panel(1, "All Passenger-Car Records", "stat", 0, 0, 5, 5, q(f"WHERE {PASSENGER_SCOPE} | STATS passenger_car_records_all_statuses = COUNT(*)")),
        panel(2, "Registered Veteran Passenger Cars", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS veteran_registered_cars = COUNT(*) WHERE {VETERAN} == true")),
        panel(3, "Oldest Registered First Year", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {YEAR} >= 1900 AND {YEAR} <= DATE_EXTRACT(\"year\", NOW()) | STATS oldest_registered_first_year = MIN({YEAR})"), "none", 0),
        panel(4, "Invalid or Missing Registration Year", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS invalid_or_missing_registration_year = COUNT(*) WHERE {YEAR} IS NULL OR {YEAR} < 1900 OR {YEAR} > DATE_EXTRACT(\"year\", NOW())")),
        panel(5, "Unknown Colour", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} | STATS unknown_colour = COUNT(*) WHERE {COLOR} == "Ukendt"')),
        panel(6, "Passenger-Car Records by First Registration Year (All Statuses)", "timeseries", 0, 5, 12, 9, q(f'WHERE {PASSENGER_SCOPE} AND {YEAR_FILTER} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS passenger_car_records = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(7, "Current Survivorship by Decade (All Passenger-Car Statuses)", "barchart", 12, 5, 12, 9, q(f'WHERE {PASSENGER_SCOPE} AND {YEAR_FILTER} | EVAL decade = CASE({YEAR} < 1950, "Before 1950", {YEAR} < 1960, "1950s", {YEAR} < 1970, "1960s", {YEAR} < 1980, "1970s", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS all_time = COUNT(*), currently_registered = COUNT(*) WHERE {STATUS} == "Registreret" BY decade | EVAL survival_pct = ROUND(currently_registered * 100.0 / all_time, 1) | SORT decade ASC | LIMIT 20'), "percent", 1),
        panel(8, "Current Registered Fleet by First Registration Decade", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} | EVAL decade = CASE({YEAR} < 1950, "Before 1950", {YEAR} < 1960, "1950s", {YEAR} < 1970, "1960s", {YEAR} < 1980, "1970s", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*) BY decade | SORT decade ASC')),
        panel(9, "Veteran Cars by Brand", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {VETERAN} == true AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 15")),
        panel(10, "Deregistered Passenger Cars by Year", "timeseries", 16, 14, 8, 9, q(f'WHERE {PASSENGER_SCOPE} AND {STATUS} == "Afmeldt" AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL dereg_year = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) | WHERE dereg_year >= 1990 AND dereg_year <= DATE_EXTRACT("year", NOW()) | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING(dereg_year), "-01-01")) | STATS deregistered_cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(11, "Oldest Current Brands", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {YEAR} IS NOT NULL | STATS current_count = COUNT(*), oldest_first_registration_year = MIN({YEAR}), avg_first_registration_year = AVG({YEAR}) BY brand = {BRAND} | WHERE current_count >= 5 | SORT oldest_first_registration_year ASC | LIMIT 30")),
        panel(12, "Newest Current Brands", "table", 8, 23, 8, 9, q(f"WHERE {PASSENGER_SCOPE} AND {BRAND} IS NOT NULL | STATS first_registered_year = MIN({YEAR}), current_count = COUNT(*) WHERE {STATUS} == \"Registreret\", all_time_count = COUNT(*) BY brand = {BRAND} | WHERE current_count >= 5 AND first_registered_year IS NOT NULL | SORT first_registered_year DESC | LIMIT 30")),
        panel(13, "Forgotten Brands (All Passenger-Car Statuses)", "table", 16, 23, 8, 9, q(f"WHERE {PASSENGER_SCOPE} AND {BRAND} IS NOT NULL | STATS all_time = COUNT(*), current = COUNT(*) WHERE {STATUS} == \"Registreret\" BY brand = {BRAND} | EVAL gone_pct = ROUND((all_time - current) * 100.0 / all_time, 1) | WHERE all_time >= 5000 AND gone_pct >= 90 | SORT all_time DESC | LIMIT 30")),
    ]
    return dashboard("DMR History & Heritage", "dmr-history-heritage", "All-status passenger-car history, survivorship, veteran cars, oldest/newest brands, deregistration trends, and historical long-tail brands.", panels, year_vars())


def environmental():
    panels = [
        panel(1, "Cars With CO2 Data", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {CO2} IS NOT NULL AND {CO2} > 0 | STATS cars_with_co2 = COUNT(*)")),
        panel(2, "Avg CO2 — Non-Electric (g/km)", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} != "El" AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_clean = CLAMP({CO2}, 1, 500) | STATS avg_co2_g_per_km = AVG(co2_clean)'), "short", 0),
        panel(3, "Zero-Emission Registered Cars", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND ({FUEL} == "El" OR {FUEL} == "Plugin hybrid") | STATS zero_emission_cars = COUNT(*)')),
        panel(4, "WLTP-Measured Registered Cars", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {MAALE_NORM} == "WLTP" | STATS wltp_measured_cars = COUNT(*)')),
        panel(5, "Avg Fuel Economy — Non-Electric (km/L)", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} != "El" AND {KM_PER_LITER} > 0 AND {KM_PER_LITER} < 50 | EVAL fuel_eco = CLAMP({KM_PER_LITER}, 1, 50) | STATS avg_km_per_liter = AVG(fuel_eco)'), "short", 1),
        panel(6, "CO2 Trend by First Registration Year (Non-Electric)", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} != "El" AND {CO2} > 0 AND {CO2} < 500 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), co2_clean = CLAMP({CO2}, 1, 500) | STATS avg_co2_g_per_km = AVG(co2_clean) BY year_date | SORT year_date ASC')),
        panel(7, "Average CO2 by Fuel Type", "barchart", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {FUEL} != "El" AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_clean = CLAMP({CO2}, 1, 500) | STATS cars = COUNT(*), avg_co2_g_per_km = AVG(co2_clean) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_co2_g_per_km ASC | LIMIT 10')),
        panel(8, "CO2 Tier Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_tier = CASE({CO2} < 50, "<50 g/km", {CO2} < 100, "50-99 g/km", {CO2} < 130, "100-129 g/km", {CO2} < 160, "130-159 g/km", {CO2} < 200, "160-199 g/km", "200+ g/km") | STATS cars = COUNT(*) BY co2_tier | SORT cars DESC')),
        panel(9, "Avg CO2 by Body Style (Non-Electric)", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {FUEL} != "El" AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_clean = CLAMP({CO2}, 1, 500) | STATS cars = COUNT(*), avg_co2_g_per_km = AVG(co2_clean) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_co2_g_per_km ASC | LIMIT 15')),
        panel(10, "Measurement Norm Distribution", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {MAALE_NORM} IS NOT NULL | STATS cars = COUNT(*) BY maale_norm = {MAALE_NORM} | SORT cars DESC | LIMIT 15')),
        panel(11, "Cleanest Non-EV Brands (Avg CO2)", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} != "El" AND {BRAND} IS NOT NULL AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_clean = CLAMP({CO2}, 1, 500) | STATS cars = COUNT(*), avg_co2_g_per_km = AVG(co2_clean) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_co2_g_per_km ASC | LIMIT 25')),
        panel(12, "Highest CO2 Brand-Model Combinations", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} != "El" AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_clean = CLAMP({CO2}, 1, 500) | STATS cars = COUNT(*), avg_co2_g_per_km = AVG(co2_clean) BY brand = {BRAND}, model = {MODEL} | WHERE cars >= 50 | SORT avg_co2_g_per_km DESC | LIMIT 25')),
        panel(13, "Avg CO2 by Registration Decade", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {FUEL} != "El" AND {CO2} > 0 AND {CO2} < 500 | EVAL co2_clean = CLAMP({CO2}, 1, 500), decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*), avg_co2_g_per_km = AVG(co2_clean) BY decade | SORT decade ASC | LIMIT 10')),
    ]
    return dashboard("DMR Environmental Profile", "dmr-environmental-profile", "CO2 emissions, fuel economy, measurement norms, and environmental benchmarks for registered Danish passenger cars.", panels, fuel_year_vars())


def body_colour():
    panels = [
        panel(1, "Registered Passenger Cars", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS registered_cars = COUNT(*)")),
        panel(2, "Grey/Silver Registered Cars", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS grey_silver_cars = COUNT(*) WHERE {COLOR} == "Grå"')),
        panel(3, "Grey/Silver Share of Registered Passenger Cars", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS total = COUNT(*), grey_silver_cars = COUNT(*) WHERE {COLOR} == "Grå" | EVAL grey_silver_share = 1.0 * grey_silver_cars / total | KEEP grey_silver_share'), "percentunit", 1),
        panel(4, "Unknown Color", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS unknown_colour = COUNT(*) WHERE {COLOR} == "Ukendt"')),
        panel(5, "Missing Body Style", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} | STATS missing_body_style = COUNT(*) WHERE {BODY} IS NULL")),
        panel(6, "Color Distribution (Top 15, Known Only)", "barchart", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" | STATS cars = COUNT(*) BY color = {COLOR} | SORT cars DESC | LIMIT 15')),
        panel(7, "Body Style Distribution", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY body_style = {BODY} | SORT cars DESC | LIMIT 15")),
        panel(8, "Grey/Silver Share by First Registration Year", "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {YEAR} >= 1990 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), grey_cars = COUNT(*) WHERE {COLOR} == "Grå" BY year_date | EVAL grey_share_pct = ROUND(grey_cars * 100.0 / total, 1) | KEEP year_date, grey_share_pct | SORT year_date ASC'), "percent", 1),
        panel(9, "Body Style by First Registration Decade", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL | EVAL decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*) BY decade, body_style = {BODY} | SORT decade ASC, cars DESC | LIMIT 80'), stacking="normal"),
        panel(10, "Door Count Distribution", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {DOORS} IS NOT NULL | EVAL door_bucket = CASE({DOORS} == 2, "2-door", {DOORS} == 3, "3-door", {DOORS} == 4, "4-door", {DOORS} == 5, "5-door", {DOORS} == 6, "6-door", "Other") | STATS cars = COUNT(*) BY door_bucket | SORT cars DESC | LIMIT 10')),
        panel(11, "Color by Brand", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND}, color = {COLOR} | SORT cars DESC | LIMIT 50')),
        panel(12, "Color by Body Style", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" | STATS cars = COUNT(*) BY body_style = {BODY}, color = {COLOR} | SORT cars DESC | LIMIT 50')),
        panel(13, "Grey, White & Black Share by First Registration Year", "timeseries", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {YEAR} >= 1990 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), grey = COUNT(*) WHERE {COLOR} == "Grå", white = COUNT(*) WHERE {COLOR} == "Hvid", black = COUNT(*) WHERE {COLOR} == "Sort" BY year_date | EVAL grey_pct = ROUND(grey * 100.0 / total, 1), white_pct = ROUND(white * 100.0 / total, 1), black_pct = ROUND(black * 100.0 / total, 1) | KEEP year_date, grey_pct, white_pct, black_pct | SORT year_date ASC'), "percent", 1),
    ]
    return dashboard("DMR Body, Colour & Consumer Preferences", "dmr-body-colour-preferences", "Colour distribution, grey/silver dominance, body style evolution, door counts, and colour-by-brand breakdown for registered Danish passenger cars.", panels, fuel_year_vars())


def engine_extinction():
    panels = [
        panel(1,  "Zero-Cylinder Cars (EVs)",                        "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {CYLINDERS} IS NOT NULL | STATS zero_cyl_cars = COUNT(*) WHERE {CYLINDERS} == 0")),
        panel(2,  "Three-Cylinder Cars",                             "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {CYLINDERS} IS NOT NULL | STATS three_cyl_cars = COUNT(*) WHERE {CYLINDERS} == 3")),
        panel(3,  "Four-Cylinder Cars",                              "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {CYLINDERS} IS NOT NULL | STATS four_cyl_cars = COUNT(*) WHERE {CYLINDERS} == 4")),
        panel(4,  "Six-Plus Cylinder Cars",                          "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {CYLINDERS} IS NOT NULL | STATS six_plus_cyl_cars = COUNT(*) WHERE {CYLINDERS} >= 6")),
        panel(5,  "Cars With Cylinder Data",                         "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {CYLINDERS} IS NOT NULL | STATS cars_with_cylinder_data = COUNT(*)")),
        panel(6,  "Cylinder Count Distribution",                     "barchart",   0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL | EVAL cyl_group = CASE({CYLINDERS} == 0, "0 (EV)", {CYLINDERS} == 3, "3", {CYLINDERS} == 4, "4", {CYLINDERS} == 6, "6", {CYLINDERS} == 8, "8", {CYLINDERS} >= 10, "10+", "Other (1,2,5,7)") | STATS cars = COUNT(*) BY cyl_group | SORT cars DESC')),
        panel(7,  "Cylinder Groups by First Registration Decade",    "barchart",  12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL | EVAL decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s"), cyl_group = CASE({CYLINDERS} == 0, "0-cyl (EV)", {CYLINDERS} <= 3, "1-3 cyl", {CYLINDERS} == 4, "4-cyl", {CYLINDERS} == 6, "6-cyl", {CYLINDERS} >= 8, "8+-cyl", "Other") | STATS cars = COUNT(*) BY decade, cyl_group | SORT decade ASC, cars DESC | LIMIT 80'), stacking="normal"),
        panel(8,  "Avg Cylinder Count by First Registration Year",   "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_cylinders = AVG({CYLINDERS}) BY year_date | SORT year_date ASC')),
        panel(9,  "Zero-Cylinder (EV) Share by Year",                "timeseries", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), zero_cyl = COUNT(*) WHERE {CYLINDERS} == 0 BY year_date | EVAL zero_cyl_pct = ROUND(zero_cyl * 100.0 / total, 1) | KEEP year_date, zero_cyl_pct | SORT year_date ASC'), "percent", 1),
        panel(10, "Six-Plus Cylinder Share by Year (Extinction Arc)", "timeseries",16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), six_plus = COUNT(*) WHERE {CYLINDERS} >= 6 BY year_date | EVAL six_plus_pct = ROUND(six_plus * 100.0 / total, 1) | KEEP year_date, six_plus_pct | SORT year_date ASC'), "percent", 1),
        panel(11, "Brands With Most 8+ Cylinder Cars",               "table",      0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {CYLINDERS} >= 8 AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 25")),
        panel(12, "Brands With Highest Zero-Cylinder (EV) Share",    "table",      8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL AND {BRAND} IS NOT NULL | STATS total = COUNT(*), zero_cyl = COUNT(*) WHERE {CYLINDERS} == 0 BY brand = {BRAND} | WHERE total >= 500 | EVAL zero_cyl_pct = ROUND(zero_cyl * 100.0 / total, 1) | SORT zero_cyl_pct DESC | LIMIT 25")),
        panel(13, "Cylinder Count by Fuel Type",                     "table",     16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {CYLINDERS} IS NOT NULL AND {FUEL} IS NOT NULL | STATS cars = COUNT(*) BY fuel = {FUEL}, cylinders = {CYLINDERS} | SORT fuel ASC, cars DESC | LIMIT 60")),
    ]
    return dashboard("DMR Engine Extinction Event", "dmr-engine-extinction", "The cylinder count revolution: 0-cylinder EVs, the 3-cylinder turbo takeover, and the decline of V6/V8 in registered Danish passenger cars.", panels, fuel_year_vars())


def paper_speed():
    spd = f"CLAMP({MAX_SPEED}, 80, 350)"
    panels = [
        panel(1,  "Cars With Speed Data",                            "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS cars_with_speed_data = COUNT(*)")),
        panel(2,  "Avg Registered Max Speed (km/h)",                 "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS avg_max_speed_kmh = AVG({MAX_SPEED})")),
        panel(3,  "Cars Certified Over 200 km/h",                    "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS over_200_kmh = COUNT(*) WHERE {MAX_SPEED} > 200")),
        panel(4,  "Cars Certified Over 250 km/h",                    "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS over_250_kmh = COUNT(*) WHERE {MAX_SPEED} > 250")),
        panel(5,  "Cars Certified Over 300 km/h",                    "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS over_300_kmh = COUNT(*) WHERE {MAX_SPEED} > 300")),
        panel(6,  "Max Speed Distribution",                          "barchart",   0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | EVAL speed_tier = CASE({MAX_SPEED} < 140, "<140 km/h", {MAX_SPEED} < 160, "140-159 km/h", {MAX_SPEED} < 180, "160-179 km/h", {MAX_SPEED} < 200, "180-199 km/h", {MAX_SPEED} < 220, "200-219 km/h", {MAX_SPEED} < 250, "220-249 km/h", "250+ km/h") | STATS cars = COUNT(*) BY speed_tier | SORT cars DESC')),
        panel(7,  "Avg Registered Max Speed by Fuel Type",           "barchart",  12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS cars = COUNT(*), avg_max_speed_kmh = AVG({MAX_SPEED}) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_max_speed_kmh DESC | LIMIT 10')),
        panel(8,  "Avg Registered Max Speed by First Registration Year", "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_max_speed_kmh = AVG({MAX_SPEED}) BY year_date | SORT year_date ASC')),
        panel(9,  "200+ km/h Certified Share by Year",               "timeseries", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), over_200 = COUNT(*) WHERE {MAX_SPEED} > 200 BY year_date | EVAL over_200_pct = ROUND(over_200 * 100.0 / total, 1) | KEEP year_date, over_200_pct | SORT year_date ASC'), "percent", 1),
        panel(10, "Avg Max Speed by Body Style",                     "barchart",  16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS cars = COUNT(*), avg_max_speed_kmh = AVG({MAX_SPEED}) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_max_speed_kmh DESC | LIMIT 15')),
        panel(11, "Fastest Brands (Avg Certified Max Speed)",        "table",      0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS cars = COUNT(*), avg_max_speed_kmh = AVG({MAX_SPEED}), p90_max_speed_kmh = PERCENTILE({MAX_SPEED}, 90) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_max_speed_kmh DESC | LIMIT 25')),
        panel(12, "Most Conservative Brands (Lowest Certified Speed)","table",     8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {MAX_SPEED} >= 80 AND {MAX_SPEED} <= 350 | STATS cars = COUNT(*), avg_max_speed_kmh = AVG({MAX_SPEED}) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_max_speed_kmh ASC | LIMIT 25')),
        panel(13, "Speed Over 250 km/h by Brand",                    "table",     16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {MAX_SPEED} > 250 AND {MAX_SPEED} <= 350 | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 25')),
    ]
    return dashboard("DMR Paper Speed Records", "dmr-paper-speed", "Every registered Danish passenger car has a certified max speed — the average is 185 km/h on roads with a 130 km/h limit. Who holds the paper records?", panels, fuel_year_vars())


def acoustic_profile():
    noise_filter = f"{DRIVE_NOISE} >= 50 AND {DRIVE_NOISE} <= 110"
    panels = [
        panel(1,  "Cars With Driving Noise Data",                    "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {noise_filter} | STATS cars_with_noise_data = COUNT(*)")),
        panel(2,  "Avg Fleet Driving Noise (dB(A))",                 "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {noise_filter} | EVAL noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS avg_driving_noise_db = AVG(noise_clean)")),
        panel(3,  "Cars Quieter Than 65 dB(A)",                      "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {noise_filter} | STATS quiet_cars = COUNT(*) WHERE {DRIVE_NOISE} < 65")),
        panel(4,  "Cars Louder Than 75 dB(A)",                       "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {noise_filter} | STATS loud_cars = COUNT(*) WHERE {DRIVE_NOISE} > 75")),
        panel(5,  "EV Avg Driving Noise (dB(A))",                    "stat",      20,  0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "El" AND {noise_filter} | EVAL noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS ev_avg_noise_db = AVG(noise_clean)')),
        panel(6,  "Driving Noise Distribution",                      "barchart",   0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {noise_filter} | EVAL noise_tier = CASE({DRIVE_NOISE} < 60, "<60 dB", {DRIVE_NOISE} < 65, "60-64 dB", {DRIVE_NOISE} < 70, "65-69 dB", {DRIVE_NOISE} < 75, "70-74 dB", {DRIVE_NOISE} < 80, "75-79 dB", "80+ dB") | STATS cars = COUNT(*) BY noise_tier | SORT cars DESC')),
        panel(7,  "Avg Driving Noise by Fuel Type",                  "barchart",  12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {noise_filter} | EVAL noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS cars = COUNT(*), avg_noise_db = AVG(noise_clean) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_noise_db ASC | LIMIT 10')),
        panel(8,  "Avg Driving Noise by First Registration Year",    "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {noise_filter} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS avg_noise_db = AVG(noise_clean) BY year_date | SORT year_date ASC')),
        panel(9,  "EV vs Petrol Noise Trend by Year",                "timeseries", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {noise_filter} AND ({FUEL} == "El" OR {FUEL} == "Benzin") | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS avg_noise_db = AVG(noise_clean) BY year_date, fuel = {FUEL} | SORT year_date ASC | LIMIT 80')),
        panel(10, "Avg Driving Noise by Body Style",                 "barchart",  16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {noise_filter} | EVAL noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS cars = COUNT(*), avg_noise_db = AVG(noise_clean) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_noise_db ASC | LIMIT 15')),
        panel(11, "Quietest Brands (Avg Driving Noise)",             "table",      0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {noise_filter} | EVAL noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS cars = COUNT(*), avg_noise_db = AVG(noise_clean) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_noise_db ASC | LIMIT 25')),
        panel(12, "Loudest Brands (Avg Driving Noise)",              "table",      8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {noise_filter} | EVAL noise_clean = CLAMP({DRIVE_NOISE}, 50, 110) | STATS cars = COUNT(*), avg_noise_db = AVG(noise_clean) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_noise_db DESC | LIMIT 25')),
        panel(13, "Noise Below 65 dB — Share by Brand",             "table",     16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {noise_filter} | STATS total = COUNT(*), quiet_cars = COUNT(*) WHERE {DRIVE_NOISE} < 65 BY brand = {BRAND} | WHERE total >= 100 | EVAL quiet_share_pct = ROUND(quiet_cars * 100.0 / total, 1) | SORT quiet_share_pct DESC | LIMIT 25')),
    ]
    return dashboard("DMR Acoustic Fleet Profile", "dmr-acoustic-profile", "The Danish Motor Register records driving noise in dB(A). As EVs enter the fleet, Denmark's roads are measurably getting quieter — here is the proof.", panels, fuel_year_vars())


def model_year_lag():
    lag_filter = f"{MODEL_YEAR} IS NOT NULL AND {MODEL_YEAR} > 1900 AND {MODEL_YEAR} <= 2026 AND {YEAR} IS NOT NULL"
    panels = [
        panel(1,  "Cars With Model Year Data",                       "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {lag_filter} | STATS cars_with_model_year = COUNT(*)")),
        panel(2,  "Cars Registered Same Year as Model Year",         "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR} | STATS fresh_registrations = COUNT(*) WHERE lag == 0")),
        panel(3,  "Cars Registered 5+ Years After Model Year",       "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR} | STATS delayed_5plus = COUNT(*) WHERE lag >= 5")),
        panel(4,  "Cars Registered 20+ Years After Model Year",      "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR} | STATS classic_imports = COUNT(*) WHERE lag >= 20")),
        panel(5,  "Max Lag on Record (years)",                       "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR} | WHERE lag >= 0 AND lag <= 80 | STATS max_lag_years = MAX(lag)"), "none", 0),
        panel(6,  "Model Year Lag Distribution",                     "barchart",   0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR}, lag_bucket = CASE(lag < 0, "Pre-model (anomaly)", lag == 0, "Same year", lag == 1, "1 year", lag == 2, "2 years", lag <= 5, "3-5 years", lag <= 10, "6-10 years", lag <= 20, "11-20 years", lag <= 30, "21-30 years", "31+ years") | STATS cars = COUNT(*) BY lag_bucket | SORT cars DESC')),
        panel(7,  "Avg Model Year Lag by First Registration Year",   "timeseries",12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR}, year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | WHERE lag >= 0 AND lag <= 50 | STATS avg_model_year_lag = AVG(lag) BY year_date | SORT year_date ASC')),
        panel(8,  "Brands With Longest Avg Model Year Lag",          "barchart",   0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {lag_filter} AND {BRAND} IS NOT NULL | EVAL lag = {YEAR} - {MODEL_YEAR} | WHERE lag >= 0 AND lag <= 60 | STATS cars = COUNT(*), avg_lag = AVG(lag) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_lag DESC | LIMIT 15')),
        panel(9,  "Brands With Shortest Avg Model Year Lag",         "barchart",   8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {lag_filter} AND {BRAND} IS NOT NULL | EVAL lag = {YEAR} - {MODEL_YEAR} | WHERE lag >= 0 AND lag <= 10 | STATS cars = COUNT(*), avg_lag = AVG(lag) BY brand = {BRAND} | WHERE cars >= 500 | SORT avg_lag ASC | LIMIT 15')),
        panel(10, "Lag > 20 Years by First Registration Decade",     "barchart",  16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {lag_filter} | EVAL lag = {YEAR} - {MODEL_YEAR}, decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | WHERE lag > 20 | STATS cars = COUNT(*) BY decade | SORT decade ASC')),
        panel(11, "Brands With Avg Lag by Car Count",                "table",      0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {lag_filter} AND {BRAND} IS NOT NULL | EVAL lag = {YEAR} - {MODEL_YEAR} | WHERE lag >= 0 AND lag <= 60 | STATS cars = COUNT(*), avg_lag_years = AVG(lag), max_lag_years = MAX(lag) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_lag_years DESC | LIMIT 30')),
        panel(12, "Time Travellers: 30+ Year Lag by Brand",          "table",      8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {lag_filter} AND {BRAND} IS NOT NULL | EVAL lag = {YEAR} - {MODEL_YEAR} | WHERE lag >= 30 | STATS cars = COUNT(*), max_lag_years = MAX(lag) BY brand = {BRAND} | SORT cars DESC | LIMIT 30')),
        panel(13, "Lag Distribution by Fuel Type",                   "table",     16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {lag_filter} AND {FUEL} IS NOT NULL | EVAL lag = {YEAR} - {MODEL_YEAR}, lag_bucket = CASE(lag == 0, "Same year", lag <= 2, "1-2 years", lag <= 5, "3-5 years", lag <= 10, "6-10 years", "10+ years") | WHERE lag >= 0 | STATS cars = COUNT(*) BY fuel = {FUEL}, lag_bucket | SORT fuel ASC, cars DESC | LIMIT 60')),
    ]
    return dashboard("DMR Model Year Time Machine", "dmr-model-year-lag", "How old was a car when first registered in Denmark? The max lag on record is 44 years. This dashboard reveals the import culture, classic car registrations, and data anomalies behind the numbers.", panels, fuel_year_vars())


def shrinking_engine():
    disp_filter = f"{DISPLACEMENT} > 0 AND {DISPLACEMENT} < 9000"
    panels = [
        panel(1,  "Cars With Displacement Data",                     "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {disp_filter} | STATS cars_with_displacement = COUNT(*)")),
        panel(2,  "Avg Engine Displacement (cc)",                    "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {disp_filter} | EVAL cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS avg_displacement_cc = AVG(cc)")),
        panel(3,  "Engines Over 2,000 cc",                           "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {disp_filter} | STATS large_engines = COUNT(*) WHERE {DISPLACEMENT} > 2000")),
        panel(4,  "Engines Under 1,000 cc",                          "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {disp_filter} | STATS micro_engines = COUNT(*) WHERE {DISPLACEMENT} < 1000")),
        panel(5,  "Engines 1,000–1,500 cc (Modern Sweet Spot)",      "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {disp_filter} | STATS sweet_spot_engines = COUNT(*) WHERE {DISPLACEMENT} >= 1000 AND {DISPLACEMENT} <= 1500")),
        panel(6,  "Displacement Distribution",                       "barchart",   0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {disp_filter} | EVAL cc_tier = CASE({DISPLACEMENT} < 500, "<500 cc", {DISPLACEMENT} < 1000, "500-999 cc", {DISPLACEMENT} < 1500, "1000-1499 cc", {DISPLACEMENT} < 2000, "1500-1999 cc", {DISPLACEMENT} < 3000, "2000-2999 cc", "3000+ cc") | STATS cars = COUNT(*) BY cc_tier | SORT cars DESC')),
        panel(7,  "Avg Displacement by Fuel Type",                   "barchart",  12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {disp_filter} | EVAL cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS cars = COUNT(*), avg_displacement_cc = AVG(cc) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_displacement_cc DESC | LIMIT 10')),
        panel(8,  "Avg Displacement by First Registration Year",     "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {disp_filter} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS avg_displacement_cc = AVG(cc) BY year_date | SORT year_date ASC')),
        panel(9,  "Displacement by First Registration Decade",       "barchart",   8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {disp_filter} | EVAL decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s"), cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS avg_displacement_cc = AVG(cc) BY decade | SORT decade ASC')),
        panel(10, "Avg Displacement by Body Style",                  "barchart",  16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {disp_filter} | EVAL cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS cars = COUNT(*), avg_displacement_cc = AVG(cc) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_displacement_cc DESC | LIMIT 15')),
        panel(11, "Biggest Engine Brands (Avg Displacement)",        "table",      0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {disp_filter} | EVAL cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS cars = COUNT(*), avg_displacement_cc = AVG(cc), max_displacement_cc = MAX(cc) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_displacement_cc DESC | LIMIT 25')),
        panel(12, "Smallest Engine Brands (Avg Displacement)",       "table",      8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {disp_filter} | EVAL cc = CLAMP({DISPLACEMENT}, 50, 9000) | STATS cars = COUNT(*), avg_displacement_cc = AVG(cc) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_displacement_cc ASC | LIMIT 25')),
        panel(13, "Displacement Under 1,000 cc by Brand",            "table",     16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {DISPLACEMENT} > 0 AND {DISPLACEMENT} < 1000 | STATS micro_engine_cars = COUNT(*) BY brand = {BRAND} | SORT micro_engine_cars DESC | LIMIT 25')),
    ]
    return dashboard("DMR Shrinking Engine", "dmr-shrinking-engine", "Average engine displacement is now 1,196 cc — barely over 1 litre. Denmark's engines have been shrinking for 30 years. This dashboard quantifies the downsizing from 2.0L naturals to 1.0T turbos to 0cc EVs.", panels, fuel_year_vars())


def weight_power():
    kw_ok = f"CLAMP({KW}, 1, 750)"
    wb_ok = f"CLAMP({KERB_WEIGHT}, 300, 4000)"
    panels = [
        panel(1,  "Cars With Weight & Power Data",                   "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {KW} >= 1 AND {KW} <= 750 AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | STATS cars_with_both = COUNT(*)")),
        panel(2,  "Avg Fleet Kerb Weight (kg)",                      "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL kg = CLAMP({KERB_WEIGHT}, 300, 4000) | STATS avg_kerb_weight_kg = AVG(kg)"), "kg", 0),
        panel(3,  "Avg Fleet Power (kW)",                            "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {KW} >= 1 AND {KW} <= 750 | EVAL kw_clean = CLAMP({KW}, 1, 750) | STATS avg_power_kw = AVG(kw_clean)"), "kwatth", 0),
        panel(4,  "Avg Power-to-Weight (kW/tonne)",                  "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {KW} >= 1 AND {KW} <= 750 AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL pw = CLAMP({KW}, 1, 750) / (CLAMP({KERB_WEIGHT}, 300, 4000) / 1000.0) | STATS avg_power_to_weight_kw_per_tonne = AVG(pw)"), "short", 0),
        panel(5,  "Cars Over 2,000 kg Kerb Weight",                  "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {KERB_WEIGHT} > 2000 AND {KERB_WEIGHT} <= 4000 | STATS heavy_cars = COUNT(*)")),
        panel(6,  "Avg Kerb Weight by First Registration Year",      "timeseries", 0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), kg = CLAMP({KERB_WEIGHT}, 300, 4000) | STATS avg_kerb_weight_kg = AVG(kg) BY year_date | SORT year_date ASC'), "kg", 0),
        panel(7,  "Power-to-Weight by Fuel Type",                    "barchart",  12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {KW} >= 1 AND {KW} <= 750 AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL pw = CLAMP({KW}, 1, 750) / (CLAMP({KERB_WEIGHT}, 300, 4000) / 1000.0) | STATS cars = COUNT(*), avg_pw_kw_per_tonne = AVG(pw) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_pw_kw_per_tonne DESC | LIMIT 10')),
        panel(8,  "Weight Distribution",                             "barchart",   0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL weight_tier = CASE({KERB_WEIGHT} < 900, "<900 kg", {KERB_WEIGHT} < 1100, "900-1099 kg", {KERB_WEIGHT} < 1300, "1100-1299 kg", {KERB_WEIGHT} < 1500, "1300-1499 kg", {KERB_WEIGHT} < 2000, "1500-1999 kg", "2000+ kg") | STATS cars = COUNT(*) BY weight_tier | SORT cars DESC')),
        panel(9,  "Avg Power-to-Weight by First Registration Year",  "timeseries", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {KW} >= 1 AND {KW} <= 750 AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), pw = CLAMP({KW}, 1, 750) / (CLAMP({KERB_WEIGHT}, 300, 4000) / 1000.0) | STATS avg_pw_kw_per_tonne = AVG(pw) BY year_date | SORT year_date ASC')),
        panel(10, "Power-to-Weight by Body Style",                   "barchart",  16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {KW} >= 1 AND {KW} <= 750 AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL pw = CLAMP({KW}, 1, 750) / (CLAMP({KERB_WEIGHT}, 300, 4000) / 1000.0) | STATS cars = COUNT(*), avg_pw_kw_per_tonne = AVG(pw) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_pw_kw_per_tonne DESC | LIMIT 15')),
        panel(11, "Heaviest Brands (Avg Kerb Weight)",               "table",      0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL kg = CLAMP({KERB_WEIGHT}, 300, 4000) | STATS cars = COUNT(*), avg_kerb_weight_kg = AVG(kg) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_kerb_weight_kg DESC | LIMIT 25')),
        panel(12, "Best Power-to-Weight Brands",                     "table",      8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {KW} >= 1 AND {KW} <= 750 AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL pw = CLAMP({KW}, 1, 750) / (CLAMP({KERB_WEIGHT}, 300, 4000) / 1000.0) | STATS cars = COUNT(*), avg_pw_kw_per_tonne = AVG(pw) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_pw_kw_per_tonne DESC | LIMIT 25')),
        panel(13, "Lightest Brands (Avg Kerb Weight)",               "table",     16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {KERB_WEIGHT} >= 300 AND {KERB_WEIGHT} <= 4000 | EVAL kg = CLAMP({KERB_WEIGHT}, 300, 4000) | STATS cars = COUNT(*), avg_kerb_weight_kg = AVG(kg) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_kerb_weight_kg ASC | LIMIT 25')),
    ]
    return dashboard("DMR Fleet Weight & Power-to-Weight", "dmr-weight-power", "Cars are getting heavier decade by decade. Power is rising too. The power-to-weight ratio (kW/tonne) is the most honest performance metric at fleet scale — and it reveals which fuels and brands truly punch above their weight.", panels, fuel_year_vars())


def accident_files():
    panels = [
        panel(1,  "Traffic Accident Flagged Cars",                   "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL | STATS accident_flagged_cars = COUNT(*) WHERE {TRAFIKSKADE} == true")),
        panel(2,  "Cars With Accident Data Field",                   "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL | STATS cars_with_accident_data = COUNT(*)")),
        panel(3,  "Accident Flag Rate (% of Cars With Data)",        "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL | STATS total = COUNT(*), flagged = COUNT(*) WHERE {TRAFIKSKADE} == true | EVAL accident_flag_rate = 1.0 * flagged / total | KEEP accident_flag_rate"), "percentunit", 2),
        panel(4,  "Accident-Flagged Cars — Pre-2010 Registration",   "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {YEAR} IS NOT NULL AND {YEAR} < 2010 | STATS older_accident_flagged = COUNT(*) WHERE {TRAFIKSKADE} == true")),
        panel(5,  "Accident-Flagged Cars — 2020s Registration",      "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {YEAR} IS NOT NULL AND {YEAR} >= 2020 | STATS recent_accident_flagged = COUNT(*) WHERE {TRAFIKSKADE} == true")),
        panel(6,  "Accident Flag Rate by Brand",                     "barchart",   0,  5,12, 9, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {BRAND} IS NOT NULL | STATS total = COUNT(*), flagged = COUNT(*) WHERE {TRAFIKSKADE} == true BY brand = {BRAND} | WHERE total >= 500 AND flagged > 0 | EVAL flag_rate_pct = ROUND(flagged * 100.0 / total, 2) | SORT flag_rate_pct DESC | LIMIT 20"), "percent", 2),
        panel(7,  "Accident Flag Rate by Car Age Band",              "barchart",  12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {YEAR} IS NOT NULL | EVAL age_band = CASE({YEAR} >= 2020, "2020s", {YEAR} >= 2010, "2010s", {YEAR} >= 2000, "2000s", {YEAR} >= 1990, "1990s", "Pre-1990") | STATS total = COUNT(*), flagged = COUNT(*) WHERE {TRAFIKSKADE} == true BY age_band | EVAL flag_rate_pct = ROUND(flagged * 100.0 / total, 2) | SORT age_band ASC | LIMIT 10'), "percent", 2),
        panel(8,  "Accident-Flagged Cars by First Registration Year", "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} == true AND {YEAR} IS NOT NULL | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS accident_flagged = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(9,  "Accident Flag Rate by Fuel Type",                 "barchart",   8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {FUEL} IS NOT NULL | STATS total = COUNT(*), flagged = COUNT(*) WHERE {TRAFIKSKADE} == true BY fuel = {FUEL} | WHERE total >= 500 | EVAL flag_rate_pct = ROUND(flagged * 100.0 / total, 2) | SORT flag_rate_pct DESC | LIMIT 10"), "percent", 2),
        panel(10, "Accident Flag Rate by Body Style",                 "barchart",  16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {BODY} IS NOT NULL | STATS total = COUNT(*), flagged = COUNT(*) WHERE {TRAFIKSKADE} == true BY body_style = {BODY} | WHERE total >= 500 AND flagged > 0 | EVAL flag_rate_pct = ROUND(flagged * 100.0 / total, 2) | SORT flag_rate_pct DESC | LIMIT 15"), "percent", 2),
        panel(11, "Most Accident-Flagged Brands (Count)",            "table",      0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} == true AND {BRAND} IS NOT NULL | STATS accident_flagged_cars = COUNT(*) BY brand = {BRAND} | SORT accident_flagged_cars DESC | LIMIT 25")),
        panel(12, "Brands With Highest Accident Flag Rate",          "table",      8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {BRAND} IS NOT NULL | STATS total = COUNT(*), flagged = COUNT(*) WHERE {TRAFIKSKADE} == true BY brand = {BRAND} | WHERE total >= 500 AND flagged > 0 | EVAL flag_rate_pct = ROUND(flagged * 100.0 / total, 2) | SORT flag_rate_pct DESC | LIMIT 25")),
        panel(13, "Accident-Flagged Cars by Registration Decade",      "table",   16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} == true AND {YEAR} IS NOT NULL | EVAL decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS accident_flagged_cars = COUNT(*) BY decade | SORT decade ASC')),
    ]
    return dashboard("DMR Accident & Damage Files", "dmr-accident-files", "3,866 currently registered Danish passenger cars carry a traffic accident flag. This dashboard maps the damage — by brand, fuel, age, and administrative blocking status.", panels, fuel_year_vars())


def wheelbase_creep():
    wb_filter = f"{WHEELBASE} >= 1500 AND {WHEELBASE} <= 4000"
    panels = [
        panel(1,  "Cars With Wheelbase Data",                        "stat",       0,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {wb_filter} | STATS cars_with_wheelbase = COUNT(*)")),
        panel(2,  "Avg Fleet Wheelbase (mm)",                        "stat",       5,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {wb_filter} | EVAL wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS avg_wheelbase_mm = AVG(wb)")),
        panel(3,  "Cars Over 2,800 mm Wheelbase (Full-Size)",        "stat",      10,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {wb_filter} | STATS full_size_cars = COUNT(*) WHERE {WHEELBASE} > 2800")),
        panel(4,  "Cars Over 3,000 mm Wheelbase",                    "stat",      15,  0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {wb_filter} | STATS long_cars = COUNT(*) WHERE {WHEELBASE} > 3000")),
        panel(5,  "City Cars Under 2,400 mm Wheelbase",              "stat",      20,  0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {wb_filter} | STATS city_cars = COUNT(*) WHERE {WHEELBASE} < 2400")),
        panel(6,  "Wheelbase Distribution",                          "barchart",   0,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {wb_filter} | EVAL wb_tier = CASE({WHEELBASE} < 2200, "<2200 mm", {WHEELBASE} < 2400, "2200-2399 mm", {WHEELBASE} < 2600, "2400-2599 mm", {WHEELBASE} < 2800, "2600-2799 mm", {WHEELBASE} < 3000, "2800-2999 mm", "3000+ mm") | STATS cars = COUNT(*) BY wb_tier | SORT cars DESC')),
        panel(7,  "Avg Wheelbase by First Registration Year",        "timeseries",12,  5,12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {wb_filter} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS avg_wheelbase_mm = AVG(wb) BY year_date | SORT year_date ASC')),
        panel(8,  "Avg Wheelbase by Body Style",                     "barchart",   0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {BODY} IS NOT NULL AND {wb_filter} | EVAL wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS cars = COUNT(*), avg_wheelbase_mm = AVG(wb) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_wheelbase_mm DESC | LIMIT 15')),
        panel(9,  "Avg Wheelbase by Fuel Type",                      "barchart",   8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {wb_filter} | EVAL wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS cars = COUNT(*), avg_wheelbase_mm = AVG(wb) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_wheelbase_mm DESC | LIMIT 10')),
        panel(10, "Avg Wheelbase by First Registration Decade",      "barchart",  16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {wb_filter} | EVAL decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s"), wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS avg_wheelbase_mm = AVG(wb) BY decade | SORT decade ASC')),
        panel(11, "Longest Wheelbase Brands",                        "table",      0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {wb_filter} | EVAL wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS cars = COUNT(*), avg_wheelbase_mm = AVG(wb), max_wheelbase_mm = MAX(wb) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_wheelbase_mm DESC | LIMIT 25')),
        panel(12, "Shortest Wheelbase Brands",                       "table",      8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {wb_filter} | EVAL wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS cars = COUNT(*), avg_wheelbase_mm = AVG(wb) BY brand = {BRAND} | WHERE cars >= 100 | SORT avg_wheelbase_mm ASC | LIMIT 25')),
        panel(13, "Wheelbase by Brand and Decade",                   "table",     16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {BRAND} IS NOT NULL AND {wb_filter} | EVAL decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s"), wb = CLAMP({WHEELBASE}, 1500, 4000) | STATS cars = COUNT(*), avg_wheelbase_mm = AVG(wb) BY brand = {BRAND}, decade | WHERE cars >= 100 | SORT brand ASC, decade ASC | LIMIT 60')),
    ]
    return dashboard("DMR Wheelbase Chronicles", "dmr-wheelbase-creep", "Parking spots haven't grown. Cars have. The average Danish passenger car wheelbase is 2,627 mm and rising — this dashboard tracks the size creep decade by decade across brands, fuels, and body styles.", panels, fuel_year_vars())


def fake_two_seater():
    panels = [
        panel(1, "1-Seat Passenger Cars (Yellow-Plate)", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS one_seat_cars = COUNT(*) WHERE {SEATS} == 1")),
        panel(2, "2-Seat Passenger Cars", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS two_seat_cars = COUNT(*) WHERE {SEATS} == 2")),
        panel(3, "1-Seat Share of Fleet", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS total = COUNT(*), one_seat = COUNT(*) WHERE {SEATS} == 1 | EVAL one_seat_share = 1.0 * one_seat / total | KEEP one_seat_share"), "percentunit", 1),
        panel(4, "5-Seat (Normal Family) Cars", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS five_seat_cars = COUNT(*) WHERE {SEATS} == 5")),
        panel(5, "Cars With Absurd Seat Count (>9)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} | STATS absurd_seat_cars = COUNT(*) WHERE {SEATS} > 9")),
        panel(6, "Seat Count Distribution", "barchart", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {SEATS} IS NOT NULL AND {SEATS} >= 0 AND {SEATS} <= 9 | STATS cars = COUNT(*) BY seats = {SEATS} | SORT seats ASC')),
        panel(7, "1-Seat Registrations by First Registration Year", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {YEAR_FILTER} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS one_seat_cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(8, "1-Seat Cars by Body Style", "barchart", 0, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY body_style = {BODY} | SORT cars DESC | LIMIT 12")),
        panel(9, "1-Seat Cars by Fuel", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {FUEL} IS NOT NULL | STATS cars = COUNT(*) BY fuel = {FUEL} | SORT cars DESC | LIMIT 10")),
        panel(10, "Seat Count by First Registration Decade", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {SEATS} IS NOT NULL | EVAL decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s"), seat_group = CASE({SEATS} == 1, "1", {SEATS} == 2, "2", {SEATS} <= 5, "3-5", {SEATS} <= 9, "6-9", "10+") | STATS cars = COUNT(*) BY decade, seat_group | SORT decade ASC, cars DESC | LIMIT 60'), stacking="normal"),
        panel(11, "Top 1-Seat Brands (Yellow-Plate Leaders)", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {BRAND} IS NOT NULL | STATS one_seat_cars = COUNT(*) BY brand = {BRAND} | SORT one_seat_cars DESC | LIMIT 25")),
        panel(12, "Top 1-Seat Models", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS one_seat_cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | SORT one_seat_cars DESC | LIMIT 25")),
        panel(13, "Brand 1-Seat Conversion Rate", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS total_cars = COUNT(*), one_seat = COUNT(*) WHERE {SEATS} == 1 BY brand = {BRAND} | WHERE total_cars >= 5000 | EVAL one_seat_pct = ROUND(one_seat * 100.0 / total_cars, 1) | SORT one_seat_pct DESC | LIMIT 25")),
    ]
    return dashboard("DMR Fake Two-Seater (Yellow-Plate Fleet)", "dmr-fake-two-seater", "364k registered passenger cars in Denmark have only ONE seat — the famous 'gulpladebiler', commercial-tax-converted hatchbacks where the rear seats were legally removed. This dashboard tracks Denmark's unique yellow-plate fleet.", panels, year_vars())


def tow_it_all():
    tow_ratio = f"{TOW_BRAKED} * 1.0 / {KERB_WEIGHT}"
    base_filter = f"{TOW_BRAKED} > 0 AND {TOW_BRAKED} <= 5000 AND {KERB_WEIGHT} > 300 AND {KERB_WEIGHT} <= 5000"
    panels = [
        panel(1, "Tow-Capable Passenger Cars", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} | STATS tow_capable = COUNT(*)")),
        panel(2, "Cars That Can Tow More Than They Weigh", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} | EVAL ratio = {tow_ratio} | STATS supercar_tow = COUNT(*) WHERE ratio >= 1.0")),
        panel(3, "Avg Tow-to-Weight Ratio", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} | EVAL ratio = {tow_ratio} | STATS avg_ratio = AVG(ratio)"), "short", 2),
        panel(4, "Max Braked Towing Capacity (kg)", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} | STATS max_tow_kg = MAX({TOW_BRAKED})"), "kg", 0),
        panel(5, "Cars With Tow Ratio ≥ 1.5×", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} | EVAL ratio = {tow_ratio} | STATS ultra_tow = COUNT(*) WHERE ratio >= 1.5")),
        panel(6, "Tow-to-Weight Ratio Distribution", "barchart", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {base_filter} | EVAL ratio = {tow_ratio}, tier = CASE(ratio < 0.5, "<0.5×", ratio < 1.0, "0.5-0.99×", ratio < 1.25, "1.0-1.24×", ratio < 1.5, "1.25-1.49×", ratio < 1.75, "1.5-1.74×", "1.75×+") | STATS cars = COUNT(*) BY tier | SORT cars DESC')),
        panel(7, "Avg Tow-to-Weight Ratio by Fuel", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} AND {FUEL} IS NOT NULL | EVAL ratio = {tow_ratio} | STATS cars = COUNT(*), avg_ratio = AVG(ratio) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_ratio DESC | LIMIT 10"), "short", 2),
        panel(8, "Avg Tow Capacity by First Registration Decade", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {base_filter} | EVAL decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*), avg_tow_kg = AVG({TOW_BRAKED}) BY decade | SORT decade ASC'), "kg", 0),
        panel(9, "Tow Ratio by Body Style", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} AND {BODY} IS NOT NULL | EVAL ratio = {tow_ratio} | STATS cars = COUNT(*), avg_ratio = AVG(ratio) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_ratio DESC | LIMIT 15"), "short", 2),
        panel(10, "Avg Tow Capacity by First Registration Year", "timeseries", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {base_filter} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_tow_kg = AVG({TOW_BRAKED}) BY year_date | SORT year_date ASC'), "kg", 0),
        panel(11, "Brands Tow > Own Weight (Count)", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} AND {BRAND} IS NOT NULL | EVAL ratio = {tow_ratio} | STATS tow_supercars = COUNT(*) WHERE ratio >= 1.0 BY brand = {BRAND} | WHERE tow_supercars >= 100 | SORT tow_supercars DESC | LIMIT 25")),
        panel(12, "Highest Avg Tow Ratio by Brand", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} AND {BRAND} IS NOT NULL | EVAL ratio = {tow_ratio} | STATS cars = COUNT(*), avg_ratio = AVG(ratio), max_tow_kg = MAX({TOW_BRAKED}) BY brand = {BRAND} | WHERE cars >= 500 | SORT avg_ratio DESC | LIMIT 25")),
        panel(13, "Most Extreme Tow Models", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {base_filter} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | EVAL ratio = {tow_ratio} | STATS cars = COUNT(*), avg_ratio = AVG(ratio) BY brand = {BRAND}, model = {MODEL} | WHERE cars >= 100 | SORT avg_ratio DESC | LIMIT 25")),
    ]
    return dashboard("DMR Tow-It-All Index", "dmr-tow-it-all", "Hundreds of thousands of Danish cars are certified to tow a braked trailer heavier than themselves. VW leads with 72k. Suzuki — the tiny Jimny effect — is in the top 3. This dashboard charts every car's tow-to-weight ratio.", panels, fuel_year_vars())


def sound_of_silence():
    drive_filter = f"{DRIVE_NOISE} > 30 AND {DRIVE_NOISE} < 150"
    stand_filter = f"{STAND_NOISE} >= 0 AND {STAND_NOISE} < 150"
    panels = [
        panel(1, "Cars With Stationary Noise Data", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {STAND_NOISE} IS NOT NULL | STATS cars_with_stand_noise = COUNT(*)")),
        panel(2, "Avg Stand Noise — Petrol (dB)", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Benzin" AND {stand_filter} | STATS avg_stand_db = AVG({STAND_NOISE})'), "short", 1),
        panel(3, "Avg Stand Noise — Diesel (dB)", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {stand_filter} | STATS avg_stand_db = AVG({STAND_NOISE})'), "short", 1),
        panel(4, "Avg Stand Noise — EV (dB)", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "El" AND {stand_filter} | STATS avg_stand_db = AVG({STAND_NOISE})'), "short", 2),
        panel(5, "Silent Cars (Stand Noise = 0)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {STAND_NOISE} == 0 | STATS silent_cars = COUNT(*)")),
        panel(6, "Avg Stand vs Drive Noise by Fuel", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {FUEL} IS NOT NULL AND {drive_filter} AND {stand_filter} | STATS cars = COUNT(*), avg_drive_db = AVG({DRIVE_NOISE}), avg_stand_db = AVG({STAND_NOISE}) BY fuel = {FUEL} | WHERE cars >= 100 | SORT cars DESC | LIMIT 10"), "short", 1),
        panel(7, "Avg Stationary Noise by First Registration Year", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {stand_filter} | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_stand_db = AVG({STAND_NOISE}) BY year_date | SORT year_date ASC'), "short", 1),
        panel(8, "Stationary Noise Tier Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {stand_filter} | EVAL tier = CASE({STAND_NOISE} == 0, "0 dB (silent)", {STAND_NOISE} < 50, "<50 dB", {STAND_NOISE} < 70, "50-69 dB", {STAND_NOISE} < 80, "70-79 dB", {STAND_NOISE} < 90, "80-89 dB", "90+ dB") | STATS cars = COUNT(*) BY tier | SORT cars DESC')),
        panel(9, "Drive-Minus-Stand Noise Gap by Fuel (Combustion Fingerprint)", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {FUEL} IS NOT NULL AND {drive_filter} AND {stand_filter} | EVAL gap = {DRIVE_NOISE} - {STAND_NOISE} | STATS cars = COUNT(*), avg_gap_db = AVG(gap) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_gap_db DESC | LIMIT 10"), "short", 1),
        panel(10, "EV Share by Stationary-Noise Tier", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {stand_filter} | EVAL tier = CASE({STAND_NOISE} == 0, "0 dB", {STAND_NOISE} < 50, "<50 dB", {STAND_NOISE} < 70, "50-69 dB", {STAND_NOISE} < 80, "70-79 dB", "80+ dB") | STATS total = COUNT(*), evs = COUNT(*) WHERE {FUEL} == "El" BY tier | EVAL ev_pct = ROUND(evs * 100.0 / total, 1) | SORT tier ASC'), "percent", 1),
        panel(11, "Quietest Brands at Idle", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {stand_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_stand_db = AVG({STAND_NOISE}) BY brand = {BRAND} | WHERE cars >= 500 | SORT avg_stand_db ASC | LIMIT 25")),
        panel(12, "Loudest Brands at Idle", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {stand_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_stand_db = AVG({STAND_NOISE}) BY brand = {BRAND} | WHERE cars >= 500 | SORT avg_stand_db DESC | LIMIT 25")),
        panel(13, "Stand-Noise Outliers (Very Loud Cars)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {STAND_NOISE} > 95 AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_stand_db = AVG({STAND_NOISE}), max_db = MAX({STAND_NOISE}) BY brand = {BRAND}, fuel = {FUEL} | SORT max_db DESC | LIMIT 25")),
    ]
    return dashboard("DMR Sound of Silence (Stationary Noise)", "dmr-sound-of-silence", "EVs idle at 0.02 dB. Petrol idles at 75.8 dB. Stationary noise is the cleanest single-number proof of fleet electrification — and the drive-minus-stand gap is the fingerprint of combustion.", panels, fuel_year_vars())


def track_width_creep():
    tw_filter = f"{FRONT_TRACK} > 1000 AND {FRONT_TRACK} < 2500 AND {REAR_TRACK} > 1000 AND {REAR_TRACK} < 2500"
    panels = [
        panel(1, "Cars With Track Width Data", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} | STATS cars_with_track = COUNT(*)")),
        panel(2, "Avg Front Track (mm)", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} | STATS avg_front_track = AVG({FRONT_TRACK})"), "lengthmm", 0),
        panel(3, "Avg Rear Track (mm)", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} | STATS avg_rear_track = AVG({REAR_TRACK})"), "lengthmm", 0),
        panel(4, "Widest Car Front Track (mm)", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} | STATS max_front_track = MAX({FRONT_TRACK})"), "lengthmm", 0),
        panel(5, "Narrowest Car Front Track (mm)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} | STATS min_front_track = MIN({FRONT_TRACK})"), "lengthmm", 0),
        panel(6, "Avg Front + Rear Track by First Registration Decade", "barchart", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {tw_filter} | EVAL decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*), avg_front = AVG({FRONT_TRACK}), avg_rear = AVG({REAR_TRACK}) BY decade | SORT decade ASC'), "lengthmm", 0),
        panel(7, "Avg Front Track by First Registration Year", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {tw_filter} AND {YEAR} >= 1960 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_front_track = AVG({FRONT_TRACK}) BY year_date | SORT year_date ASC'), "lengthmm", 0),
        panel(8, "Track Width Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {tw_filter} | EVAL tier = CASE({FRONT_TRACK} < 1400, "<1400 mm", {FRONT_TRACK} < 1500, "1400-1499 mm", {FRONT_TRACK} < 1600, "1500-1599 mm", {FRONT_TRACK} < 1700, "1600-1699 mm", "1700+ mm") | STATS cars = COUNT(*) BY tier | SORT cars DESC')),
        panel(9, "Avg Track Width by Body Style", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} AND {BODY} IS NOT NULL | STATS cars = COUNT(*), avg_front_track = AVG({FRONT_TRACK}) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_front_track DESC | LIMIT 15"), "lengthmm", 0),
        panel(10, "Avg Track Width by Fuel", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} AND {FUEL} IS NOT NULL | STATS cars = COUNT(*), avg_front_track = AVG({FRONT_TRACK}) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_front_track DESC | LIMIT 10"), "lengthmm", 0),
        panel(11, "Widest Brands", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_front_track = AVG({FRONT_TRACK}), max_front_track = MAX({FRONT_TRACK}) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_front_track DESC | LIMIT 25")),
        panel(12, "Narrowest Brands", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_front_track = AVG({FRONT_TRACK}) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_front_track ASC | LIMIT 25")),
        panel(13, "Track Width Asymmetry (Front − Rear)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {tw_filter} AND {BRAND} IS NOT NULL | EVAL diff = {FRONT_TRACK} - {REAR_TRACK} | STATS cars = COUNT(*), avg_diff_mm = AVG(diff), max_diff_mm = MAX(diff) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_diff_mm DESC | LIMIT 25")),
    ]
    return dashboard("DMR Track Width Creep", "dmr-track-width-creep", "Cars aren't just longer — they're noticeably wider. Average front track has grown from 1,297 mm in the 1950s fleet to 1,568 mm in the 2020s fleet (+271 mm, +21%).", panels, fuel_year_vars())


def nox_co_honesty():
    nox_filter = f"{NOX} IS NOT NULL AND {NOX} >= 0 AND {NOX} < 2000"
    co_filter = f"{CO_EMIT} IS NOT NULL AND {CO_EMIT} >= 0 AND {CO_EMIT} < 5000"
    panels = [
        panel(1, "Cars With NOx Data", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {nox_filter} | STATS cars_with_nox = COUNT(*)")),
        panel(2, "Avg NOx — Petrol (mg/km)", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Benzin" AND {nox_filter} | STATS avg_nox = AVG({NOX})'), "short", 1),
        panel(3, "Avg NOx — Diesel (mg/km)", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {nox_filter} | STATS avg_nox = AVG({NOX})'), "short", 1),
        panel(4, "Avg CO — Petrol (mg/km)", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Benzin" AND {co_filter} | STATS avg_co = AVG({CO_EMIT})'), "short", 1),
        panel(5, "Cars Above 100 mg/km NOx", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {nox_filter} | STATS high_nox = COUNT(*) WHERE {NOX} > 100")),
        panel(6, "Avg NOx by Emission Norm × Fuel", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {nox_filter} AND {EMISSION_NORM} IS NOT NULL AND {FUEL} IS NOT NULL | STATS cars = COUNT(*), avg_nox = AVG({NOX}) BY norm = {EMISSION_NORM}, fuel = {FUEL} | WHERE cars >= 500 | SORT norm ASC, avg_nox DESC | LIMIT 30"), "short", 1),
        panel(7, "Avg NOx by First Registration Year (Dieselgate Cliff)", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {nox_filter} AND {YEAR_FILTER} AND {YEAR} >= 2005 AND {FUEL} IN ("Diesel", "Benzin") | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_nox = AVG({NOX}) BY year_date, fuel = {FUEL} | SORT year_date ASC | LIMIT 100'), "short", 1),
        panel(8, "NOx Distribution Tier", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {nox_filter} | EVAL tier = CASE({NOX} == 0, "0 (EV)", {NOX} < 20, "<20", {NOX} < 50, "20-49", {NOX} < 100, "50-99", {NOX} < 200, "100-199", "200+") | STATS cars = COUNT(*) BY tier | SORT cars DESC')),
        panel(9, "Avg CO by Norm × Fuel", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {co_filter} AND {EMISSION_NORM} IS NOT NULL AND {FUEL} IS NOT NULL | STATS cars = COUNT(*), avg_co = AVG({CO_EMIT}) BY norm = {EMISSION_NORM}, fuel = {FUEL} | WHERE cars >= 500 | SORT norm ASC, avg_co DESC | LIMIT 30"), "short", 1),
        panel(10, "Avg NOx by Body Style (Diesel only)", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {nox_filter} AND {BODY} IS NOT NULL | STATS cars = COUNT(*), avg_nox = AVG({NOX}) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_nox DESC | LIMIT 12'), "short", 1),
        panel(11, "Cleanest Diesel Brands (Euro VI)", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {EMISSION_NORM} == "Euro VI" AND {nox_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_nox = AVG({NOX}) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_nox ASC | LIMIT 25')),
        panel(12, "Highest NOx Diesel Brands (Euro VI)", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {EMISSION_NORM} == "Euro VI" AND {nox_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_nox = AVG({NOX}) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_nox DESC | LIMIT 25')),
        panel(13, "Avg NOx + CO by Norm × Fuel (Full)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {nox_filter} AND {co_filter} AND {EMISSION_NORM} IS NOT NULL AND {FUEL} IS NOT NULL | STATS cars = COUNT(*), avg_nox = AVG({NOX}), avg_co = AVG({CO_EMIT}) BY norm = {EMISSION_NORM}, fuel = {FUEL} | WHERE cars >= 200 | SORT norm ASC, fuel ASC | LIMIT 60")),
    ]
    return dashboard("DMR NOx & CO Honesty Check", "dmr-nox-co-honesty", "Euro VI fixed diesel NOx dramatically (134 → 41 mg/km) — but petrol NOx didn't budge. This dashboard cross-tabulates real emission readings by norm, fuel, and brand.", panels, fuel_year_vars())


def driving_habits():
    km_filter = f"{INSP_KM} > 0 AND {INSP_KM} < 1000"
    panels = [
        panel(1, "Cars With Inspection Odometer", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} | STATS cars_with_km = COUNT(*)")),
        panel(2, "Avg Odometer at Inspection (k km)", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} | STATS avg_km = AVG({INSP_KM})"), "short", 0),
        panel(3, "Median Odometer (k km)", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} | STATS med_km = MEDIAN({INSP_KM})"), "short", 0),
        panel(4, "Cars > 300k km at Inspection", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} | STATS high_km = COUNT(*) WHERE {INSP_KM} >= 300")),
        panel(5, "Highest Single Odometer (k km)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} | STATS max_km = MAX({INSP_KM})"), "short", 0),
        panel(6, "Avg Odometer at Inspection by Fuel", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} AND {FUEL} IS NOT NULL | STATS cars = COUNT(*), avg_km = AVG({INSP_KM}), med_km = MEDIAN({INSP_KM}) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_km DESC | LIMIT 10"), "short", 0),
        panel(7, "Avg Odometer by First Registration Year (Age Curve)", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {km_filter} AND {YEAR} >= 1990 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_km = AVG({INSP_KM}) BY year_date | SORT year_date ASC'), "short", 0),
        panel(8, "Odometer Tier Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {km_filter} | EVAL tier = CASE({INSP_KM} < 50, "<50k", {INSP_KM} < 100, "50-99k", {INSP_KM} < 150, "100-149k", {INSP_KM} < 200, "150-199k", {INSP_KM} < 300, "200-299k", "300k+") | STATS cars = COUNT(*) BY tier | SORT cars DESC')),
        panel(9, "Median Annual km by Fuel (Age-Adjusted)", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {km_filter} AND {FUEL} IS NOT NULL AND {YEAR} IS NOT NULL AND {YEAR} >= 1995 | EVAL age = 2026 - {YEAR} | WHERE age > 0 AND age < 35 | EVAL km_per_year = {INSP_KM} * 1.0 / age | STATS cars = COUNT(*), med_km_per_year = MEDIAN(km_per_year) BY fuel = {FUEL} | WHERE cars >= 100 | SORT med_km_per_year DESC | LIMIT 10'), "short", 1),
        panel(10, "Odometer by Body Style", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} AND {BODY} IS NOT NULL | STATS cars = COUNT(*), avg_km = AVG({INSP_KM}) BY body_style = {BODY} | WHERE cars >= 500 | SORT avg_km DESC | LIMIT 12"), "short", 0),
        panel(11, "Brands That Drive Most (Avg Odom)", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_km = AVG({INSP_KM}), med_km = MEDIAN({INSP_KM}) BY brand = {BRAND} | WHERE cars >= 1000 | SORT avg_km DESC | LIMIT 25")),
        panel(12, "Brands That Drive Least (Avg Odom)", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), avg_km = AVG({INSP_KM}) BY brand = {BRAND} | WHERE cars >= 1000 | SORT avg_km ASC | LIMIT 25")),
        panel(13, "Driven-Into-The-Ground (Highest Single Odometers)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {km_filter} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS top_km = MAX({INSP_KM}) BY brand = {BRAND}, model = {MODEL} | WHERE top_km > 500 | SORT top_km DESC | LIMIT 25")),
    ]
    return dashboard("DMR Danish Driving Habits (Odometers at Inspection)", "dmr-driving-habits", "Volvo drivers average 208k km, Mercedes 193k, Kia 140k. Diesel does ~18k km/year per car, EVs 14k, petrol 11k. The DMR's 2.16M inspection odometers reveal how Danes actually drive.", panels, fuel_year_vars())


def chiptuning_hall():
    chip = '"Chiptuning Godkendt"'
    panels = [
        panel(1, "Chip-Tuned Cars (Permit Active)", "stat", 0, 0, 6, 5, q(f"WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == {chip} | STATS chiptuned_cars = COUNT(*)")),
        panel(2, "Veterankørsel Permits (Veteran Driving)", "stat", 6, 0, 6, 5, q(f'WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == "Veterankørsel" | STATS cars = COUNT(*)')),
        panel(3, "Rental Permits (Udlejning Uden Fører)", "stat", 12, 0, 6, 5, q(f'WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == "Udlejning Uden Fører" | STATS cars = COUNT(*)')),
        panel(4, "Driving School (Øvelseskørsel)", "stat", 18, 0, 6, 5, q(f'WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == "Øvelseskørsel" | STATS cars = COUNT(*)')),
        panel(5, "Chip-Tuning Permits by Brand", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == {chip} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 20")),
        panel(6, "Chip-Tuning Permits by Fuel", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == {chip} AND {FUEL} IS NOT NULL | STATS cars = COUNT(*) BY fuel = {FUEL} | SORT cars DESC | LIMIT 10")),
        panel(7, "Permit Type Inventory (All Quirky Permits)", "barchart", 0, 14, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} IS NOT NULL | STATS cars = COUNT(*) BY permit_type = {PERMIT_TYPE} | SORT cars DESC | LIMIT 25")),
        panel(8, "Chip-Tuning Permits by Registration Decade", "barchart", 12, 14, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == {chip} AND {YEAR} IS NOT NULL | EVAL decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*) BY decade | SORT decade ASC')),
        panel(9, "Chip-Tuned Brand-Model Hall of Fame", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == {chip} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), avg_kw = AVG({KW}) BY brand = {BRAND}, model = {MODEL} | SORT cars DESC | LIMIT 25")),
        panel(10, "Chip-Tuning Permits by Body Style", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} == {chip} AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY body_style = {BODY} | SORT cars DESC | LIMIT 15")),
        panel(11, "Rare Permits (Limousine, Emergency, etc.)", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {PERMIT_TYPE} IS NOT NULL AND {PERMIT_TYPE} NOT IN ("Synsfri Sammenkobling", "Veterankørsel", "Udlejning Uden Fører", "Øvelseskørsel") | STATS cars = COUNT(*) BY permit_type = {PERMIT_TYPE} | SORT cars ASC | LIMIT 20')),
    ]
    return dashboard("DMR Chiptuning Hall of Fame", "dmr-chiptuning-hall", "Denmark legally permits chip-tuning — and 1,611 cars hold an active Chiptuning Godkendt permit. Volvo leads with 136. SAAB is #2 with 42 — a dead brand still being tuned. Even 8 Polestar EVs are tuned.", panels, year_vars())


def two_fifty_club():
    speed_filter = f"{SPEED} > 250 AND {SPEED} < 500"
    panels = [
        panel(1, "Cars Certified >250 km/h", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} | STATS cars = COUNT(*)")),
        panel(2, "EVs in the 250 Club", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {speed_filter} AND {FUEL} == "El" | STATS evs = COUNT(*)')),
        panel(3, "Cars Certified >300 km/h", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {SPEED} > 300 AND {SPEED} < 500 | STATS cars = COUNT(*)")),
        panel(4, "Leased Cars in the 250 Club", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} AND {LEASE} IS NOT NULL | STATS leased = COUNT(*)")),
        panel(5, "Top Certified Speed (km/h)", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} | STATS top_speed = MAX({SPEED})"), "short", 0),
        panel(6, "250 km/h Club by Brand", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 20")),
        panel(7, "250 km/h Club by Fuel", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} AND {FUEL} IS NOT NULL | STATS cars = COUNT(*) BY fuel = {FUEL} | SORT cars DESC | LIMIT 10")),
        panel(8, "Top Speed Tier Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {speed_filter} | EVAL tier = CASE({SPEED} < 260, "250-259", {SPEED} < 280, "260-279", {SPEED} < 300, "280-299", {SPEED} < 320, "300-319", "320+") | STATS cars = COUNT(*) BY tier | SORT tier ASC')),
        panel(9, "250 Club by Color", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {speed_filter} AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" | STATS cars = COUNT(*) BY color = {COLOR} | SORT cars DESC | LIMIT 12')),
        panel(10, "250 Club Leasing Share by Brand", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} AND {BRAND} IS NOT NULL | STATS total = COUNT(*), leased = COUNT(*) WHERE {LEASE} IS NOT NULL BY brand = {BRAND} | WHERE total >= 30 | EVAL leased_pct = ROUND(leased * 100.0 / total, 1) | SORT total DESC | LIMIT 12"), "percent", 1),
        panel(11, "Top Brand-Model Combos >250 km/h", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), avg_kw = AVG({KW}), max_speed = MAX({SPEED}) BY brand = {BRAND}, model = {MODEL} | SORT cars DESC | LIMIT 25")),
        panel(12, "Diesel Supercars (>250 km/h)", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {speed_filter} AND {FUEL} == "Diesel" AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), max_speed = MAX({SPEED}), avg_kw = AVG({KW}) BY brand = {BRAND}, model = {MODEL} | SORT max_speed DESC | LIMIT 25')),
        panel(13, "Fastest Cars in Denmark (by Brand Max)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {speed_filter} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), max_speed = MAX({SPEED}), avg_kw = AVG({KW}) BY brand = {BRAND} | SORT max_speed DESC | LIMIT 25")),
    ]
    return dashboard("DMR 250 km/h Club", "dmr-250-club", "4,400+ Danish-registered cars are certified for >250 km/h. Tesla (2,501 EVs) outnumbers all combined Porsche petrol (1,994). Even 38 diesel Porsches qualify.", panels, year_vars())


def vintage_leasing():
    panels = [
        panel(1, "Leased Cars First Registered Before 2000", "stat", 0, 0, 6, 5, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} < 2000 AND {YEAR} >= 1900 | STATS vintage_leases = COUNT(*)")),
        panel(2, "Leased Cars Before 1990", "stat", 6, 0, 6, 5, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} < 1990 AND {YEAR} >= 1900 | STATS pre90_leases = COUNT(*)")),
        panel(3, "Leased Veteran Cars (Flag = True)", "stat", 12, 0, 6, 5, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {VETERAN} == true | STATS veteran_leases = COUNT(*)")),
        panel(4, "Oldest Leased Car (Registration Year)", "stat", 18, 0, 6, 5, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} >= 1900 | STATS oldest_year = MIN({YEAR})"), "none", 0),
        panel(5, "Leased Cars by First Registration Year (pre-2010)", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} >= 1960 AND {YEAR} < 2010 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS leased_cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(6, "Vintage-Leased Cars by Decade", "barchart", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} >= 1900 AND {YEAR} < 2010 | EVAL decade = CASE({YEAR} < 1970, "Before 1970", {YEAR} < 1980, "1970s", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", "2000s") | STATS cars = COUNT(*) BY decade | SORT decade ASC')),
        panel(7, "Vintage-Leased Cars by Brand", "barchart", 0, 14, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} < 2000 AND {YEAR} >= 1900 AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 20")),
        panel(8, "Vintage-Leased Body Mix", "barchart", 12, 14, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} < 2000 AND {YEAR} >= 1900 AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY body_style = {BODY} | SORT cars DESC | LIMIT 12")),
        panel(9, "Oldest Leased Cars (Year + Brand + Model)", "table", 0, 23, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {LEASE} IS NOT NULL AND {YEAR} >= 1900 AND {YEAR} < 2000 AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), oldest_year = MIN({YEAR}) BY brand = {BRAND}, model = {MODEL} | SORT oldest_year ASC | LIMIT 30")),
        panel(10, "Leasing Share by Registration Decade", "table", 12, 23, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR} >= 1960 AND {YEAR} <= 2025 | EVAL decade = CASE({YEAR} < 1970, "1960s", {YEAR} < 1980, "1970s", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS total = COUNT(*), leased = COUNT(*) WHERE {LEASE} IS NOT NULL BY decade | EVAL leased_pct = ROUND(leased * 100.0 / total, 1) | SORT decade ASC')),
    ]
    return dashboard("DMR Vintage Leasing", "dmr-vintage-leasing", "A 1966 car is currently on an active leasing contract in Denmark. So is one from 1970, 1972, and several from the late 1970s. Classic-car leasing companies in numbers.", panels, [])


def diesel_last_stand():
    panels = [
        panel(1, "Diesel Cars Registered 2020-2026", "stat", 0, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2020 | STATS recent_diesels = COUNT(*)')),
        panel(2, "New Diesels — 2026", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} == 2026 | STATS y2026 = COUNT(*)')),
        panel(3, "New Diesels — 2025", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} == 2025 | STATS y2025 = COUNT(*)')),
        panel(4, "Mercedes Share of New Diesels (2024-2026)", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2024 | STATS total = COUNT(*), mb = COUNT(*) WHERE {BRAND} == "MERCEDES-BENZ" | EVAL share = 1.0 * mb / total | KEEP share'), "percentunit", 1),
        panel(5, "Diesel SUVs Among Recent Diesels", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2020 AND {BODY} == "SUV" | STATS suvs = COUNT(*)')),
        panel(6, "Diesel Registrations by Year (2015+)", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2015 AND {YEAR} <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS diesel_cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(7, "Diesel Share of All Registrations by Year", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR} >= 2010 AND {YEAR} <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS total = COUNT(*), diesels = COUNT(*) WHERE {FUEL} == "Diesel" BY year_date | EVAL diesel_pct = ROUND(diesels * 100.0 / total, 1) | KEEP year_date, diesel_pct | SORT year_date ASC'), "percent", 1),
        panel(8, "Post-2020 Diesel Body Mix", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2020 AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY body_style = {BODY} | SORT cars DESC | LIMIT 12')),
        panel(9, "Avg Power of New Diesels by Year (Premium-SUV Signature)", "timeseries", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2015 AND {YEAR} <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), kw_clean = CLAMP({KW}, 30, 600) | STATS avg_kw = AVG(kw_clean) BY year_date | SORT year_date ASC'), "kwatth", 0),
        panel(10, "Avg Weight of New Diesels by Year", "timeseries", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2015 AND {YEAR} <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), wt = CLAMP({KERB_WEIGHT}, 500, 5000) | STATS avg_kg = AVG(wt) BY year_date | SORT year_date ASC'), "kg", 0),
        panel(11, "New Diesel Brand Leaderboard (2024-2026)", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2024 AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 20')),
        panel(12, "Diesel Stacked by Brand and Year", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} >= 2018 AND {YEAR} <= 2026 AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY year = {YEAR}, brand = {BRAND} | WHERE cars >= 50 | SORT year DESC, cars DESC | LIMIT 60')),
        panel(13, "Brands That Exited Diesel (last reg year)", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL} == "Diesel" AND {YEAR} IS NOT NULL AND {BRAND} IS NOT NULL | STATS diesel_count = COUNT(*), last_diesel_year = MAX({YEAR}) BY brand = {BRAND} | WHERE diesel_count >= 500 AND last_diesel_year <= 2023 | SORT last_diesel_year ASC, brand ASC | LIMIT 25')),
    ]
    return dashboard("DMR Diesel's Last Stand", "dmr-diesel-last-stand", "Diesel registrations are collapsing — but unevenly. Mercedes alone carries the segment (~50% of new diesel registrations 2024-2026). This dashboard tracks which brands held diesel longest and which exited.", panels, [])


def red_car_myth():
    panels = [
        panel(1, "Red Registered Cars", "stat", 0, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} | STATS red_cars = COUNT(*) WHERE {COLOR} == "Rød"')),
        panel(2, "Red Accident Rate", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {COLOR} == "Rød" AND {TRAFIKSKADE} IS NOT NULL | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true | EVAL accident_pct = 1.0 * accidents / total | KEEP accident_pct'), "percentunit", 2),
        panel(3, "Grey Accident Rate", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {COLOR} == "Grå" AND {TRAFIKSKADE} IS NOT NULL | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true | EVAL accident_pct = 1.0 * accidents / total | KEEP accident_pct'), "percentunit", 2),
        panel(4, "Green Accident Rate", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {COLOR} == "Grøn" AND {TRAFIKSKADE} IS NOT NULL | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true | EVAL accident_pct = 1.0 * accidents / total | KEEP accident_pct'), "percentunit", 2),
        panel(5, "Red-vs-Green Risk Ratio", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND ({COLOR} == "Rød" OR {COLOR} == "Grøn") | STATS red_total = COUNT(*) WHERE {COLOR} == "Rød", red_acc = COUNT(*) WHERE {COLOR} == "Rød" AND {TRAFIKSKADE} == true, green_total = COUNT(*) WHERE {COLOR} == "Grøn", green_acc = COUNT(*) WHERE {COLOR} == "Grøn" AND {TRAFIKSKADE} == true | EVAL ratio = (red_acc * 1.0 / red_total) / (green_acc * 1.0 / green_total) | KEEP ratio'), "short", 2),
        panel(6, "Accident Rate by Colour", "barchart", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true BY color = {COLOR} | WHERE total >= 5000 | EVAL accident_pct = ROUND(accidents * 100.0 / total, 2) | SORT accident_pct DESC | LIMIT 15'), "percent", 2),
        panel(7, "Accident Count by Colour", "barchart", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} == true AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" | STATS accidents = COUNT(*) BY color = {COLOR} | SORT accidents DESC | LIMIT 15')),
        panel(8, "Red Accident Rate by Decade", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {COLOR} == "Rød" AND {TRAFIKSKADE} IS NOT NULL AND {YEAR_FILTER} | EVAL decade = CASE({YEAR} < 1990, "Before 1990", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true BY decade | EVAL accident_pct = ROUND(accidents * 100.0 / total, 2) | SORT decade ASC'), "percent", 2),
        panel(9, "Colour × Fuel Accident Rate", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" AND {FUEL_FILTER} | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true BY color = {COLOR} | WHERE total >= 5000 | EVAL accident_pct = ROUND(accidents * 100.0 / total, 2) | SORT accident_pct DESC | LIMIT 15'), "percent", 2),
        panel(10, "Red-Car Brand Mix", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {COLOR} == "Rød" AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 15')),
        panel(11, "Most Crash-Prone Red Brands", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {COLOR} == "Rød" AND {TRAFIKSKADE} IS NOT NULL AND {BRAND} IS NOT NULL | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true BY brand = {BRAND} | WHERE total >= 500 | EVAL accident_pct = ROUND(accidents * 100.0 / total, 2) | SORT accident_pct DESC | LIMIT 25')),
        panel(12, "Safest Colour-Brand Combos", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" AND {BRAND} IS NOT NULL | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true BY brand = {BRAND}, color = {COLOR} | WHERE total >= 2000 | EVAL accident_pct = ROUND(accidents * 100.0 / total, 2) | SORT accident_pct ASC | LIMIT 25')),
        panel(13, "Riskiest Colour-Brand Combos", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {TRAFIKSKADE} IS NOT NULL AND {COLOR} IS NOT NULL AND {COLOR} != "Ukendt" AND {BRAND} IS NOT NULL | STATS total = COUNT(*), accidents = COUNT(*) WHERE {TRAFIKSKADE} == true BY brand = {BRAND}, color = {COLOR} | WHERE total >= 2000 | EVAL accident_pct = ROUND(accidents * 100.0 / total, 2) | SORT accident_pct DESC | LIMIT 25')),
    ]
    return dashboard("DMR Red Car Myth (Colour × Accidents)", "dmr-red-car-myth", "Red passenger cars in Denmark have a 1.01% accident-flag rate — 3.5× higher than green cars (0.28%). Folk wisdom about red drivers is statistically real in the DMR.", panels, fuel_year_vars())


def ghost_fleet():
    dereg_filter = f'{PASSENGER_SCOPE} AND {STATUS} == "Afmeldt" AND {YEAR} IS NOT NULL AND KoeretoejRegistreringStatusDato IS NOT NULL'
    panels = [
        panel(1, "Deregistered Passenger Cars (Ghost Fleet)", "stat", 0, 0, 5, 5, q(f'WHERE {PASSENGER_SCOPE} AND {STATUS} == "Afmeldt" | STATS dead_cars = COUNT(*)')),
        panel(2, "Currently Registered Cars", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} | STATS alive_cars = COUNT(*)")),
        panel(3, "Dead-to-Alive Ratio", "stat", 10, 0, 5, 5, q(f'WHERE {PASSENGER_SCOPE} | STATS dead = COUNT(*) WHERE {STATUS} == "Afmeldt", alive = COUNT(*) WHERE {STATUS} == "Registreret" | EVAL ratio = 1.0 * dead / alive | KEEP ratio'), "short", 2),
        panel(4, "Avg Lifespan — 1990s Cohort (years)", "stat", 15, 0, 5, 5, q(f'WHERE {dereg_filter} AND {YEAR} >= 1990 AND {YEAR} < 2000 | EVAL age = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) - {YEAR} | WHERE age >= 0 AND age < 60 | STATS avg_lifespan_years = AVG(age)'), "short", 1),
        panel(5, "Avg Lifespan — 2000s Cohort (years)", "stat", 20, 0, 4, 5, q(f'WHERE {dereg_filter} AND {YEAR} >= 2000 AND {YEAR} < 2010 | EVAL age = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) - {YEAR} | WHERE age >= 0 AND age < 60 | STATS avg_lifespan_years = AVG(age)'), "short", 1),
        panel(6, "Age at Deregistration Distribution", "barchart", 0, 5, 12, 9, q(f'WHERE {dereg_filter} | EVAL age = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) - {YEAR} | WHERE age >= 0 AND age < 50 | EVAL tier = CASE(age < 5, "<5y", age < 10, "5-9y", age < 15, "10-14y", age < 20, "15-19y", age < 25, "20-24y", age < 30, "25-29y", "30+y") | STATS cars = COUNT(*) BY tier | SORT tier ASC')),
        panel(7, "Deregistrations Per Year", "timeseries", 12, 5, 12, 9, q(f'WHERE {dereg_filter} | EVAL dereg_year = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) | WHERE dereg_year >= 1990 AND dereg_year <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING(dereg_year), "-01-01")) | STATS dereg_cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(8, "Avg Lifespan by Birth Decade", "barchart", 0, 14, 8, 9, q(f'WHERE {dereg_filter} AND {YEAR} >= 1960 AND {YEAR} < 2026 | EVAL age = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) - {YEAR}, decade = CASE({YEAR} < 1970, "1960s", {YEAR} < 1980, "1970s", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | WHERE age >= 0 AND age < 60 | STATS cars = COUNT(*), avg_age_yrs = AVG(age), med_age_yrs = MEDIAN(age) BY decade | SORT decade ASC'), "short", 1),
        panel(9, "Survivorship — Currently Alive Share by Birth Decade", "barchart", 8, 14, 8, 9, q(f'WHERE {PASSENGER_SCOPE} AND {YEAR_FILTER} | EVAL decade = CASE({YEAR} < 1970, "1960s", {YEAR} < 1980, "1970s", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS total = COUNT(*), alive = COUNT(*) WHERE {STATUS} == "Registreret" BY decade | EVAL alive_pct = ROUND(alive * 100.0 / total, 1) | SORT decade ASC'), "percent", 1),
        panel(10, "Ghost Fleet by Fuel Type", "barchart", 16, 14, 8, 9, q(f'WHERE {PASSENGER_SCOPE} AND {STATUS} == "Afmeldt" AND {FUEL} IS NOT NULL | STATS dead_cars = COUNT(*) BY fuel = {FUEL} | SORT dead_cars DESC | LIMIT 10')),
        panel(11, "Brands With Shortest Avg Lifespan", "table", 0, 23, 8, 9, q(f'WHERE {dereg_filter} AND {BRAND} IS NOT NULL AND {YEAR} >= 1990 | EVAL age = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) - {YEAR} | WHERE age >= 0 AND age < 60 | STATS dead = COUNT(*), avg_age_yrs = AVG(age) BY brand = {BRAND} | WHERE dead >= 5000 | SORT avg_age_yrs ASC | LIMIT 25')),
        panel(12, "Brands With Longest Avg Lifespan", "table", 8, 23, 8, 9, q(f'WHERE {dereg_filter} AND {BRAND} IS NOT NULL AND {YEAR} >= 1990 | EVAL age = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) - {YEAR} | WHERE age >= 0 AND age < 60 | STATS dead = COUNT(*), avg_age_yrs = AVG(age) BY brand = {BRAND} | WHERE dead >= 5000 | SORT avg_age_yrs DESC | LIMIT 25')),
        panel(13, "Most Common Dead Brand-Models", "table", 16, 23, 8, 9, q(f'WHERE {PASSENGER_SCOPE} AND {STATUS} == "Afmeldt" AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS dead_cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | SORT dead_cars DESC | LIMIT 25')),
    ]
    return dashboard("DMR Ghost Fleet (Lifespan & Mortality)", "dmr-ghost-fleet", "6.46M deregistered passenger cars vs 5.10M registered — the dead fleet outnumbers the living. 1980s cars lasted 17.8 years on average; 2010s cars deregistered after just 6.3y so far.", panels, year_vars())


def turbocharging_era():
    eng_filter = f"{CYLINDERS} > 0 AND {CYLINDERS} <= 12 AND {DISPLACEMENT} > 100 AND {DISPLACEMENT} < 8000 AND {KW} > 10 AND {KW} <= 800"
    panels = [
        panel(1, "Cars With Engine Spec Data", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} | STATS cars = COUNT(*)")),
        panel(2, "Avg cc per Cylinder (whole fleet)", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} | EVAL cc_per_cyl = {DISPLACEMENT} * 1.0 / {CYLINDERS} | STATS avg_cc_per_cyl = AVG(cc_per_cyl)"), "short", 1),
        panel(3, "Avg kW per Litre", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS avg_kw_per_l = AVG(kw_per_l)"), "short", 1),
        panel(4, "High-Density Cars (≥100 kW/L)", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS high_density = COUNT(*) WHERE kw_per_l >= 100")),
        panel(5, "Top kW/L in Fleet", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS max_kw_per_l = MAX(kw_per_l)"), "short", 1),
        panel(6, "Avg kW per Litre by First Registration Year", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {eng_filter} AND {YEAR} >= 1980 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS avg_kw_per_l = AVG(kw_per_l) BY year_date | SORT year_date ASC'), "short", 1),
        panel(7, "Avg cc per Cylinder by First Registration Year", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {eng_filter} AND {YEAR} >= 1980 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")), cc_per_cyl = {DISPLACEMENT} * 1.0 / {CYLINDERS} | STATS avg_cc_per_cyl = AVG(cc_per_cyl) BY year_date | SORT year_date ASC'), "short", 1),
        panel(8, "kW/L Tier Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {FUEL_FILTER} AND {YEAR_FILTER} AND {eng_filter} | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT}, tier = CASE(kw_per_l < 40, "<40", kw_per_l < 60, "40-59", kw_per_l < 80, "60-79", kw_per_l < 100, "80-99", kw_per_l < 130, "100-129", "130+") | STATS cars = COUNT(*) BY tier | SORT tier ASC')),
        panel(9, "Avg kW/L by Fuel", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} AND {FUEL} IS NOT NULL | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS cars = COUNT(*), avg_kw_per_l = AVG(kw_per_l) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_kw_per_l DESC | LIMIT 10"), "short", 1),
        panel(10, "Avg cc/cyl by Fuel", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} AND {FUEL} IS NOT NULL | EVAL cc_per_cyl = {DISPLACEMENT} * 1.0 / {CYLINDERS} | STATS cars = COUNT(*), avg_cc_per_cyl = AVG(cc_per_cyl) BY fuel = {FUEL} | WHERE cars >= 100 | SORT avg_cc_per_cyl DESC | LIMIT 10"), "short", 1),
        panel(11, "Highest kW/L Brands", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} AND {BRAND} IS NOT NULL | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS cars = COUNT(*), avg_kw_per_l = AVG(kw_per_l), max_kw_per_l = MAX(kw_per_l) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_kw_per_l DESC | LIMIT 25")),
        panel(12, "Lowest kW/L Brands (Naturally Aspirated Survivors)", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} AND {BRAND} IS NOT NULL | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS cars = COUNT(*), avg_kw_per_l = AVG(kw_per_l), avg_cc_per_cyl = AVG({DISPLACEMENT} * 1.0 / {CYLINDERS}) BY brand = {BRAND} | WHERE cars >= 200 | SORT avg_kw_per_l ASC | LIMIT 25")),
        panel(13, "Top Brand-Model kW/L (Pocket Rockets)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {eng_filter} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | EVAL kw_per_l = {KW} * 1000.0 / {DISPLACEMENT} | STATS cars = COUNT(*), avg_kw_per_l = AVG(kw_per_l), max_kw_per_l = MAX(kw_per_l) BY brand = {BRAND}, model = {MODEL} | WHERE cars >= 50 | SORT avg_kw_per_l DESC | LIMIT 25")),
    ]
    return dashboard("DMR Turbocharging Era (Specific Output)", "dmr-turbocharging-era", "Engines downsized AND turbocharged: cc-per-cylinder fell from 485 (1980s) to 379 (2010s), while kW-per-litre rose from 41 to 65 — +58% specific output. The downsizing-turbo era in one number.", panels, fuel_year_vars())


def brand_invasion():
    panels = [
        panel(1, "Distinct Brands Registered Ever", "stat", 0, 0, 5, 5, q(f"WHERE {PASSENGER_SCOPE} AND {BRAND} IS NOT NULL | STATS distinct_brands = COUNT_DISTINCT({BRAND})")),
        panel(2, "Distinct Brands — Currently Registered", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS distinct_brands = COUNT_DISTINCT({BRAND})")),
        panel(3, "Brands With New 2025 Regs", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {YEAR} == 2025 AND {BRAND} IS NOT NULL | STATS brands_2025 = COUNT_DISTINCT({BRAND})")),
        panel(4, "Brands With New 2000 Regs", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {YEAR} == 2000 AND {BRAND} IS NOT NULL | STATS brands_2000 = COUNT_DISTINCT({BRAND})")),
        panel(5, "Distinct Models Ever Registered", "stat", 20, 0, 4, 5, q(f"WHERE {PASSENGER_SCOPE} AND {MODEL} IS NOT NULL | STATS distinct_models = COUNT_DISTINCT({MODEL})")),
        panel(6, "Brand & Model Count by First Registration Year", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {YEAR} >= 2000 AND {YEAR} <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS distinct_brands = COUNT_DISTINCT({BRAND}), distinct_models = COUNT_DISTINCT({MODEL}) BY year_date | SORT year_date ASC')),
        panel(7, "New 2020+ Brands (Never Registered Before 2020)", "table", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), first_year = MIN({YEAR}) BY brand = {BRAND} | WHERE first_year >= 2020 AND cars >= 10 | SORT first_year ASC, cars DESC | LIMIT 30")),
        panel(8, "Newcomer Share of Registrations by Year", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {YEAR_FILTER} AND {YEAR} >= 2010 AND {YEAR} <= 2026 AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY year = {YEAR} | SORT year ASC')),
        panel(9, "Brands by Decade of First Registration", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), first_year = MIN({YEAR}) BY brand = {BRAND} | EVAL decade = CASE(first_year < 1990, "Before 1990", first_year < 2000, "1990s", first_year < 2010, "2000s", first_year < 2020, "2010s", "2020s") | STATS brands = COUNT(*) BY decade | SORT decade ASC')),
        panel(10, "Last-Reg-Year Distribution (When Brands Faded)", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), last_year = MAX({YEAR}) BY brand = {BRAND} | WHERE cars >= 100 | EVAL bucket = CASE(last_year >= 2024, "Active", last_year >= 2020, "2020-23", last_year >= 2015, "2015-19", last_year >= 2010, "2010-14", "Pre-2010") | STATS brands = COUNT(*) BY bucket | SORT bucket DESC')),
        panel(11, "Biggest 2020+ Newcomer Brands", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), first_year = MIN({YEAR}) BY brand = {BRAND} | WHERE first_year >= 2020 | SORT cars DESC | LIMIT 25")),
        panel(12, "Brands That Stopped Registering New Cars", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), last_year = MAX({YEAR}) BY brand = {BRAND} | WHERE cars >= 1000 AND last_year <= 2020 | SORT last_year ASC, cars DESC | LIMIT 25")),
        panel(13, "Brand Lifespan (First → Last Registration Year)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*), first_year = MIN({YEAR}), last_year = MAX({YEAR}) BY brand = {BRAND} | WHERE cars >= 500 | EVAL span_years = last_year - first_year | SORT span_years DESC | LIMIT 25")),
    ]
    return dashboard("DMR Brand Invasion (Newcomers & Departures)", "dmr-brand-invasion", "Distinct brands registering new cars in Denmark grew from 64 (2000) to 192 (2025). The Chinese-EV wave is visible in real time. Model variety peaked at 1,618 in 2021 and consolidation has begun.", panels, year_vars())


def door_seat_matrix():
    panels = [
        panel(1, "1-Seat Cars with 5 Doors", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {DOORS} == 5 | STATS cars = COUNT(*)")),
        panel(2, "1-Seat Cars with 4 Doors", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {DOORS} == 4 | STATS cars = COUNT(*)")),
        panel(3, "True 2-Door 2-Seat Coupés", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 2 AND {DOORS} == 2 | STATS cars = COUNT(*)")),
        panel(4, "3-Door 9-Seat Minibuses", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 9 AND {DOORS} == 3 | STATS cars = COUNT(*)")),
        panel(5, "Zero-Door Cars", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {DOORS} == 0 | STATS cars = COUNT(*)")),
        panel(6, "Top Door×Seat Combinations", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {DOORS} IS NOT NULL AND {SEATS} IS NOT NULL AND {DOORS} <= 6 AND {SEATS} <= 9 | EVAL combo = CONCAT(TO_STRING({DOORS}), \"-door, \", TO_STRING({SEATS}), \"-seat\") | STATS cars = COUNT(*) BY combo | SORT cars DESC | LIMIT 20")),
        panel(7, "Weird Door×Seat Combos (≤2000 cars)", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {DOORS} IS NOT NULL AND {SEATS} IS NOT NULL AND {DOORS} <= 6 AND {SEATS} <= 9 | EVAL combo = CONCAT(TO_STRING({DOORS}), \"-door, \", TO_STRING({SEATS}), \"-seat\") | STATS cars = COUNT(*) BY combo | WHERE cars <= 2000 AND cars >= 50 | SORT cars DESC | LIMIT 20")),
        panel(8, "Doors-per-Seat Ratio Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {DOORS} > 0 AND {SEATS} > 0 AND {DOORS} <= 6 AND {SEATS} <= 9 | EVAL ratio = {DOORS} * 1.0 / {SEATS}, tier = CASE(ratio < 0.5, "<0.5 (cramped)", ratio < 0.8, "0.5-0.79", ratio < 1.0, "0.8-0.99", ratio < 1.5, "1.0-1.49", ratio < 2.0, "1.5-1.99", "2.0+ (luxury)") | STATS cars = COUNT(*) BY tier | SORT cars DESC')),
        panel(9, "1-Seat Conversions by Door Count", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} == 1 AND {DOORS} IS NOT NULL AND {DOORS} <= 6 | STATS cars = COUNT(*) BY doors = {DOORS} | SORT doors ASC")),
        panel(10, "7+ Seat Cars by Door Count", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {SEATS} >= 7 AND {SEATS} <= 9 AND {DOORS} IS NOT NULL AND {DOORS} <= 6 | STATS cars = COUNT(*) BY doors = {DOORS} | SORT doors ASC")),
        panel(11, "Door×Seat Matrix — Full Table", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {DOORS} IS NOT NULL AND {SEATS} IS NOT NULL AND {DOORS} <= 6 AND {SEATS} <= 9 | STATS cars = COUNT(*) BY doors = {DOORS}, seats = {SEATS} | WHERE cars >= 100 | SORT doors ASC, seats ASC | LIMIT 60")),
        panel(12, "Weirdest Brands (≥1 rare combo)", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {DOORS} IS NOT NULL AND {SEATS} IS NOT NULL AND (({SEATS} == 1 AND {DOORS} >= 4) OR ({SEATS} >= 6 AND {DOORS} <= 3) OR ({DOORS} == 0)) | STATS weird_cars = COUNT(*) BY brand = {BRAND} | WHERE weird_cars >= 50 | SORT weird_cars DESC | LIMIT 25")),
        panel(13, "Models of Each Rare Combo", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL AND {DOORS} IS NOT NULL AND {SEATS} IS NOT NULL AND (({SEATS} == 1 AND {DOORS} == 5) OR ({SEATS} == 2 AND {DOORS} == 2) OR ({SEATS} >= 7 AND {DOORS} <= 3)) | STATS cars = COUNT(*) BY brand = {BRAND}, model = {MODEL}, doors = {DOORS}, seats = {SEATS} | SORT cars DESC | LIMIT 30")),
    ]
    return dashboard("DMR Door-Seat Weirdness Matrix", "dmr-door-seat-matrix", "Every door×seat combination exists in the DMR — including 40,653 cars with 5 doors but only 1 seat (yellow-plate conversions) and 2,460 with 3 doors and 9 seats (minibuses).", panels, [])


def seven_seat_explosion():
    seven = f"{SEATS} == 7"
    panels = [
        panel(1, "7-Seat Cars Registered", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {seven} | STATS seven_seat_cars = COUNT(*)")),
        panel(2, "New 7-Seaters Registered 2020-2026", "stat", 5, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {seven} AND {YEAR} >= 2020 | STATS recent = COUNT(*)")),
        panel(3, "7-Seat MPVs", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {BODY} == "MPV" | STATS mpv = COUNT(*)')),
        panel(4, "7-Seat Stationcars", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {BODY} == "Stationcar" | STATS stc = COUNT(*)')),
        panel(5, "7-Seat Hatchbacks", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {BODY} == "Hatchback" | STATS hatch = COUNT(*)')),
        panel(6, "7-Seat Registrations by Year", "timeseries", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {YEAR} >= 2000 AND {YEAR} <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS seven_seaters = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(7, "7-Seat Body Mix by Year", "barchart", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {YEAR} >= 2010 AND {YEAR} <= 2026 AND {BODY} IS NOT NULL | STATS cars = COUNT(*) BY year = {YEAR}, body = {BODY} | SORT year ASC, cars DESC | LIMIT 80'), stacking="normal"),
        panel(8, "7-Seat Avg Weight Over Time", "timeseries", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {YEAR} >= 2000 AND {YEAR} <= 2026 AND {KERB_WEIGHT} > 500 AND {KERB_WEIGHT} < 5000 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_kg = AVG({KERB_WEIGHT}) BY year_date | SORT year_date ASC'), "kg", 0),
        panel(9, "7-Seat Fuel Mix", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {seven} AND {FUEL} IS NOT NULL | STATS cars = COUNT(*) BY fuel = {FUEL} | SORT cars DESC | LIMIT 10")),
        panel(10, "7-Seat Avg Power Over Time", "timeseries", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {YEAR} >= 2000 AND {YEAR} <= 2026 AND {KW} > 10 AND {KW} <= 600 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING({YEAR}), "-01-01")) | STATS avg_kw = AVG({KW}) BY year_date | SORT year_date ASC'), "kwatth", 0),
        panel(11, "Top 7-Seat Brands", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {seven} AND {BRAND} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 25")),
        panel(12, "Top 7-Seat Models", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {seven} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | SORT cars DESC | LIMIT 25")),
        panel(13, "MPV vs Stationcar 7-Seat Race", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {seven} AND {YEAR} >= 2010 AND {YEAR} <= 2026 AND ({BODY} == "MPV" OR {BODY} == "Stationcar" OR {BODY} == "SUV") | STATS cars = COUNT(*) BY year = {YEAR}, body = {BODY} | SORT year DESC, body ASC | LIMIT 60')),
    ]
    return dashboard("DMR 7-Seat Explosion", "dmr-seven-seat-explosion", "7-seat MPVs jumped from 363 (2006) to 5,338 (2017) — a 14× rise in a decade. Then stationcars and SUVs muscled in. The body-style migration of the Danish family-of-five.", panels, [])


def dormant_fleet():
    panels = [
        panel(1, "Cars Touched in Last 6 Months", "stat", 0, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS recent = COUNT(*) WHERE months_since < 6')),
        panel(2, "Cars Untouched 5-10 Years", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS dormant = COUNT(*) WHERE months_since >= 60 AND months_since < 120')),
        panel(3, "Cars Untouched 10+ Years (Ghosts)", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS ghosts = COUNT(*) WHERE months_since >= 120')),
        panel(4, "Cars Untouched 20+ Years", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS deep_ghosts = COUNT(*) WHERE months_since >= 240')),
        panel(5, "Median Months Since Status Change", "stat", 20, 0, 4, 5, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS med_months = MEDIAN(months_since)'), "short", 0),
        panel(6, "Activity Recency Distribution", "barchart", 0, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | EVAL bucket = CASE(months_since < 6, "0-6 mo", months_since < 12, "6-12 mo", months_since < 24, "1-2 y", months_since < 60, "2-5 y", months_since < 120, "5-10 y", "10+ y") | STATS cars = COUNT(*) BY bucket | SORT cars DESC')),
        panel(7, "Status-Date Year Distribution", "timeseries", 12, 5, 12, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL status_year = DATE_EXTRACT("year", KoeretoejRegistreringStatusDato) | WHERE status_year >= 1990 AND status_year <= 2026 | EVAL year_date = TO_DATETIME(CONCAT(TO_STRING(status_year), "-01-01")) | STATS cars = COUNT(*) BY year_date | SORT year_date ASC')),
        panel(8, "Dormant Cars (10+ years) by Fuel", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL AND {FUEL} IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | WHERE months_since >= 120 | STATS dormant = COUNT(*) BY fuel = {FUEL} | SORT dormant DESC | LIMIT 10')),
        panel(9, "Dormant Cars by Registration Decade", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL AND {YEAR} IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()), decade = CASE({YEAR} < 1980, "Before 1980", {YEAR} < 1990, "1980s", {YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | WHERE months_since >= 120 | STATS dormant = COUNT(*) BY decade | SORT decade ASC')),
        panel(10, "Inspection Coverage of Dormant Cars", "barchart", 16, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()), bucket = CASE(months_since < 12, "<1y", months_since < 60, "1-5y", months_since < 120, "5-10y", "10+y") | STATS total = COUNT(*), with_inspection = COUNT(*) WHERE {INSPECTION_RESULT} IS NOT NULL BY bucket | EVAL inspection_pct = ROUND(with_inspection * 100.0 / total, 1) | SORT bucket ASC'), "percent", 1),
        panel(11, "Most Dormant Brands (10+y Untouched Count)", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL AND {BRAND} IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | WHERE months_since >= 120 | STATS dormant_cars = COUNT(*) BY brand = {BRAND} | SORT dormant_cars DESC | LIMIT 25')),
        panel(12, "Brands With Highest Dormancy Rate", "table", 8, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL AND {BRAND} IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS total = COUNT(*), dormant = COUNT(*) WHERE months_since >= 120 BY brand = {BRAND} | WHERE total >= 1000 | EVAL dormancy_pct = ROUND(dormant * 100.0 / total, 1) | SORT dormancy_pct DESC | LIMIT 25')),
        panel(13, "Oldest Status-Date Cars (Deep Ghosts)", "table", 16, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND KoeretoejRegistreringStatusDato IS NOT NULL AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | EVAL months_since = DATE_DIFF("month", KoeretoejRegistreringStatusDato, NOW()) | STATS deepest_months = MAX(months_since), cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | WHERE deepest_months >= 240 | SORT deepest_months DESC | LIMIT 25')),
    ]
    return dashboard("DMR Dormant Fleet (Untouched Cars)", "dmr-dormant-fleet", "283,390 currently-registered passenger cars haven't had a status update in 10+ years. The dormant fleet — barn finds, forgotten leasing, abandoned-but-still-on-plates — visualized.", panels, [])


def brand_concentration():
    panels = [
        panel(1, "Tesla Cars per Model", "stat", 0, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} == "TESLA" | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) | EVAL cars_per_model = cars * 1.0 / models | KEEP cars_per_model'), "short", 0),
        panel(2, "VW Cars per Model", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} == "VOLKSWAGEN" | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) | EVAL cars_per_model = cars * 1.0 / models | KEEP cars_per_model'), "short", 0),
        panel(3, "Total Distinct Models — Current Fleet", "stat", 10, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {MODEL} IS NOT NULL | STATS distinct_models = COUNT_DISTINCT({MODEL})")),
        panel(4, "Brands With ≥10 Distinct Models", "stat", 15, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE models >= 10 | STATS brands_wide_lineup = COUNT(*)")),
        panel(5, "Brands With Only 1 Model", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE models == 1 | STATS one_model_brands = COUNT(*)")),
        panel(6, "Cars per Model — Top 20 Brands", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE cars >= 10000 | EVAL cars_per_model = cars * 1.0 / models | SORT cars_per_model DESC | LIMIT 20")),
        panel(7, "Distinct Models per Brand — Top 20", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE cars >= 10000 | SORT models DESC | LIMIT 20")),
        panel(8, "Lineup Width Distribution", "barchart", 0, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE cars >= 100 | EVAL tier = CASE(models == 1, "1 model", models <= 3, "2-3", models <= 10, "4-10", models <= 30, "11-30", models <= 100, "31-100", "100+") | STATS brands = COUNT(*) BY tier | SORT brands DESC')),
        panel(9, "Cars per Model by Decade of First Registration", "barchart", 8, 14, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL AND {YEAR} >= 1990 | EVAL decade = CASE({YEAR} < 2000, "1990s", {YEAR} < 2010, "2000s", {YEAR} < 2020, "2010s", "2020s") | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY decade | EVAL cars_per_model = cars * 1.0 / models | SORT decade ASC')),
        panel(10, "Top-Model Concentration (Top Model Share)", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*) BY brand = {BRAND}, model = {MODEL} | STATS top_model_cars = MAX(cars), total_cars = SUM(cars) BY brand | WHERE total_cars >= 10000 | EVAL top_model_share_pct = ROUND(top_model_cars * 100.0 / total_cars, 1) | SORT top_model_share_pct DESC | LIMIT 20"), "percent", 1),
        panel(11, "Most Concentrated Brands (Few Models)", "table", 0, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE cars >= 5000 | EVAL cars_per_model = cars * 1.0 / models | SORT cars_per_model DESC | LIMIT 25")),
        panel(12, "Widest Lineup Brands (Many Models)", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE cars >= 5000 | EVAL cars_per_model = cars * 1.0 / models | SORT models DESC | LIMIT 25")),
        panel(13, "Brands With Only 1 Distinct Model", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {MODEL} IS NOT NULL | STATS cars = COUNT(*), models = COUNT_DISTINCT({MODEL}) BY brand = {BRAND} | WHERE models == 1 AND cars >= 5 | SORT cars DESC | LIMIT 25")),
    ]
    return dashboard("DMR Brand Concentration (Lineup Width)", "dmr-brand-concentration", "Tesla sells 4,479 cars per model; VW sells 819. Brand strategy is measurable: concentrated (Tesla, Suzuki, Kia) vs sprawling (VW, Citroën, Peugeot). The platform-strategy story in one chart.", panels, [])


def alphabet_of_brands():
    panels = [
        panel(1, "Distinct Brands in Current Fleet", "stat", 0, 0, 5, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | STATS distinct_brands = COUNT_DISTINCT({BRAND})")),
        panel(2, "Top Letter — V (cars)", "stat", 5, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS v_cars = COUNT(*) WHERE init_letter == "V"')),
        panel(3, "Most Diverse Letter — F (brands)", "stat", 10, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS f_brands = COUNT_DISTINCT({BRAND}) WHERE init_letter == "F"')),
        panel(4, "Rarest Letter — Q (cars)", "stat", 15, 0, 5, 5, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS q_cars = COUNT(*) WHERE init_letter == "Q"')),
        panel(5, "Letters With ≥10 Brands", "stat", 20, 0, 4, 5, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS brands = COUNT_DISTINCT({BRAND}) BY first | WHERE brands >= 10 | STATS diverse_letters = COUNT(*)")),
        panel(6, "Cars by First Letter", "barchart", 0, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS cars = COUNT(*) BY first_letter = first | SORT cars DESC | LIMIT 30")),
        panel(7, "Distinct Brands per Letter", "barchart", 12, 5, 12, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS brands = COUNT_DISTINCT({BRAND}) BY first_letter = first | SORT brands DESC | LIMIT 30")),
        panel(8, "Avg Cars per Brand by Letter", "barchart", 0, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS cars = COUNT(*), brands = COUNT_DISTINCT({BRAND}) BY first_letter = first | WHERE brands >= 3 | EVAL cars_per_brand = cars * 1.0 / brands | SORT cars_per_brand DESC | LIMIT 20")),
        panel(9, "Fuel Mix by First Letter", "barchart", 8, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {FUEL} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS cars = COUNT(*) BY first_letter = first, fuel = {FUEL} | SORT first_letter ASC, cars DESC | LIMIT 80"), stacking="normal"),
        panel(10, "Avg Car Age by First Letter", "barchart", 16, 14, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL AND {YEAR} >= 1980 AND {YEAR} <= 2026 | EVAL init_letter = SUBSTRING({BRAND}, 1, 1), age = 2026 - {YEAR} | STATS cars = COUNT(*), avg_age = AVG(age) BY first_letter = first | WHERE cars >= 1000 | SORT avg_age DESC | LIMIT 20")),
        panel(11, "Q-Brand Spotlight", "table", 0, 23, 8, 9, q(f'WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | WHERE init_letter == "Q" | STATS cars = COUNT(*) BY brand = {BRAND} | SORT cars DESC | LIMIT 10')),
        panel(12, "Letters Sorted by Brand Diversity", "table", 8, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS cars = COUNT(*), brands = COUNT_DISTINCT({BRAND}) BY first_letter = first | SORT brands DESC | LIMIT 30")),
        panel(13, "Endangered Letters (≤25 cars total)", "table", 16, 23, 8, 9, q(f"WHERE {CURRENT_SCOPE} AND {BRAND} IS NOT NULL | EVAL init_letter = SUBSTRING({BRAND}, 1, 1) | STATS cars = COUNT(*), brands = COUNT_DISTINCT({BRAND}) BY first_letter = first | WHERE cars <= 100 | SORT cars ASC | LIMIT 15")),
    ]
    return dashboard("DMR Alphabet of Brands", "dmr-alphabet-of-brands", "V dominates (465k cars, 24 brands) thanks to Volvo + VW. F is most diverse (84 distinct brands — Ferrari to Ford). Q is the rarest letter — just 1 brand, 3 cars. The alphabet of Danish motoring.", panels, [])


SUITE_LINKS = [
    {"title": "Electrification & Fuel Transition", "type": "dashboards", "dashboard": "dmr-electrification-fuel-transition", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Market, Leasing & Brands", "type": "dashboards", "dashboard": "dmr-market-leasing-brands", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Performance & Practicality", "type": "dashboards", "dashboard": "dmr-performance-practicality", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Inspection & Compliance", "type": "dashboards", "dashboard": "dmr-inspection-compliance", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "History & Heritage", "type": "dashboards", "dashboard": "dmr-history-heritage", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Environmental Profile", "type": "dashboards", "dashboard": "dmr-environmental-profile", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Body, Colour & Preferences", "type": "dashboards", "dashboard": "dmr-body-colour-preferences", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Engine Extinction Event", "type": "dashboards", "dashboard": "dmr-engine-extinction", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Paper Speed Records", "type": "dashboards", "dashboard": "dmr-paper-speed", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Acoustic Fleet Profile", "type": "dashboards", "dashboard": "dmr-acoustic-profile", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Model Year Time Machine", "type": "dashboards", "dashboard": "dmr-model-year-lag", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Shrinking Engine", "type": "dashboards", "dashboard": "dmr-shrinking-engine", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Fleet Weight & Power-to-Weight", "type": "dashboards", "dashboard": "dmr-weight-power", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Accident & Damage Files", "type": "dashboards", "dashboard": "dmr-accident-files", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Wheelbase Chronicles", "type": "dashboards", "dashboard": "dmr-wheelbase-creep", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Fake Two-Seater (Yellow-Plate Fleet)", "type": "dashboards", "dashboard": "dmr-fake-two-seater", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Tow-It-All Index", "type": "dashboards", "dashboard": "dmr-tow-it-all", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Sound of Silence (Stationary Noise)", "type": "dashboards", "dashboard": "dmr-sound-of-silence", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Track Width Creep", "type": "dashboards", "dashboard": "dmr-track-width-creep", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "NOx & CO Honesty Check", "type": "dashboards", "dashboard": "dmr-nox-co-honesty", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Danish Driving Habits", "type": "dashboards", "dashboard": "dmr-driving-habits", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Chiptuning Hall of Fame", "type": "dashboards", "dashboard": "dmr-chiptuning-hall", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "250 km/h Club", "type": "dashboards", "dashboard": "dmr-250-club", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Vintage Leasing", "type": "dashboards", "dashboard": "dmr-vintage-leasing", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Diesel's Last Stand", "type": "dashboards", "dashboard": "dmr-diesel-last-stand", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Red Car Myth (Colour × Accidents)", "type": "dashboards", "dashboard": "dmr-red-car-myth", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Ghost Fleet (Lifespan & Mortality)", "type": "dashboards", "dashboard": "dmr-ghost-fleet", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Turbocharging Era (Specific Output)", "type": "dashboards", "dashboard": "dmr-turbocharging-era", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Brand Invasion (Newcomers & Departures)", "type": "dashboards", "dashboard": "dmr-brand-invasion", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Door-Seat Weirdness Matrix", "type": "dashboards", "dashboard": "dmr-door-seat-matrix", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "7-Seat Explosion", "type": "dashboards", "dashboard": "dmr-seven-seat-explosion", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Dormant Fleet (Untouched Cars)", "type": "dashboards", "dashboard": "dmr-dormant-fleet", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Brand Concentration (Lineup Width)", "type": "dashboards", "dashboard": "dmr-brand-concentration", "includeVars": False, "keepTime": True, "targetBlank": False},
    {"title": "Alphabet of Brands", "type": "dashboards", "dashboard": "dmr-alphabet-of-brands", "includeVars": False, "keepTime": True, "targetBlank": False},
]


CATEGORIES = {
    "01 Fleet & Overview": [
        ("dmr-overview", None),  # already exists on disk, just relocate
        ("dmr-electrification-fuel-transition", "electrification"),
        ("dmr-market-leasing-brands", "market"),
        ("dmr-history-heritage", "history"),
        ("dmr-environmental-profile", "environmental"),
    ],
    "02 Performance & Engineering": [
        ("dmr-performance-practicality", "performance"),
        ("dmr-weight-power", "weight_power"),
        ("dmr-engine-extinction", "engine_extinction"),
        ("dmr-shrinking-engine", "shrinking_engine"),
        ("dmr-turbocharging-era", "turbocharging_era"),
        ("dmr-paper-speed", "paper_speed"),
        ("dmr-250-club", "two_fifty_club"),
        ("dmr-tow-it-all", "tow_it_all"),
    ],
    "03 Body, Design & Sound": [
        ("dmr-body-colour-preferences", "body_colour"),
        ("dmr-wheelbase-creep", "wheelbase_creep"),
        ("dmr-track-width-creep", "track_width_creep"),
        ("dmr-door-seat-matrix", "door_seat_matrix"),
        ("dmr-seven-seat-explosion", "seven_seat_explosion"),
        ("dmr-fake-two-seater", "fake_two_seater"),
        ("dmr-acoustic-profile", "acoustic_profile"),
        ("dmr-sound-of-silence", "sound_of_silence"),
    ],
    "04 Compliance, Safety & Emissions": [
        ("dmr-inspection-compliance", "inspection"),
        ("dmr-nox-co-honesty", "nox_co_honesty"),
        ("dmr-accident-files", "accident_files"),
        ("dmr-red-car-myth", "red_car_myth"),
        ("dmr-driving-habits", "driving_habits"),
    ],
    "05 Market & Lifecycle": [
        ("dmr-brand-invasion", "brand_invasion"),
        ("dmr-brand-concentration", "brand_concentration"),
        ("dmr-chiptuning-hall", "chiptuning_hall"),
        ("dmr-vintage-leasing", "vintage_leasing"),
        ("dmr-diesel-last-stand", "diesel_last_stand"),
        ("dmr-alphabet-of-brands", "alphabet_of_brands"),
        ("dmr-model-year-lag", "model_year_lag"),
        ("dmr-ghost-fleet", "ghost_fleet"),
        ("dmr-dormant-fleet", "dormant_fleet"),
    ],
}


def update_overview_links(overview_path):
    overview = json.loads(overview_path.read_text(encoding="utf-8"))
    suite_uids = {link["dashboard"] for link in SUITE_LINKS}
    existing = [link for link in overview.get("links", []) if link.get("dashboard") not in suite_uids]
    overview["links"] = SUITE_LINKS + existing
    overview_path.write_text(json.dumps(overview, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    # Wipe old layout (root JSONs + previous subfolders) so deletions propagate cleanly
    if DASHBOARD_DIR.exists():
        for entry in DASHBOARD_DIR.iterdir():
            if entry.is_file() and entry.suffix == ".json":
                # Preserve dmr-overview.json content (the only one not regenerated)
                if entry.name == "dmr-overview.json":
                    overview_cached = entry.read_text(encoding="utf-8")
                entry.unlink()
            elif entry.is_dir():
                for sub in entry.rglob("*.json"):
                    sub.unlink()
                entry.rmdir() if not any(entry.iterdir()) else None
        # Best-effort second pass to remove now-empty dirs
        for entry in list(DASHBOARD_DIR.iterdir()):
            if entry.is_dir() and not any(entry.iterdir()):
                entry.rmdir()

    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    overview_target = None
    for category, items in CATEGORIES.items():
        cat_dir = DASHBOARD_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        for uid, builder_name in items:
            target = cat_dir / f"{uid}.json"
            if uid == "dmr-overview":
                target.write_text(overview_cached, encoding="utf-8")
                overview_target = target
            else:
                builder = globals()[builder_name]
                doc = builder()
                target.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if overview_target:
        update_overview_links(overview_target)


if __name__ == "__main__":
    main()
