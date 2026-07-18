import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { to: '/dashboard',    label: 'Dashboard',     icon: '▦' },
  { to: '/transactions', label: 'Transactions',  icon: '↕' },
  { to: '/parse',        label: 'Add SMS',        icon: '+' },
  { to: '/budgets',      label: 'Budgets',        icon: '◎' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')  // ← go to landing page after logout, was /login
}

  return (
    <aside style={{
      width: 220,
      minHeight: '100vh',
      background: 'var(--color-surface)',
      borderRight: '1px solid var(--color-border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{ padding: '0 20px 32px' }}>
        <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-accent-light)', letterSpacing: '-0.5px' }}>
          ₹ UPI Tracker
        </div>
      </div>

      {/* Nav links */}
      <nav style={{ flex: 1 }}>
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '10px 20px',
              textDecoration: 'none',
              fontSize: 14,
              fontWeight: isActive ? 600 : 400,
              color: isActive ? 'var(--color-accent-light)' : 'var(--color-muted)',
              background: isActive ? 'rgba(108,99,255,0.1)' : 'transparent',
              borderLeft: isActive ? '2px solid var(--color-accent)' : '2px solid transparent',
              transition: 'all 0.15s',
            })}
          >
            <span style={{ fontSize: 16, width: 20, textAlign: 'center' }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User + logout */}
      <div style={{ padding: '0 20px', borderTop: '1px solid var(--color-border)', paddingTop: 16 }}>
        <div style={{ fontSize: 13, color: 'var(--color-muted)', marginBottom: 8, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {user?.email}
        </div>
        <button
          onClick={handleLogout}
          style={{
            width: '100%',
            padding: '8px 0',
            background: 'transparent',
            border: '1px solid var(--color-border)',
            color: 'var(--color-muted)',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 13,
          }}
        >
          Sign out
        </button>
      </div>
    </aside>
  )
}