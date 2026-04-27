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
# Dataset registry — add a new entry here when a new dataset is ingested.
# ---------------------------------------------------------------------------

DATASET_REGISTRY: dict[str, dict] = {
    "slsa_v1.2": {
        "id": "slsa_v1.2",
        "label": "SLSA v1.2",
        "framework_key": "SLSA v1.2",
        "description": (
            "Supply-chain Levels for Software Artifacts, Build Track. "
            "Defines three levels (L1-L3) of provenance and build-hardening requirements."
        ),
        "source_file": "dataset/checklist_SLSAv1.2.txt",
        "version": "1.2",
        "control_count": 26,
    },
    "owasp_asvs_5.0": {
        "id": "owasp_asvs_5.0",
        "label": "OWASP ASVS 5.0",
        "framework_key": "OWASP ASVS 5.0",
        "description": (
            "OWASP Application Security Verification Standard v5.0. "
            "345 requirements across 17 chapters covering web application security."
        ),
        "source_file": "dataset/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv",
        "version": "5.0.0",
        "control_count": 208,  # controls mapped to SLSA-relevant domains
    },
}


# ---------------------------------------------------------------------------
# Unified mapping loader (cached — file is read once per process lifetime)
# ---------------------------------------------------------------------------

def _mapping_path() -> Path:
    # backend/app/api/mapping.py → backend/app/ → backend/app/mapping/output/
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
# Pydantic models
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
    datasets: list[str]  # list of dataset ids, e.g. ["slsa_v1.2", "owasp_asvs_5.0"]


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


class MappedDomainOut(BaseModel):
    key: str
    label: str
    description: str
    slsa_controls: list[SLSAControlOut]
    owasp_controls: list[OWASPControlOut]


class CompareResponse(BaseModel):
    selected_datasets: list[str]          # human-readable labels
    domain_count: int
    total_slsa_controls: int
    total_owasp_controls: int
    domains: list[MappedDomainOut]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/datasets", response_model=DatasetsResponse)
def list_datasets() -> DatasetsResponse:
    """Return the list of datasets available for mapping."""
    return DatasetsResponse(
        datasets=[DatasetInfo(**v) for v in DATASET_REGISTRY.values()]
    )


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    """
    Return the unified mapping filtered to the requested datasets.

    At least one dataset must be selected. Both datasets may be selected to
    produce a side-by-side cross-framework comparison.
    """
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

    try:
        raw = _load_unified_mapping()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    domains_out: list[MappedDomainOut] = []
    total_slsa = 0
    total_owasp = 0

    for domain in raw["domains"]:
        slsa_controls: list[SLSAControlOut] = []
        owasp_controls: list[OWASPControlOut] = []

        if include_slsa:
            slsa_controls = [
                SLSAControlOut(
                    id=c["id"],
                    level=c["level"],
                    section=c["section"],
                    text=c["text"],
                    description=c["description"],
                )
                for c in domain["slsa_controls"]
            ]

        if include_owasp:
            owasp_controls = [
                OWASPControlOut(
                    id=c["id"],
                    chapter_id=c["chapter_id"],
                    chapter_name=c["chapter_name"],
                    section_id=c["section_id"],
                    section_name=c["section_name"],
                    req_description=c["req_description"],
                    level=c["level"],
                )
                for c in domain["owasp_controls"]
            ]

        # Skip domain if it has no controls for the selected datasets
        if not slsa_controls and not owasp_controls:
            continue

        total_slsa += len(slsa_controls)
        total_owasp += len(owasp_controls)

        domains_out.append(
            MappedDomainOut(
                key=domain["key"],
                label=domain["label"],
                description=domain["description"],
                slsa_controls=slsa_controls,
                owasp_controls=owasp_controls,
            )
        )

    selected_labels = [DATASET_REGISTRY[d]["label"] for d in request.datasets]

    return CompareResponse(
        selected_datasets=selected_labels,
        domain_count=len(domains_out),
        total_slsa_controls=total_slsa,
        total_owasp_controls=total_owasp,
        domains=domains_out,
    )
