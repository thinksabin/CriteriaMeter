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
