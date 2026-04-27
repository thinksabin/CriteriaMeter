import { useEffect, useState } from 'react'
import {
  mappingApi,
  type CompareResponse,
  type DatasetInfo,
  type MappedDomain,
  type OWASPControl,
  type SLSAControl,
} from '../api/mappingApi'

// ── Sub-components ────────────────────────────────────────────────────────────

function LevelBadge({ level, framework }: { level: string | number; framework: 'slsa' | 'owasp' }) {
  return (
    <span className={`level-pill level-pill--${framework} level-pill--${String(level).toLowerCase()}`}>
      {framework === 'slsa' ? level : `L${level}`}
    </span>
  )
}

function SLSARow({ ctrl }: { ctrl: SLSAControl }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="map-row">
      <div className="map-row-header">
        <LevelBadge level={ctrl.level} framework="slsa" />
        <span className="map-row-section">{ctrl.section}</span>
        <button className="expand-btn map-expand" onClick={() => setOpen(o => !o)}>
          {open ? '−' : '+'}
        </button>
      </div>
      <p className="map-row-text">{ctrl.text}</p>
      {open && <p className="map-row-desc">{ctrl.description}</p>}
    </div>
  )
}

function OWASPRow({ ctrl }: { ctrl: OWASPControl }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="map-row">
      <div className="map-row-header">
        <span className="map-row-id">{ctrl.id}</span>
        <LevelBadge level={ctrl.level} framework="owasp" />
        <button className="expand-btn map-expand" onClick={() => setOpen(o => !o)}>
          {open ? '−' : '+'}
        </button>
      </div>
      <p className="map-row-section">{ctrl.chapter_name} › {ctrl.section_name}</p>
      {open && <p className="map-row-desc">{ctrl.req_description}</p>}
    </div>
  )
}

function DomainBlock({
  domain,
  showSlsa,
  showOwasp,
}: {
  domain: MappedDomain
  showSlsa: boolean
  showOwasp: boolean
}) {
  const cols = [showSlsa, showOwasp].filter(Boolean).length

  return (
    <div className="domain-block">
      <div className="domain-block-header">
        <span className="domain-block-label">{domain.label}</span>
        <span className="domain-block-desc">{domain.description}</span>
        <div className="domain-block-counts">
          {showSlsa && domain.slsa_controls.length > 0 && (
            <span className="count-badge count-badge--slsa">
              SLSA: {domain.slsa_controls.length}
            </span>
          )}
          {showOwasp && domain.owasp_controls.length > 0 && (
            <span className="count-badge count-badge--owasp">
              OWASP: {domain.owasp_controls.length}
            </span>
          )}
        </div>
      </div>

      <div className={`domain-cols domain-cols--${cols}`}>
        {showSlsa && (
          <div className="domain-col">
            <div className="domain-col-head">SLSA v1.2</div>
            <div className="domain-col-body">
              {domain.slsa_controls.length === 0 ? (
                <p className="no-controls">No controls in this domain</p>
              ) : (
                domain.slsa_controls.map(c => <SLSARow key={c.id} ctrl={c} />)
              )}
            </div>
          </div>
        )}

        {showOwasp && (
          <div className="domain-col">
            <div className="domain-col-head">OWASP ASVS 5.0</div>
            <div className="domain-col-body">
              {domain.owasp_controls.length === 0 ? (
                <p className="no-controls">No controls in this domain</p>
              ) : (
                domain.owasp_controls.map(c => <OWASPRow key={c.id} ctrl={c} />)
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function Mapper() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loadingDatasets, setLoadingDatasets] = useState(true)
  const [datasetsError, setDatasetsError] = useState<string | null>(null)

  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<CompareResponse | null>(null)

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
    // Clear previous result when selection changes
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

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Mapper</h1>
        <p className="page-subtitle">
          Select datasets to compare and press <strong>Map</strong> to generate a
          cross-framework control mapping.
        </p>
      </div>

      {/* Dataset selection */}
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

      {/* Error */}
      {status === 'error' && error && (
        <div className="mapper-error-card">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
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
            </div>
          </div>

          <div className="domain-list">
            {result.domains.map(domain => (
              <DomainBlock
                key={domain.key}
                domain={domain}
                showSlsa={showSlsa}
                showOwasp={showOwasp}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
