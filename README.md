# DMR Vehicle Registry Agent Builder Showcase

A complete Elastic Agent Builder project for exploring Danish Motor Register (DMR) data with natural-language agents, ES|QL tools, Kibana dashboards, and a repeatable Elasticsearch ingest pipeline.

This repo is designed to be both a polished demo and a practical reference implementation. You can inspect how the agents are built, sync the assets into your own Kibana space, ingest the public DMR statistics export, and replicate the full experience on your own Elastic stack.

> [!IMPORTANT]
> The full DMR XML export is not included. Download it from Motorstyrelsen and keep it outside the repo. The XML files in `dmr_parser/` are small parser samples only.

> [!NOTE]
> All screenshots and LLM responses shown in this repo were produced with a 100% local setup using the 9B `Qwen3.5-9b` model.

## What You Can Ask

The agent family can answer questions about Danish passenger cars, market composition, vehicle lookup, inspection outcomes, leasing, EV adoption, performance, towing, registration history, and long-tail brands.

| Example question | Best agent |
| --- | --- |
| How many registered passenger cars are there? | `dmr-core` |
| What are the top passenger-car models in Denmark right now? | `dmr-core` |
| Find vehicle EN44360 and summarize it in English. | `dmr-core` |
| Which brands have above-fleet-average power? | `dmr-performance` |
| Which brands have the best inspection pass rates? | `dmr-market` |
| Do Danish registrations have a seasonal pattern by month? | `dmr-history` |
| What is the oldest car brand in Denmark? | `dmr-history` |
| Ask an open-ended question against the flat ES|QL view. | `dmr-explorer` |

More prompts are available in [docs/dmr-agent-test-prompts.md](docs/dmr-agent-test-prompts.md).

## Screenshots

These examples were captured from the DMR agents answering real registry questions with a local `Qwen3.5-9b` LLM.

<table>
  <tr>
    <td width="50%"><img src="screenshots/Find%20vehicle.png" alt="Vehicle lookup result" /><br /><strong>Vehicle lookup</strong></td>
    <td width="50%"><img src="screenshots/What%20are%20the%20top%20passenger-car%20models%20in%20Denmark%20right%20now.png" alt="Top passenger car models result" /><br /><strong>Top passenger-car models</strong></td>
  </tr>
  <tr>
    <td width="50%"><img src="screenshots/Which%20brands%20have%20above-fleet-average%20power.png" alt="Above fleet average power brands result" /><br /><strong>Above-average power brands</strong></td>
    <td width="50%"><img src="screenshots/Which%20brands%20have%20the%20best%20inspection%20pass%20rates.png" alt="Inspection pass rates result" /><br /><strong>Inspection pass rates</strong></td>
  </tr>
  <tr>
    <td width="50%"><img src="screenshots/Do%20Danish%20registrations%20have%20a%20seasonal%20pattern%20by%20month.png" alt="Registration seasonality result" /><br /><strong>Registration seasonality</strong></td>
    <td width="50%"><img src="screenshots/How%20many%20veteran%20passenger%20cars%20are%20registered,%20and%20which%20brands%20are%20most%20common.png" alt="Veteran passenger cars result" /><br /><strong>Veteran passenger cars</strong></td>
  </tr>
  <tr>
    <td width="50%"><img src="screenshots/How%20many%20registered%20passenger%20cars%20are%20leased.png" alt="Registered passenger car leasing result" /><br /><strong>Leased passenger cars</strong></td>
    <td width="50%"><img src="screenshots/Show%20EV%20adoption%20over%20time.png" alt="EV adoption over time result" /><br /><strong>EV adoption over time</strong></td>
  </tr>
  <tr>
    <td width="50%"><img src="screenshots/What%20is%20the%20oldest%20car%20brand%20in%20Denmark.png" alt="Oldest car brand result" /><br /><strong>Oldest car brand</strong></td>
    <td width="50%"><img src="screenshots/Which%20car%20brands%20are%20newest%20in%20the%20Danish%20registry.png" alt="Newest car brands result" /><br /><strong>Newest registry brands</strong></td>
  </tr>
  <tr>
    <td width="50%"><img src="screenshots/how%20many%20LADA%20cars.png" alt="LADA registered cars result" /><br /><strong>LADA lookup</strong></td>
    <td width="50%"><img src="screenshots/powerful%20car%20brands.png" alt="Powerful car brands result" /><br /><strong>Powerful car brands</strong></td>
  </tr>
  <tr>
    <td width="50%"><img src="screenshots/rarest%20cars.png" alt="Rarest registered car brands result" /><br /><strong>Rarest brands</strong></td>
    <td width="50%"><img src="screenshots/top%203%20registered%20passenger-car%20models.png" alt="Top 3 registered passenger car models per brand result" /><br /><strong>Top 3 models per brand</strong></td>
  </tr>
</table>

## What Is Included

| Area | Contents |
| --- | --- |
| Agent specs | 10 Kibana Agent Builder agent definitions in `specs/agents/` |
| Tool specs | 90 parameterized ES|QL tools in `specs/tools/` |
| Skill specs | 6 Agent Builder skills in `specs/skills/` |
| Prompts | Focused agent instruction files in `prompts/` |
| Dashboards | 3 Kibana dashboard JSON definitions in `dashboards/` |
| Grafana | Docker Compose service with provisioned Elasticsearch datasource and 35 DMR dashboards (5 folders) in `grafana/` |
| Importer | DMR XML to Elasticsearch importer in `dmr_parser/`; use `dmr_import_elastic_v6.py` for new imports |
| Catalog | Dataset notes and field dictionary in `catalog/` |
| Scripts | Validation, sync, export, ES|QL, and dashboard helpers in `scripts/` |

## Architecture

```text
Motorstyrelsen DMR XML export
        |
        v
dmr_parser/dmr_import_elastic_v6.py
        |
        v
Elasticsearch index: dmr-raw-000002
        |
        +--> Kibana Agent Builder ES|QL tools
        +--> Kibana Agent Builder skills
        +--> Kibana dashboards
        |
        v
Focused DMR agents, explorer agents, and dashboard views
```

The focused agents use dedicated ES|QL tools for common questions. The explorer agents use flat ES|QL views with readable column names for open-ended analysis.

## Quick Start

Use this path if you already have DMR records indexed in Elasticsearch:

```bash
git clone <repo-url>
cd elastic-agent-build-repo
npm install
cp .env.example .env
```

Edit `.env` with your Kibana and Elasticsearch URLs and credentials, then validate the repo:

```bash
npm run validate:env
npm run validate:specs
```

Preview and apply the Agent Builder sync:

```bash
npm run sync:plan
npm run sync:agent-builder -- --apply
```

Create the optional ES|QL views used by `dmr-explorer`:

```bash
npm run create:views:dry-run
```

Paste the generated `PUT /_query/view/...` commands into Kibana Dev Tools, or run `npm run create:views` if your Elasticsearch API key has the required privileges.

Start the optional local Grafana dashboard service:

```bash
docker compose up -d grafana
```

Grafana uses `ELASTICSEARCH_URL`, `ELASTICSEARCH_API_KEY`, and `ES_INDEX` from `.env` to provision the DMR Elasticsearch datasource and **35 DMR dashboards** organized into five folders — `01 Fleet & Overview`, `02 Performance & Engineering`, `03 Body, Design & Sound`, `04 Compliance, Safety & Emissions`, `05 Market & Lifecycle`. Open it at `http://localhost:3009` with the Grafana admin credentials from `.env`. Folder layout, full dashboard list, and rebuild instructions live in [docs/grafana.md](docs/grafana.md).

Detailed fast path: [docs/dmr-agent-quickstart.md](docs/dmr-agent-quickstart.md)

## Replicate From Scratch

Use this path when you need to download and ingest the DMR statistics export first:

1. Set up Elasticsearch and Kibana with Agent Builder enabled.
2. Download the DMR statistics export from Motorstyrelsen.
3. Ingest the XML into `dmr-raw-000002`.
4. Sync the Agent Builder tools, skills, and agents.
5. Install dashboards and run smoke tests.

Full guide: [docs/setup-dmr-agent.md](docs/setup-dmr-agent.md)  
Data-only ingest guide: [docs/get-and-ingest-dmr-data.md](docs/get-and-ingest-dmr-data.md)

## Agent Family

| Agent | Purpose | Model target |
| --- | --- | --- |
| `dmr-core` | Fleet counts, brands, models, lookup, fuel mix | local `Qwen3.5-9b` |
| `dmr-performance` | Power, weight, towing, CO2, performance bands | local `Qwen3.5-9b` |
| `dmr-history` | Decades, registrations, EV adoption, veteran cars | local `Qwen3.5-9b` |
| `dmr-market` | Leasing, inspection, rarity, compliance signals | local `Qwen3.5-9b` |
| `dmr-micro` | Minimal 8-tool agent for constrained routing tests | local `Qwen3.5-9b` |
| `dmr-explorer` | Free-form ES|QL against flat views | local `Qwen3.5-9b` |
| `dmr-analyst` | Broad fallback agent with all DMR tools | local `Qwen3.5-9b` |
| Discovery agents | Dataset sampling and schema explanation | local `Qwen3.5-9b` |

## Requirements

- Elasticsearch and Kibana with Agent Builder enabled.
- Node.js 18 or newer.
- Python 3.10 or newer for DMR XML ingest.
- Kibana API key or basic auth.
- Elasticsearch API key or basic auth.
- Local OpenAI-compatible LLM connector configured in Kibana for `Qwen3.5-9b`.

The repo was built around Elastic 9.x behavior. Some Agent Builder and ES|QL View APIs may differ on earlier versions.

## Common Commands

```bash
# Validate local JSON specs and referenced prompt files.
npm run validate:specs

# Validate required environment variables.
npm run validate:env

# Preview changes against Kibana Agent Builder.
npm run sync:plan

# Sync skills, tools, then agents.
npm run sync:agent-builder -- --apply

# List deployed Agent Builder agents.
npm run agent-builder -- list-agents

# Run an ES|QL query through Elasticsearch.
npm run esql -- raw 'FROM dmr-raw-000002 | STATS count = COUNT(*) | LIMIT 1' --tsv

# Install a dashboard.
npm run dashboards -- upsert dmr-fleet-overview dashboards/dmr-fleet-overview.json
```

## Repo Map

```text
specs/       Source-of-truth Agent Builder agents, tools, and skills.
prompts/     Agent instructions referenced by the specs.
scripts/     Validation, sync, ES|QL, export, and dashboard helpers.
dashboards/  Kibana dashboard definitions and deployment notes.
grafana/     Grafana datasource and dashboard provisioning for local DMR views.
docs/        Quickstart, full setup, ingest, and testing guides.
catalog/     Dataset descriptions and DMR field dictionary.
dmr_parser/  DMR XML importer and parser samples.
screenshots/ Showcase screenshots used by this README.
```

## Data Notes

The DMR registry includes technical and registration information for Danish vehicles. The agent tools default to currently registered passenger cars where that is the natural interpretation of a question.

The `dmr-cars-flat` ES|QL view exposes readable columns such as `brand`, `model`, `fuel`, `year`, `power_kw`, `kerb_kg`, `is_leased`, and `inspection_result`, so explorer agents do not need to reason over deeply nested Danish field names.

## Public Safety

Real `.env` files, raw exports, eval reports, local assistant configuration, and archived private notes are intentionally ignored. Before publishing a fork, run a secret scan and rotate any key that has ever appeared in local history.
