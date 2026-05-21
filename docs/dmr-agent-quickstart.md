# DMR Agent Family Quickstart

Use this guide when the DMR data is already indexed in Elasticsearch and you only need to install the Kibana Agent Builder assets from this repo.

For the full data download and ingest path, use [setup-dmr-agent.md](setup-dmr-agent.md).

> [!TIP]
> Start here if you want the fastest path from an existing `dmr-raw-000002` index to working agents. For a visual overview and screenshots, see the root [README](../README.md).

## What This Installs

- 10 Agent Builder agents from `specs/agents/`
- 90 DMR ES|QL tools from `specs/tools/`
- 6 Kibana skills from `specs/skills/`
- Optional ES|QL views used by `dmr-explorer`
- Optional Kibana dashboards from `dashboards/`

The guide does not ingest DMR XML data. Use [get-and-ingest-dmr-data.md](get-and-ingest-dmr-data.md) if you still need the data.

After this guide, you can optionally install dashboards from [dashboards/README.md](../dashboards/README.md) and use manual smoke prompts from [dmr-agent-test-prompts.md](dmr-agent-test-prompts.md).

## Prerequisites

You need:

- Kibana with Agent Builder enabled.
- Elasticsearch with DMR records in `dmr-raw-000002`.
- Node.js 18 or newer.
- Kibana credentials with permission to create/update Agent Builder assets.
- Elasticsearch credentials for validation and optional ES|QL view creation.
- A local OpenAI-compatible LLM connector in Kibana serving `Qwen3.5-9b`.

If your DMR index has another name, update the tool specs before syncing.

## Install Dependencies

```bash
git clone <repo-url>
cd elastic-agent-build-repo
npm install
cp .env.example .env
```

Edit `.env`:

```bash
KIBANA_URL=https://your-kibana.example.com
KIBANA_API_KEY=your-kibana-api-key
KIBANA_SPACE_ID=default

ELASTICSEARCH_URL=https://your-elasticsearch.example.com
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key
```

For a local Elastic stack, `KIBANA_URL` is usually `http://localhost:5601` and `ELASTICSEARCH_URL` is usually `http://localhost:9200`. Do not point `KIBANA_URL` at Elasticsearch; Agent Builder APIs live in Kibana.

Load it in bash or zsh:

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

## Validate

```bash
npm run validate:env
npm run validate:specs
```

Check that the DMR index responds:

```bash
npm run esql -- raw 'FROM dmr-raw-000002 | STATS count = COUNT(*) BY status = KoeretoejRegistreringStatus.keyword | SORT count DESC | LIMIT 5' --tsv
```

## Sync Agent Builder Assets

Preview the sync:

```bash
npm run sync:plan
```

Apply the sync:

```bash
npm run sync:agent-builder -- --apply
```

The sync writes skills first, then tools, then agents.

The source specs stay in this repo under `specs/`, so changes can be reviewed before they are applied to Kibana.

## Create ES|QL Views

The `dmr-explorer` agent uses ES|QL views with readable column names. Preview the exact commands:

```bash
npm run create:views:dry-run
```

Paste each generated `PUT /_query/view/...` block into Kibana Dev Tools, or run:

```bash
npm run create:views
```

Verify the flat view:

```bash
npm run esql -- raw 'FROM dmr-cars-flat | WHERE fuel == "El" | STATS count = COUNT(*) BY brand | SORT count DESC | LIMIT 5' --tsv
```

## Verify Agents

List installed agents:

```bash
npm run agent-builder -- list-agents
```

Inspect the fallback agent:

```bash
npm run agent-builder -- get-agent --id dmr-analyst
```

Run one smoke test in Kibana Agent Builder, or use the API helper:

```bash
npm run agent-builder -- chat --id dmr-analyst --message 'How many registered passenger cars are there?'
```

Expected behavior:

- the agent uses a dedicated DMR tool for common questions
- passenger-car answers are scoped to `Personbil`
- current-fleet answers are scoped to `Registreret`
- on the reference dataset, the passenger-car count is about 2.9 million

## Post-Deployment Smoke Tests

After **every** change to `specs/tools/`, `specs/skills/`, `specs/agents/`, or `scripts/create-esql-views.mjs`, run these in order. Each step has a regression-detection number — if you see a different number, the change has not propagated.

**1. Re-create the flat views** (only if `scripts/create-esql-views.mjs` changed):
```bash
npm run create:views
```
Expect: `created/updated view dmr-cars`, `dmr-vehicles`, `dmr-cars-flat`, `dmr-vehicles-flat`, `dmr-cars-all-flat`.

**2. Re-sync agents/tools/skills:**
```bash
npm run sync:agent-builder -- --apply
```
Expect: all new tools listed in the diff, no errors.

**3. Lifecycle smoke test (catches the Registreret-filter bug):**
```bash
npm run esql -- raw 'FROM dmr-cars-all-flat | WHERE blocking_reason == "Totalskadet køretøj" | STATS c = COUNT(*) | LIMIT 1' --tsv
```
Expect: **c = 561,770** (give or take, depending on dataset vintage). If you see **0**, **2**, or **3**, the `dmr-cars-all-flat` view was not deployed — re-run step 1.

**4. New flat-view columns smoke test:**
```bash
npm run esql -- raw 'FROM dmr-cars-flat | WHERE vehicle_condition IS NOT NULL | STATS c = COUNT(*) BY vehicle_condition | SORT c DESC | LIMIT 5' --tsv
```
Expect: rows for `Middel`, `UnderMiddel`, `OverMiddel`. If you get `Unknown column [vehicle_condition]`, re-run step 1.

**5. Skill propagation smoke test:**
```bash
npm run agent-builder -- chat --id dmr-explorer --message 'What does KoeretoejOplysningIbrugtagningDato mean and should I use it for year-of-service queries?'
```
Expect: the answer surfaces the ≈ 0 % coverage warning. If the agent says "not documented", the `dmr-domain` skill was not re-uploaded — re-run step 2.

**6. Danish-vocabulary smoke test:**
```bash
npm run agent-builder -- chat --id dmr-explorer --message 'Have totalskadede cars increased over time?'
```
Expect: the answer interprets `totalskadede` as write-offs (not "total") and groups by year. The 2010 bucket should be roughly 17,000 and 2025 should be in single digits.

**7. New-tool routing smoke test (Market & Compliance):**
```bash
npm run agent-builder -- chat --id dmr-market --message 'Which brands have the most totalskadede passenger cars?'
```
Expect: `dmr-car-block-reason-by-brand` is called and the top brand is **FORD** with ~2,800+ cars (Mangel) or several thousand Totalskadet — never a single-digit count.

## Optional: Install Dashboards

```bash
npm run dashboards -- upsert dmr-fleet-overview dashboards/dmr-fleet-overview.json
npm run dashboards -- upsert dmr-performance-history-market dashboards/dmr-performance-history-market.json
npm run dashboards -- upsert elastic-operations-overview dashboards/elastic-operations-overview.json
```

More manual test prompts are in [dmr-agent-test-prompts.md](dmr-agent-test-prompts.md).
