# Full Setup Guide: DMR Agents On Your Elastic Stack

This guide takes you from an empty Elastic stack to a working DMR vehicle assistant in Kibana Agent Builder.

> [!TIP]
> Use this guide for a full replication from raw DMR XML. If your DMR index already exists, use the shorter [DMR Agent Family Quickstart](dmr-agent-quickstart.md).

## 1. What You Are Building

```text
Motorstyrelsen DMR XML export
        |
        v
dmr_parser/dmr_import_elastic_v6.py
        |
        v
Elasticsearch index: dmr-raw-000002
        |
        v
Kibana Agent Builder tools, skills, agents, and dashboards
```

The focused agents use predefined ES|QL tools for common questions. This keeps normal answers consistent, reviewable, and easier to run on smaller local models.

The root [README](../README.md) shows screenshots and a higher-level tour of the final result.

## 2. Prerequisites

You need:

- Elasticsearch and Kibana.
- Kibana Agent Builder enabled.
- Permission to create/update Agent Builder tools, skills, and agents.
- Permission to create/update dashboards if you want the dashboard step.
- Node.js 18 or newer.
- Python 3.10 or newer.
- Enough disk space for the unpacked DMR XML export.

Credentials used by this repo:

- `KIBANA_API_KEY` or `KIBANA_USERNAME` plus `KIBANA_PASSWORD`
- `ELASTICSEARCH_API_KEY` or `ELASTICSEARCH_USERNAME` plus `ELASTICSEARCH_PASSWORD`
- `ES_API_KEY` for the Python importer

Kibana setup used by the agents:

- an LLM connector available in Kibana
- Agent Builder enabled
- a Kibana API key with permission to create Agent Builder tools, skills, agents, dashboards, and ES|QL views

## 3. Clone And Install

```bash
git clone <repo-url>
cd elastic-agent-build-repo
npm install

python3 -m venv .venv
source .venv/bin/activate
pip install -r dmr_parser/requirements.txt
```

In fish, activate the virtualenv with:

```fish
source .venv/bin/activate.fish
python -m pip install -r dmr_parser/requirements.txt
```

Create a private env file:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
KIBANA_URL=https://your-kibana.example.com
KIBANA_API_KEY=your-kibana-api-key
KIBANA_SPACE_ID=default

ELASTICSEARCH_URL=https://your-elasticsearch.example.com
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key

ES_URL=https://your-elasticsearch.example.com
ES_API_KEY=your-elasticsearch-api-key
ES_INDEX=dmr-raw-000002
```

For local installs, Kibana and Elasticsearch normally use different ports: `KIBANA_URL=http://localhost:5601`, while `ELASTICSEARCH_URL` and `ES_URL` point at `http://localhost:9200`. The Agent Builder sync commands must talk to Kibana, not Elasticsearch.

Load the values in bash or zsh:

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

Validate:

```bash
npm run validate:env
npm run validate:specs
```

## 4. Prepare Kibana

Open Kibana:

```text
http://localhost:5601/app/home
```

For a remote/local network install, replace `localhost` with your Kibana host, for example `http://<your-kibana-host>:5601/app/home`.

Create or verify the LLM connector:

1. Go to **Stack Management > Connectors**.
2. Create an OpenAI-compatible connector for your local `Qwen3.5-9b` model server.
3. For LM Studio or another local OpenAI-compatible runtime, use its chat completions endpoint, for example `http://<local-llm-host>:1234/v1/chat/completions`.
4. Add the connector API key expected by your local model server, if your runtime requires one.
5. Run the connector test and confirm Kibana receives a successful response.

Create the Kibana API key:

1. Go to **Stack Management > Security > API keys**.
2. Create an API key for this repo.
3. Put the value in `.env` as `KIBANA_API_KEY`.

Use an Elasticsearch API key for `ELASTICSEARCH_API_KEY` and `ES_API_KEY`. `KIBANA_URL` must point to Kibana on port `5601`; `ELASTICSEARCH_URL` and `ES_URL` point to Elasticsearch on port `9200`.

Run:

```bash
npm run validate:env
```

This catches the common mistake of pointing `KIBANA_URL` at Elasticsearch.

## 5. Get The DMR Statistics Export

Motorstyrelsen publishes a statistics extract of public technical data from Motorregistret.

Open the official page and find the `Statistikudtraek` section:

https://motorst.dk/erhverv/motorregistret-for-virksomheder/faa-adgang-til-motorregistret/andre-adgange

Download and unpack the archive. The XML file is usually named like:

```text
ESStatistikListeModtag-YYYYMMDD-HHMMSS.xml
```

The download link points to an FTP server. You can download with a browser, or use a resumable CLI download. Example with `aria2c`:

```bash
aria2c \
  --ftp-user="<dmr-ftp-user>" \
  --ftp-passwd="<dmr-ftp-password>" \
  --ftp-pasv=true \
  --continue=true \
  --max-connection-per-server=16 \
  --split=16 \
  --min-split-size=64M \
  --disk-cache=512M \
  --file-allocation=falloc \
  --summary-interval=10 \
  --out="ESStatistikListeModtag-YYYYMMDD-HHMMSS.zip" \
  "ftp://<motorstyrelsen-ftp-host>/ESStatistikListeModtag/ESStatistikListeModtag-YYYYMMDD-HHMMSS.zip"
```

Replace the timestamp with the current filename shown by Motorstyrelsen.

Put the zip and XML outside this repo, for example:

```text
/data/dmr/ESStatistikListeModtag-YYYYMMDD-HHMMSS.xml
```

If you temporarily download into the repo root, the root DMR zip/XML patterns are ignored by `.gitignore`, but keeping 100GB+ data files outside the repo is cleaner.

Unpack the archive:

```bash
unzip ESStatistikListeModtag-YYYYMMDD-HHMMSS.zip
```

The extracted XML can be very large. A 100GB+ XML file is expected for a full extract.

## 6. Ingest The DMR XML

Set `DMR_XML_PATH` in `.env`:

```bash
DMR_XML_PATH=/absolute/path/to/ESStatistikListeModtag-YYYYMMDD-HHMMSS.xml
ES_INDEX=dmr-raw-000002
```

Reload `.env` in bash or zsh:

```bash
set -a
source .env
set +a
```

In fish, use the same loop from Step 3. The Python importer also reads `.env` directly, so sourcing is optional for ingest if the values are present in `.env`.

Run a small test import:

```bash
env MAX_RECORDS=1000 python3 dmr_parser/dmr_import_elastic_v6.py
```

Check the document count in Kibana Index Management or with ES|QL. For a 1,000-record test, the visible count may be slightly below 1,000 if records share the same `KoeretoejIdent` and overwrite earlier test documents.

Delete the test index before the full import so the final index is clean:

```bash
curl -X DELETE "$ES_URL/dmr-raw-000002" \
  -H "Authorization: ApiKey $ES_API_KEY"
```

Run the full import:

```bash
env MAX_RECORDS=0 python3 dmr_parser/dmr_import_elastic_v6.py
```

The importer streams the XML and writes bulk requests to Elasticsearch. The v6 importer creates an explicit mapping for the main dashboard and agent fields before ingest, which avoids common dynamic mapping failures in mixed numeric/string DMR fields.

During the full import, Kibana may show the index storage growing while the document count stays stale. That is expected because v6 disables refresh during ingest for speed and restores refresh at the end.

## 7. Validate The Index

```bash
npm run esql -- test
```

Check that records exist:

```bash
npm run esql -- raw 'FROM dmr-raw-000002 | STATS count = COUNT(*) BY status = KoeretoejRegistreringStatus.keyword | SORT count DESC | LIMIT 5' --tsv
```

Check the mapping:

```bash
npm run esql -- schema dmr-raw-000002
```

The DMR tools expect fields such as:

- `KoeretoejRegistreringStatus.keyword`
- `KoeretoejArtNavn.keyword`
- `RegistreringNummerNummer.keyword`
- `KoeretoejIdent`
- `_drivkraft_primaer`
- `_foerste_registrering_aar`
- `_co2_g_per_km_primaer`

If your index name or field names differ, update the affected JSON files in `specs/tools/` before syncing.

## 8. Install Agent Builder Assets

Preview:

```bash
npm run sync:plan
```

Apply:

```bash
npm run sync:agent-builder -- --apply
```

Verify:

```bash
npm run agent-builder -- list-agents
npm run agent-builder -- get-agent --id dmr-analyst
```

## 9. Create ES|QL Views

```bash
npm run create:views:dry-run
```

Paste the generated view commands into Kibana Dev Tools, or run:

```bash
npm run create:views
```

## 10. Install Dashboards

```bash
npm run dashboards -- test
npm run dashboards -- upsert dmr-fleet-overview dashboards/dmr-fleet-overview.json
npm run dashboards -- upsert dmr-performance-history-market dashboards/dmr-performance-history-market.json
npm run dashboards -- upsert elastic-operations-overview dashboards/elastic-operations-overview.json
```

Verify:

```bash
npm run dashboards -- get dmr-fleet-overview
npm run dashboards -- get dmr-performance-history-market
npm run dashboards -- get elastic-operations-overview
```

## 11. Smoke-Test The Agents

Run these in Kibana Agent Builder, or with the helper script:

```bash
npm run agent-builder -- chat --id dmr-analyst --message 'How many registered passenger cars are there?'
npm run agent-builder -- chat --id dmr-performance --message 'How powerful are registered Danish passenger cars? Show P50, P90, and P99 in kW and hp.'
npm run agent-builder -- chat --id dmr-market --message 'How many registered passenger cars are leased, and what share of the fleet is that?'
```

Expected behavior:

- current-fleet answers use `Registreret`
- car answers use `Personbil`
- common questions use dedicated DMR tools
- Danish registry labels are explained in English where useful

More prompts are in [dmr-agent-test-prompts.md](dmr-agent-test-prompts.md).

For dashboard deployment details and expected panel counts, see [dashboards/README.md](../dashboards/README.md).

## Troubleshooting

`KIBANA_URL is not set`

- Load `.env` using the bash/zsh or fish snippet in Step 3.

`no handler found for uri [/api/agent_builder/...]`

- `KIBANA_URL` is probably pointing at Elasticsearch on port `9200`. Set it to Kibana, usually port `5601`, then run `npm run validate:env`.

`401` or `403`

- Check that the API key is valid and has enough privileges for the target Kibana space or Elasticsearch cluster.

`index not found: dmr-raw-000002`

- Ingest the DMR XML first, or update the tool specs to your chosen index name.

`Unknown column` or ES|QL field errors

- Run `npm run esql -- schema dmr-raw-000002` and compare your mapping with the expected fields.

Importer says SMB credentials are missing

- Set `DMR_XML_PATH` for a local XML file. SMB settings are only needed for the network-share workflow.
