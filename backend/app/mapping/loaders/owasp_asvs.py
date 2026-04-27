"""
Loads OWASP ASVS 5.0 requirements from the local CSV file.
Source: dataset/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

from app.mapping.domains import OWASP_EXCLUDED_CHAPTERS, OWASP_SECTION_DOMAIN_MAP
from app.mapping.models import OWASPControl


def _dataset_dir() -> Path:
    env = os.getenv("CRITERIAMETER_DATASET_DIR")
    if env:
        return Path(env)
    # Default: relative to this file → backend/app/mapping/loaders/ → ../../../../dataset/
    return Path(__file__).resolve().parents[4] / "dataset"


def load_owasp_controls() -> list[OWASPControl]:
    csv_path = _dataset_dir() / "OWASP_Application_Security_Verification_Standard_5.0.0_en.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"OWASP ASVS CSV not found at {csv_path}. "
            "Set CRITERIAMETER_DATASET_DIR to point at the dataset directory."
        )

    controls: list[OWASPControl] = []

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            chapter_id = row["chapter_id"].strip()

            # Skip chapters with no SLSA relevance
            if chapter_id in OWASP_EXCLUDED_CHAPTERS:
                continue

            section_id = row["section_id"].strip()
            domains = OWASP_SECTION_DOMAIN_MAP.get(section_id, [])

            # Skip requirements that don't map to any domain
            if not domains:
                continue

            level_raw = row["L"].strip()
            try:
                level = int(level_raw)
            except ValueError:
                continue  # malformed row

            controls.append(
                OWASPControl(
                    id=row["req_id"].strip(),
                    chapter_id=chapter_id,
                    chapter_name=row["chapter_name"].strip(),
                    section_id=section_id,
                    section_name=row["section_name"].strip(),
                    req_description=row["req_description"].strip(),
                    level=level,
                    domains=domains,
                )
            )

    return controls
