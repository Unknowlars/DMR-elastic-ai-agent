# DMR Agent Test Prompts

Use this guide in Kibana Agent Builder Chat. Pick the agent by the visible name in the Kibana agent list, then paste one prompt.

Last updated: 2026-05-12 for the public local-LLM README pass (all DMR screenshots and test targets use local Qwen3.5-9b).

## Quick Agent Chooser

| If the question is about... | Use this Kibana agent | LLM target |
|---|---|---|
| Exact lookup, fleet size, current registered passenger cars, top brands/models, fuel mix, colour, body style, doors, AWD, usage | DMR Fleet & Lookup | Qwen3.5-9b |
| Power, speed, cylinders, weight, towing, CO2 bands, emission norms, power-to-weight, powerful brands | DMR Performance Analyst | Qwen3.5-9b |
| Registration years, decades, EV adoption over time, diesel history, old/new brands, veteran cars, 100-year trends | DMR Historical Analyst | Qwen3.5-9b |
| Leasing, inspection results, pass/fail rates, accidents, rare brands, permits | DMR Market & Compliance | Qwen3.5-9b |
| Simple single-question lookup through the minimal 8-tool agent | DMR Micro Agent | Qwen3.5-9b |
| Any open-ended or creative question not covered by a dedicated tool — free ES|QL against the flat view | DMR Explorer | Qwen3.5-9b |
| Cross-domain question, dedicated multi-filter tool, or unusual filter combination | DMR Vehicle Registry Analyst | Qwen3.5-9b |
| Index discovery, mappings, or non-DMR data setup | Data Catalog Explorer, Dataset Sampler, Schema Explainer, or Elastic AI Agent | — |

Rule of thumb: start with a focused DMR agent. For anything a focused agent can't answer, try DMR Explorer (writes its own ES|QL query). Use DMR Vehicle Registry Analyst for cross-domain questions that need the broad dedicated-tool set. Use DMR Micro Agent to test minimal-tool routing on simple questions. These prompts were written for a 100% local Qwen3.5-9b setup.

## Must-Pass Smoke Tests

These prompts verify the newest fixes are deployed.

### DMR Fleet & Lookup

Prompt:
```text
How many registered passenger cars are there?
```

Expected:
- Uses the passenger-car fleet overview tool.
- Reports registered passenger cars, not all vehicles.
- Count should be `2,935,158` on the current `dmr-raw-000002` data.

Prompt:
```text
What does the current Danish passenger-car fleet look like? Include total count, average first registration year, model year, and total weight.
```

Expected:
- Count is still `2,935,158`.
- Average/year/weight fields are computed from cleaned values.

### DMR Market & Compliance

Prompt:
```text
How many registered passenger cars are leased, and what share of the fleet is that?
```

Expected:
- Uses the leasing summary.
- The total fleet denominator should match `2,935,158`.
- Leased count should be around `534,900`.

### DMR Performance Analyst

Prompt:
```text
Which brands have above-fleet-average power among registered passenger cars?
```

Expected:
- Uses the new above-average power tool.
- Mentions kW, and can convert to hp if reporting power values.

Prompt:
```text
Show the top 3 registered passenger-car models per brand.
```

Expected:
- Uses the new top-models-per-brand tool.
- Returns grouped brand/model/count rows.

## DMR Fleet & Lookup Prompts

Use this agent for lookup and current fleet composition.

Prompt:
```text
Find vehicle EN44360 and summarize the key details in English.
```

Expected:
- Uses plate lookup.
- Returns status, type, brand, model, fuel, and registration details if present.

Prompt:
```text
What are the top 10 passenger-car brands in the current Danish registry?
```

Expected:
- Uses passenger-car top brands.
- States scope: registered passenger cars.

Prompt:
```text
What are the top passenger-car models in Denmark right now?
```

Expected:
- Uses passenger-car top models.
- Does not switch to all-vehicle scope.

Prompt:
```text
What is the current fuel mix for registered Danish passenger cars?
```

Expected:
- Uses passenger-car fuel/age summary.
- Explains `El` as electric if shown.

Prompt:
```text
What is the most common colour among registered Danish passenger cars?
```

Expected:
- Uses colour summary.
- Explains `Ukendt` as unknown if it appears.

Prompt:
```text
How many AWD cars are registered in Denmark?
```

Expected:
- Uses AWD summary.
- Explains driven axle coding in plain English.

Prompt:
```text
How are registered Danish passenger cars used? Include private use and taxi use.
```

Expected:
- Uses usage summary.
- Translates Danish usage labels when needed.

## DMR Performance Analyst Prompts

Use this agent for technical and performance questions.

Prompt:
```text
How powerful are registered Danish passenger cars? Show P50, P90, and P99 in kW and hp.
```

Expected:
- Uses performance summary.
- Uses cleaned/clamped power values.
- Converts kW to approximate hp.

Prompt:
```text
Show registered passenger cars with more than 300 kW.
```

Expected:
- Uses high-power list with a 300 kW threshold.
- Returns individual cars sorted by cleaned power.

Prompt:
```text
Which passenger-car brands have the highest average power?
```

Expected:
- Uses brand performance summary.
- Applies the minimum brand sample size.

Prompt:
```text
Are electric cars heavier than petrol cars in Denmark?
```

Expected:
- Uses weight distribution.
- Compares by fuel type and states the passenger-car scope.

Prompt:
```text
Which brands are best for towing a caravan?
```

Expected:
- Uses towing capacity by brand.
- Makes clear it is based on braked towing capacity.

Prompt:
```text
What are the power-to-weight percentiles by fuel type?
```

Expected:
- Uses power-to-weight summary.
- Reports kW/kg and explains the heuristic if needed.

Prompt:
```text
How many V8, V12, and V16 passenger cars are registered?
```

Expected:
- Uses cylinder brand/model or cylinder count tools.
- Does not infer engine layout beyond cylinder count.

Prompt:
```text
How many Euro 6 passenger cars are registered?
```

Expected:
- Uses emission norm summary.
- Explains emission standard labels if needed.

## DMR Historical Analyst Prompts

Use this agent for time, year, and decade questions.

Prompt:
```text
How has the Danish passenger-car fleet changed over the last 100 years?
```

Expected:
- Uses decade profile.
- Mentions survivorship bias for older decades.

Prompt:
```text
Tell me the story of diesel cars in Denmark. When did diesel rise and when did it fall?
```

Expected:
- Uses decade profile or diesel particle-filter adoption where appropriate.
- Grounds the answer in returned decade/year data.

Prompt:
```text
How fast has EV adoption grown in Denmark year by year?
```

Expected:
- Uses EV adoption trend.
- Gives a year-by-year trend, not just a current count.

Prompt:
```text
Are cars getting cleaner in Denmark? Show the CO2 trend by registration year.
```

Expected:
- Uses CO2 by year.
- Mentions NEDC/WLTP caveat.

Prompt:
```text
Which car brands are newest in the Danish registry?
```

Expected:
- Uses newest brands.
- Treats first registration year as registry evidence, not a company founding year.

Prompt:
```text
How many veteran passenger cars are registered, and which brands are most common?
```

Expected:
- Uses veteran summary.
- States the result is based on the registry veteran flag.

Prompt:
```text
Do Danish registrations have a seasonal pattern by month?
```

Expected:
- Uses registration-by-month.
- Summarizes peak and low months.

## DMR Market & Compliance Prompts

Use this agent for inspection, leasing, accident, write-offs / administrative blocks, rarity, and permit questions.

Prompt:
```text
What inspection results are recorded for registered Danish passenger cars?
```

Expected:
- Uses inspection summary.
- Translates labels such as `Godkendt`, `Afvist`, and `Betinget godkendt`.

Prompt:
```text
Which brands have the best inspection pass rates?
```

Expected:
- Uses inspection pass-rate by brand.
- Mentions that fleet age can influence pass rates.

Prompt:
```text
Do older cars fail inspection more often?
```

Expected:
- Uses inspection by age.
- Compares age bands and inspection outcomes.

Prompt:
```text
How common is leasing among electric cars compared with petrol and diesel cars?
```

Expected:
- Uses leasing summary.
- Breaks out electric, petrol, and diesel lease counts.

Prompt:
```text
How many registered passenger cars have a traffic accident damage flag?
```

Expected:
- Uses accident summary.
- Explains the flag as `Trafikskade`.

Prompt:
```text
Which brands have the most active leases today?
```

Expected:
- Uses `dmr-car-active-leasing-by-brand`.
- Reports brand, leased count, and lease share of brand's currently-registered fleet.
- Filters out brands with fewer than 500 currently-registered cars.

Prompt:
```text
How many passenger cars in Denmark are marked as totalskadet (write-offs)?
```

Expected:
- Uses `dmr-car-block-reason-summary` (which queries the raw index — does NOT filter to Registreret).
- **Expected numbers (Personbil, all statuses, validated 2026-05):** Totalskadet køretøj **561,770**, Skadet køretøj 21,236, Mangel 20,143, Køretøjet er blokeret 12,111, Indkaldt til registrering 531, Henvist til SKAT 172.
- States that almost all write-offs are on Afmeldt records (rebuild scenario covers only ~2 currently-registered Totalskadet cars).
- **REGRESSION FLAG:** if the agent answers "2 totalskadet cars" it is querying `dmr-cars-flat` (Registreret only). The correct answer requires raw index or `dmr-cars-all-flat`.

Prompt:
```text
Which brands have the most totalskadet cars?
```

Expected:
- Uses `dmr-car-block-reason-by-brand` with the default `Totalskadet køretøj`.
- Ranks brands by count of cars carrying that block reason.
- **Expected top brands for Mangel (cross-check):** FORD 2,889, OPEL 2,751, VOLKSWAGEN 2,038, TOYOTA 1,729, MAZDA 1,517 (validated 2026-05).
- Notes the difference from the `dmr-car-accident-summary` Trafikskade flag.
- **REGRESSION FLAG:** if the agent returns 1-3 cars total ("FORD 1, VOLVO 1"), it is querying the Registreret-only flat view — switch to raw index or `dmr-cars-all-flat`.

Prompt:
```text
What are the rarest registered passenger-car brands in Denmark?
```

Expected:
- Uses rarity by brand.
- Does not treat missing/empty rows as proof a brand never existed.

Prompt:
```text
What types of special permits exist in the Danish vehicle registry?
```

Expected:
- Uses permit type summary.
- Translates the permit labels.

Prompt:
```text
Which brands hold the most Tempo 100 caravan-towing permits?
```

Expected:
- Uses `dmr-car-permit-by-brand` with `permit_name = "Tempo 100"`.
- Ranks brands by count.
- Translates `Tempo 100` as "approved for 100 km/h caravan towing".

Prompt:
```text
Top brands with Veterankørsel permits among currently registered cars.
```

Expected:
- Uses `dmr-car-permit-by-brand` with `permit_name = "Veterankørsel"`.
- Returns count by brand limited to current registrations.

## DMR Vehicle Registry Analyst Prompts

Use this full fallback agent for cross-domain or unusual multi-filter questions. The agent now has dedicated tools for these specific multi-filter queries — it should NOT be generating ES|QL for them.

Prompt:
```text
Among registered passenger cars, which red Tesla models have towing capacity above 1500 kg?
```

Expected:
- Uses `dmr-car-red-tesla-towing-summary` dedicated tool.
- Does **not** call `platform.core.generate_esql` or `platform.core.search`.
- Groups results by model with count, avg, and max braked towing.

Prompt:
```text
How many registered passenger cars are red, electric, and have more than 300 kW?
```

Expected:
- Uses `dmr-car-red-electric-high-power-count` dedicated tool.
- Does **not** answer from memory.

Prompt:
```text
Find registered electric cabriolets and group them by brand and model.
```

Expected:
- Uses `dmr-car-electric-cabriolets-by-model` dedicated tool.
- Returns brand/model grouped counts.

Prompt:
```text
Compare Porsche, BMW, and Mercedes-Benz passenger cars by current count, average power, and leasing presence.
```

Expected:
- Uses `dmr-car-premium-brand-market-performance-comparison` dedicated tool.
- Returns all three brands in a single comparison.

## DMR Micro Agent Prompts

Use this agent when testing minimal-tool routing with the same local Qwen3.5-9b connector. Only 8 tools — suitable for single simple questions.

Prompt:
```text
How many registered passenger cars are there?
```
Prompt:
```text
What are the top 5 car brands in Denmark?
```
Prompt:
```text
Find vehicle EN44360.
```
Prompt:
```text
What is the fuel mix for Danish passenger cars?
```

Expected for all: single tool call, brief answer, no multi-step reasoning.

## Skills Tests

Use these to verify the `dmr-domain` and `dmr-glossary` skills are working. Test in DMR Vehicle Registry Analyst (has both skills assigned).

Prompt:
```text
What is the ES|QL field path for braked towing capacity?
```
Expected: Returns `KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkoblingsvaegtMedBremser` from the dmr-domain field-guide block.

Prompt:
```text
What does "Betinget godkendt" mean in the inspection results?
```
Expected: Translates as "conditionally passed" from the dmr-glossary skill. The model should NOT guess — it should load the skill.

Prompt:
```text
What does "Synsfri Sammenkobling" mean?
```
Expected: "Inspection-free towing coupling permit" — a common mis-translation test.

Prompt:
```text
What data quality rules apply to power values in the DMR dataset?
```
Expected: States the 750 kW cap and explains CLAMP behaviour from the dmr-domain data-quality block.

## Redirect Tests

These are useful when checking small-model routing behavior.

Prompt for DMR Fleet & Lookup:
```text
Which brands have above-fleet-average power?
```

Expected:
- Should redirect to DMR Performance Analyst, or use no data tool if out of scope.

Prompt for DMR Performance Analyst:
```text
How many cars are leased?
```

Expected:
- Should redirect to DMR Market & Compliance.

Prompt for DMR Historical Analyst:
```text
Find vehicle EN44360.
```

Expected:
- Should redirect to DMR Fleet & Lookup.

Prompt for DMR Market & Compliance:
```text
How fast has EV adoption grown year by year?
```

Expected:
- Should redirect to DMR Historical Analyst.

## Non-DMR Agents

These are not the default choice for DMR vehicle questions.

| Agent | Use when |
|---|---|
| Data Catalog Explorer | You want to discover indices or decide what datasets exist. |
| Dataset Sampler | You want example documents from an index. |
| Schema Explainer | You want field mappings, IDs, timestamps, or safe analytics paths explained. |
| Elastic AI Agent | You want general Elastic platform help outside the focused DMR agents. |

## DMR Explorer Prompts

Use this agent for any question not covered by a dedicated tool. It writes its own ES|QL query against `dmr-cars-flat` or `dmr-vehicles-flat` and executes it live. The public screenshots and tests use local Qwen3.5-9b plus the flat views created in Kibana DevTools.

**Free-form ES|QL tests — flat view:**

Prompt:
```text
How many cars have all four of these: electric fuel, AWD, more than 5 seats, registered after 2020?
```
Expected: Writes `FROM dmr-cars-flat | WHERE fuel == "El" AND awd == 2 AND seats > 5 AND year > 2020 | STATS count = COUNT(*) | LIMIT 1` or similar. Does NOT answer from memory.

Prompt:
```text
Which body styles have the highest inspection failure rate?
```
Expected: Writes a query grouping by body_style with conditional counts for IkkeGodkendt vs Godkendt, computes a failure percentage.

Prompt:
```text
Show the median kerbweight of cars by registration year from 2000 to 2024.
```
Expected: Writes `FROM dmr-cars-flat | WHERE year BETWEEN 2000 AND 2024 | STATS median_kg = PERCENTILE(kerb_kg, 50) BY year | SORT year ASC | LIMIT 30` or similar.

Prompt:
```text
What percentage of leased cars are electric vs diesel, broken out by year registered?
```
Expected: Writes a query with `is_leased == TRUE` filter, per-aggregation WHERE for fuel types, grouped by year. Multi-dimensional query.

Prompt:
```text
Which brands have both above-average power AND above-average towing capacity?
```
Expected: Uses INLINE STATS for fleet averages, then filters where both conditions are true. Demonstrates a complex analytical pattern.

**Error recovery test:**

Prompt:
```text
Show cars with fuel type = petrol and body style = station wagon.
```
Expected: The agent translates "petrol" to "Benzin" and "station wagon" to "Stationcar" (from `dmr-glossary` skill), writes `FROM dmr-cars-flat | WHERE fuel == "Benzin" AND body_style == "Stationcar"`, executes, and returns results.

**New flat-view column tests (post-2026-05-16 column additions):**

Prompt:
```text
Which brands have the most currently-registered cars carrying a totalskadet block reason?
```
Expected: Uses `blocking_reason == "Totalskadet køretøj"` against `dmr-cars-flat` (which IS the right view here — the user explicitly asked "currently-registered"). Returns ~2-3 cars (rebuild scenario). The agent must explicitly mention that the full-registry count is ≈561,770 to contextualise.

Prompt:
```text
Have totalskadede cars increased over time?
```
Expected: Uses `dmr-cars-all-flat` (NOT `dmr-cars-flat` — would return near-zero). Groups by `year` with `blocking_reason == "Totalskadet køretøj"`. **Expected trend:** ~17k/year in 2010-2011, declining steadily to ~5k/year by 2018 and single digits for 2025-2026 (newer cars haven't had time to be totalled). The agent must NOT interpret "totalskadede" as a contraction of "total" — that misreading produced an answer about total registrations, not write-offs.

Prompt:
```text
Show me the highest NOx emission diesel cars by brand for cars from 2010 onward.
```
Expected: Queries the new `nox_emission` column against `dmr-cars-flat`, filters `fuel == "Diesel" AND year >= 2010 AND nox_emission IS NOT NULL`, groups by brand. States the value is registry-recorded (unit varies by measurement norm).

Prompt:
```text
Distribution of particle emissions (pm_emission) for Euro V vs Euro VI diesels.
```
Expected: Uses the new `pm_emission` column with euro_norm grouping. Notes that pre-Euro records are mostly null.

## Simple Test Checklist

For each answer, check:

- The selected agent matches the question category.
- The answer uses a tool before making data claims.
- "Cars" defaults to registered passenger cars unless the prompt asks for all vehicles.
- Counts, percentages, and rankings come from tool output.
- Danish labels are translated when they appear.
- Performance answers report kW and approximate hp where useful.
- Historical answers include survivorship or measurement caveats where relevant.
- The answer stays concise unless the prompt asks for a full breakdown.

---

## DMR Explorer — Free-Form ES|QL Tests

Last validated: 2026-05-11. Use `DMR Explorer` agent.

### Confirmed working in 1-2 calls (high confidence)

```text
What are the top 20 most common car models in Denmark?
```
Expected: `STATS count = COUNT(*) BY brand, model | SORT count DESC | LIMIT 20`. VW UP! leads.

```text
Which car brands dominate the Danish market? Show the top 15.
```
Expected: `STATS count = COUNT(*) BY brand | SORT count DESC | LIMIT 15`. VW at 371K.

```text
What Tesla models are registered in Denmark?
```
Expected: `dmr-car-brand-models` with `brand_upper=TESLA`. 1 call.

```text
What Porsche models are most popular?
```
Expected: `dmr-car-brand-models` with `brand_upper=PORSCHE`. 911 leads. Bar chart.

```text
In which year were the most diesel cars registered?
```
Expected: `STATS count = COUNT(*) BY year | WHERE fuel == "Diesel"`. Peak: 2017 at 56,958.

```text
Show new car registrations by year from 2005 to 2024.
```
Expected: Line chart. Peak 2021 at ~194K.

### Brand discovery tests (uses dmr-car-find-brand tool)

```text
What models does Alfa Romeo have in Denmark?
```
Expected: `dmr-car-find-brand(brand_pattern="(?i).*alfa.*")` → finds "ALFA", then `dmr-car-brand-models(brand_upper="ALFA")`. ~23 cars total.

```text
What Mercedes models are registered?
```
Expected: Discovers MERCEDES-BENZ (with hyphen). C-Klasse leads.

### Known ES|QL syntax facts (confirmed via testing)

Valid:
- `FROM dmr-cars-flat | STATS count = COUNT(*) BY field | SORT count DESC | LIMIT N`
- `TO_UPPER(brand) == "POLESTAR"` — exact case-insensitive match
- `brand RLIKE "(?i).*mercedes.*"` — case-insensitive partial match
- `WHERE year >= 2020 AND year <= 2024` — integer comparison (no DATE_EXTRACT needed)

Invalid in ES|QL — these cause parse errors:
- `STATS count() AS total` — AS keyword
- `GROUP BY field` — use `STATS BY field`
- `ORDER BY count` — use `SORT count DESC`
- `SELECT ...` — not valid ES|QL
- `AGG COUNT(*)` — not valid
- `DATE_EXTRACT("year", year)` on integer year field

### Data interpretation notes

- `taxi_suitable == TRUE`: 170K cars (type-approval flag), NOT 5K actual taxis
- `km_per_liter` for EVs: ~67 km/L is energy-equivalent, not real fuel consumption
- `awd` valid values: 1 (FWD/RWD) and 2 (AWD) — others are corrupt → NULL in flat view
- `body_style` is NULL for 14% of cars — add `IS NOT NULL` for clean breakdowns
- `ALFA ROMEO` is stored as `"ALFA"` in the DMR registry
