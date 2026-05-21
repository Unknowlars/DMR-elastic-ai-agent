#!/usr/bin/env python3
r"""
DMR -> Elasticsearch importer v6.

This version is intentionally separate from dmr_import_elastic_2.py so a running
import is not affected.

Main changes:
  - creates a safer target index mapping before import when the index is missing
  - keeps VIN/frame/registration identifiers as strings, while KoeretoejIdent
    remains numeric for existing lookup tools
  - detects known incompatible mappings before import
  - writes failed bulk items to an NDJSON file for later inspection
  - sets parser metadata to version 6

Common usage:
    env ES_INDEX=dmr-raw-000003 MAX_RECORDS=0 python dmr_parser/dmr_import_elastic_v6.py

Optional destructive reset:
    env ES_DELETE_EXISTING=true ES_INDEX=dmr-raw-000003 python dmr_parser/dmr_import_elastic_v6.py

Validate a truncated repository sample without treating the missing closing XML
tags as a production import success:
    env DMR_XML_PATH=dmr_parser/small_sample.xml DMR_ALLOW_TRUNCATED_XML=true \
      MAX_RECORDS=0 python dmr_parser/dmr_import_elastic_v6.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import xml.etree.ElementTree as ET


def load_env_file(path: str = ".env") -> None:
    """Load simple KEY=VALUE lines without requiring shell-specific source syntax."""
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dmr_import_elastic_2 as base


PARSER_VERSION = 6
CREATE_INDEX = os.environ.get("ES_CREATE_INDEX", "true").lower() == "true"
DELETE_EXISTING = os.environ.get("ES_DELETE_EXISTING", "false").lower() == "true"
ALLOW_INCOMPATIBLE_INDEX = os.environ.get("ES_ALLOW_INCOMPATIBLE_INDEX", "false").lower() == "true"
ALLOW_TRUNCATED_XML = os.environ.get("DMR_ALLOW_TRUNCATED_XML", "false").lower() == "true"
FAIL_LOG_PATH = Path(os.environ.get("DMR_FAIL_LOG", "dmr_parser/data/import_failures.ndjson"))
FINAL_REFRESH_INTERVAL = os.environ.get("ES_FINAL_REFRESH_INTERVAL", "1s")
FINAL_REPLICAS = os.environ.get("ES_FINAL_REPLICAS")

# Keep VIN, frame, registration identifiers, and Danish label/name fields as
# strings. Some DMR labels are numeric-looking codes such as "7J0", but they are
# still categorical names, not numbers. KoeretoejIdent stays numeric because
# existing lookup tools use it as the stable vehicle id.
STRING_TAG_RE = re.compile(r"(Navn|StelNummer|Stelnr|RegistreringNummerNummer)$")


def parse_scalar_v6(text: str | None, tag: str | None = None) -> Any:
    if text is None:
        return None
    value = text.strip()
    if not value:
        return None
    if tag and STRING_TAG_RE.search(tag):
        return value
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if base.INT_RE.match(value):
        try:
            return int(value)
        except Exception:
            return value
    if base.FLOAT_RE.match(value):
        try:
            return float(value)
        except Exception:
            return value
    return value


def xml_to_dict_v6(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return parse_scalar_v6(element.text, base.strip_namespace(element.tag))
    result: dict[str, Any] = {}
    for child in children:
        tag = base.strip_namespace(child.tag)
        value = xml_to_dict_v6(child)
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value
    return result


def text_with_keyword(ignore_above: int = 1024) -> dict[str, Any]:
    return {
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": ignore_above,
            }
        },
    }


def keyword(ignore_above: int = 1024) -> dict[str, Any]:
    return {"type": "keyword", "ignore_above": ignore_above}


def date_field() -> dict[str, Any]:
    return {"type": "date", "format": "strict_date_optional_time||yyyy-MM-dd||yyyy-MM-ddXXX"}


def dmr_index_body() -> dict[str, Any]:
    return {
        "settings": {
            "index": {
                "number_of_shards": int(os.environ.get("ES_NUMBER_OF_SHARDS", "1")),
                "number_of_replicas": int(os.environ.get("ES_INITIAL_REPLICAS", "0")),
                "refresh_interval": os.environ.get("ES_INITIAL_REFRESH_INTERVAL", "-1"),
            }
        },
        "mappings": {
            "dynamic": True,
            "dynamic_templates": [
                {
                    "dmr_date_strings": {
                        "match": "*Dato",
                        "match_mapping_type": "string",
                        "mapping": date_field(),
                    }
                },
                {
                    "dmr_default_strings": {
                        "match_mapping_type": "string",
                        "mapping": text_with_keyword(),
                    }
                },
            ],
            "properties": {
                "KoeretoejIdent": {"type": "long"},
                "RegistreringNummerNummer": text_with_keyword(256),
                "KoeretoejRegistreringStatus": text_with_keyword(256),
                "KoeretoejRegistreringStatusDato": date_field(),
                "KoeretoejArtNavn": text_with_keyword(256),
                "KoeretoejArtNummer": {"type": "long"},
                "LeasingGyldigFra": date_field(),
                "LeasingGyldigTil": date_field(),
                "RegistreringNummerUdloebDato": date_field(),
                "RegistreringNummerRettighedGyldigFra": date_field(),
                "RegistreringNummerRettighedGyldigTil": date_field(),
                "_drivkraft_primaer": keyword(256),
                "_co2_g_per_km_primaer": {"type": "double"},
                "_km_per_liter_primaer": {"type": "double"},
                "_maale_norm_primaer": keyword(256),
                "_foerste_registrering_aar": {"type": "integer"},
                "_parser": {
                    "properties": {
                        "name": keyword(128),
                        "version": {"type": "integer"},
                    }
                },
                "KoeretoejOplysningGrundStruktur": {
                    "properties": {
                        "KoeretoejOplysningStelNummer": text_with_keyword(512),
                        "KoeretoejOplysningTilkobletSidevognStelnr": text_with_keyword(512),
                        "KoeretoejOplysningFoersteRegistreringDato": date_field(),
                        "KoeretoejOplysningIbrugtagningDato": date_field(),
                        "KoeretoejOplysningStatusDato": date_field(),
                        "KoeretoejOplysningModelAar": {"type": "integer"},
                        "KoeretoejOplysningAkselAntal": {"type": "integer"},
                        "KoeretoejOplysningAntalDoere": {"type": "integer"},
                        "KoeretoejOplysningSiddepladserMinimum": {"type": "integer"},
                        "KoeretoejOplysningSiddepladserMaksimum": {"type": "integer"},
                        "KoeretoejOplysningEgenVaegt": {"type": "integer"},
                        "KoeretoejOplysningTotalVaegt": {"type": "integer"},
                        "KoeretoejOplysningKoereklarVaegtMinimum": {"type": "integer"},
                        "KoeretoejOplysningKoereklarVaegtMaksimum": {"type": "integer"},
                        "KoeretoejOplysningTraekkendeAkslerRaw": keyword(128),
                        "KoeretoejOplysningTraekkendeAkslerListe": {"type": "integer"},
                        "KoeretoejBetegnelseStruktur": {
                            "properties": {
                                "KoeretoejMaerkeTypeNavn": text_with_keyword(256),
                                "KoeretoejMaerkeTypeNummer": {"type": "long"},
                                "Model": {
                                    "properties": {
                                        "KoeretoejModelTypeNavn": text_with_keyword(256),
                                        "KoeretoejModelTypeNummer": {"type": "long"},
                                    }
                                },
                                "Type": {
                                    "properties": {
                                        "KoeretoejTypeTypeNavn": text_with_keyword(256),
                                        "KoeretoejTypeTypeNummer": {"type": "long"},
                                    }
                                },
                                "Variant": {
                                    "properties": {
                                        "KoeretoejVariantTypeNavn": text_with_keyword(256),
                                        "KoeretoejVariantTypeNummer": {"type": "long"},
                                    }
                                },
                            }
                        },
                        "KarrosseriTypeStruktur": {
                            "properties": {
                                "KarrosseriTypeNavn": text_with_keyword(256),
                                "KarrosseriTypeNummer": {"type": "long"},
                            }
                        },
                        "KoeretoejFarveStruktur": {
                            "properties": {
                                "FarveTypeStruktur": {
                                    "properties": {
                                        "FarveTypeNavn": text_with_keyword(256),
                                        "FarveTypeNummer": {"type": "long"},
                                    }
                                }
                            }
                        },
                        "KoeretoejMotorStruktur": {
                            "properties": {
                                "KoeretoejMotorStoersteEffekt": {"type": "double"},
                                "KoeretoejMotorSlagVolumen": {"type": "double"},
                                "KoeretoejMotorCylinderAntal": {"type": "integer"},
                                "KoeretoejMotorKilometerstand": {"type": "long"},
                            }
                        },
                    }
                },
                "SynResultatStruktur": {
                    "properties": {
                        "SynResultatSynsDato": date_field(),
                        "SynResultatSynStatusDato": date_field(),
                        "SynResultatSynsResultat": text_with_keyword(256),
                        "KoeretoejMotorKilometerstand": {"type": "long"},
                    }
                },
            },
        },
    }


def flatten_properties(properties: dict[str, Any], prefix: str = "") -> dict[str, str]:
    flattened: dict[str, str] = {}
    for name, definition in properties.items():
        path = f"{prefix}.{name}" if prefix else name
        field_type = definition.get("type")
        if field_type:
            flattened[path] = field_type
        child_props = definition.get("properties")
        if isinstance(child_props, dict):
            flattened.update(flatten_properties(child_props, path))
    return flattened


def index_exists(client) -> bool:
    return bool(client.indices.exists(index=base.ES_INDEX))


def create_index(client) -> None:
    client.indices.create(index=base.ES_INDEX, **dmr_index_body())
    print(f"Created index {base.ES_INDEX} with v6 DMR mappings.")


def delete_index(client) -> None:
    client.indices.delete(index=base.ES_INDEX, ignore_unavailable=True)
    print(f"Deleted existing index {base.ES_INDEX}.")


def get_field_types(client) -> dict[str, str]:
    mapping = client.indices.get_mapping(index=base.ES_INDEX)
    index_mapping = next(iter(mapping.values())).get("mappings", {})
    return flatten_properties(index_mapping.get("properties", {}))


def check_mapping_compatibility(client) -> None:
    field_types = get_field_types(client)
    required = {
        "KoeretoejIdent": "long",
        "RegistreringNummerNummer": "text",
        "KoeretoejOplysningGrundStruktur.KoeretoejOplysningStelNummer": "text",
        "KoeretoejOplysningGrundStruktur.KoeretoejOplysningTilkobletSidevognStelnr": "text",
        "KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.KoeretoejMaerkeTypeNavn": "text",
        "KoeretoejOplysningGrundStruktur.KoeretoejBetegnelseStruktur.Model.KoeretoejModelTypeNavn": "text",
        "KoeretoejOplysningGrundStruktur.KoeretoejMotorStruktur.KoeretoejMotorStoersteEffekt": "double",
        "_drivkraft_primaer": "keyword",
        "_foerste_registrering_aar": "integer",
    }
    incompatible = []
    for field, expected in required.items():
        actual = field_types.get(field)
        if actual and actual != expected:
            incompatible.append((field, expected, actual))

    if not incompatible:
        return

    print("Incompatible existing index mapping detected:", file=sys.stderr)
    for field, expected, actual in incompatible:
        print(f"  {field}: expected {expected}, found {actual}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Use a fresh ES_INDEX, or set ES_DELETE_EXISTING=true to recreate it.", file=sys.stderr)
    if not ALLOW_INCOMPATIBLE_INDEX:
        raise SystemExit(3)


def prepare_index(client) -> bool:
    created = False
    if DELETE_EXISTING:
        delete_index(client)

    if index_exists(client):
        check_mapping_compatibility(client)
        return created

    if not CREATE_INDEX:
        return created

    create_index(client)
    return True


def restore_index_settings(client, created: bool) -> None:
    if not created:
        return
    settings: dict[str, Any] = {"refresh_interval": FINAL_REFRESH_INTERVAL}
    if FINAL_REPLICAS is not None:
        settings["number_of_replicas"] = int(FINAL_REPLICAS)
    client.indices.put_settings(index=base.ES_INDEX, settings=settings)
    client.indices.refresh(index=base.ES_INDEX)
    print(f"Restored index refresh_interval={settings['refresh_interval']}.")


def generate_actions_v6() -> Iterable[dict[str, Any]]:
    fh, is_smb = base.open_source_file()
    context = ET.iterparse(fh, events=("start", "end"))
    _, root = next(context)
    count = 0
    try:
        try:
            for event, elem in context:
                if event != "end":
                    continue
                if base.strip_namespace(elem.tag) != "Statistik":
                    continue

                record = xml_to_dict_v6(elem)
                record = base.normalize_known_list_shapes(record)
                record = base.normalize_traekkende_aksler(record)
                record = base.normalize_date_fields(record)
                record = base.extract_primary_drivmiddel(record)
                record["_parser"] = {"name": "xml_to_elastic_direct_smb", "version": PARSER_VERSION}

                doc_id = record.get("KoeretoejIdent")
                yield {
                    "_op_type": "index",
                    "_index": base.ES_INDEX,
                    "_id": str(doc_id) if doc_id is not None else None,
                    "_source": record,
                }

                count += 1
                if base.PROGRESS_EVERY > 0 and count % base.PROGRESS_EVERY == 0:
                    print(f"Prepared {count:,} records ...", flush=True)

                elem.clear()
                root.clear()

                if base.MAX_RECORDS and count >= base.MAX_RECORDS:
                    break
        except ET.ParseError as exc:
            if not ALLOW_TRUNCATED_XML:
                raise
            print(
                f"WARNING: truncated XML accepted after {count:,} complete records: {exc}",
                file=sys.stderr,
            )
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


def append_failure(info: Any) -> None:
    FAIL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FAIL_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": time.time(), "error": info}, ensure_ascii=False) + "\n")


def main() -> int:
    from elasticsearch import helpers

    source = base.DMR_XML_PATH or base.SMB_PATH
    source_type = "local file" if base.DMR_XML_PATH else "SMB"
    print(f"Source : {source} ({source_type})")
    print(f"Target : {base.ES_INDEX}  @  {base.ES_URL}")
    print(f"Parser : v{PARSER_VERSION}")
    print(f"Failure log: {FAIL_LOG_PATH}")
    print()

    client = base.build_client()
    created = prepare_index(client)

    sent = ok = failed = 0
    for success, info in helpers.streaming_bulk(
        client,
        generate_actions_v6(),
        chunk_size=base.CHUNK_SIZE,
        max_retries=5,
        initial_backoff=2,
        max_backoff=60,
        raise_on_error=False,
        raise_on_exception=False,
        request_timeout=120,
    ):
        sent += 1
        if success:
            ok += 1
        else:
            failed += 1
            append_failure(info)
            print(f"FAILED: {info}", file=sys.stderr)
        if base.PROGRESS_EVERY > 0 and sent % base.PROGRESS_EVERY == 0:
            print(f"Indexed {ok:,}/{sent:,}  failed={failed}", flush=True)

    restore_index_settings(client, created)
    print()
    print(f"Done. indexed={ok:,} failed={failed} total={sent:,}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
