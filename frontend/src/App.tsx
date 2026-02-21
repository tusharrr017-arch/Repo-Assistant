import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import QA from './pages/QA'
import Status from './pages/Status'
import History from './pages/History'

const nav = [
  { path: '/', label: 'Home' },
  { path: '/qa', label: 'Q&A' },
  { path: '/status', label: 'Status' },
  { path: '/history', label: 'History' },
]

export default function App() {
  const loc = useLocation()
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{
        borderBottom: '1px solid var(--border)',
        padding: '0.875rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1.5rem',
        flexWrap: 'wrap',
        background: 'var(--surface)',
      }}>
        <Link to="/" style={{ fontWeight: 600, fontSize: '1.0625rem', color: 'var(--text)', textDecoration: 'none' }}>
          Codebase Q&A with Proof
        </Link>
        <nav style={{ display: 'flex', gap: '1.25rem' }}>
          {nav.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              style={{
                color: loc.pathname === path ? 'var(--accent)' : 'var(--muted)',
                textDecoration: 'none',
                fontSize: '0.9375rem',
                fontWeight: loc.pathname === path ? 500 : 400,
              }}
            >
              {label}
            </Link>
          ))}
        </nav>
      </header>
      <main style={{ flex: 1, padding: '1.5rem 1.25rem', maxWidth: 920, margin: '0 auto', width: '100%' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/qa" element={<QA />} />
          <Route path="/status" element={<Status />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  )
}
