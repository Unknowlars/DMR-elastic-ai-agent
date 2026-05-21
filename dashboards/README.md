# Kibana Dashboards

This directory contains repo-backed Kibana dashboard definitions for the DMR project.

The dashboards use inline ES|QL panels, so you do not need separate visualization saved objects.

For the full project overview, screenshots, and agent setup flow, start with the root [README](../README.md).

## Included Dashboards

| ID | Title | Purpose |
| --- | --- | --- |
| `dmr-fleet-overview` | `DMR Fleet Overview` | Current registered Danish passenger-car fleet composition. |
| `dmr-performance-history-market` | `DMR Performance, History & Market` | Passenger-car performance, history, inspection, leasing, and rare-brand views. |
| `elastic-operations-overview` | `Elastic Operations Overview` | Elastic system, Docker, and log operations over the last 24 hours. |

## Requirements

Load your `.env` first in bash or zsh:

```bash
set -a
source .env
set +a
```

In fish, use:

```fish
for line in (grep -v '^\s*#' .env | grep -v '^\s*$')
    set -gx (string split -m 1 = $line)
end
```

Required:

- `KIBANA_URL`
- `KIBANA_API_KEY` or `KIBANA_USERNAME` plus `KIBANA_PASSWORD`

The DMR dashboards expect `dmr-raw-000002` to exist. The operations dashboard expects Elastic Agent, system, Docker, and log data streams. If you do not have those, install only the two DMR dashboards or adapt `elastic-operations-overview.json`.

## Deploy

```bash
npm run dashboards -- test

npm run dashboards -- upsert dmr-fleet-overview dashboards/dmr-fleet-overview.json
npm run dashboards -- upsert dmr-performance-history-market dashboards/dmr-performance-history-market.json
npm run dashboards -- upsert elastic-operations-overview dashboards/elastic-operations-overview.json
```

## Verify

```bash
npm run dashboards -- get dmr-fleet-overview
npm run dashboards -- get dmr-performance-history-market
npm run dashboards -- get elastic-operations-overview
```

Expected panel counts:

| ID | Panels |
| --- | ---: |
| `dmr-fleet-overview` | 10 |
| `dmr-performance-history-market` | 11 |
| `elastic-operations-overview` | 9 |

## Query Checks

Run representative ES|QL checks before opening the dashboards:

```bash
npm run esql -- raw 'FROM dmr-raw-000002 | WHERE KoeretoejRegistreringStatus.keyword == "Registreret" AND KoeretoejArtNavn.keyword == "Personbil" AND _drivkraft_primaer IS NOT NULL | STATS car_count = COUNT(*) BY primary_fuel = _drivkraft_primaer | SORT car_count DESC | LIMIT 10' --tsv
```
