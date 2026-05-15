"""
Mapping API — serves the unified cross-framework control mapping.

Endpoints
---------
GET  /api/mapping/datasets        List available datasets with metadata.
POST /api/mapping/compare         Return mapping filtered to selected datasets.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/mapping", tags=["mapping"])

# ---------------------------------------------------------------------------
# Dataset registry
# ---------------------------------------------------------------------------

DATASET_REGISTRY: dict[str, dict] = {
    "slsa_v1.2": {
        "id": "slsa_v1.2",
        "label": "SLSA v1.2",
        "description": (
            "Supply-chain Levels for Software Artifacts, Build Track. "
            "Defines three levels (L1–L3) of provenance and build-hardening requirements."
        ),
        "source_file": "dataset/checklist_SLSAv1.2.txt",
        "version": "1.2",
        "control_count": 26,
    },
    "owasp_asvs_5.0": {
        "id": "owasp_asvs_5.0",
        "label": "OWASP ASVS 5.0",
        "description": (
            "OWASP Application Security Verification Standard v5.0. "
            "345 requirements across 17 chapters covering web application security."
        ),
        "source_file": "dataset/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv",
        "version": "5.0.0",
        "control_count": 208,
    },
    "soc2": {
        "id": "soc2",
        "label": "SOC 2",
        "description": (
            "AICPA Trust Services Criteria (2017, incl. 2022 points of focus). "
            "51 criteria across Common Criteria, Availability, Confidentiality, "
            "Processing Integrity, and Privacy categories."
        ),
        "source_file": "dataset/soc2_checklist.csv",
        "version": "2017 (2022 PoF)",
        "control_count": 51,
    },
    "gdpr": {
        "id": "gdpr",
        "label": "GDPR",
        "description": (
            "EU General Data Protection Regulation. "
            "46 requirements covering lawful processing, data subject rights, "
            "security, breach notification, and international transfers."
        ),
        "source_file": "dataset/gdpr_checklist.csv",
        "version": "2018",
        "control_count": 46,
    },
    "iso27001": {
        "id": "iso27001",
        "label": "ISO 27001:2022",
        "description": (
            "ISO/IEC 27001:2022 Information Security Management System standard. "
            "116 controls across management clauses and Annex A technical controls."
        ),
        "source_file": "dataset/iso27001_checklist.csv",
        "version": "2022",
        "control_count": 116,
    },
}


# ---------------------------------------------------------------------------
# Unified mapping loader (cached — file is read once per process lifetime)
# ---------------------------------------------------------------------------

def _mapping_path() -> Path:
    return Path(__file__).resolve().parents[1] / "mapping" / "output" / "unified_mapping.json"


@lru_cache(maxsize=1)
def _load_unified_mapping() -> dict:
    path = _mapping_path()
    if not path.exists():
        raise FileNotFoundError(
            f"unified_mapping.json not found at {path}. "
            "Run: cd backend && python -m app.mapping.run_mapping"
        )
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class DatasetInfo(BaseModel):
    id: str
    label: str
    description: str
    source_file: str
    version: str
    control_count: int


class DatasetsResponse(BaseModel):
    datasets: list[DatasetInfo]


class CompareRequest(BaseModel):
    datasets: list[str]


class SLSAControlOut(BaseModel):
    id: str
    level: str
    section: str
    text: str
    description: str


class OWASPControlOut(BaseModel):
    id: str
    chapter_id: str
    chapter_name: str
    section_id: str
    section_name: str
    req_description: str
    level: int


class SOC2ControlOut(BaseModel):
    id: str
    control_ref: str
    category: str
    requirement: str
    description: str
    priority: str


class GDPRControlOut(BaseModel):
    id: str
    control_ref: str
    category: str
    requirement: str
    description: str
    priority: str


class ISO27001ControlOut(BaseModel):
    id: str
    control_ref: str
    category: str
    requirement: str
    description: str
    priority: str


class MappedDomainOut(BaseModel):
    key: str
    label: str
    description: str
    slsa_controls: list[SLSAControlOut]
    owasp_controls: list[OWASPControlOut]
    soc2_controls: list[SOC2ControlOut]
    gdpr_controls: list[GDPRControlOut]
    iso27001_controls: list[ISO27001ControlOut]


class CompareResponse(BaseModel):
    selected_datasets: list[str]
    domain_count: int
    total_slsa_controls: int
    total_owasp_controls: int
    total_soc2_controls: int
    total_gdpr_controls: int
    total_iso27001_controls: int
    domains: list[MappedDomainOut]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/datasets", response_model=DatasetsResponse)
def list_datasets() -> DatasetsResponse:
    return DatasetsResponse(
        datasets=[DatasetInfo(**v) for v in DATASET_REGISTRY.values()]
    )


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    if not request.datasets:
        raise HTTPException(status_code=422, detail="Select at least one dataset.")

    unknown = [d for d in request.datasets if d not in DATASET_REGISTRY]
    if unknown:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown dataset id(s): {', '.join(unknown)}. "
                   f"Valid ids: {', '.join(DATASET_REGISTRY)}",
        )

    include_slsa = "slsa_v1.2" in request.datasets
    include_owasp = "owasp_asvs_5.0" in request.datasets
    include_soc2 = "soc2" in request.datasets
    include_gdpr = "gdpr" in request.datasets
    include_iso27001 = "iso27001" in request.datasets

    try:
        raw = _load_unified_mapping()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    domains_out: list[MappedDomainOut] = []
    total_slsa = total_owasp = total_soc2 = total_gdpr = total_iso27001 = 0

    for domain in raw["domains"]:
        is_compliance = domain["key"].startswith("comp_")

        slsa_controls: list[SLSAControlOut] = []
        owasp_controls: list[OWASPControlOut] = []
        soc2_controls: list[SOC2ControlOut] = []
        gdpr_controls: list[GDPRControlOut] = []
        iso27001_controls: list[ISO27001ControlOut] = []

        if not is_compliance:
            if include_slsa:
                slsa_controls = [
                    SLSAControlOut(
                        id=c["id"], level=c["level"], section=c["section"],
                        text=c["text"], description=c["description"],
                    )
                    for c in domain["slsa_controls"]
                ]
            if include_owasp:
                owasp_controls = [
                    OWASPControlOut(
                        id=c["id"], chapter_id=c["chapter_id"],
                        chapter_name=c["chapter_name"], section_id=c["section_id"],
                        section_name=c["section_name"],
                        req_description=c["req_description"], level=c["level"],
                    )
                    for c in domain["owasp_controls"]
                ]
        else:
            if include_soc2:
                soc2_controls = [
                    SOC2ControlOut(
                        id=c["id"], control_ref=c["control_ref"],
                        category=c["category"], requirement=c["requirement"],
                        description=c["description"], priority=c["priority"],
                    )
                    for c in domain["soc2_controls"]
                ]
            if include_gdpr:
                gdpr_controls = [
                    GDPRControlOut(
                        id=c["id"], control_ref=c["control_ref"],
                        category=c["category"], requirement=c["requirement"],
                        description=c["description"], priority=c["priority"],
                    )
                    for c in domain["gdpr_controls"]
                ]
            if include_iso27001:
                iso27001_controls = [
                    ISO27001ControlOut(
                        id=c["id"], control_ref=c["control_ref"],
                        category=c["category"], requirement=c["requirement"],
                        description=c["description"], priority=c["priority"],
                    )
                    for c in domain["iso27001_controls"]
                ]

        if not any([slsa_controls, owasp_controls, soc2_controls,
                    gdpr_controls, iso27001_controls]):
            continue

        total_slsa += len(slsa_controls)
        total_owasp += len(owasp_controls)
        total_soc2 += len(soc2_controls)
        total_gdpr += len(gdpr_controls)
        total_iso27001 += len(iso27001_controls)

        domains_out.append(MappedDomainOut(
            key=domain["key"],
            label=domain["label"],
            description=domain["description"],
            slsa_controls=slsa_controls,
            owasp_controls=owasp_controls,
            soc2_controls=soc2_controls,
            gdpr_controls=gdpr_controls,
            iso27001_controls=iso27001_controls,
        ))

    return CompareResponse(
        selected_datasets=[DATASET_REGISTRY[d]["label"] for d in request.datasets],
        domain_count=len(domains_out),
        total_slsa_controls=total_slsa,
        total_owasp_controls=total_owasp,
        total_soc2_controls=total_soc2,
        total_gdpr_controls=total_gdpr,
        total_iso27001_controls=total_iso27001,
        domains=domains_out,
    )
