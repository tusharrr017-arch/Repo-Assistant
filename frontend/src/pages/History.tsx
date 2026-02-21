import { useEffect, useState } from 'react'
import { api, HistoryEntry } from '../api'
import MarkdownContent from '../components/MarkdownContent'

export default function History() {
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.history()
      .then((r) => setHistory(r.history || []))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load history'))
  }, [])

  if (error) {
    return (
      <div>
        <h1 style={{ marginTop: 0, fontWeight: 600 }}>History</h1>
        <p style={{ color: 'var(--error)' }}>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <h1 style={{ marginTop: 0, fontWeight: 600 }}>History</h1>
      <p style={{ color: 'var(--muted)', marginBottom: '1.5rem', fontSize: '0.9375rem' }}>
        Last 10 Q&A pairs. Newest at the bottom.
      </p>
      {history.length === 0 ? (
        <p style={{ color: 'var(--muted)' }}>No Q&A history yet. Ask something on the Q&A page.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {history.map((item, i) => (
            <div key={i} className="section-card">
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--muted)', marginBottom: 6 }}>QUESTION</div>
              <div style={{ marginBottom: '1rem', color: 'var(--text)' }}>{item.question}</div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--muted)', marginBottom: 6 }}>ANSWER</div>
              <div className="markdown-content">
                <MarkdownContent content={item.answer} />
              </div>
              {item.references?.length ? (
                <div style={{ marginTop: '0.75rem', fontSize: '0.8125rem', color: 'var(--muted)' }}>
                  References:{' '}
                  {item.references.map((r, j) => (
                    <span key={j}>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>{r.file_path}</span>
                      {' '}({r.start_line}–{r.end_line}){j < item.references!.length - 1 ? '; ' : ''}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
