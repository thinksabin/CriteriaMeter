import { useEffect, useMemo, useState } from 'react'
import { mappingApi } from '../api/mappingApi'
import type {
  GDPRControl,
  ISO27001Control,
  MappedDomain,
  SOC2Control,
} from '../api/mappingApi'

// ── Types ─────────────────────────────────────────────────────────────────────

interface CtrlItem {
  id: string
  control_ref: string
  requirement: string
  description: string
  priority: string
}

interface CtrlSection {
  category: string
  items: CtrlItem[]
}

interface CtrlFramework {
  id: string
  label: string
  sections: CtrlSection[]
  total: number
}

type CheckedState = Record<string, boolean>

// ── Helpers ───────────────────────────────────────────────────────────────────

function dedup<T extends { id: string }>(items: T[]): T[] {
  const seen = new Set<string>()
  return items.filter(item => !seen.has(item.id) && seen.add(item.id) as unknown as boolean)
}

function toItem(c: SOC2Control | GDPRControl | ISO27001Control): CtrlItem {
  return {
    id: c.id,
    control_ref: c.control_ref,
    requirement: c.requirement,
    description: c.description,
    priority: c.priority,
  }
}

function groupByCategory(items: CtrlItem[], rawControls: (SOC2Control | GDPRControl | ISO27001Control)[]): CtrlSection[] {
  const catMap = new Map<string, string>()
  for (const c of rawControls) catMap.set(c.id, c.category)

  const map = new Map<string, CtrlItem[]>()
  for (const item of items) {
    const cat = catMap.get(item.id) ?? 'General'
    if (!map.has(cat)) map.set(cat, [])
    map.get(cat)!.push(item)
  }
  return Array.from(map.entries()).map(([category, items]) => ({ category, items }))
}

function buildFrameworks(domains: MappedDomain[]): CtrlFramework[] {
  const soc2Raw: SOC2Control[] = []
  const gdprRaw: GDPRControl[] = []
  const isoRaw:  ISO27001Control[] = []

  for (const d of domains) {
    soc2Raw.push(...d.soc2_controls)
    gdprRaw.push(...d.gdpr_controls)
    isoRaw.push(...d.iso27001_controls)
  }

  const soc2 = dedup(soc2Raw)
  const gdpr = dedup(gdprRaw)
  const iso  = dedup(isoRaw)

  return [
    {
      id: 'soc2',
      label: 'SOC 2',
      sections: groupByCategory(soc2.map(toItem), soc2Raw),
      total: soc2.length,
    },
    {
      id: 'gdpr',
      label: 'GDPR',
      sections: groupByCategory(gdpr.map(toItem), gdprRaw),
      total: gdpr.length,
    },
    {
      id: 'iso27001',
      label: 'ISO 27001:2022',
      sections: groupByCategory(iso.map(toItem), isoRaw),
      total: iso.length,
    },
  ]
}

function buildInitialState(frameworks: CtrlFramework[]): CheckedState {
  const state: CheckedState = {}
  for (const fw of frameworks) {
    for (const sec of fw.sections) {
      for (const item of sec.items) {
        state[item.id] = false
      }
    }
  }
  return state
}

// ── Sub-components ────────────────────────────────────────────────────────────

function PriorityBadge({ priority }: { priority: string }) {
  return (
    <span className={`level-pill level-pill--priority-${priority.toLowerCase()}`}>
      {priority}
    </span>
  )
}

function ControlItem({
  item,
  checked,
  onToggle,
}: {
  item: CtrlItem
  checked: boolean
  onToggle: (id: string) => void
}) {
  const [open, setOpen] = useState(false)
  return (
    <li className={`checklist-item${checked ? ' checklist-item--checked' : ''}`}>
      <label className="checklist-label">
        <input
          type="checkbox"
          className="checklist-checkbox"
          checked={checked}
          onChange={() => onToggle(item.id)}
        />
        <span className="ctrl-ref">{item.control_ref}</span>
        <PriorityBadge priority={item.priority} />
        <span className="checklist-text">{item.requirement}</span>
      </label>
      {item.description && (
        <button
          className="expand-btn"
          onClick={() => setOpen(o => !o)}
          aria-label={open ? 'Hide detail' : 'Show detail'}
        >
          {open ? '−' : '+'}
        </button>
      )}
      {item.description && open && (
        <p className="checklist-description">{item.description}</p>
      )}
    </li>
  )
}

function FrameworkCard({
  fw,
  checked,
  onToggle,
  onReset,
}: {
  fw: CtrlFramework
  checked: CheckedState
  onToggle: (id: string) => void
  onReset: (fw: CtrlFramework) => void
}) {
  const done = fw.sections.reduce(
    (sum, s) => sum + s.items.filter(i => checked[i.id]).length,
    0,
  )
  const pct = fw.total === 0 ? 0 : Math.round((done / fw.total) * 100)
  const complete = done === fw.total

  return (
    <div className={`level-card${complete ? ' level-card--complete' : ''}`}>
      <div className="level-header">
        <div className="level-header-left">
          <span className={`level-badge level-badge--fw level-badge--fw-${fw.id}${complete ? ' level-badge--complete' : ''}`}>
            {complete ? '✓' : fw.label.slice(0, 3).toUpperCase()}
          </span>
          <div>
            <h2 className="level-title">{fw.label}</h2>
          </div>
        </div>
        <div className="level-header-right">
          <span className="level-count">{done}/{fw.total}</span>
          <button
            className="reset-btn"
            onClick={() => onReset(fw)}
            title="Reset this framework"
          >
            ↺
          </button>
        </div>
      </div>

      <div className="progress-bar progress-bar--sm">
        <div
          className="progress-fill"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {fw.sections.map(sec => (
        <div key={sec.category} className="checklist-section">
          <h3 className="section-title">{sec.category}</h3>
          <ul className="checklist-list">
            {sec.items.map(item => (
              <ControlItem
                key={item.id}
                item={item}
                checked={!!checked[item.id]}
                onToggle={onToggle}
              />
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ComplianceChecklist() {
  const [frameworks, setFrameworks] = useState<CtrlFramework[]>([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState<string | null>(null)
  const [checked, setChecked]       = useState<CheckedState>({})

  useEffect(() => {
    mappingApi
      .compare(['soc2', 'gdpr', 'iso27001'])
      .then(res => {
        const fws = buildFrameworks(res.domains)
        setFrameworks(fws)
        setChecked(buildInitialState(fws))
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const totalItems = useMemo(
    () => frameworks.reduce((s, fw) => s + fw.total, 0),
    [frameworks],
  )
  const totalDone = useMemo(
    () => Object.values(checked).filter(Boolean).length,
    [checked],
  )
  const overallPct = totalItems === 0 ? 0 : Math.round((totalDone / totalItems) * 100)

  function toggle(id: string) {
    setChecked(prev => ({ ...prev, [id]: !prev[id] }))
  }

  function resetFramework(fw: CtrlFramework) {
    const updates: CheckedState = {}
    for (const sec of fw.sections) {
      for (const item of sec.items) updates[item.id] = false
    }
    setChecked(prev => ({ ...prev, ...updates }))
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Compliance Checklist</h1>
        <p className="page-subtitle">
          SOC 2, GDPR, and ISO 27001:2022 controls — work through each framework
          to assess your compliance posture.
        </p>
      </div>

      {loading && <p className="mapper-loading">Loading controls…</p>}
      {error   && <p className="mapper-error">Error: {error}</p>}

      {!loading && !error && (
        <>
          <div className="meter-summary">
            <div className="meter-summary-top">
              <span className="meter-summary-label">Overall progress</span>
              <span className="meter-summary-count">{totalDone} / {totalItems} controls</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${overallPct}%` }}
                role="progressbar"
                aria-valuenow={overallPct}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </div>
            <span className="meter-summary-pct">{overallPct}%</span>
          </div>

          {frameworks.map(fw => (
            <FrameworkCard
              key={fw.id}
              fw={fw}
              checked={checked}
              onToggle={toggle}
              onReset={resetFramework}
            />
          ))}
        </>
      )}
    </div>
  )
}
