# Grafana Dashboards

This repo includes a local Grafana Docker Compose service that connects to the Elasticsearch URL and API key from `.env`.

Grafana provisions:

- an Elasticsearch datasource named by `GRAFANA_DATASOURCE_NAME`
- **35 DMR dashboards** organized into 5 folders that mirror the on-disk directory layout under `grafana/dashboards/`

## Folder Layout

| Folder | Count | Theme |
| --- | --- | --- |
| `01 Fleet & Overview` | 5 | Landing page, electrification, market/leasing, history, environmental profile |
| `02 Performance & Engineering` | 8 | Power, weight, engines, towing, paper speed, 250 km/h club, turbocharging |
| `03 Body, Design & Sound` | 8 | Body styles, colour, wheelbase, track width, door/seat oddities, acoustic profile |
| `04 Compliance, Safety & Emissions` | 5 | Inspection, NOx/CO, accidents, red-car myth, driving habits |
| `05 Market & Lifecycle` | 9 | Brand invasion/concentration, chiptuning, vintage leasing, diesel exit, ghost & dormant fleet |

### `01 Fleet & Overview`

- `DMR Overview` — landing page with cross-suite links
- `DMR Electrification & Fuel Transition`
- `DMR Market, Leasing & Brands`
- `DMR History & Heritage`
- `DMR Environmental Profile`

### `02 Performance & Engineering`

- `DMR Performance & Practicality`
- `DMR Fleet Weight & Power-to-Weight`
- `DMR Engine Extinction Event`
- `DMR Shrinking Engine`
- `DMR Turbocharging Era (Specific Output)`
- `DMR Paper Speed Records`
- `DMR 250 km/h Club`
- `DMR Tow-It-All Index`

### `03 Body, Design & Sound`

- `DMR Body, Colour & Consumer Preferences`
- `DMR Wheelbase Chronicles`
- `DMR Track Width Creep`
- `DMR Door-Seat Weirdness Matrix`
- `DMR 7-Seat Explosion`
- `DMR Fake Two-Seater (Yellow-Plate Fleet)`
- `DMR Acoustic Fleet Profile`
- `DMR Sound of Silence (Stationary Noise)`

### `04 Compliance, Safety & Emissions`

- `DMR Inspection & Compliance`
- `DMR NOx & CO Honesty Check`
- `DMR Accident & Damage Files`
- `DMR Red Car Myth (Colour × Accidents)`
- `DMR Danish Driving Habits (Odometers at Inspection)`

### `05 Market & Lifecycle`

- `DMR Brand Invasion (Newcomers & Departures)`
- `DMR Brand Concentration (Lineup Width)`
- `DMR Chiptuning Hall of Fame`
- `DMR Vintage Leasing`
- `DMR Diesel's Last Stand`
- `DMR Alphabet of Brands`
- `DMR Model Year Time Machine`
- `DMR Ghost Fleet (Lifespan & Mortality)`
- `DMR Dormant Fleet (Untouched Cars)`

## Required Environment

Copy `.env.example` to `.env` and set these values:

```bash
ELASTICSEARCH_URL=https://your-elasticsearch.example.com
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key
ES_INDEX=dmr-raw-000002
```

Optional Grafana settings:

```bash
GRAFANA_PORT=3009
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
GRAFANA_DATASOURCE_NAME=DMR Elasticsearch
```

Use `ELASTICSEARCH_INSECURE=true` only for local or self-signed Elasticsearch TLS.

## Start Grafana

```bash
docker compose up -d grafana
```

Open Grafana at:

```text
http://localhost:3009
```

Log in with `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`. The five DMR folders appear in the dashboards sidebar.

## Provisioned Files

Grafana reads these files at startup:

- `grafana/provisioning/datasources/elasticsearch.yml`
- `grafana/provisioning/dashboards/dmr.yml`
- All `*.json` files under `grafana/dashboards/<folder>/` — one file per dashboard

The provisioning config uses `foldersFromFilesStructure: true`, so the directory layout under `grafana/dashboards/` becomes the Grafana folder structure. Do not set a `folder:` value at the provider level — the two options are mutually exclusive.

After editing provisioning or dashboard files, either wait up to `updateIntervalSeconds: 10` for Grafana's file watcher to pick the change up, or trigger a reload:

```bash
curl -s -X POST -u "$GRAFANA_ADMIN_USER:$GRAFANA_ADMIN_PASSWORD" \
  http://localhost:3009/api/admin/provisioning/dashboards/reload
```

A full container restart is rarely needed:

```bash
docker compose restart grafana
```

## Rebuilding the Dashboard Suite

The 34 generated dashboards (everything except `dmr-overview.json`, which is hand-curated) come from a single Python builder:

```bash
python3 scripts/build_grafana_dmr_dashboards.py
```

The builder reads the `CATEGORIES` map at the bottom of `scripts/build_grafana_dmr_dashboards.py`, wipes the dashboard tree under `grafana/dashboards/`, and writes each dashboard into its category subdirectory. `dmr-overview.json` is preserved and only its cross-suite links are updated. After running, refresh Grafana with the reload curl above.

## Re-organizing Categories or Renaming Folders

Provisioned dashboards cannot be deleted through the API ("provisioned dashboard cannot be deleted"). If you move dashboards into new folders or rename categories, follow this sequence so Grafana relocates them cleanly:

```bash
python3 scripts/build_grafana_dmr_dashboards.py            # writes the new layout to disk
mv grafana/dashboards grafana/dashboards.tmp               # hide the tree
mkdir grafana/dashboards                                   # empty mount point
curl -s -X POST -u "$GRAFANA_ADMIN_USER:$GRAFANA_ADMIN_PASSWORD" \
  http://localhost:3009/api/admin/provisioning/dashboards/reload   # Grafana removes them from its DB
mv grafana/dashboards.tmp/* grafana/dashboards/             # restore the new layout
rmdir grafana/dashboards.tmp
curl -s -X POST -u "$GRAFANA_ADMIN_USER:$GRAFANA_ADMIN_PASSWORD" \
  http://localhost:3009/api/admin/provisioning/dashboards/reload   # re-import into the new folders
```

## Verify

Check Compose configuration:

```bash
docker compose config
```

Check Grafana health:

```bash
curl http://localhost:3009/api/health
```

Validate the generated dashboard JSON and every ES|QL panel query through Grafana:

```bash
python3 scripts/build_grafana_dmr_dashboards.py
node scripts/validate_grafana_dmr_panels.mjs
```

List the live dashboard tree from the Grafana API:

```bash
curl -s -u "$GRAFANA_ADMIN_USER:$GRAFANA_ADMIN_PASSWORD" \
  "http://localhost:3009/api/search?type=dash-db&tag=dmr&limit=100" \
  | python3 -c "import sys,json;from collections import defaultdict;d=defaultdict(list);[d[x.get('folderTitle') or '(root)'].append(x['title']) for x in json.load(sys.stdin)];[print(f, len(d[f])) for f in sorted(d)]"
```

## Scope and Time Range

The dashboards query registered passenger cars from `ES_INDEX` using the same DMR scope as the Kibana dashboards:

```text
KoeretoejRegistreringStatus.keyword == "Registreret"
KoeretoejArtNavn.keyword == "Personbil"
```

A handful of dashboards (`DMR History & Heritage`, `DMR Ghost Fleet`, `DMR Brand Invasion`) intentionally drop the registration-status filter so they can see deregistered (`Afmeldt`) records too. Each dashboard sets its own time range; the default is `1900-01-01` → `now` so historical panels show the whole DMR history unless you narrow the Grafana time picker.

The Elasticsearch datasource uses `KoeretoejOplysningGrundStruktur.KoeretoejOplysningFoersteRegistreringDato` as its Grafana time field.
