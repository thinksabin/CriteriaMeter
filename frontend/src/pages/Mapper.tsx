import { type ReactNode, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  mappingApi,
  type CompareResponse,
  type DatasetInfo,
  type GDPRControl,
  type ISO27001Control,
  type MappedDomain,
  type OWASPControl,
  type SLSAControl,
  type SOC2Control,
} from '../api/mappingApi'

// ── Shared badges ─────────────────────────────────────────────────────────────

function LevelBadge({ level, framework }: { level: string | number; framework: 'slsa' | 'owasp' }) {
  return (
    <span className={`level-pill level-pill--${framework} level-pill--${String(level).toLowerCase()}`}>
      {framework === 'slsa' ? level : `L${level}`}
    </span>
  )
}

function PriorityBadge({ priority }: { priority: string }) {
  return (
    <span className={`level-pill level-pill--priority-${priority.toLowerCase()}`}>
      {priority}
    </span>
  )
}

// ── Uniform control row ───────────────────────────────────────────────────────
// All five frameworks render through this single component so layout is
// structurally identical across the entire mapper.
//
//  [id]  [badge]  [expand]   ← header
//  [category / section]      ← context (always shown)
//  [requirement text]        ← always shown
//  [description]             ← shown on expand (only when detail is provided)

interface ControlRowProps {
  id?: string       // monospace control reference (omit for SLSA — level badge serves as ID)
  badge: ReactNode  // level badge (SLSA/OWASP) or priority badge (compliance)
  category: string  // section path or domain category
  text: string      // main requirement / control title
  detail?: string   // expandable description (omit when not available)
}

function ControlRow({ id, badge, category, text, detail }: ControlRowProps) {
  const [open, setOpen] = useState(false)
  return (
    <div className="map-row">
      <div className="map-row-header">
        {id ? <span className="map-row-id">{id}</span> : null}
        {badge}
        {detail ? (
          <button className="expand-btn map-expand" onClick={() => setOpen(o => !o)}>
            {open ? '−' : '+'}
          </button>
        ) : null}
      </div>
      <p className="map-row-section">{category}</p>
      <p className="map-row-text">{text}</p>
      {open && detail ? <p className="map-row-desc">{detail}</p> : null}
    </div>
  )
}

// ── Per-framework row adapters ────────────────────────────────────────────────

function SLSARow({ ctrl }: { ctrl: SLSAControl }) {
  return (
    <ControlRow
      badge={<LevelBadge level={ctrl.level} framework="slsa" />}
      category={ctrl.section}
      text={ctrl.text}
      detail={ctrl.description}
    />
  )
}

function OWASPRow({ ctrl }: { ctrl: OWASPControl }) {
  return (
    <ControlRow
      id={ctrl.id}
      badge={<LevelBadge level={ctrl.level} framework="owasp" />}
      category={`${ctrl.chapter_name} › ${ctrl.section_name}`}
      text={ctrl.req_description}
      // OWASP has no separate description field — detail omitted, no expand button
    />
  )
}

function SOC2Row({ ctrl }: { ctrl: SOC2Control }) {
  return (
    <ControlRow
      id={ctrl.control_ref}
      badge={<PriorityBadge priority={ctrl.priority} />}
      category={ctrl.category}
      text={ctrl.requirement}
      detail={ctrl.description}
    />
  )
}

function GDPRRow({ ctrl }: { ctrl: GDPRControl }) {
  return (
    <ControlRow
      id={ctrl.control_ref}
      badge={<PriorityBadge priority={ctrl.priority} />}
      category={ctrl.category}
      text={ctrl.requirement}
      detail={ctrl.description}
    />
  )
}

function ISO27001Row({ ctrl }: { ctrl: ISO27001Control }) {
  return (
    <ControlRow
      id={ctrl.control_ref}
      badge={<PriorityBadge priority={ctrl.priority} />}
      category={ctrl.category}
      text={ctrl.requirement}
      detail={ctrl.description}
    />
  )
}

// ── Domain block ──────────────────────────────────────────────────────────────

function DomainBlock({
  domain,
  showSlsa, showOwasp,
  showSoc2, showGdpr, showIso27001,
}: {
  domain: MappedDomain
  showSlsa: boolean
  showOwasp: boolean
  showSoc2: boolean
  showGdpr: boolean
  showIso27001: boolean
}) {
  const isCompliance = domain.key.startsWith('comp_')

  const cols = isCompliance
    ? [showSoc2, showGdpr, showIso27001].filter(Boolean).length
    : [showSlsa, showOwasp].filter(Boolean).length

  return (
    <div className="domain-block">
      <div className="domain-block-header">
        <span className="domain-block-label">{domain.label}</span>
        <span className="domain-block-desc">{domain.description}</span>
        <div className="domain-block-counts">
          {!isCompliance && showSlsa && domain.slsa_controls.length > 0 && (
            <span className="count-badge count-badge--slsa">SLSA: {domain.slsa_controls.length}</span>
          )}
          {!isCompliance && showOwasp && domain.owasp_controls.length > 0 && (
            <span className="count-badge count-badge--owasp">OWASP: {domain.owasp_controls.length}</span>
          )}
          {isCompliance && showSoc2 && domain.soc2_controls.length > 0 && (
            <span className="count-badge count-badge--soc2">SOC 2: {domain.soc2_controls.length}</span>
          )}
          {isCompliance && showGdpr && domain.gdpr_controls.length > 0 && (
            <span className="count-badge count-badge--gdpr">GDPR: {domain.gdpr_controls.length}</span>
          )}
          {isCompliance && showIso27001 && domain.iso27001_controls.length > 0 && (
            <span className="count-badge count-badge--iso27001">ISO 27001: {domain.iso27001_controls.length}</span>
          )}
        </div>
      </div>

      <div className={`domain-cols domain-cols--${cols}`}>
        {!isCompliance && showSlsa && (
          <div className="domain-col">
            <div className="domain-col-head">SLSA v1.2</div>
            <div className="domain-col-body">
              {domain.slsa_controls.length === 0
                ? <p className="no-controls">No controls in this domain</p>
                : domain.slsa_controls.map(c => <SLSARow key={c.id} ctrl={c} />)}
            </div>
          </div>
        )}
        {!isCompliance && showOwasp && (
          <div className="domain-col">
            <div className="domain-col-head">OWASP ASVS 5.0</div>
            <div className="domain-col-body">
              {domain.owasp_controls.length === 0
                ? <p className="no-controls">No controls in this domain</p>
                : domain.owasp_controls.map(c => <OWASPRow key={c.id} ctrl={c} />)}
            </div>
          </div>
        )}
        {isCompliance && showSoc2 && (
          <div className="domain-col">
            <div className="domain-col-head">SOC 2</div>
            <div className="domain-col-body">
              {domain.soc2_controls.length === 0
                ? <p className="no-controls">No controls in this domain</p>
                : domain.soc2_controls.map(c => <SOC2Row key={c.id} ctrl={c} />)}
            </div>
          </div>
        )}
        {isCompliance && showGdpr && (
          <div className="domain-col">
            <div className="domain-col-head">GDPR</div>
            <div className="domain-col-body">
              {domain.gdpr_controls.length === 0
                ? <p className="no-controls">No controls in this domain</p>
                : domain.gdpr_controls.map(c => <GDPRRow key={c.id} ctrl={c} />)}
            </div>
          </div>
        )}
        {isCompliance && showIso27001 && (
          <div className="domain-col">
            <div className="domain-col-head">ISO 27001:2022</div>
            <div className="domain-col-body">
              {domain.iso27001_controls.length === 0
                ? <p className="no-controls">No controls in this domain</p>
                : domain.iso27001_controls.map(c => <ISO27001Row key={c.id} ctrl={c} />)}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

const PRESET: Record<string, string[]> = {
  'supply-chain': ['slsa_v1.2', 'owasp_asvs_5.0'],
  'compliance':   ['soc2', 'gdpr', 'iso27001'],
}

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function Mapper() {
  const { group } = useParams<{ group?: string }>()

  const [datasets, setDatasets] = useState<DatasetInfo[]>([])
  const [selected, setSelected] = useState<Set<string>>(
    () => new Set(group ? (PRESET[group] ?? []) : [])
  )
  const [loadingDatasets, setLoadingDatasets] = useState(true)
  const [datasetsError, setDatasetsError] = useState<string | null>(null)

  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<CompareResponse | null>(null)

  // Reset selection when navigating between sub-routes
  useEffect(() => {
    setSelected(new Set(group ? (PRESET[group] ?? []) : []))
    setResult(null)
    setStatus('idle')
  }, [group])

  useEffect(() => {
    mappingApi
      .datasets()
      .then(r => setDatasets(r.datasets))
      .catch(e => setDatasetsError(e.message))
      .finally(() => setLoadingDatasets(false))
  }, [])

  function toggleDataset(id: string) {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
    setResult(null)
    setStatus('idle')
  }

  async function handleMap() {
    if (selected.size === 0) return
    setStatus('loading')
    setError(null)
    setResult(null)
    try {
      const data = await mappingApi.compare([...selected])
      setResult(data)
      setStatus('success')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
      setStatus('error')
    }
  }

  const showSlsa = selected.has('slsa_v1.2')
  const showOwasp = selected.has('owasp_asvs_5.0')
  const showSoc2 = selected.has('soc2')
  const showGdpr = selected.has('gdpr')
  const showIso27001 = selected.has('iso27001')

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Mapper</h1>
        <p className="page-subtitle">
          Select frameworks to compare and press <strong>Map</strong> to generate a
          cross-framework control mapping.
        </p>
      </div>

      <section className="mapper-select-card">
        <h2 className="mapper-section-title">Available datasets</h2>

        {loadingDatasets && <p className="mapper-loading">Loading datasets…</p>}
        {datasetsError && <p className="mapper-error">{datasetsError}</p>}

        {!loadingDatasets && !datasetsError && (
          <ul className="dataset-list">
            {datasets.map(ds => (
              <li key={ds.id} className="dataset-item">
                <label className="dataset-label">
                  <input
                    type="checkbox"
                    className="checklist-checkbox"
                    checked={selected.has(ds.id)}
                    onChange={() => toggleDataset(ds.id)}
                  />
                  <div className="dataset-info">
                    <span className="dataset-name">{ds.label}</span>
                    <span className="dataset-meta">
                      v{ds.version} · {ds.control_count} controls
                    </span>
                    <span className="dataset-desc">{ds.description}</span>
                  </div>
                </label>
              </li>
            ))}
          </ul>
        )}

        <div className="mapper-actions">
          <button
            className="map-btn"
            disabled={selected.size === 0 || status === 'loading'}
            onClick={handleMap}
          >
            {status === 'loading' ? 'Mapping…' : 'Map'}
          </button>
          {selected.size === 0 && (
            <span className="map-hint">Select at least one dataset to continue</span>
          )}
        </div>
      </section>

      {status === 'error' && error && (
        <div className="mapper-error-card">
          <strong>Error:</strong> {error}
        </div>
      )}

      {status === 'success' && result && (
        <section className="mapper-results">
          <div className="results-summary">
            <div className="results-summary-inner">
              <span className="results-title">Mapping result</span>
              <div className="results-pills">
                {result.selected_datasets.map(ds => (
                  <span key={ds} className="results-dataset-pill">{ds}</span>
                ))}
              </div>
            </div>
            <div className="results-stats">
              <div className="stat">
                <span className="stat-value">{result.domain_count}</span>
                <span className="stat-label">domains</span>
              </div>
              {showSlsa && (
                <div className="stat">
                  <span className="stat-value">{result.total_slsa_controls}</span>
                  <span className="stat-label">SLSA controls</span>
                </div>
              )}
              {showOwasp && (
                <div className="stat">
                  <span className="stat-value">{result.total_owasp_controls}</span>
                  <span className="stat-label">OWASP requirements</span>
                </div>
              )}
              {showSoc2 && (
                <div className="stat">
                  <span className="stat-value">{result.total_soc2_controls}</span>
                  <span className="stat-label">SOC 2 criteria</span>
                </div>
              )}
              {showGdpr && (
                <div className="stat">
                  <span className="stat-value">{result.total_gdpr_controls}</span>
                  <span className="stat-label">GDPR requirements</span>
                </div>
              )}
              {showIso27001 && (
                <div className="stat">
                  <span className="stat-value">{result.total_iso27001_controls}</span>
                  <span className="stat-label">ISO 27001 controls</span>
                </div>
              )}
            </div>
          </div>

          <div className="domain-list">
            {result.domains.map(domain => (
              <DomainBlock
                key={domain.key}
                domain={domain}
                showSlsa={showSlsa}
                showOwasp={showOwasp}
                showSoc2={showSoc2}
                showGdpr={showGdpr}
                showIso27001={showIso27001}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
