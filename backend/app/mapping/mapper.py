"""
Builds the unified cross-framework control mapping.

Each control domain groups the SLSA v1.2 requirements and the OWASP ASVS 5.0
requirements that address the same security concern.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.mapping.domains import DOMAINS
from app.mapping.loaders.owasp_asvs import load_owasp_controls
from app.mapping.loaders.slsa import load_slsa_controls
from app.mapping.models import ControlDomain, OWASPControl, SLSAControl, UnifiedMapping


def build_mapping() -> UnifiedMapping:
    slsa_controls: list[SLSAControl] = load_slsa_controls()
    owasp_controls: list[OWASPControl] = load_owasp_controls()

    # Index controls by domain key
    slsa_by_domain: dict[str, list[SLSAControl]] = {d["key"]: [] for d in DOMAINS}
    owasp_by_domain: dict[str, list[OWASPControl]] = {d["key"]: [] for d in DOMAINS}

    for ctrl in slsa_controls:
        for domain_key in ctrl.domains:
            if domain_key in slsa_by_domain:
                slsa_by_domain[domain_key].append(ctrl)

    for ctrl in owasp_controls:
        for domain_key in ctrl.domains:
            if domain_key in owasp_by_domain:
                owasp_by_domain[domain_key].append(ctrl)

    domains: list[ControlDomain] = []
    for d in DOMAINS:
        key = d["key"]
        slsa = slsa_by_domain[key]
        owasp = owasp_by_domain[key]

        # Only include domains that have at least one control from either framework
        if not slsa and not owasp:
            continue

        domains.append(
            ControlDomain(
                key=key,
                label=d["label"],
                description=d["description"],
                slsa_controls=slsa,
                owasp_controls=owasp,
            )
        )

    return UnifiedMapping(
        generated_at=datetime.now(timezone.utc).isoformat(),
        frameworks=["SLSA v1.2", "OWASP ASVS 5.0"],
        sources={
            "SLSA v1.2": "dataset/checklist_SLSAv1.2.txt",
            "OWASP ASVS 5.0": "dataset/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv",
        },
        domain_count=len(domains),
        slsa_control_count=len(slsa_controls),
        owasp_control_count=len(owasp_controls),
        domains=domains,
    )
