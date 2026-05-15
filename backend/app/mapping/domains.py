"""
Control domain taxonomy and mapping rules.

Each domain represents a security concern that SLSA v1.2 and OWASP ASVS 5.0
both address, allowing controls from both frameworks to be compared side-by-side.

OWASP rules are applied at the section level (section_id prefix match) so that
the mapper stays accurate without hard-coding every individual requirement ID.
"""
from __future__ import annotations

# ── Domain definitions ────────────────────────────────────────────────────────

DOMAINS: list[dict] = [
    {
        "key": "build_process_integrity",
        "label": "Build Process Integrity",
        "description": (
            "Ensuring builds are performed consistently, reproducibly, and on "
            "auditable platforms, with configuration managed as code."
        ),
    },
    {
        "key": "provenance_and_traceability",
        "label": "Provenance and Traceability",
        "description": (
            "Generating, distributing, and verifying attestations that describe "
            "how software artefacts were produced, including inputs and the build "
            "platform identity."
        ),
    },
    {
        "key": "cryptography_and_signing",
        "label": "Cryptography and Signing",
        "description": (
            "Using cryptographic signatures and algorithms to authenticate "
            "provenance, protect artefact integrity, and verify identity."
        ),
    },
    {
        "key": "secret_management",
        "label": "Secret Management",
        "description": (
            "Protecting signing keys, credentials, and other secret material so "
            "that they cannot be accessed or exfiltrated by build steps or "
            "unauthorised parties."
        ),
    },
    {
        "key": "build_isolation",
        "label": "Build Isolation",
        "description": (
            "Preventing cross-build influence through ephemeral environments, "
            "memory isolation, cache integrity, and restricting access to "
            "platform-level resources."
        ),
    },
    {
        "key": "dependency_management",
        "label": "Dependency Management",
        "description": (
            "Tracking, verifying, and securing third-party components and build "
            "dependencies to reduce supply-chain risk."
        ),
    },
    {
        "key": "access_control_and_authorization",
        "label": "Access Control and Authorization",
        "description": (
            "Controlling who can trigger builds, access build infrastructure, "
            "and modify provenance, using authentication and least-privilege "
            "authorization."
        ),
    },
    {
        "key": "audit_logging",
        "label": "Audit Logging",
        "description": (
            "Recording security-relevant events — including build invocations, "
            "signing actions, and validation results — in tamper-evident, "
            "structured logs."
        ),
    },
]

DOMAIN_KEYS: set[str] = {d["key"] for d in DOMAINS}


# ── SLSA control → domain mapping ────────────────────────────────────────────
# Keyed by the SLSA control id (matches slsaChecklist.ts ids).

SLSA_DOMAIN_MAP: dict[str, list[str]] = {
    # L1 — Software Producer
    "l1-sp-1": ["build_process_integrity"],
    "l1-sp-2": ["build_process_integrity"],
    "l1-sp-3": ["provenance_and_traceability"],
    # L1 — Build Platform
    "l1-bp-1": ["provenance_and_traceability"],
    # L1 — Provenance Content
    "l1-prov-1": ["provenance_and_traceability"],
    "l1-prov-2": ["provenance_and_traceability"],
    "l1-prov-3": ["provenance_and_traceability"],

    # L2 — Software Producer
    "l2-sp-1": ["build_process_integrity"],
    "l2-sp-2": ["provenance_and_traceability", "cryptography_and_signing"],
    # L2 — Build Platform
    "l2-bp-1": ["cryptography_and_signing"],
    "l2-bp-2": ["access_control_and_authorization"],
    "l2-bp-3": ["build_process_integrity", "access_control_and_authorization"],
    # L2 — Consumer
    "l2-con-1": ["cryptography_and_signing"],
    # L2 — Provenance Authenticity
    "l2-prov-1": ["cryptography_and_signing"],
    "l2-prov-2": ["audit_logging", "cryptography_and_signing"],

    # L3 — Build Platform
    "l3-bp-1": ["build_isolation"],
    "l3-bp-2": ["secret_management"],
    "l3-bp-3": ["provenance_and_traceability", "access_control_and_authorization"],
    "l3-bp-4": ["secret_management"],
    # L3 — Isolation Strength
    "l3-iso-1": ["secret_management", "build_isolation"],
    "l3-iso-2": ["build_isolation"],
    "l3-iso-3": ["build_isolation"],
    "l3-iso-4": ["build_isolation"],
    "l3-iso-5": ["provenance_and_traceability"],
    # L3 — Provenance Completeness
    "l3-comp-1": ["provenance_and_traceability"],
    "l3-comp-2": ["dependency_management"],
}


# ── OWASP section → domain mapping ───────────────────────────────────────────
# section_id prefix → list of domain keys.
# A requirement inherits all domains from its section.

OWASP_SECTION_DOMAIN_MAP: dict[str, list[str]] = {
    # V11 — Cryptography
    "V11.1": ["cryptography_and_signing"],
    "V11.2": ["cryptography_and_signing"],
    "V11.3": ["cryptography_and_signing"],
    "V11.4": ["cryptography_and_signing"],
    "V11.5": ["cryptography_and_signing", "secret_management"],
    "V11.6": ["cryptography_and_signing"],
    "V11.7": ["secret_management"],

    # V12 — Secure Communication (provenance delivery & signing transport)
    "V12.1": ["provenance_and_traceability"],
    "V12.2": ["provenance_and_traceability"],
    "V12.3": ["provenance_and_traceability"],

    # V13 — Configuration
    "V13.1": ["build_process_integrity"],
    "V13.2": ["build_isolation"],
    "V13.3": ["secret_management"],
    "V13.4": ["secret_management"],

    # V14 — Data Protection
    "V14.1": ["secret_management"],
    "V14.2": ["secret_management"],

    # V15 — Secure Coding and Architecture
    "V15.1": ["build_process_integrity"],
    "V15.2": ["dependency_management"],
    "V15.3": ["build_process_integrity"],
    "V15.4": ["build_isolation"],

    # V16 — Security Logging and Error Handling
    "V16.1": ["audit_logging"],
    "V16.2": ["audit_logging", "provenance_and_traceability"],
    "V16.3": ["audit_logging", "provenance_and_traceability"],
    "V16.4": ["audit_logging"],
    "V16.5": ["audit_logging"],

    # V6 — Authentication (platform access)
    "V6.1": ["access_control_and_authorization"],
    "V6.2": ["access_control_and_authorization"],
    "V6.3": ["access_control_and_authorization"],
    "V6.4": ["access_control_and_authorization"],
    "V6.5": ["access_control_and_authorization"],
    "V6.6": ["access_control_and_authorization"],
    "V6.7": ["cryptography_and_signing", "access_control_and_authorization"],
    "V6.8": ["access_control_and_authorization"],

    # V8 — Authorization
    "V8.1": ["access_control_and_authorization"],
    "V8.2": ["access_control_and_authorization"],
    "V8.3": ["access_control_and_authorization"],
    "V8.4": ["access_control_and_authorization"],

    # V9 — Self-contained Tokens (JWT / JWS signing relevant to provenance)
    "V9.1": ["cryptography_and_signing"],
    "V9.2": ["cryptography_and_signing"],

    # V10 — OAuth and OIDC (build platform identity/access)
    "V10.1": ["access_control_and_authorization"],
    "V10.2": ["access_control_and_authorization"],
    "V10.3": ["access_control_and_authorization"],
    "V10.4": ["access_control_and_authorization"],
    "V10.5": ["access_control_and_authorization"],
    "V10.6": ["access_control_and_authorization"],
    "V10.7": ["access_control_and_authorization"],
}

# Chapters with no meaningful overlap with SLSA (skipped from output)
OWASP_EXCLUDED_CHAPTERS: set[str] = {"V1", "V2", "V3", "V4", "V5", "V7", "V17"}


# ── Compliance bridge domains (SOC 2 · GDPR · ISO 27001) ─────────────────────
# 10 shared security/compliance concerns that span all three frameworks.
# Domain keys use the "comp_" prefix to distinguish from supply-chain domains.

COMPLIANCE_DOMAINS: list[dict] = [
    {
        "key": "comp_governance",
        "label": "Governance & Accountability",
        "description": (
            "Leadership commitment, organisational roles and responsibilities, "
            "policies, awareness training, and accountability structures."
        ),
    },
    {
        "key": "comp_risk",
        "label": "Risk Management",
        "description": (
            "Identification, analysis, and treatment of information security risks, "
            "including Data Protection Impact Assessments and change impact analysis."
        ),
    },
    {
        "key": "comp_access_control",
        "label": "Access Control & Identity",
        "description": (
            "Logical access security, identity lifecycle management, authentication, "
            "privileged access, and access rights governance."
        ),
    },
    {
        "key": "comp_data_protection",
        "label": "Data Protection & Privacy",
        "description": (
            "Lawful processing, data minimisation, purpose limitation, data subject rights, "
            "classification, confidentiality, retention, and cross-border transfers."
        ),
    },
    {
        "key": "comp_security_ops",
        "label": "Security Operations",
        "description": (
            "Vulnerability management, monitoring, change and configuration management, "
            "secure development, malware protection, and processing integrity."
        ),
    },
    {
        "key": "comp_physical",
        "label": "Physical Security",
        "description": (
            "Physical perimeters, entry controls, secure areas, equipment protection, "
            "environmental safeguards, and media handling."
        ),
    },
    {
        "key": "comp_vendor",
        "label": "Vendor & Third-party Management",
        "description": (
            "Due diligence, contractual obligations, and ongoing monitoring of suppliers, "
            "processors, cloud services, and ICT supply-chain partners."
        ),
    },
    {
        "key": "comp_incident",
        "label": "Incident & Breach Management",
        "description": (
            "Detection, assessment, response, notification, evidence collection, and "
            "recovery from information security incidents and personal-data breaches."
        ),
    },
    {
        "key": "comp_audit",
        "label": "Compliance & Audit",
        "description": (
            "Internal and independent audits, monitoring and measurement, management review, "
            "records of processing, and continual improvement."
        ),
    },
    {
        "key": "comp_continuity",
        "label": "Business Continuity & Availability",
        "description": (
            "Capacity planning, backup, redundancy, disaster recovery, ICT readiness, "
            "and tested restoration of information-processing capabilities."
        ),
    },
]

COMPLIANCE_DOMAIN_KEYS: set[str] = {d["key"] for d in COMPLIANCE_DOMAINS}


# ── SOC 2 control → compliance domain map ─────────────────────────────────────

SOC2_CONTROL_DOMAIN_MAP: dict[str, list[str]] = {
    # Control Environment
    "SOC2-CC1.1": ["comp_governance"],
    "SOC2-CC1.2": ["comp_governance"],
    "SOC2-CC1.3": ["comp_governance"],
    "SOC2-CC1.4": ["comp_governance"],
    "SOC2-CC1.5": ["comp_governance"],
    # Communication
    "SOC2-CC2.1": ["comp_governance"],
    "SOC2-CC2.2": ["comp_governance"],
    "SOC2-CC2.3": ["comp_governance"],
    # Risk Assessment
    "SOC2-CC3.1": ["comp_risk"],
    "SOC2-CC3.2": ["comp_risk"],
    "SOC2-CC3.3": ["comp_risk"],
    "SOC2-CC3.4": ["comp_risk"],
    # Monitoring
    "SOC2-CC4.1": ["comp_audit", "comp_security_ops"],
    # CC4.2: deficiencies must be communicated to management and the board —
    # that escalation obligation is a governance responsibility, not audit alone.
    "SOC2-CC4.2": ["comp_audit", "comp_governance"],
    # Control Activities
    "SOC2-CC5.1": ["comp_governance", "comp_risk"],
    "SOC2-CC5.2": ["comp_governance", "comp_security_ops"],
    "SOC2-CC5.3": ["comp_governance"],
    # Logical Access
    # CC6.1: covers logical access security SOFTWARE, INFRASTRUCTURE, and
    # ARCHITECTURES — the architecture and infrastructure elements place this
    # squarely in security operations as well as access control.
    "SOC2-CC6.1": ["comp_access_control", "comp_security_ops"],
    "SOC2-CC6.2": ["comp_access_control"],
    "SOC2-CC6.3": ["comp_access_control"],
    "SOC2-CC6.4": ["comp_physical"],
    "SOC2-CC6.5": ["comp_access_control"],
    "SOC2-CC6.6": ["comp_access_control", "comp_security_ops"],
    "SOC2-CC6.7": ["comp_data_protection", "comp_access_control"],
    "SOC2-CC6.8": ["comp_security_ops"],
    # System Operations
    "SOC2-CC7.1": ["comp_security_ops"],
    "SOC2-CC7.2": ["comp_security_ops"],
    "SOC2-CC7.3": ["comp_security_ops", "comp_incident"],
    "SOC2-CC7.4": ["comp_incident"],
    "SOC2-CC7.5": ["comp_incident", "comp_continuity"],
    # Change Management
    "SOC2-CC8.1": ["comp_security_ops"],
    # Risk Mitigation / Vendor
    "SOC2-CC9.1": ["comp_risk"],
    "SOC2-CC9.2": ["comp_vendor"],
    # Availability
    "SOC2-A1.1": ["comp_continuity"],
    "SOC2-A1.2": ["comp_continuity"],
    "SOC2-A1.3": ["comp_continuity"],
    # Confidentiality
    "SOC2-C1.1": ["comp_data_protection"],
    "SOC2-C1.2": ["comp_data_protection"],
    # Processing Integrity
    "SOC2-PI1.1": ["comp_security_ops"],
    "SOC2-PI1.2": ["comp_security_ops"],
    "SOC2-PI1.3": ["comp_security_ops"],
    "SOC2-PI1.4": ["comp_security_ops"],
    "SOC2-PI1.5": ["comp_security_ops"],
    # Privacy
    "SOC2-P1.1": ["comp_data_protection"],
    "SOC2-P2.1": ["comp_data_protection"],
    "SOC2-P3.1": ["comp_data_protection"],
    "SOC2-P4.1": ["comp_data_protection"],
    "SOC2-P5.1": ["comp_data_protection"],
    "SOC2-P6.1": ["comp_data_protection", "comp_vendor"],
    "SOC2-P7.1": ["comp_data_protection"],
    "SOC2-P8.1": ["comp_audit", "comp_data_protection"],
}


# ── GDPR control → compliance domain map ──────────────────────────────────────

GDPR_CONTROL_DOMAIN_MAP: dict[str, list[str]] = {
    # Principles (Art. 5)
    "GDPR-A5.1a": ["comp_data_protection"],
    "GDPR-A5.1b": ["comp_data_protection"],
    "GDPR-A5.1c": ["comp_data_protection"],
    "GDPR-A5.1d": ["comp_data_protection"],
    "GDPR-A5.1e": ["comp_data_protection"],
    "GDPR-A5.1f": ["comp_data_protection", "comp_security_ops"],
    "GDPR-A5.2":  ["comp_governance", "comp_audit"],
    # Lawful Basis
    "GDPR-A6":    ["comp_data_protection"],
    # Consent
    "GDPR-A7":    ["comp_data_protection"],
    "GDPR-A8":    ["comp_data_protection"],
    # Special categories / Criminal data
    "GDPR-A9":    ["comp_data_protection"],
    "GDPR-A10":   ["comp_data_protection"],
    # Rights
    "GDPR-A12":   ["comp_data_protection"],
    "GDPR-A13":   ["comp_data_protection"],
    "GDPR-A14":   ["comp_data_protection"],
    "GDPR-A15":   ["comp_data_protection"],
    "GDPR-A16":   ["comp_data_protection"],
    "GDPR-A17":   ["comp_data_protection"],
    "GDPR-A18":   ["comp_data_protection"],
    "GDPR-A19":   ["comp_data_protection"],
    "GDPR-A20":   ["comp_data_protection"],
    "GDPR-A21":   ["comp_data_protection"],
    "GDPR-A22":   ["comp_data_protection"],
    # Controller responsibility / DPO / Representative
    # A24: controllers must DEMONSTRATE compliance (Art.5(2)) — that demonstration
    # is an audit obligation as much as a governance one.
    "GDPR-A24":   ["comp_governance", "comp_audit"],
    # A25: Privacy by Design requires both TECHNICAL measures (security ops) and
    # ORGANISATIONAL measures (governance) — not just data protection and risk.
    "GDPR-A25":   ["comp_data_protection", "comp_risk", "comp_governance", "comp_security_ops"],
    # A26: Joint controllers are CO-DATA CONTROLLERS, not vendors or processors.
    # They share accountability for lawful processing — this is a governance and
    # accountability obligation, not a third-party / supply-chain matter.
    "GDPR-A26":   ["comp_governance"],
    "GDPR-A27":   ["comp_governance"],
    # A28: Processor contracts must include mandatory audit rights; controllers are
    # obliged to audit processor compliance — comp_audit is required here.
    "GDPR-A28":   ["comp_vendor", "comp_audit"],
    # Records
    "GDPR-A30":   ["comp_audit"],
    # A32: Art.32 explicitly mandates (a) confidentiality/integrity/availability,
    # (b) RESILIENCE of processing systems, and (c) the ability to RESTORE
    # availability in a timely manner — resilience and restoration are continuity
    # obligations and must appear under comp_continuity.
    "GDPR-A32":   ["comp_security_ops", "comp_access_control", "comp_data_protection",
                   "comp_continuity"],
    # Breach notification
    "GDPR-A33":   ["comp_incident"],
    # A34: The decision to notify data subjects involves assessing "likely high risk"
    # — a threshold judgement requiring board/DPO-level accountability (governance).
    "GDPR-A34":   ["comp_incident", "comp_governance"],
    # DPIA
    # A35: DPIAs must be carried out PRIOR to processing and require DPO consultation
    # and controller sign-off — a governance obligation alongside risk management.
    "GDPR-A35":   ["comp_risk", "comp_governance"],
    "GDPR-A36":   ["comp_risk"],
    # DPO
    "GDPR-A37":   ["comp_governance"],
    "GDPR-A38":   ["comp_governance"],
    "GDPR-A39":   ["comp_governance", "comp_data_protection"],
    # Transfers
    "GDPR-A44":   ["comp_data_protection"],
    "GDPR-A45":   ["comp_data_protection"],
    # A46: Standard Contractual Clauses and Binding Corporate Rules govern the
    # processor and sub-processor transfer chain — comp_vendor is required.
    "GDPR-A46":   ["comp_data_protection", "comp_vendor"],
    # A47: BCRs are group-wide governance instruments requiring DPA approval;
    # they represent an organisational accountability commitment.
    "GDPR-A47":   ["comp_data_protection", "comp_governance"],
    "GDPR-A49":   ["comp_data_protection"],
    # Training / Vendor / Cookies / Marketing
    # TRN: training completion records are compliance evidence — comp_audit required.
    "GDPR-TRN":   ["comp_governance", "comp_audit"],
    "GDPR-VEN":   ["comp_vendor"],
    "GDPR-COK":   ["comp_data_protection"],
    "GDPR-MKT":   ["comp_data_protection"],
}


# ── ISO 27001 control → compliance domain map ─────────────────────────────────

ISO27001_CONTROL_DOMAIN_MAP: dict[str, list[str]] = {
    # Context
    "ISO-4.1": ["comp_governance"], "ISO-4.2": ["comp_governance"],
    "ISO-4.3": ["comp_governance"], "ISO-4.4": ["comp_governance"],
    # Leadership
    "ISO-5.1": ["comp_governance"], "ISO-5.2": ["comp_governance"],
    "ISO-5.3": ["comp_governance"],
    # Planning
    "ISO-6.1": ["comp_risk"],
    "ISO-6.2": ["comp_governance", "comp_risk"],
    "ISO-6.3": ["comp_risk", "comp_security_ops"],
    # Support
    "ISO-7.1": ["comp_governance"], "ISO-7.2": ["comp_governance"],
    "ISO-7.3": ["comp_governance"], "ISO-7.4": ["comp_governance"],
    "ISO-7.5": ["comp_governance", "comp_audit"],
    # Operation
    "ISO-8.1": ["comp_security_ops"],
    "ISO-8.2": ["comp_risk"], "ISO-8.3": ["comp_risk"],
    # Performance
    "ISO-9.1": ["comp_audit"], "ISO-9.2": ["comp_audit"], "ISO-9.3": ["comp_audit"],
    # Improvement
    "ISO-10.1": ["comp_audit"], "ISO-10.2": ["comp_audit"],
    # Organisational (A5)
    "ISO-A5.1":  ["comp_governance"],
    "ISO-A5.2":  ["comp_governance"],
    "ISO-A5.3":  ["comp_governance"],
    "ISO-A5.4":  ["comp_governance"],
    # A5.5: Contact with authorities is a primary incident response obligation
    # (regulatory notification, law enforcement liaison) — not just governance.
    "ISO-A5.5":  ["comp_governance", "comp_incident"],
    "ISO-A5.6":  ["comp_governance"],
    "ISO-A5.7":  ["comp_risk", "comp_security_ops"],
    "ISO-A5.8":  ["comp_governance", "comp_risk"],
    "ISO-A5.9":  ["comp_governance", "comp_data_protection"],
    "ISO-A5.10": ["comp_data_protection", "comp_governance"],
    # A5.11: Return of assets must immediately trigger access revocation and
    # media sanitisation — access control lifecycle is the primary risk here.
    "ISO-A5.11": ["comp_governance", "comp_access_control"],
    "ISO-A5.12": ["comp_data_protection"],
    "ISO-A5.13": ["comp_data_protection"],
    "ISO-A5.14": ["comp_data_protection", "comp_vendor"],
    "ISO-A5.15": ["comp_access_control"],
    "ISO-A5.16": ["comp_access_control"],
    "ISO-A5.17": ["comp_access_control"],
    "ISO-A5.18": ["comp_access_control"],
    "ISO-A5.19": ["comp_vendor"],
    "ISO-A5.20": ["comp_vendor"],
    "ISO-A5.21": ["comp_vendor"],
    "ISO-A5.22": ["comp_vendor"],
    # A5.23: Cloud services require active security monitoring, configuration
    # hardening, and patch management — security operations coverage is required.
    "ISO-A5.23": ["comp_vendor", "comp_security_ops"],
    # A5.24: Incident management planning requires management commitment, defined
    # roles and authority, and resource allocation — a governance obligation.
    "ISO-A5.24": ["comp_incident", "comp_governance"],
    "ISO-A5.25": ["comp_incident"],
    "ISO-A5.26": ["comp_incident"],
    "ISO-A5.27": ["comp_incident"],
    "ISO-A5.28": ["comp_incident"],
    "ISO-A5.29": ["comp_continuity"],
    "ISO-A5.30": ["comp_continuity"],
    "ISO-A5.31": ["comp_audit", "comp_governance"],
    "ISO-A5.32": ["comp_audit", "comp_governance"],
    "ISO-A5.33": ["comp_audit", "comp_data_protection"],
    "ISO-A5.34": ["comp_data_protection"],
    "ISO-A5.35": ["comp_audit"],
    "ISO-A5.36": ["comp_audit"],
    "ISO-A5.37": ["comp_governance", "comp_security_ops"],
    # People (A6)
    # A6.1: Pre-employment screening is a prerequisite for granting access,
    # especially privileged access — the access control lifecycle starts here.
    "ISO-A6.1": ["comp_governance", "comp_access_control"],
    "ISO-A6.2": ["comp_governance"],
    "ISO-A6.3": ["comp_governance"],
    "ISO-A6.4": ["comp_governance"],
    # A6.5: Offboarding access revocation is the single highest-risk access
    # control activity — the leading cause of insider threat incidents. Mapping
    # only to governance misses the primary technical obligation.
    "ISO-A6.5": ["comp_governance", "comp_access_control"],
    "ISO-A6.6": ["comp_governance", "comp_data_protection"],
    # A6.7: Remote working mandates VPN, MFA, and least-privilege remote access
    # policies — access control is a primary technical control here.
    "ISO-A6.7": ["comp_security_ops", "comp_access_control"],
    "ISO-A6.8": ["comp_incident"],
    # Physical (A7)
    "ISO-A7.1":  ["comp_physical"], "ISO-A7.2":  ["comp_physical"],
    "ISO-A7.3":  ["comp_physical"], "ISO-A7.4":  ["comp_physical"],
    # A7.5: Protecting against physical and environmental threats (fire, flood,
    # power failure) is a business continuity risk, not physical security alone.
    "ISO-A7.5":  ["comp_physical", "comp_continuity"],
    "ISO-A7.6":  ["comp_physical"],
    # A7.7: Clear desk / clear screen is a physical security discipline — it has
    # no direct relationship to logical access control systems. Removed comp_access_control.
    "ISO-A7.7":  ["comp_physical"],
    "ISO-A7.8":  ["comp_physical"],
    # A7.9: Security of assets off-premises is primarily a DATA LEAKAGE risk
    # (confidential data on laptops, USB drives, phones). Access control is not
    # the primary concern — replaced comp_access_control with comp_data_protection.
    "ISO-A7.9":  ["comp_physical", "comp_data_protection"],
    "ISO-A7.10": ["comp_physical", "comp_data_protection"],
    "ISO-A7.11": ["comp_physical", "comp_continuity"],
    "ISO-A7.12": ["comp_physical"], "ISO-A7.13": ["comp_physical"],
    "ISO-A7.14": ["comp_physical", "comp_data_protection"],
    # Technological (A8)
    "ISO-A8.1":  ["comp_security_ops", "comp_access_control"],
    "ISO-A8.2":  ["comp_access_control"],
    "ISO-A8.3":  ["comp_access_control", "comp_data_protection"],
    "ISO-A8.4":  ["comp_access_control"],
    "ISO-A8.5":  ["comp_access_control"],
    "ISO-A8.6":  ["comp_continuity", "comp_security_ops"],
    "ISO-A8.7":  ["comp_security_ops"],
    "ISO-A8.8":  ["comp_security_ops", "comp_risk"],
    "ISO-A8.9":  ["comp_security_ops"],
    "ISO-A8.10": ["comp_data_protection"],
    "ISO-A8.11": ["comp_data_protection"],
    "ISO-A8.12": ["comp_data_protection"],
    "ISO-A8.13": ["comp_continuity"],
    "ISO-A8.14": ["comp_continuity"],
    "ISO-A8.15": ["comp_security_ops", "comp_audit"],
    "ISO-A8.16": ["comp_security_ops", "comp_audit"],
    # A8.17: Accurate clock synchronisation is essential for audit log integrity
    # and the admissibility of digital forensic evidence — comp_audit required.
    "ISO-A8.17": ["comp_security_ops", "comp_audit"],
    "ISO-A8.18": ["comp_security_ops", "comp_access_control"],
    "ISO-A8.19": ["comp_security_ops"],
    "ISO-A8.20": ["comp_security_ops"],
    "ISO-A8.21": ["comp_security_ops"],
    "ISO-A8.22": ["comp_security_ops"],
    "ISO-A8.23": ["comp_security_ops"],
    "ISO-A8.24": ["comp_data_protection", "comp_security_ops"],
    "ISO-A8.25": ["comp_security_ops"],
    "ISO-A8.26": ["comp_security_ops"],
    "ISO-A8.27": ["comp_security_ops"],
    "ISO-A8.28": ["comp_security_ops"],
    "ISO-A8.29": ["comp_security_ops", "comp_audit"],
    "ISO-A8.30": ["comp_vendor", "comp_security_ops"],
    "ISO-A8.31": ["comp_security_ops"],
    "ISO-A8.32": ["comp_security_ops"],
    # A8.33: Test information must be anonymised or pseudonymised — GDPR Art.25
    # and ISO 27001:2022 both treat this as a data protection obligation.
    "ISO-A8.33": ["comp_security_ops", "comp_data_protection"],
    "ISO-A8.34": ["comp_audit", "comp_security_ops"],
}
