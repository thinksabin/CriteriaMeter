"""
Entry point: generate unified_mapping.json.

Usage (from repo root):
    cd backend
    python -m app.mapping.run_mapping

The output is written to backend/app/mapping/output/unified_mapping.json.
Re-running overwrites the file; the script is idempotent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from app.mapping.mapper import build_mapping


OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "unified_mapping.json"


def main() -> None:
    print("Building unified control mapping …")

    try:
        mapping = build_mapping()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(mapping.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Done.")
    print(f"  Frameworks : {', '.join(mapping.frameworks)}")
    print(f"  Domains    : {mapping.domain_count}")
    print(f"  SLSA items : {mapping.slsa_control_count}")
    print(f"  OWASP reqs : {mapping.owasp_control_count}")
    print(f"  SOC 2      : {mapping.soc2_control_count}")
    print(f"  GDPR       : {mapping.gdpr_control_count}")
    print(f"  ISO 27001  : {mapping.iso27001_control_count}")
    print(f"  Output     : {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
