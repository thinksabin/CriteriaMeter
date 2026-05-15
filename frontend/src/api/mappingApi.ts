const BASE = '/api/mapping'

export interface DatasetInfo {
  id: string
  label: string
  description: string
  source_file: string
  version: string
  control_count: number
}

export interface SLSAControl {
  id: string
  level: string
  section: string
  text: string
  description: string
}

export interface OWASPControl {
  id: string
  chapter_id: string
  chapter_name: string
  section_id: string
  section_name: string
  req_description: string
  level: number
}

export interface SOC2Control {
  id: string
  control_ref: string
  category: string
  requirement: string
  description: string
  priority: string
}

export interface GDPRControl {
  id: string
  control_ref: string
  category: string
  requirement: string
  description: string
  priority: string
}

export interface ISO27001Control {
  id: string
  control_ref: string
  category: string
  requirement: string
  description: string
  priority: string
}

export interface MappedDomain {
  key: string
  label: string
  description: string
  slsa_controls: SLSAControl[]
  owasp_controls: OWASPControl[]
  soc2_controls: SOC2Control[]
  gdpr_controls: GDPRControl[]
  iso27001_controls: ISO27001Control[]
}

export interface CompareResponse {
  selected_datasets: string[]
  domain_count: number
  total_slsa_controls: number
  total_owasp_controls: number
  total_soc2_controls: number
  total_gdpr_controls: number
  total_iso27001_controls: number
  domains: MappedDomain[]
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const mappingApi = {
  datasets: (): Promise<{ datasets: DatasetInfo[] }> =>
    request('/datasets'),

  compare: (datasetIds: string[]): Promise<CompareResponse> =>
    request('/compare', {
      method: 'POST',
      body: JSON.stringify({ datasets: datasetIds }),
    }),
}
