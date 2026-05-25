import { useEffect, useState } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { APP_VERSION } from '../config'
import { useAuth } from '../context/AuthContext'

const TOP_LINKS = [
  { to: '/', label: 'Home', icon: '⌂' },
]

const ABOUT_LINK = { to: '/about', label: 'About', icon: '◉' }

const METER_CHILDREN = [
  { to: '/meter-reading/supply-chain', label: 'Supply Chain' },
  { to: '/meter-reading/compliance',   label: 'Compliance'   },
]

const MAPPER_CHILDREN = [
  { to: '/mapper/supply-chain', label: 'Supply Chain' },
  { to: '/mapper/compliance',   label: 'Compliance'   },
]

const ADMIN_CHILDREN = [
  { to: '/admin/user-management', label: 'User Management' },
  { to: '/admin/authentication',  label: 'Authentication'  },
]

export default function NavBar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, isAdmin, user, logout } = useAuth()

  const onMeter  = location.pathname.startsWith('/meter-reading')
  const onMapper = location.pathname.startsWith('/mapper')
  const onAdmin  = location.pathname.startsWith('/admin')

  const [meterOpen,  setMeterOpen]  = useState(onMeter)
  const [mapperOpen, setMapperOpen] = useState(onMapper)
  const [adminOpen,  setAdminOpen]  = useState(onAdmin)

  useEffect(() => { if (onMeter)  setMeterOpen(true)  }, [onMeter])
  useEffect(() => { if (onMapper) setMapperOpen(true) }, [onMapper])
  useEffect(() => { if (onAdmin)  setAdminOpen(true)  }, [onAdmin])

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    ['nav-link', isActive ? 'nav-link--active' : ''].join(' ').trim()

  function handleLogout() {
    logout()
    navigate('/')
  }

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

        {/* Meter Reading — authenticated users only */}
        {isAuthenticated && (
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
        )}

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

        {/* Administration — only visible to admin users */}
        {isAdmin && (
          <li>
            <button
              className={`nav-link nav-group-btn${onAdmin ? ' nav-link--active' : ''}`}
              onClick={() => setAdminOpen(o => !o)}
              aria-expanded={adminOpen}
            >
              <span className="nav-icon">⚙</span>
              <span>Administration</span>
              <span className="nav-chevron">{adminOpen ? '▾' : '▸'}</span>
            </button>

            {adminOpen && (
              <ul className="nav-sub-list">
                {ADMIN_CHILDREN.map(({ to, label }) => (
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
        )}

        {/* Dashboard — authenticated users only */}
        {isAuthenticated && (
          <li>
            <NavLink to="/dashboard" className={navLinkClass}>
              <span className="nav-icon">◈</span>
              <span>Dashboard</span>
            </NavLink>
          </li>
        )}

        {/* About — always visible */}
        <li>
          <NavLink to={ABOUT_LINK.to} className={navLinkClass}>
            <span className="nav-icon">{ABOUT_LINK.icon}</span>
            <span>{ABOUT_LINK.label}</span>
          </NavLink>
        </li>
      </ul>

      <div className="sidebar-footer">
        {isAuthenticated && user ? (
          <div className="nav-user">
            <span className="nav-user-name">{user.first_name} {user.last_name}</span>
            <NavLink to="/settings" className="nav-settings-link">Settings</NavLink>
            <button className="nav-logout-btn" onClick={handleLogout}>Log out</button>
          </div>
        ) : (
          <div className="nav-auth-links">
            <NavLink to="/login"  className="nav-auth-link">Log in</NavLink>
            <NavLink to="/signup" className="nav-auth-link nav-auth-link--primary">Sign up</NavLink>
          </div>
        )}
        <span className="sidebar-version">v{APP_VERSION}</span>
      </div>
    </nav>
  )
}
