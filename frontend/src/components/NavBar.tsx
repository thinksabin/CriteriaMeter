import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',               label: 'Home',          icon: '⌂' },
  { to: '/meter-reading',  label: 'Meter Reading', icon: '⊡' },
  { to: '/mapper',         label: 'Mapper',        icon: '⇄' },
  { to: '/dashboard',      label: 'Dashboard',     icon: '◈' },
  { to: '/about',          label: 'About',         icon: '◉' },
]

export default function NavBar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-mark">⬡</span>
        <span className="logo-text">CriteriaMeter</span>
      </div>

      <ul className="nav-list">
        {links.map(({ to, label, icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                ['nav-link', isActive ? 'nav-link--active' : ''].join(' ').trim()
              }
            >
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
