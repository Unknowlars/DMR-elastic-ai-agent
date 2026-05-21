#!/usr/bin/env python3
r"""
DMR → Elasticsearch importer  (drop-in replacement, v4)
=========================================================
Changes vs v3:
  - normalize_date_fields()       : strips +HH:MM from date-only fields so ES
                                    can map them as `date` type in dmr-raw-000002
  - extract_primary_drivmiddel()  : adds flat top-level fields:
                                      _drivkraft_primaer         (keyword)
                                      _co2_g_per_km_primaer      (float)
                                      _km_per_liter_primaer      (float)
                                      _maale_norm_primaer        (keyword)
                                      _foerste_registrering_aar  (integer)
                                    Picks only the entry where
                                    KoeretoejMotorDrivmiddelPrimaer == true,
                                    so NEDC vs WLTP duplicates never pollute aggs.
  - _parser.version bumped to 4

Usage:
    DMR_XML_PATH=/path/to/ESStatistikListeModtag.xml python3 dmr_parser/dmr_import_elastic_2.py
    SMB_PASS=your-smb-password SMB_PATH='\\server\share\DMR\ESStatistikListeModtag.xml' python3 dmr_parser/dmr_import_elastic_2.py

Environment variables:
    DMR_XML_PATH      local XML file path; preferred for most users
    SMB_USER          optional SMB username
    SMB_PASS          required only when DMR_XML_PATH is not set
    SMB_PATH          optional SMB path to the extracted XML file
    ES_URL            default: http://localhost:9200
    ES_USER           optional basic-auth username
    ES_PASS           optional basic-auth password
    ES_API_KEY        optional API key (takes priority over basic-auth)
    ES_INDEX          default: dmr-raw-000002
    CHUNK_SIZE        default: 500
    MAX_RECORDS       default: 0  (0 = no limit)
    PROGRESS_EVERY    default: 10000
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Iterable

# ── Settings ───────────────────────────────────────────────────────────────────

DMR_XML_PATH = os.environ.get("DMR_XML_PATH")

SMB_USER = os.environ.get("SMB_USER", "")
SMB_PASS = os.environ.get("SMB_PASS", "")
SMB_PATH = os.environ.get(
    "SMB_PATH",
    r"\\server\share\DMR\ESStatistikListeModtag.xml",
)

ES_URL     = os.environ.get("ES_URL",   "http://localhost:9200")
ES_USER    = os.environ.get("ES_USER")
ES_PASS    = os.environ.get("ES_PASS")
ES_API_KEY = os.environ.get("ES_API_KEY")
ES_INDEX   = os.environ.get("ES_INDEX", "dmr-raw-000002")

CHUNK_SIZE     = int(os.environ.get("CHUNK_SIZE",     "500"))
MAX_RECORDS    = int(os.environ.get("MAX_RECORDS",    "0"))
PROGRESS_EVERY = int(os.environ.get("PROGRESS_EVERY", "10000"))

INT_RE   = re.compile(r"^-?\d+$")
FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\+\d{2}:\d{2}$")

# Date-only fields that arrive as "yyyy-MM-dd+HH:MM" — strip to "yyyy-MM-dd"
_DATE_ONLY_IN_GRUND = {
    "KoeretoejOplysningFoersteRegistreringDato",
    "KoeretoejOplysningStatusDato",      # sometimes date-only, sometimes full datetime
}
_DATE_ONLY_TOPLEVEL = {
    "LeasingGyldigFra",
    "LeasingGyldigTil",
    "RegistreringNummerUdloebDato",
}
_DATE_ONLY_IN_SYN = {
    "SynResultatSynsDato",
    "SynResultatSynStatusDato",
}
_DATE_ONLY_IN_TILLADELSE = {
    "TilladelseGyldigFra",
}


# ── XML helpers ────────────────────────────────────────────────────────────────

def strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    if ":" in tag:
        return tag.split(":", 1)[1]
    return tag


def parse_scalar(text: str | None) -> Any:
    if text is None:
        return None
    value = text.strip()
    if not value:
        return None
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if INT_RE.match(value):
        try:
            return int(value)
        except Exception:
            return value
    if FLOAT_RE.match(value):
        try:
            return float(value)
        except Exception:
            return value
    return value


def xml_to_dict(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return parse_scalar(element.text)
    result: dict = {}
    for child in children:
        tag   = strip_namespace(child.tag)
        value = xml_to_dict(child)
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value
    return result


def ensure_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def ensure_list_at_path(data: dict, path: list[str]) -> None:
    current = data
    for key in path[:-1]:
        if not isinstance(current, dict):
            return
        current = current.get(key)
        if current is None:
            return
    last_key = path[-1]
    if isinstance(current, dict) and last_key in current \
            and not isinstance(current[last_key], list):
        current[last_key] = [current[last_key]]


# ── Normalizers ────────────────────────────────────────────────────────────────

def normalize_known_list_shapes(record: dict) -> dict:
    ensure_list_at_path(record, ["TilladelseSamling", "Tilladelse"])
    ensure_list_at_path(record, [
        "KoeretoejOplysningGrundStruktur",
        "KoeretoejUdstyrSamlingStruktur",
        "KoeretoejUdstyrSamling",
        "KoeretoejUdstyrStruktur",
    ])
    ensure_list_at_path(record, [
        "KoeretoejOplysningGrundStruktur",
        "KoeretoejBlokeringAarsagListeStruktur",
        "KoeretoejBlokeringAarsagListe",
        "KoeretoejBlokeringAarsag",
    ])
    ensure_list_at_path(record, [
        "KoeretoejOplysningGrundStruktur",
        "KoeretoejSupplerendeKarrosseriSamlingStruktur",
        "KoeretoejSupplerendeKarrosseriSamling",
    ])
    ensure_list_at_path(record, [
        "KoeretoejAnvendelseSamlingStruktur",
        "KoeretoejAnvendelseSamling",
    ])
    ensure_list_at_path(record, [
        "KoeretoejOplysningGrundStruktur",
        "KoeretoejMotorStruktur",
        "KoeretoejDrivmiddelSamlingStruktur",
        "KoeretoejDrivmiddelSamling",
    ])
    samlinger = (
        record.get("KoeretoejOplysningGrundStruktur", {})
              .get("KoeretoejMotorStruktur", {})
              .get("KoeretoejDrivmiddelSamlingStruktur", {})
              .get("KoeretoejDrivmiddelSamling")
    )
    for samling in ensure_list(samlinger):
        if isinstance(samling, dict) and "DrivmiddelStruktur" in samling:
            if not isinstance(samling["DrivmiddelStruktur"], list):
                samling["DrivmiddelStruktur"] = [samling["DrivmiddelStruktur"]]
    return record


def normalize_traekkende_aksler(record: dict) -> dict:
    grund = record.get("KoeretoejOplysningGrundStruktur")
    if not isinstance(grund, dict):
        return record
    key   = "KoeretoejOplysningTraekkendeAksler"
    value = grund.get(key)
    if value is None:
        return record
    if isinstance(value, int):
        grund[key + "Raw"]   = str(value)
        grund[key + "Liste"] = [value]
        return record
    s    = str(value).strip()
    nums = [int(x) for x in re.findall(r"\d+", s)]
    grund[key + "Raw"] = s
    if nums:
        grund[key + "Liste"] = nums
    if s.isdigit():
        grund[key] = int(s)
    else:
        grund.pop(key, None)
    return record


def _clean_date(val: Any) -> str | None:
    """Return the first 10 chars (yyyy-MM-dd) if val looks like a date string."""
    if not isinstance(val, str):
        return None
    s = val.strip()
    # Full datetime like 2017-09-15T14:52:45.000+02:00 — leave as-is (ES handles it)
    if "T" in s:
        return s
    # Date-only with offset like 2014-10-13+02:00 → 2014-10-13
    if DATE_ONLY_RE.match(s):
        return s[:10]
    return s


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def normalize_date_fields(record: dict) -> dict:
    """
    Strips timezone offsets from date-only fields so they parse cleanly as
    `date` type in Elasticsearch (format: yyyy-MM-dd).

    Full datetime fields (containing 'T') are left untouched — ES handles
    strict_date_optional_time fine for those.
    """
    # Top-level fields
    for key in _DATE_ONLY_TOPLEVEL:
        if key in record:
            cleaned = _clean_date(record[key])
            if cleaned is not None:
                record[key] = cleaned

    # Fields inside KoeretoejOplysningGrundStruktur
    grund = record.get("KoeretoejOplysningGrundStruktur")
    if isinstance(grund, dict):
        for key in _DATE_ONLY_IN_GRUND:
            if key in grund:
                cleaned = _clean_date(grund[key])
                if cleaned is not None:
                    grund[key] = cleaned

    # SynResultatStruktur
    syn = record.get("SynResultatStruktur")
    if isinstance(syn, dict):
        for key in _DATE_ONLY_IN_SYN:
            if key in syn:
                cleaned = _clean_date(syn[key])
                if cleaned is not None:
                    syn[key] = cleaned

    # TilladelseSamling → Tilladelse[] → TilladelseStruktur
    tilladelse_samling = record.get("TilladelseSamling")
    if isinstance(tilladelse_samling, dict):
        for tilladelse in ensure_list(tilladelse_samling.get("Tilladelse")):
            if not isinstance(tilladelse, dict):
                continue
            struktur = tilladelse.get("TilladelseStruktur")
            if not isinstance(struktur, dict):
                continue
            for key in _DATE_ONLY_IN_TILLADELSE:
                if key in struktur:
                    cleaned = _clean_date(struktur[key])
                    if cleaned is not None:
                        struktur[key] = cleaned

    return record


def extract_primary_drivmiddel(record: dict) -> dict:
    """
    Adds flat top-level fields derived from the primary fuel entry
    (KoeretoejMotorDrivmiddelPrimaer == true):

      _drivkraft_primaer         str   "Benzin" | "Diesel" | "El" | …
      _co2_g_per_km_primaer      float grams CO2 per km
      _km_per_liter_primaer      float km per litre
      _maale_norm_primaer        str   "WLTP" | "NEDC-2" | "NEDC" | …
      _foerste_registrering_aar  int   year of first registration

    These flat fields let Kibana aggregate fuel type and emissions without
    traversing the 6-level nested DrivmiddelStruktur array, and avoid the
    double-counting problem that occurs when both NEDC and WLTP entries exist
    for the same vehicle.
    """
    grund = record.get("KoeretoejOplysningGrundStruktur")
    if not isinstance(grund, dict):
        return record

    # ── Registration year ──────────────────────────────────────────────────────
    dato = grund.get("KoeretoejOplysningFoersteRegistreringDato")
    if isinstance(dato, str) and len(dato) >= 4:
        try:
            record["_foerste_registrering_aar"] = int(dato[:4])
        except ValueError:
            pass

    # ── Primary fuel traversal ─────────────────────────────────────────────────
    motor = grund.get("KoeretoejMotorStruktur")
    if not isinstance(motor, dict):
        return record

    samlinger = (
        motor.get("KoeretoejDrivmiddelSamlingStruktur", {})
             .get("KoeretoejDrivmiddelSamling")
    )
    if samlinger is None:
        return record

    for samling in ensure_list(samlinger):
        if not isinstance(samling, dict):
            continue
        for dm in ensure_list(samling.get("DrivmiddelStruktur")):
            if not isinstance(dm, dict):
                continue
            if not dm.get("KoeretoejMotorDrivmiddelPrimaer", False):
                continue

            # DrivkraftTypeNavn
            drivkraft = dm.get("DrivkraftTypeStruktur")
            if isinstance(drivkraft, dict):
                navn = drivkraft.get("DrivkraftTypeNavn")
                if navn:
                    record["_drivkraft_primaer"] = navn

            # CO2 and km/L
            braendstof = dm.get("KoeretoejBraendstofStruktur")
            if isinstance(braendstof, dict):
                co2 = braendstof.get("KoeretoejMiljoeOplysningCO2Udslip")
                kml = braendstof.get("KoeretoejMotorKmPerLiter")
                co2_value = _coerce_float(co2)
                kml_value = _coerce_float(kml)
                if co2_value is not None:
                    record["_co2_g_per_km_primaer"] = co2_value
                if kml_value is not None:
                    record["_km_per_liter_primaer"] = kml_value

            # Measurement standard (WLTP / NEDC / NEDC-2)
            maale = dm.get("MaaleNormStruktur")
            if isinstance(maale, dict):
                norm = maale.get("KoeretoejMotorMaaleNormTypeNavn")
                if norm:
                    record["_maale_norm_primaer"] = norm

            break  # stop after the first primary entry

    return record


# ── Elasticsearch client ───────────────────────────────────────────────────────

def build_client():
    from elasticsearch import Elasticsearch

    if ES_API_KEY:
        return Elasticsearch(
            ES_URL, api_key=ES_API_KEY,
            request_timeout=120, retry_on_timeout=True,
        )
    if ES_USER and ES_PASS:
        return Elasticsearch(
            ES_URL, basic_auth=(ES_USER, ES_PASS),
            request_timeout=120, retry_on_timeout=True,
        )
    return Elasticsearch(ES_URL, request_timeout=120, retry_on_timeout=True)


# ── SMB / XML source ───────────────────────────────────────────────────────────

def open_local_file():
    if not DMR_XML_PATH:
        raise RuntimeError("DMR_XML_PATH is empty.")
    return open(DMR_XML_PATH, "rb")


def open_smb_file():
    if not SMB_PASS:
        raise RuntimeError("SMB_PASS is empty. Set DMR_XML_PATH for a local XML file or set SMB_PASS for SMB.")
    import smbclient

    smbclient.ClientConfig(username=SMB_USER, password=SMB_PASS)
    return smbclient.open_file(SMB_PATH, mode="rb")


def open_source_file() -> tuple[Any, bool]:
    if DMR_XML_PATH:
        return open_local_file(), False
    return open_smb_file(), True


def generate_actions() -> Iterable[dict]:
    fh, is_smb = open_source_file()
    context = ET.iterparse(fh, events=("start", "end"))
    _, root = next(context)
    count   = 0
    try:
        for event, elem in context:
            if event != "end":
                continue
            if strip_namespace(elem.tag) != "Statistik":
                continue

            record = xml_to_dict(elem)

            # ── Normalisation pipeline ─────────────────────────────────────────
            record = normalize_known_list_shapes(record)
            record = normalize_traekkende_aksler(record)
            record = normalize_date_fields(record)
            record = extract_primary_drivmiddel(record)
            # ──────────────────────────────────────────────────────────────────

            record["_parser"] = {"name": "xml_to_elastic_direct_smb", "version": 4}

            doc_id = record.get("KoeretoejIdent")
            yield {
                "_op_type": "index",
                "_index":   ES_INDEX,
                "_id":      str(doc_id) if doc_id is not None else None,
                "_source":  record,
            }

            count += 1
            if PROGRESS_EVERY > 0 and count % PROGRESS_EVERY == 0:
                print(f"Prepared {count:,} records …", flush=True)

            elem.clear()
            root.clear()

            if MAX_RECORDS and count >= MAX_RECORDS:
                break
    finally:
        try:
            fh.close()
        except Exception:
            pass
        if is_smb:
            try:
                import smbclient

                smbclient.reset_connection_cache()
            except Exception:
                pass


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    from elasticsearch import helpers

    source = DMR_XML_PATH or SMB_PATH
    source_type = "local file" if DMR_XML_PATH else "SMB"
    print(f"Source : {source} ({source_type})")
    print(f"Target : {ES_INDEX}  @  {ES_URL}")
    print()

    client = build_client()
    sent = ok = failed = 0

    for success, info in helpers.streaming_bulk(
        client,
        generate_actions(),
        chunk_size=CHUNK_SIZE,
        max_retries=3,
        initial_backoff=2,
        max_backoff=30,
        raise_on_error=False,
        raise_on_exception=False,
    ):
        sent += 1
        if success:
            ok += 1
        else:
            failed += 1
            print(f"FAILED: {info}", file=sys.stderr)
        if PROGRESS_EVERY > 0 and sent % PROGRESS_EVERY == 0:
            print(f"Indexed {ok:,}/{sent:,}  failed={failed}", flush=True)

    print()
    print(f"Done.  indexed={ok:,}  failed={failed}  total={sent:,}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
