# Get And Ingest DMR Data

This guide covers only the DMR XML download and Elasticsearch ingest flow. After the data is indexed, continue with [dmr-agent-quickstart.md](dmr-agent-quickstart.md).

## What The Importer Does

`dmr_parser/dmr_import_elastic_v6.py` reads the DMR XML file one vehicle record at a time and writes documents to Elasticsearch.

The v6 importer is the recommended public version. It creates a safer explicit Elasticsearch mapping, keeps VIN/frame/registration identifiers as strings, validates incompatible existing mappings before import, and writes failed bulk items to an NDJSON failure log.

It also adds helper fields used by the tools and dashboards:

- `_drivkraft_primaer`
- `_co2_g_per_km_primaer`
- `_km_per_liter_primaer`
- `_maale_norm_primaer`
- `_foerste_registrering_aar`

The default target index is:

```text
dmr-raw-000002
```

## 1. Download The DMR Export

Motorstyrelsen publishes the DMR statistics extract on the official `Andre adgange` page under `Statistikudtraek`:

https://motorst.dk/erhverv/motorregistret-for-virksomheder/faa-adgang-til-motorregistret/andre-adgange

Download the archive from the details shown there.

The link currently opens an FTP location. A resumable command-line download is useful because the archive is large:

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

Replace `YYYYMMDD-HHMMSS` with the filename shown by Motorstyrelsen.

Notes:

- The export is large.
- Use 64-bit unzip software.
- The public extract is normally updated weekly.
- Keep the full XML export outside this repo.
- If you temporarily download into the repo root, the DMR zip/XML patterns are ignored, but external storage is cleaner for 100GB+ files.

## 2. Unpack The Archive

After unpacking, find the XML file. It is usually named like:

```text
ESStatistikListeModtag-YYYYMMDD-HHMMSS.xml
```

Place it outside the repository:

```text
/data/dmr/ESStatistikListeModtag-YYYYMMDD-HHMMSS.xml
```

If you downloaded into the repo root, the extracted file may be named:

```text
ESStatistikListeModtag.xml
```

Point `DMR_XML_PATH` at the actual extracted file.

## 3. Install Python Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r dmr_parser/requirements.txt
```

In fish, use:

```fish
source .venv/bin/activate.fish
python -m pip install -r dmr_parser/requirements.txt
```

## 4. Configure Elasticsearch

```bash
cp .env.example .env
```

Edit `.env`:

```bash
ES_URL=https://your-elasticsearch.example.com
ES_API_KEY=your-elasticsearch-api-key
ES_INDEX=dmr-raw-000002
DMR_XML_PATH=/absolute/path/to/ESStatistikListeModtag-YYYYMMDD-HHMMSS.xml

ELASTICSEARCH_URL=https://your-elasticsearch.example.com
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key
```

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

The Python importer also reads `.env` directly, so sourcing is optional for ingest if the values are present in `.env`.

## 5. Validate Parser Samples

This does not connect to Elasticsearch. It checks that the parser can read the bundled sample XML files.

```bash
python3 dmr_parser/validate_samples.py --limit 25
```

Expected result:

```text
PASS  small_sample.xml parsed=...
PASS  ESStatistikListeModtag-5MB.xml parsed=...
```

The bundled XML files are intentionally truncated parser samples, not complete DMR exports. For direct importer checks against a sample, either stop before the end:

```bash
env DMR_XML_PATH=dmr_parser/ESStatistikListeModtag-5MB.xml MAX_RECORDS=25 python3 dmr_parser/dmr_import_elastic_v6.py
```

or opt into truncated-sample mode:

```bash
env DMR_XML_PATH=dmr_parser/ESStatistikListeModtag-5MB.xml DMR_ALLOW_TRUNCATED_XML=true MAX_RECORDS=0 python3 dmr_parser/dmr_import_elastic_v6.py
```

Do not use `DMR_ALLOW_TRUNCATED_XML=true` for a full production import.

## 6. Run A Small Import

```bash
env MAX_RECORDS=1000 python3 dmr_parser/dmr_import_elastic_v6.py
```

Check the target index:

```bash
npm run esql -- raw 'FROM dmr-raw-000002 | STATS count = COUNT(*) | LIMIT 1' --tsv
```

If the test import created `dmr-raw-000002`, delete it before the full import so the full run starts from a clean v6-created index:

```bash
curl -X DELETE "$ES_URL/dmr-raw-000002" \
  -H "Authorization: ApiKey $ES_API_KEY"
```

## 7. Run The Full Import

```bash
env MAX_RECORDS=0 python3 dmr_parser/dmr_import_elastic_v6.py
```

The importer prints progress every `PROGRESS_EVERY` records. Tune `CHUNK_SIZE`, `MAX_RECORDS`, and `PROGRESS_EVERY` in `.env`.

During the full import, Kibana Index Management can show storage growth before document counts update. v6 temporarily sets `refresh_interval=-1` for import speed and refreshes the index when the import finishes.

## Optional: SMB Source

If the XML file is on a network share, leave `DMR_XML_PATH` empty and set:

```bash
SMB_USER=your-smb-user
SMB_PASS=your-smb-password
SMB_PATH=\\\\server\\share\\DMR\\ESStatistikListeModtag.xml
```

The local file path is simpler and is used first when set.
