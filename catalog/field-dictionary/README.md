# DMR Field Dictionary

Source files for the Danish Motor Register (`dmr-raw-000002`) field name reference.

Generated: 2026-05-11  
Fields: 260  
Confidence: mix of official/inferred (see each record's `confidence` field)

## Files

| File | Format | Use for |
|---|---|---|
| `dmr_field_dictionary.json` | JSON array | Machine-readable field lookup; 260 records with English name, meaning, type, preferred ES\|QL field, agent notes, confidence |
| `dmr_field_dictionary.csv` | CSV | Spreadsheet viewing of the same 260 records |
| `DMR_FIELD_DICTIONARY_SKILL.md` | Markdown | Human-readable version; vocabulary table + agent rules + full field table |
| `dmr_recommended_aliases.json` | JSON object | 17 short alias → full field path mappings used by dashboards and the flat views |

## What the dmr-domain skill uses

The `specs/skills/dmr-domain.skill.json` skill extracts the two highest-value pieces:

1. **vocabulary block** — the Danish component → English meaning table. Lets the agent decode any unknown field name from its parts.
2. **field-guide additions** — extra field paths for vehicle_type, km_per_liter, inspection_date, odometer_km (unvalidated), model_year, towing_capable, taxi_suitable.

The full 260-field dictionary is NOT imported into any skill — it would overflow the context window (65,000+ tokens).

## Accuracy notes

- All 17 recommended aliases have been verified against live Elasticsearch mapping and known-good ES|QL queries.
- `odometer_km` (`SynResultatStruktur.KoeretoejMotorKilometerstand`): path is correct but unit/scaling is unverified; max values appear corrupt. See dmr-domain data-quality block.
- Fields marked `confidence: inferred` are translated from Danish naming conventions; verify with sample values before formal reporting.
- `KoeretoejOplysningTrafikskade` is described as generic "Vehicle Trafikskade" — this is the traffic accident damage flag (Trafikskade). Our field-guide uses the more descriptive label.
