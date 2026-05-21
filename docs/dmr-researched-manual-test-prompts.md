# DMR Researched Manual Test Prompts

Researched against `dmr-raw-000002` on 2026-05-09.

Use these prompts for manual Kibana Agent Builder testing. They are designed to cover more of the dataset than the current LLM eval, including known denominator traps, Danish label translation, long-tail records, and cross-domain fallback cases.

## Dataset Cues To Expect

- Registered passenger cars: about `2,935,158`.
- Top passenger-car fuels: petrol `1,768,149`, electric `597,678`, diesel `569,235`.
- Top passenger-car brands: Volkswagen, Toyota, Peugeot, Skoda, Ford.
- Most common body styles: hatchback, station wagon, MPV; body style is missing on many rows.
- Most common colours: grey, unknown, black, white.
- Private use is about `98.8%` of registered passenger cars; taxi use is about `0.2%`.
- AWD/4WD is `389,001` cars: `13.3%` of all registered passenger cars and `17.2%` of cars with known driven-axle data.
- Power percentiles: P50 about `85 kW`, P90 about `207 kW`, P99 about `378 kW`.
- EV first registrations grow from `2,167` in 2014 to `136,265` in 2025 and `38,181` in partial 2026 data.
- Leasing: `534,900` leased cars; within-fuel leasing rates are electric `20.1%`, petrol `14.4%`, diesel `28.3%`.
- Top permit types: `Synsfri Sammenkobling`, `Veterankørsel`, `Udlejning Uden Fører`.
- Newest brands include DEEPAL, Leapmotor, OMODA, JAECOO, Exlantix, SKYWORTH, Firefly.

## DMR Fleet & Lookup

Use `DMR Fleet & Lookup`.

1. `Across all vehicle types, what are the biggest registration status and vehicle-type combinations?`
   - Expected: uses fleet status overview; should include deregistered passenger cars and registered passenger cars.

2. `Compare registered passenger cars, vans, trailers, and motorcycles by current count.`
   - Expected: all-vehicle status/type scope, not passenger-car-only scope.

3. `What are the top 15 passenger-car brands, and how far ahead is Volkswagen?`
   - Expected: Volkswagen around `371,699`; passenger-car scope.

4. `Which passenger-car models are most common, and which brands own the top 10?`
   - Expected: Volkswagen UP!, Peugeot 208, Toyota Yaris, Volkswagen Polo, Toyota Aygo.

5. `What share of registered passenger cars have unknown or missing colour data?`
   - Expected: uses color summary; explains `Ukendt` as unknown and treats blank/missing separately if shown.

6. `Which body styles dominate the registered passenger-car fleet, and how many records have no body style?`
   - Expected: hatchback, station wagon, MPV; notes missing body-style rows.

7. `How many registered passenger cars have 2, 3, 4, 5, or 6 doors?`
   - Expected: uses door summary and filters implausible door counts.

8. `For registered passenger cars, compare private passenger use with taxi, ambulance, and official-government use.`
   - Expected: uses usage summary; percentages from tool, not invented.

9. `How common is AWD/4WD among passenger cars when measured against all cars versus cars with known drivetrain data?`
   - Expected: distinguishes `13.3%` of all cars from `17.2%` of known drivetrain rows.

10. `Look up registration ES81876 and summarize the vehicle in English.`
    - Expected: plate lookup; should find a recent Porsche 911 Carrera GTS Cabriolet if data remains unchanged.

## DMR Performance Analyst

Use `DMR Performance Analyst`.

1. `What is a typical registered passenger car in power terms? Show median, P90, P99, and max valid kW with hp conversions.`
   - Expected: performance summary; no corrupt outlier claims.

2. `How do electric, petrol, and diesel cars compare by total weight?`
   - Expected: electric much heavier; median electric total weight around `2,489 kg`.

3. `Which fuel types have the best power-to-weight distribution?`
   - Expected: uses power-to-weight summary; reports kW/kg.

4. `How many 0-cylinder, 3-cylinder, 4-cylinder, 6-cylinder, 8-cylinder, 12-cylinder, and 16-cylinder cars are registered?`
   - Expected: cylinder count summary; do not infer V-layout from cylinder count.

5. `Show the strongest valid high-power cars above 500 kW, excluding corrupt registry outliers.`
   - Expected: high-power list with threshold `500`; no clamped corrupt 750 kW framing.

6. `Which brands have the highest average braked towing capacity among tow-capable passenger cars?`
   - Expected: towing by brand; mentions braked towing capacity and the minimum sample threshold.

7. `Which mainstream brands combine high tow capacity with a large sample size?`
   - Expected: towing tool; should avoid over-focusing on niche motorhome conversions.

8. `How are registered passenger cars distributed across economy, family, executive, performance, and exotic power tiers?`
   - Expected: power segment summary; explains tier thresholds if included.

9. `Which body styles have the highest electric share?`
   - Expected: EV share by body style, not general fuel mix.

10. `Compare Porsche, BMW, and Mercedes-Benz by current count, average valid power, and leasing rate.`
    - Expected: Qwen-only analyst fallback tool if asked to DMR Vehicle Registry Analyst; performance agent should redirect to analyst if it lacks the combined comparison.

## DMR Historical Analyst

Use `DMR Historical Analyst`.

1. `When did EVs move from niche to mainstream in Danish passenger-car registrations?`
   - Expected: EV adoption trend; breakout around 2019-2021, high share in 2025 and partial 2026.

2. `How did diesel's share change from the 1970s through the 2020s?`
   - Expected: decade profile; diesel peaks in the 2010s, falls in the 2020s.

3. `Which decades have the highest survival rate in the current registry, and why are old decades biased?`
   - Expected: decade profile; mentions survivorship bias for pre-1980 rows.

4. `How has the registered fleet changed from petrol dominance to electric growth by decade?`
   - Expected: decade profile; 2020s EV share around `44%` of decade records.

5. `Show EV adoption from 2014 onward and call out the biggest jumps.`
   - Expected: year-by-year EV trend; large jumps around 2019-2021.

6. `Is NCAP test coverage rising or falling for recent first-registration years?`
   - Expected: NCAP adoption by year; should avoid saying this is a safety rating.

7. `Which new passenger-car brands arrived in Denmark in 2025 and 2026?`
   - Expected: newest brands; DEEPAL in 2026, Leapmotor/OMODA/JAECOO in 2025.

8. `Which brands have the longest registry history but still have current registered cars?`
   - Expected: oldest brands or brand presence; treats first registration as registry evidence.

9. `What does the registry say about veteran passenger cars, and which brands dominate?`
   - Expected: veteran summary; explicitly says registry veteran flag.

10. `Do registration months suggest a spring or summer buying season?`
    - Expected: registration-by-month; identifies peak and low months.

## DMR Market & Compliance

Use `DMR Market & Compliance`.

1. `How common is leasing overall, and how do within-fuel leasing rates compare for electric, petrol, and diesel cars?`
   - Expected: leasing summary; diesel within-fuel rate around `28.3%`, electric `20.1%`, petrol `14.4%`.

2. `Which fuel type has the highest leasing penetration, and which has the largest absolute leased count?`
   - Expected: distinguishes rate from absolute count.

3. `What inspection outcomes exist, and how should the Danish labels be translated?`
   - Expected: inspection summary; translates `Godkendt`, reinspection, and not-approved labels.

4. `Which brands have the best inspection pass rates, and what caveat applies?`
   - Expected: pass-rate-by-brand; mentions fleet age/composition caveat.

5. `Are newer cars much more likely to pass inspection than older cars?`
   - Expected: inspection-by-age; should be nuanced rather than assume.

6. `How many registered passenger cars have the Trafikskade accident-damage flag, and which brands show up most?`
   - Expected: accident summary; names `Trafikskade` as traffic accident damage.

7. `What are the most common special permit types, and what does Synsfri Sammenkobling mean?`
   - Expected: permit summary; translates as inspection-free towing coupling permit.

8. `How many vehicles have Udlejning Uden Fører, Veterankørsel, or Chiptuning Godkendt permits?`
   - Expected: permit type summary; translates labels.

9. `What are some currently registered passenger-car brands with only one to three cars?`
   - Expected: rarity by brand with a low threshold; avoids claiming missing brands never existed.

10. `Which brands have the most active passenger-car leases today?`
    - Expected: `dmr-car-active-leasing-by-brand`; ranks brands by currently-active leases (`LeasingGyldigFra <= now <= LeasingGyldigTil`) with a minimum 500-car fleet filter.

11. `How many cars carry a totalskadet block reason, and how is that different from the Trafikskade flag?`
    - Expected: `dmr-car-block-reason-summary`; ~562k passenger cars Totalskadet køretøj, ~21k Skadet køretøj, ~20k Mangel. Names the Trafikskade boolean (~5.5k) as a separate, narrower signal. Notes that some cars are still in `Registreret` status (rebuild scenario).

12. `Which brands have the most totalskadede passenger cars?`
    - Expected: `dmr-car-block-reason-by-brand` with default `Totalskadet køretøj`.

13. `Which brands hold the most Tempo 100 caravan-towing permits?`
    - Expected: `dmr-car-permit-by-brand` with `permit_name = "Tempo 100"`.

10. `Can the inspection result fields be treated as a current campaign result, or are they registry fields?`
    - Expected: explains stored registry fields, not a time-bounded campaign.

## DMR Vehicle Registry Analyst

Use `DMR Vehicle Registry Analyst`.

1. `Among registered passenger cars, which red Tesla models have braked towing capacity above 1500 kg?`
   - Expected: dedicated red Tesla towing fallback tool.

2. `How many registered passenger cars are red, electric, and above 300 kW?`
   - Expected: dedicated red electric high-power fallback tool.

3. `Find registered electric cabriolets and group them by brand and model.`
   - Expected: dedicated electric cabriolet fallback tool.

4. `Compare Porsche, BMW, and Mercedes-Benz passenger cars by current count, average valid power, and leasing rate.`
   - Expected: dedicated premium-brand comparison fallback tool.

5. `Which recent 2026 registrations are electric, and can you summarize a few examples?`
   - Expected: if no dedicated tool covers it, should say it cannot verify with available tools rather than inventing ES|QL.

6. `Among red Teslas that can tow, which model has the highest average braked towing capacity?`
   - Expected: red Tesla towing fallback; grouped by model.

7. `Are electric cabriolets a large or tiny segment of the current passenger-car fleet?`
   - Expected: electric cabriolet fallback; should present it as niche.

8. `For Porsche, BMW, and Mercedes-Benz, which has the highest leasing penetration and which has the highest average power?`
   - Expected: premium-brand comparison fallback; separates rate from count and power.

## Redirect And Robustness Tests

Use these to check scoped agents produce a visible redirect sentence and do not call tools.

1. Ask `DMR Fleet & Lookup`: `Which brands have the highest average power?`
   - Expected: redirects to `dmr-performance`.

2. Ask `DMR Performance Analyst`: `What are the rarest registered passenger-car brands?`
   - Expected: redirects to `dmr-market`.

3. Ask `DMR Historical Analyst`: `How many cars are leased by fuel type?`
   - Expected: redirects to `dmr-market`.

4. Ask `DMR Market & Compliance`: `What was EV adoption by year since 2014?`
   - Expected: redirects to `dmr-history`.

5. Ask `DMR Fleet & Lookup`: `Compare Porsche, BMW, and Mercedes-Benz by count, average power, and leasing.`
   - Expected: redirects to `dmr-analyst`.

6. Ask `DMR Performance Analyst`: `Find vehicle ES81876.`
   - Expected: redirects to `dmr-core`.

7. Ask `DMR Market & Compliance`: `Which body styles have the highest electric share?`
   - Expected: redirects to `dmr-performance`.

8. Ask `DMR Historical Analyst`: `What is the current AWD share?`
   - Expected: redirects to `dmr-core`.
