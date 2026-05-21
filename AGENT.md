# AGENT.md

This file is the persistent Codex session bootstrap for this repository. Read it first in new sessions.

## Purpose

This repo is the source of truth for stable Elastic Agent Builder assets for my Elasticsearch and Kibana setup.

Use it to:

- manage agent specs in `specs/agents/`
- manage custom tool specs in `specs/tools/`
- store reusable prompt text in `prompts/`
- track discovered datasets in `catalog/datasets/`
- use repo scripts for validation, export, dry-run sync, and apply sync

Do not treat Kibana UI state as the source of truth for stable assets. If something is worth keeping, it should be represented in this repo.

## Environment

Current known endpoints:

- `KIBANA_URL=http://192.168.0.238:5601`
- `ELASTICSEARCH_URL=http://192.168.0.238:9200`
- `KIBANA_SPACE_ID=default` unless explicitly overridden

Current temporary test key:

- `API_KEY=V2gzRXhKMEIwTG9yQi1Zekoya186Umh5WWtINl9sMEoySU9WMm9maWJVUQ==`

Use that key only as cached bootstrap context. Prefer runtime environment variables or `.env` for actual commands:

- `KIBANA_API_KEY`
- `ELASTICSEARCH_API_KEY`

This key is temporary and expected to be rotated/deleted. If a live command fails, verify the current key before assuming the repo or scripts are wrong.

## Repo Map

- `README.md`: beginner-friendly repo overview and path chooser
- `docs/setup-dmr-agent.md`: full get-data, ingest, agent install, dashboard install, and verification guide
- `docs/get-and-ingest-dmr-data.md`: focused DMR statistics export download and Elasticsearch ingest guide
- `catalog/datasets/`: stable dataset summaries and discovery notes
- `catalog/raw/`: exported snapshots such as live index inventory
- `dashboards/`: repo-backed Kibana dashboard definitions with fixed IDs
- `specs/agents/`: machine-readable Kibana agent specs
- `specs/tools/`: machine-readable custom tool specs
- `prompts/`: system-instruction files referenced by agent specs
- `scripts/`: validation, export, dry-run sync, and apply-sync helpers
- `.agents/skills/kibana-agent-builder/`: Elastic skill guidance and underlying CLI references
- `.agents/skills/elasticsearch-esql/`: ES|QL skill and live query validation helpers

## Current Known Cluster Context

These are cached facts from live discovery and follow-up validation on 2026-04-25. Use them to start fast, but verify live state before changing tools or agents.

Known live Agent Builder state:

- Built-in read-only agents:
  - `elastic-ai-agent`
  - `observability.agent`
  - `security.agent`
- Editable repo-created agents:
  - `data-catalog-explorer`
  - `schema-explainer`
  - `dataset-sampler`
  - `dmr-analyst` (65-tool full fallback with generated ES|QL workflow)
  - `dmr-core` (19 tools — small-model fleet composition and lookup)
  - `dmr-performance` (15 tools — small-model engine, power, weight, CO2)
  - `dmr-history` (20 tools — small-model decade trends and brand timelines)
  - `dmr-market` (8 tools — small-model inspection, leasing, accidents, rarity discovery)
- Current custom tools include:
  - `dmr-raw-search`
  - `dmr-fleet-status-overview`
  - `dmr-top-brands`
  - `dmr-top-models`
  - `dmr-car-top-brands` (Personbil-scoped variant)
  - `dmr-car-top-models` (Personbil-scoped variant)
  - `dmr-fuel-mix-summary`
  - `dmr-registration-trends`
  - `dmr-fleet-age-summary`
  - `dmr-car-fleet-overview`
  - `dmr-car-fuel-age-summary`
  - `dmr-car-body-style-summary`
  - `dmr-car-practical-features-summary`
  - `dmr-car-usage-summary`
  - `dmr-car-inspection-summary`
  - `dmr-lookup-by-registration-number`
  - `dmr-lookup-by-vin`
  - `dmr-lookup-by-vehicle-id`
  - `dmr-car-age-band-summary`
  - `dmr-car-color-summary`
  - `dmr-car-performance-summary`
  - `dmr-car-high-power-list`
  - `dmr-car-ev-adoption-trend`
  - `dmr-car-fuel-brand-breakdown`
  - `dmr-car-doors-summary`
  - `dmr-car-emission-norm-summary`
  - `dmr-car-brand-performance-summary`
  - `dmr-car-weight-distribution`
  - `dmr-car-inspection-by-age`
  - `dmr-car-awd-summary`
  - `dmr-permit-type-summary`
  - `dmr-car-co2-by-year`
  - `dmr-car-rarity-by-brand`

Known live inventory facts:

- Cluster inventory snapshot found 108 indices
- Agent Builder had 25 available tools at discovery time
- Main visible data families:
  - Docker container logs and metrics
  - system logs and system metrics
  - Elastic Agent and Fleet telemetry
  - synthetics and stack monitoring
  - internal alerts and security control-plane data
  - `dmr-raw-*` and related test indices
  - `content-oracle-*`

Priority dataset:

- `dmr-raw-*` is the main non-platform dataset and should be the first place to deepen with custom tools and domain agents
- `dmr-raw-000002` is the primary production target for the DMR vehicle agent

Reference files:

- `catalog/datasets/dmr-raw.dataset.json`
- `catalog/datasets/observability-platform.dataset.json`
- `catalog/datasets/alerts-and-security.dataset.json`
- `catalog/raw/indices.snapshot.json`

Known repo-backed Kibana dashboards:

- `dmr-fleet-overview` — `DMR Fleet Overview`
  - purpose: current registered Danish passenger-car fleet composition from `dmr-raw-000002`
  - source: `dashboards/dmr-fleet-overview.json`
  - validation: 10 inline ES|QL panels validated live and upserted to Kibana default space on 2026-05-09
- `dmr-performance-history-market` — `DMR Performance, History & Market`
  - purpose: passenger-car performance, registration history, inspections, leasing, and rare brands
  - source: `dashboards/dmr-performance-history-market.json`
  - validation: 11 inline ES|QL panels validated live and upserted to Kibana default space on 2026-05-09
- `elastic-operations-overview` — `Elastic Operations Overview`
  - purpose: local Elastic system, Docker, and log operations over the last 24 hours
  - source: `dashboards/elastic-operations-overview.json`
  - validation: 9 inline ES|QL panels validated live and upserted to Kibana default space on 2026-05-09

## How Codex Should Work In This Repo

Start each relevant session by reading:

1. `AGENT.md`
2. `README.md`
3. the relevant files in `catalog/datasets/`
4. the relevant files in `specs/agents/` and `specs/tools/`

When asked to help with Kibana Agent Builder, use the `kibana-agent-builder` skill.

Default operating rules:

- validate specs before sync:
  - `npm run validate:specs`
- validate environment before live work:
  - `npm run validate:env`
- inspect live state before mutations:
  - list tools
  - list agents
  - export index inventory if dataset discovery is needed
- use dry-run sync before apply:
  - `node scripts/sync-agent-builder.mjs`
  - then `node scripts/sync-agent-builder.mjs --apply`
- prefer built-in tools first for discovery
- keep custom tools narrow and dataset-scoped
- never invent tool IDs; use live tool listings or repo specs
- for ES|QL tools, keep queries compact and always include `LIMIT`
- prefer `KEEP` in ES|QL results to reduce token volume
- when using ES|QL in this repo, prefer the `elasticsearch-esql` skill for schema checks and live query validation
- for exact filters and groupings, prefer `.keyword` fields when the live mapping exposes them
- confirm before delete actions

## Known Agent Builder API Constraints

These are important. Do not relearn them by trial and error.

- Tool create accepts only:
  - `id`
  - `type`
  - `description`
  - `configuration`
  - `tags`
- Agent update accepts only:
  - `description`
  - `configuration`
- In this repo workflow, do not send `tags` on agent update payloads
- In this repo workflow, agent create must not send `tags` in the POST payload
- Index search tools must use `configuration.pattern`
- ES|QL tools must always include `configuration.params`, even when empty
- ES|QL param definitions support only:
  - `type`
  - `description`
- Do not send `name` in tool create payloads
- Do not send immutable fields like `id` or `type` on PUT updates

## Preferred Workflow

Use this sequence unless the user explicitly wants something else:

1. Read `AGENT.md`
2. Run `npm run validate:env`
3. Run `npm run validate:specs`
4. Inspect live tools and agents
5. Inspect mappings and/or small samples for the target dataset
6. If ES|QL is involved, validate schema and query shape with the `elasticsearch-esql` skill
7. Add or update tool specs
8. Add or update agent specs and prompt files
9. Run dry-run sync
10. Apply sync
11. Verify with live list/get/chat commands
12. Update dataset catalog notes and docs if discovery produced durable new facts

## DMR Focus

The first domain dataset to deepen is `dmr-raw-*`.

Current known facts:

- observed indices include `dmr-raw-000001`, `dmr-raw-000002`, `dmr-raw-smoke-000001`, `dmr-raw-test-*`, and `test_dmr`
- the working Kibana data view name used by the user is `dmr_v2_full`
- the largest backing indices observed were:
  - `dmr-raw-000002` at about `17.1gb` and `12.7M` docs
  - `dmr-raw-000001` at about `5.1gb` and `3.9M` docs
- confirmed exact lookup fields include:
  - `RegistreringNummerNummer`
  - `KoeretoejIdent`
  - `KoeretoejOplysningGrundStruktur.KoeretoejOplysningStelNummer`
- confirmed helper fields include:
  - `_drivkraft_primaer`
  - `_co2_g_per_km_primaer`
  - `_km_per_liter_primaer`
  - `_maale_norm_primaer`
  - `_foerste_registrering_aar`
- live mapping also confirms useful `.keyword` exact/grouping fields for:
  - `KoeretoejRegistreringStatus`
  - `KoeretoejArtNavn`
  - `RegistreringNummerNummer`
  - `KoeretoejAnvendelseStruktur.KoeretoejAnvendelseNavn`
  - `KoeretoejOplysningGrundStruktur.KarrosseriTypeStruktur.KarrosseriTypeNavn`
  - `KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.KoeretoejMaerkeTypeNavn`
  - `KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.Model.KoeretoejModelTypeNavn`
  - `SynResultatStruktur.SynResultatSynsResultat`

Current DMR agent/tool coverage:

- exact lookup by: plate, VIN, vehicle ID
- whole-fleet summaries: fleet status, fleet age, fuel mix, registration trends
- passenger-car summaries: fleet overview, fuel/age mix, body-style mix, practical features, usage, inspection results
- v2 additions (2026-04-25):
  - age-band cohort histogram, color, doors, emission norm, AWD, weight distribution
  - performance percentiles (power kW, speed km/h), high-power list, brand performance
  - EV adoption trend, fuel mix by brand, CO2 by year
  - inspection by age, permit types, rare brand finder
  - Personbil-scoped top-brands and top-models
- v3 additions (2026-04-25):
  - decade-profile: 100-year fleet summary (fuel mix%, survival%, avg power/weight/displacement)
  - body-style-by-decade: cabriolet/coupe/sedan/hatchback/MPV evolution
  - power-to-weight summary and list (kW/kg performance proxy)
  - fleet scorecard: headline facts in one call (oldest car 1902, 5 hydrogen cars, etc.)
  - veteran-summary: 12,671 veteran cars by brand (Ford leads, Porsche 904)
  - noise-by-decade: ICE noise dB trend from 1960s to 2020s
  - ncap-adoption-by-year: 0.2% in 1995 to 77% peak by 2013-2019
  - newest-brands: Chinese EV arrivals (DEEPAL 2026, Exlantix/OMODA/JAECOO 2025)
  - oldest-brands: heritage brands with earliest Danish registry appearance
  - leasing-summary: 534,900 cars on active lease (~18% of fleet)
  - accident-summary: 3,839 cars with documented Trafikskade flag
- v4 additions (2026-04-25):
  - cylinder-count summary: 0-cylinder EVs, 3-cylinder downsizing, V8/V12/16-cylinder rarity
  - EV share by body style: sedan at 42.7% electric, body-style fuel mix comparison
  - registration-by-month: strong spring seasonality, March peak
  - CO2 tier summary: current non-EV fleet grouped into emissions bands
  - inspection freshness: latest stored inspection-year distribution on registered cars
  - power segment summary: economy/family/executive/performance/exotic fleet split
  - inspection pass rate by brand: current-record pass/fail proxy with fleet-age caveat
  - cylinder-count by decade: historical downsizing and 0-cylinder EV arrival
  - model-year lag summary: early next-model-year registrations and rare long-lag imports
  - diesel particle-filter adoption: regulatory step-change by registration year
  - towing-capacity by brand: brand-level braked towing leaders
  - forgotten brands: once-common brands now largely gone from Danish roads
  - wheelbase by decade: 2010s vs 2020s size growth
  - deregistration by year: current non-registered status dates grouped annually
- v5 additions (2026-04-26):
  - agent split: dmr-analyst (65 tools) split into 4 focused sub-agents (dmr-core, dmr-performance, dmr-history, dmr-market) of ≤23 tools each to reduce VRAM/context pressure on local LLMs
  - prompt fixes applied to dmr-analyst.instructions.md: global ≤5 sentence brevity rule, explicit "I don't know" permission, tightened get_index_mapping guard (only fires when field is NOT in the inline field guide), scope-continuity rule for follow-up questions, general zero-rows rule, improved fallback failure message (now suggests closest tool), Compact Guardrails section (7 regression prohibitions)
  - dmr-raw-search description updated to LAST RESORT with explicit "Never use for aggregate, statistical, trend, or analytical questions"
      - dmr-car-decade-profile year cap corrected to exclude future registration years with `DATE_EXTRACT("year", NOW())`
  - disambiguation pointers added to 6 tool descriptions (dmr-car-fuel-age-summary, dmr-car-fleet-overview, dmr-fleet-age-summary, dmr-car-inspection-summary, dmr-car-fleet-scorecard, dmr-car-decade-profile)
  - each focused sub-agent prompt includes an out-of-scope redirect naming the other 3 agents
- v6 small-model optimization (2026-04-26):
  - focused agents are now dedicated-tool-only: `dmr-core` 19 tools, `dmr-performance` 15, `dmr-history` 20, `dmr-market` 8
  - removed generated-ES|QL built-ins from focused agents; uncovered in-scope edge cases should redirect to `dmr-analyst`
  - compressed DMR prompts and custom tool descriptions while preserving grounding, zero-row handling, scope defaults, prompt-leak resistance, and generated-ES|QL guardrails on `dmr-analyst`
- v7 small-LLM phase 1 deployment (2026-05-09):
  - deployed the compressed DMR tool descriptions and small-model prompt updates to Kibana Agent Builder
  - live Agent Builder sync plan is clean after apply: all 8 repo agents and 63 repo tool specs report `keep`
  - corrected invalid ES|QL tool param types from Elasticsearch mapping types to Agent Builder param types (`string`, `integer`, `float`)
  - local spec validation now enforces Agent Builder ES|QL param constraints: only `type` and `description`, with supported types `string`, `integer`, `float`, `boolean`, `date`, and `array`
- v8 ES|QL phase 2 deployment (2026-05-09):
  - live cluster check found Elasticsearch `9.4.0` (`build_flavor=default`), so CLAMP, INLINE STATS, and LIMIT BY work was in scope
  - fixed `dmr-car-fleet-overview` count correctness: `registered_car_count` now counts all `Registreret` + `Personbil` records before year/model/weight quality cleanup
  - live validation: `dmr-car-fleet-overview.registered_car_count = 2,935,158`, matching `dmr-car-leasing-summary.total_cars = 2,935,158`; the Phase 1 value `1,991,569` was the quality-filtered subset
  - same count-vs-quality split applied to `dmr-fleet-age-summary`, `dmr-car-fuel-age-summary`, `dmr-car-body-style-summary`, `dmr-car-weight-distribution`, and `dmr-car-age-threshold-summary`
  - CLAMP / cleaned numeric work applied to `dmr-car-performance-summary`, `dmr-car-brand-performance-summary`, `dmr-car-high-power-list`, `dmr-car-power-segment-summary`, `dmr-car-power-to-weight-summary`, `dmr-car-power-to-weight-list`, `dmr-car-decade-profile`, `dmr-car-practical-features-summary`, and `dmr-car-towing-capacity-by-brand`
  - added `dmr-car-above-average-power-brands` using INLINE STATS and `dmr-car-top-models-per-brand` using LIMIT BY; both were added to `dmr-performance` (`DMR Performance Analyst`)
  - updated `dmr-raw-000002` mapping `_meta.description` and verified it live
  - live ES|QL validation passed for every changed/new query using the Elasticsearch ES|QL helper; parameterized tools were validated with representative values
  - `npm run validate:specs` passed with 8 agent specs and 65 tool specs
  - `npm run sync:agent-builder -- --apply` was run after validation; post-apply `npm run sync:plan` reported `keep` for all 8 agents and all 65 tools
  - added `docs/dmr-agent-test-prompts.md` as a user-facing prompt guide keyed to the visible Kibana agent names
- v9 repo-backed Kibana dashboard deployment (2026-05-09):
  - added `dashboards/dmr-fleet-overview.json`, `dashboards/dmr-performance-history-market.json`, and `dashboards/elastic-operations-overview.json`
  - all dashboard panels are inline ES|QL visualizations; no standalone visualization saved objects are required
  - live validation passed for all 30 dashboard ES|QL queries using the Elasticsearch ES|QL helper
  - dashboards were upserted with fixed IDs in the Kibana default space and fetched back successfully: 10, 11, and 9 panels respectively
- v10 beginner setup documentation and local-file ingest support (2026-05-09):
  - README and setup docs now target non-expert users with get-data, ingest, install, dashboard, and smoke-test flows
  - added `.env.example` and `dmr_parser/requirements.txt`
  - `dmr_parser/dmr_import_elastic_2.py` now prefers `DMR_XML_PATH` for local XML ingest and falls back to existing SMB settings when unset
 
Known DMR data-quality hazards:

- implausible future model years exist in raw data and should be bounded in analytics tools
- extreme towing-weight outliers exist in raw data and should be capped or filtered in analytics tools
- body style can be missing on passenger-car records
- Danish usage/inspection labels may need explicit English explanation in final answers
- `KoeretoejMotorStoersteEffekt` (power kW) has corrupt outlier values at exactly 1500 kW and beyond — all power tools cap at 750 kW
- `KoeretoejOplysningMaksimumHastighed` (top speed km/h) has corrupt values above 400 km/h — cap at 400 km/h
- `KoeretoejOplysningAntalDoere` (door count) has corrupt values 0, 1, 8, 44 — filter to 2–6 only
- color value "Ukendt" means unknown, not a real color
- fuel label "El" is the only electric fuel label; no separate plug-in hybrid label exists
- EV electricity-consumption field exists but was not shipped as a tool: live values appear unit-inconsistent/noisy and need deeper interpretation before public use

Recommended next tool types for DMR:

- Danish term/glossary assistance for usage and inspection categories
- more targeted buyer-style summaries if users ask for doors, seats, weight, or towing by brand/model
- permit- and trailer-related summaries if `Tilladelse*` questions become common
- field-semantic explainer prompts for Danish registry terminology

DMR working rules:

- inspect mappings and small samples before adding analytics tools
- avoid broad raw-document dumps from the largest DMR shards
- use `dmr-raw-search` only as a LAST RESORT for individual record lookup — never for aggregate, statistical, trend, or analytical questions
- in `dmr-analyst`, use `platform.core.get_index_mapping` only when a needed fallback field is absent from the prompt field guide
- use the `elasticsearch-esql` skill for schema and live ES|QL verification when editing repo-backed ES|QL tools
- use `platform.core.generate_esql` then `platform.core.execute_esql` only in `dmr-analyst` fallback when no dedicated DMR tool covers the question
- for questions about "cars", default to `KoeretoejArtNavn.keyword == "Personbil"` unless the user explicitly broadens scope
- for questions about the "current" fleet, default to `KoeretoejRegistreringStatus.keyword == "Registreret"`

## Session Defaults

Assume these defaults unless the user overrides them:

- single environment
- default Kibana space
- this repo is the source of truth for stable assets
- live-cluster facts in this file are cached context, not guaranteed current truth
- verify live state before mutations
- prefer narrow, reviewable specs over ad hoc UI-only changes
- prefer repo-backed prompts and specs over freeform one-off agent edits

## Key Commands

Common repo commands:

```bash
npm run validate:env
npm run validate:specs
npm run export:agent-builder
npm run export:indices
npm run sync:plan
npm run sync:agent-builder -- --apply
```

Useful live inspection commands:

```bash
KIBANA_URL='http://192.168.0.238:5601' \
KIBANA_API_KEY='V2gzRXhKMEIwTG9yQi1Zekoya186Umh5WWtINl9sMEoySU9WMm9maWJVUQ==' \
node .agents/skills/kibana-agent-builder/scripts/agent-builder.js list-tools

KIBANA_URL='http://192.168.0.238:5601' \
KIBANA_API_KEY='V2gzRXhKMEIwTG9yQi1Zekoya186Umh5WWtINl9sMEoySU9WMm9maWJVUQ==' \
node .agents/skills/kibana-agent-builder/scripts/agent-builder.js list-agents
```

Useful ES|QL validation commands:

```bash
ELASTICSEARCH_URL='http://192.168.0.238:9200' \
ELASTICSEARCH_API_KEY='V2gzRXhKMEIwTG9yQi1Zekoya186Umh5WWtINl9sMEoySU9WMm9maWJVUQ==' \
node .agents/skills/elasticsearch-esql/scripts/esql.js test

ELASTICSEARCH_URL='http://192.168.0.238:9200' \
ELASTICSEARCH_API_KEY='V2gzRXhKMEIwTG9yQi1Zekoya186Umh5WWtINl9sMEoySU9WMm9maWJVUQ==' \
node .agents/skills/elasticsearch-esql/scripts/esql.js schema dmr-raw-000002

ELASTICSEARCH_URL='http://192.168.0.238:9200' \
ELASTICSEARCH_API_KEY='V2gzRXhKMEIwTG9yQi1Zekoya186Umh5WWtINl9sMEoySU9WMm9maWJVUQ==' \
node .agents/skills/elasticsearch-esql/scripts/esql.js raw "FROM dmr-raw-000002 | STATS c = COUNT(*) BY s = KoeretoejRegistreringStatus.keyword | SORT c DESC | LIMIT 5" --tsv
```

If a new session starts cold, this file should provide enough context to begin useful Elastic/Kibana agent work without spending tokens rediscovering the repo purpose, endpoints, live dataset shape, or the known Agent Builder constraints.
