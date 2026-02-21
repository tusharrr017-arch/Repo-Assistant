import { useEffect, useState } from 'react'
import { api, HealthResp } from '../api'

export default function Status() {
  const [health, setHealth] = useState<HealthResp | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    api.health()
      .then((r) => { if (!cancelled) setHealth(r) })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to fetch health') })
    return () => { cancelled = true }
  }, [])

  if (error) {
    return (
      <div>
        <h1 style={{ marginTop: 0 }}>Status</h1>
        <p style={{ color: 'var(--error)' }}>{error}</p>
        <p style={{ color: 'var(--muted)' }}>Ensure the backend is running (e.g. <code>uvicorn app.main:app</code> in the backend directory).</p>
      </div>
    )
  }

  if (!health) {
    return (
      <div>
        <h1 style={{ marginTop: 0 }}>Status</h1>
        <p style={{ color: 'var(--muted)' }}>Loading…</p>
      </div>
    )
  }

  const items = [
    { label: 'Backend', ...health.backend },
    { label: 'Vector DB', ...health.vector_db, extra: health.vector_db.chunk_count != null ? ` (${health.vector_db.chunk_count} chunks)` : '' },
    { label: 'LLM', ...health.llm },
  ]

  return (
    <div>
      <h1 style={{ marginTop: 0 }}>Status</h1>
      <p style={{ color: 'var(--muted)', marginBottom: '1.5rem' }}>
        Backend, vector database, and LLM connection status.
      </p>
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        overflow: 'hidden',
      }}>
        <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: health.status === 'ok' ? 'var(--success)' : 'var(--error)',
          }} />
          <strong>Overall: {health.status}</strong>
        </div>
        {items.map((item) => (
          <div
            key={item.label}
            style={{
              padding: '0.75rem 1rem',
              borderBottom: '1px solid var(--border)',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              flexWrap: 'wrap',
            }}
          >
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: item.status === 'ok' ? 'var(--success)' : 'var(--error)',
            }} />
            <strong style={{ minWidth: 100 }}>{item.label}</strong>
            <span style={{ color: 'var(--muted)' }}>{item.message}{item.extra}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
