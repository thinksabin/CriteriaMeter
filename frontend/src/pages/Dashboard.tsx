import { useEffect, useState } from 'react'
import { mappingApi, type CompareResponse, type MappedDomain } from '../api/mappingApi'

const ALL_DATASETS = ['slsa_v1.2', 'owasp_asvs_5.0', 'soc2', 'gdpr', 'iso27001']

const FRAMEWORKS = [
  { key: 'slsa',     label: 'SLSA v1.2',      color: '#7ab0ff' },
  { key: 'owasp',    label: 'OWASP ASVS 5.0', color: '#63ca9b' },
  { key: 'soc2',     label: 'SOC 2',           color: '#c882ff' },
  { key: 'gdpr',     label: 'GDPR',            color: '#20b2aa' },
  { key: 'iso27001', label: 'ISO 27001:2022',  color: '#ffaa50' },
] as const

const SUPPLY_FW     = FRAMEWORKS.slice(0, 2)
const COMPLIANCE_FW = FRAMEWORKS.slice(2)

interface HeatRow {
  key: string
  label: string
  slsa: number
  owasp: number
  soc2: number
  gdpr: number
  iso27001: number
}

function buildHeatRows(domains: MappedDomain[]): HeatRow[] {
  return domains.map(d => ({
    key:      d.key,
    label:    d.label,
    slsa:     d.slsa_controls.length,
    owasp:    d.owasp_controls.length,
    soc2:     d.soc2_controls.length,
    gdpr:     d.gdpr_controls.length,
    iso27001: d.iso27001_controls.length,
  }))
}

function colMax(rows: HeatRow[], key: string): number {
  return Math.max(...rows.map(r => r[key as keyof HeatRow] as number), 1)
}

function cellBg(count: number, max: number, color: string): string {
  if (count === 0) return 'transparent'
  const opacity = 0.15 + 0.70 * (count / max)
  return color + Math.round(opacity * 255).toString(16).padStart(2, '0')
}

function HeatMapSection({
  title,
  frameworks,
  rows,
}: {
  title: string
  frameworks: typeof FRAMEWORKS[number][]
  rows: HeatRow[]
}) {
  const maxima = Object.fromEntries(
    frameworks.map(fw => [fw.key, colMax(rows, fw.key)])
  )
  const cols = frameworks.length

  return (
    <div className="heatmap-section">
      <h2 className="heatmap-section-title">{title}</h2>
      <div
        className="heatmap-grid"
        style={{ gridTemplateColumns: `1fr repeat(${cols}, minmax(56px, 72px))` }}
      >
        <div className="heatmap-corner" />
        {frameworks.map(fw => (
          <div key={fw.key} className="heatmap-col-head" style={{ color: fw.color }}>
            {fw.label}
          </div>
        ))}

        {rows.flatMap(row => [
          <div key={`${row.key}-lbl`} className="heatmap-row-label">
            {row.label}
          </div>,
          ...frameworks.map(fw => {
            const count = row[fw.key as keyof HeatRow] as number
            return (
              <div
                key={`${row.key}-${fw.key}`}
                className="heatmap-cell"
                style={{ background: cellBg(count, maxima[fw.key], fw.color) }}
                title={`${row.label} · ${fw.label}: ${count} controls`}
              >
                {count > 0 ? count : ''}
              </div>
            )
          }),
        ])}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [error, setError]   = useState<string | null>(null)
  const [result, setResult] = useState<CompareResponse | null>(null)

  useEffect(() => {
    setStatus('loading')
    mappingApi
      .compare(ALL_DATASETS)
      .then(data => { setResult(data); setStatus('success') })
      .catch(e => { setError(e instanceof Error ? e.message : 'Unknown error'); setStatus('error') })
  }, [])

  const rows       = result ? buildHeatRows(result.domains) : []
  const supplyRows = rows.filter(r => !r.key.startsWith('comp_'))
  const compRows   = rows.filter(r =>  r.key.startsWith('comp_'))

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Control density across frameworks and security domains.</p>
      </div>

      {status === 'loading' && <p className="mapper-loading">Loading heat map…</p>}

      {status === 'error' && error && (
        <div className="mapper-error-card"><strong>Error:</strong> {error}</div>
      )}

      {status === 'success' && result && (
        <section className="heatmap-container">
          <div className="heatmap-legend">
            {FRAMEWORKS.map(fw => (
              <div key={fw.key} className="heatmap-legend-item">
                <span className="heatmap-legend-dot" style={{ background: fw.color }} />
                <span className="heatmap-legend-label">{fw.label}</span>
              </div>
            ))}
          </div>

          <HeatMapSection title="Supply Chain" frameworks={SUPPLY_FW}     rows={supplyRows} />
          <HeatMapSection title="Compliance"   frameworks={COMPLIANCE_FW} rows={compRows}   />
        </section>
      )}
    </div>
  )
}
