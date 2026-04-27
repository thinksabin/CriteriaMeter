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


class ControlDomain(BaseModel):
    key: str
    label: str
    description: str
    slsa_controls: list[SLSAControl] = []
    owasp_controls: list[OWASPControl] = []


class UnifiedMapping(BaseModel):
    generated_at: str
    frameworks: list[str]
    sources: dict[str, str]         # framework → source file
    domain_count: int
    slsa_control_count: int
    owasp_control_count: int
    domains: list[ControlDomain]
