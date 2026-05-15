import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

const TOP_LINKS = [
  { to: '/', label: 'Home', icon: '⌂' },
]

const BOTTOM_LINKS = [
  { to: '/dashboard', label: 'Dashboard', icon: '◈' },
  { to: '/about',     label: 'About',     icon: '◉' },
]

const METER_CHILDREN = [
  { to: '/meter-reading/supply-chain', label: 'Supply Chain' },
  { to: '/meter-reading/compliance',   label: 'Compliance'   },
]

const MAPPER_CHILDREN = [
  { to: '/mapper/supply-chain', label: 'Supply Chain' },
  { to: '/mapper/compliance',   label: 'Compliance'   },
]

export default function NavBar() {
  const location = useLocation()
  const onMeter  = location.pathname.startsWith('/meter-reading')
  const onMapper = location.pathname.startsWith('/mapper')

  const [meterOpen,  setMeterOpen]  = useState(onMeter)
  const [mapperOpen, setMapperOpen] = useState(onMapper)

  useEffect(() => { if (onMeter)  setMeterOpen(true)  }, [onMeter])
  useEffect(() => { if (onMapper) setMapperOpen(true) }, [onMapper])

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    ['nav-link', isActive ? 'nav-link--active' : ''].join(' ').trim()

  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-mark">⬡</span>
        <span className="logo-text">CriteriaMeter</span>
      </div>

      <ul className="nav-list">
        {TOP_LINKS.map(({ to, label, icon }) => (
          <li key={to}>
            <NavLink to={to} end={to === '/'} className={navLinkClass}>
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          </li>
        ))}

        {/* Expandable Meter Reading group */}
        <li>
          <button
            className={`nav-link nav-group-btn${onMeter ? ' nav-link--active' : ''}`}
            onClick={() => setMeterOpen(o => !o)}
            aria-expanded={meterOpen}
          >
            <span className="nav-icon">⊡</span>
            <span>Meter Reading</span>
            <span className="nav-chevron">{meterOpen ? '▾' : '▸'}</span>
          </button>

          {meterOpen && (
            <ul className="nav-sub-list">
              {METER_CHILDREN.map(({ to, label }) => (
                <li key={to}>
                  <NavLink to={to} className={navLinkClass}>
                    <span className="nav-sub-bullet">–</span>
                    <span>{label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          )}
        </li>

        {/* Expandable Mapper group */}
        <li>
          <button
            className={`nav-link nav-group-btn${onMapper ? ' nav-link--active' : ''}`}
            onClick={() => setMapperOpen(o => !o)}
            aria-expanded={mapperOpen}
          >
            <span className="nav-icon">⇄</span>
            <span>Mapper</span>
            <span className="nav-chevron">{mapperOpen ? '▾' : '▸'}</span>
          </button>

          {mapperOpen && (
            <ul className="nav-sub-list">
              {MAPPER_CHILDREN.map(({ to, label }) => (
                <li key={to}>
                  <NavLink to={to} className={navLinkClass}>
                    <span className="nav-sub-bullet">–</span>
                    <span>{label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          )}
        </li>

        {BOTTOM_LINKS.map(({ to, label, icon }) => (
          <li key={to}>
            <NavLink to={to} className={navLinkClass}>
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          </li>
        ))}
      </ul>

      <div className="sidebar-footer">v0.1.0</div>
    </nav>
  )
}
