"""
Loads SOC 2, GDPR, and ISO 27001:2022 controls from the CSV checklist files
in the dataset/ directory.

All three CSVs share the same schema:
    id, framework, domain, control_ref, requirement, description,
    evidence_examples, responsible_role, frequency, priority, status, notes
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

from app.mapping.domains import (
    COMPLIANCE_DOMAIN_KEYS,
    GDPR_CONTROL_DOMAIN_MAP,
    ISO27001_CONTROL_DOMAIN_MAP,
    SOC2_CONTROL_DOMAIN_MAP,
)
from app.mapping.models import GDPRControl, ISO27001Control, SOC2Control


def _dataset_dir() -> Path:
    env = os.getenv("CRITERIAMETER_DATASET_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[4] / "dataset"


def _read_csv(filename: str) -> list[dict]:
    path = _dataset_dir() / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found at {path}. "
            "Set CRITERIAMETER_DATASET_DIR to point at the dataset directory."
        )
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_compliance_controls() -> tuple[
    list[SOC2Control],
    list[GDPRControl],
    list[ISO27001Control],
]:
    soc2_controls: list[SOC2Control] = []
    for row in _read_csv("soc2_checklist.csv"):
        ctrl_id = row["id"].strip()
        domains = [
            dk for dk in SOC2_CONTROL_DOMAIN_MAP.get(ctrl_id, [])
            if dk in COMPLIANCE_DOMAIN_KEYS
        ]
        if not domains:
            continue
        soc2_controls.append(SOC2Control(
            id=ctrl_id,
            control_ref=row["control_ref"].strip(),
            category=row["domain"].strip(),
            requirement=row["requirement"].strip(),
            description=row["description"].strip(),
            priority=row["priority"].strip(),
            domains=domains,
        ))

    gdpr_controls: list[GDPRControl] = []
    for row in _read_csv("gdpr_checklist.csv"):
        ctrl_id = row["id"].strip()
        domains = [
            dk for dk in GDPR_CONTROL_DOMAIN_MAP.get(ctrl_id, [])
            if dk in COMPLIANCE_DOMAIN_KEYS
        ]
        if not domains:
            continue
        gdpr_controls.append(GDPRControl(
            id=ctrl_id,
            control_ref=row["control_ref"].strip(),
            category=row["domain"].strip(),
            requirement=row["requirement"].strip(),
            description=row["description"].strip(),
            priority=row["priority"].strip(),
            domains=domains,
        ))

    iso27001_controls: list[ISO27001Control] = []
    for row in _read_csv("iso27001_checklist.csv"):
        ctrl_id = row["id"].strip()
        domains = [
            dk for dk in ISO27001_CONTROL_DOMAIN_MAP.get(ctrl_id, [])
            if dk in COMPLIANCE_DOMAIN_KEYS
        ]
        if not domains:
            continue
        iso27001_controls.append(ISO27001Control(
            id=ctrl_id,
            control_ref=row["control_ref"].strip(),
            category=row["domain"].strip(),
            requirement=row["requirement"].strip(),
            description=row["description"].strip(),
            priority=row["priority"].strip(),
            domains=domains,
        ))

    return soc2_controls, gdpr_controls, iso27001_controls
