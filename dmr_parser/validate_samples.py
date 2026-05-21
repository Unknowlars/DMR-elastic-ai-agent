#!/usr/bin/env python3
"""Validate the DMR parser against local XML sample files.

The sample XML files in this folder are truncated, so this script only parses
the first N <Statistik> records from each file and runs them through the parser
pipeline. It is intended as a quick local regression check, not a full import.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PARSER_PATH = ROOT / "dmr_import_elastic_v6.py"
DEFAULT_SAMPLES = [
    ROOT / "small_sample.xml",
    ROOT / "ESStatistikListeModtag-5MB.xml",
]


def load_parser():
    spec = importlib.util.spec_from_file_location("dmr_import_elastic_v6", PARSER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load parser module from {PARSER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def iter_sample_records(parser, path: Path, limit: int):
    count = 0
    with path.open("rb") as fh:
        context = ET.iterparse(fh, events=("end",))
        try:
            try:
                for event, elem in context:
                    if parser.base.strip_namespace(elem.tag) != "Statistik":
                        continue

                    record = parser.xml_to_dict_v6(elem)
                    record = parser.base.normalize_known_list_shapes(record)
                    record = parser.base.normalize_traekkende_aksler(record)
                    record = parser.base.normalize_date_fields(record)
                    record = parser.base.extract_primary_drivmiddel(record)
                    record["_parser"] = {
                        "name": "xml_to_elastic_direct_smb",
                        "version": parser.PARSER_VERSION,
                    }
                    count += 1
                    yield record

                    elem.clear()
                    if count >= limit:
                        break
            except ET.ParseError:
                if count == 0:
                    raise
        finally:
            try:
                fh.close()
            except Exception:
                pass


def main(argv: list[str]) -> int:
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Maximum number of Statistik records to parse from each sample file.",
    )
    argp.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=DEFAULT_SAMPLES,
        help="Sample XML files to validate.",
    )
    args = argp.parse_args(argv)

    parser = load_parser()

    failures = 0
    for path in args.paths:
        if not path.exists():
            print(f"MISS  {path}", file=sys.stderr)
            failures += 1
            continue

        parsed = 0
        try:
            for record in iter_sample_records(parser, path, args.limit):
                parsed += 1
                if parsed == 1:
                    print(
                        f"OK    {path.name} first_id={record.get('KoeretoejIdent')} "
                        f"parser_v={record.get('_parser', {}).get('version')}"
                    )
        except Exception as exc:
            print(f"FAIL  {path}  {type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
            continue

        print(f"PASS  {path.name} parsed={parsed} limit={args.limit}")

    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
