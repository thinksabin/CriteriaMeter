import { useState } from 'react'
import { slsaChecklist, type ChecklistLevel } from '../data/slsaChecklist'

type CheckedState = Record<string, boolean>

function buildInitialState(levels: ChecklistLevel[]): CheckedState {
  const state: CheckedState = {}
  for (const level of levels) {
    for (const section of level.sections) {
      for (const item of section.items) {
        state[item.id] = false
      }
    }
  }
  return state
}

function countLevel(level: ChecklistLevel, checked: CheckedState) {
  const total = level.sections.reduce((sum, s) => sum + s.items.length, 0)
  const done = level.sections.reduce(
    (sum, s) => sum + s.items.filter((i) => checked[i.id]).length,
    0,
  )
  return { total, done }
}

export default function MeterReading() {
  const [checked, setChecked] = useState<CheckedState>(
    () => buildInitialState(slsaChecklist),
  )
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const totalItems = Object.keys(checked).length
  const totalDone = Object.values(checked).filter(Boolean).length

  function toggle(id: string) {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  function toggleExpanded(id: string) {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  function resetLevel(level: ChecklistLevel) {
    const updates: CheckedState = {}
    for (const s of level.sections) {
      for (const item of s.items) {
        updates[item.id] = false
      }
    }
    setChecked((prev) => ({ ...prev, ...updates }))
  }

  const overallPct = totalItems === 0 ? 0 : Math.round((totalDone / totalItems) * 100)

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Meter Reading</h1>
        <p className="page-subtitle">
          SLSA v1.2 Build Track compliance checklist — work through each level to
          assess your supply-chain security posture.
        </p>
      </div>

      {/* Overall progress */}
      <div className="meter-summary">
        <div className="meter-summary-top">
          <span className="meter-summary-label">Overall progress</span>
          <span className="meter-summary-count">
            {totalDone} / {totalItems} items
          </span>
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

      {/* Levels */}
      {slsaChecklist.map((level) => {
        const { total, done } = countLevel(level, checked)
        const pct = total === 0 ? 0 : Math.round((done / total) * 100)
        const complete = done === total

        return (
          <div
            key={level.level}
            className={`level-card ${complete ? 'level-card--complete' : ''}`}
          >
            <div className="level-header">
              <div className="level-header-left">
                <span className={`level-badge ${complete ? 'level-badge--complete' : ''}`}>
                  {complete ? '✓' : level.level}
                </span>
                <div>
                  <h2 className="level-title">{level.label}</h2>
                  <p className="level-definition">{level.definition}</p>
                </div>
              </div>
              <div className="level-header-right">
                <span className="level-count">{done}/{total}</span>
                <button
                  className="reset-btn"
                  onClick={() => resetLevel(level)}
                  title="Reset this level"
                >
                  ↺
                </button>
              </div>
            </div>

            {/* Level progress bar */}
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

            {/* Sections */}
            {level.sections.map((section) => (
              <div key={section.title} className="checklist-section">
                <h3 className="section-title">{section.title}</h3>
                <ul className="checklist-list">
                  {section.items.map((item) => {
                    const isChecked = checked[item.id]
                    const isOpen = expanded[item.id]
                    return (
                      <li key={item.id} className={`checklist-item ${isChecked ? 'checklist-item--checked' : ''}`}>
                        <label className="checklist-label">
                          <input
                            type="checkbox"
                            className="checklist-checkbox"
                            checked={isChecked}
                            onChange={() => toggle(item.id)}
                          />
                          <span className="checklist-text">{item.text}</span>
                        </label>
                        {item.description && (
                          <button
                            className="expand-btn"
                            onClick={() => toggleExpanded(item.id)}
                            aria-label={isOpen ? 'Hide detail' : 'Show detail'}
                          >
                            {isOpen ? '−' : '+'}
                          </button>
                        )}
                        {item.description && isOpen && (
                          <p className="checklist-description">{item.description}</p>
                        )}
                      </li>
                    )
                  })}
                </ul>
              </div>
            ))}
          </div>
        )
      })}

      <p className="slsa-ref">
        Reference:{' '}
        <a
          href="https://slsa.dev/spec/v1.2/build-track-basics"
          target="_blank"
          rel="noreferrer noopener"
          className="slsa-link"
        >
          slsa.dev/spec/v1.2/build-track-basics
        </a>
      </p>
    </div>
  )
}
