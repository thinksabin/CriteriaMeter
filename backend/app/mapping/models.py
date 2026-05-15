from __future__ import annotations
from pydantic import BaseModel


class SLSAControl(BaseModel):
    id: str
    framework: str = "SLSA v1.2"
    level: str          # "L1" | "L2" | "L3"
    section: str        # e.g. "Software Producer"
    text: str
    description: str
    domains: list[str]  # control domain keys


class OWASPControl(BaseModel):
    id: str             # req_id, e.g. "V11.2.1"
    framework: str = "OWASP ASVS 5.0"
    chapter_id: str
    chapter_name: str
    section_id: str
    section_name: str
    req_description: str
    level: int          # 1 | 2 | 3
    domains: list[str]


class SOC2Control(BaseModel):
    id: str             # e.g. "SOC2-CC6.1"
    framework: str = "SOC 2"
    control_ref: str    # e.g. "CC6.1"
    category: str       # SOC2 domain name, e.g. "Logical Access"
    requirement: str    # short title
    description: str
    priority: str       # "High" | "Medium" | "Low"
    domains: list[str]  # compliance bridge domain keys


class GDPRControl(BaseModel):
    id: str             # e.g. "GDPR-A5.1a"
    framework: str = "GDPR"
    control_ref: str    # e.g. "Art.5(1)(a)"
    category: str       # GDPR domain name, e.g. "Principles"
    requirement: str
    description: str
    priority: str
    domains: list[str]


class ISO27001Control(BaseModel):
    id: str             # e.g. "ISO-4.1"
    framework: str = "ISO 27001:2022"
    control_ref: str    # e.g. "Cl.4.1"
    category: str       # ISO domain name, e.g. "Context"
    requirement: str
    description: str
    priority: str
    domains: list[str]


class ControlDomain(BaseModel):
    key: str
    label: str
    description: str
    slsa_controls: list[SLSAControl] = []
    owasp_controls: list[OWASPControl] = []
    soc2_controls: list[SOC2Control] = []
    gdpr_controls: list[GDPRControl] = []
    iso27001_controls: list[ISO27001Control] = []


class UnifiedMapping(BaseModel):
    generated_at: str
    frameworks: list[str]
    sources: dict[str, str]         # framework → source file
    domain_count: int
    slsa_control_count: int
    owasp_control_count: int
    soc2_control_count: int
    gdpr_control_count: int
    iso27001_control_count: int
    domains: list[ControlDomain]
