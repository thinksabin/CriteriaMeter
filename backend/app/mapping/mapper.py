"""
Builds the unified cross-framework control mapping.

Supply-chain domains (8):   group SLSA v1.2 and OWASP ASVS 5.0 controls.
Compliance domains (10):    group SOC 2, GDPR, and ISO 27001:2022 controls
                            around shared security and privacy concerns.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.mapping.domains import COMPLIANCE_DOMAINS, DOMAINS
from app.mapping.loaders.compliance_csv import load_compliance_controls
from app.mapping.loaders.owasp_asvs import load_owasp_controls
from app.mapping.loaders.slsa import load_slsa_controls
from app.mapping.models import (
    ControlDomain,
    GDPRControl,
    ISO27001Control,
    OWASPControl,
    SLSAControl,
    SOC2Control,
    UnifiedMapping,
)

_ALL_DOMAINS = DOMAINS + COMPLIANCE_DOMAINS


def build_mapping() -> UnifiedMapping:
    slsa_controls: list[SLSAControl] = load_slsa_controls()
    owasp_controls: list[OWASPControl] = load_owasp_controls()
    soc2_controls, gdpr_controls, iso27001_controls = load_compliance_controls()

    # ── Index supply-chain controls by domain key ─────────────────────────────
    slsa_by_domain: dict[str, list[SLSAControl]] = {d["key"]: [] for d in DOMAINS}
    owasp_by_domain: dict[str, list[OWASPControl]] = {d["key"]: [] for d in DOMAINS}

    for ctrl in slsa_controls:
        for dk in ctrl.domains:
            if dk in slsa_by_domain:
                slsa_by_domain[dk].append(ctrl)

    for ctrl in owasp_controls:
        for dk in ctrl.domains:
            if dk in owasp_by_domain:
                owasp_by_domain[dk].append(ctrl)

    # ── Index compliance controls by domain key ───────────────────────────────
    soc2_by_domain: dict[str, list[SOC2Control]] = {d["key"]: [] for d in COMPLIANCE_DOMAINS}
    gdpr_by_domain: dict[str, list[GDPRControl]] = {d["key"]: [] for d in COMPLIANCE_DOMAINS}
    iso_by_domain: dict[str, list[ISO27001Control]] = {d["key"]: [] for d in COMPLIANCE_DOMAINS}

    for ctrl in soc2_controls:
        for dk in ctrl.domains:
            if dk in soc2_by_domain:
                soc2_by_domain[dk].append(ctrl)

    for ctrl in gdpr_controls:
        for dk in ctrl.domains:
            if dk in gdpr_by_domain:
                gdpr_by_domain[dk].append(ctrl)

    for ctrl in iso27001_controls:
        for dk in ctrl.domains:
            if dk in iso_by_domain:
                iso_by_domain[dk].append(ctrl)

    # ── Assemble ControlDomain objects ────────────────────────────────────────
    domains_out: list[ControlDomain] = []
    for d in _ALL_DOMAINS:
        key = d["key"]
        is_compliance = key.startswith("comp_")

        if is_compliance:
            soc2 = soc2_by_domain.get(key, [])
            gdpr = gdpr_by_domain.get(key, [])
            iso27001 = iso_by_domain.get(key, [])
            if not soc2 and not gdpr and not iso27001:
                continue
            domains_out.append(ControlDomain(
                key=key,
                label=d["label"],
                description=d["description"],
                soc2_controls=soc2,
                gdpr_controls=gdpr,
                iso27001_controls=iso27001,
            ))
        else:
            slsa = slsa_by_domain.get(key, [])
            owasp = owasp_by_domain.get(key, [])
            if not slsa and not owasp:
                continue
            domains_out.append(ControlDomain(
                key=key,
                label=d["label"],
                description=d["description"],
                slsa_controls=slsa,
                owasp_controls=owasp,
            ))

    return UnifiedMapping(
        generated_at=datetime.now(timezone.utc).isoformat(),
        frameworks=["SLSA v1.2", "OWASP ASVS 5.0", "SOC 2", "GDPR", "ISO 27001:2022"],
        sources={
            "SLSA v1.2": "dataset/checklist_SLSAv1.2.txt",
            "OWASP ASVS 5.0": "dataset/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv",
            "SOC 2": "dataset/soc2_checklist.csv",
            "GDPR": "dataset/gdpr_checklist.csv",
            "ISO 27001:2022": "dataset/iso27001_checklist.csv",
        },
        domain_count=len(domains_out),
        slsa_control_count=len(slsa_controls),
        owasp_control_count=len(owasp_controls),
        soc2_control_count=len(soc2_controls),
        gdpr_control_count=len(gdpr_controls),
        iso27001_control_count=len(iso27001_controls),
        domains=domains_out,
    )
