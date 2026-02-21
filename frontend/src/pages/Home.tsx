import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div>
      <h1 style={{ marginTop: 0 }}>Codebase Q&A with Proof</h1>
      <p style={{ color: 'var(--muted)', marginBottom: '2rem' }}>
        Upload a codebase or connect a GitHub repo, then ask questions and get answers grounded in your code with file and line references.
      </p>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.1rem', marginBottom: '0.75rem' }}>Steps</h2>
        <ol style={{ paddingLeft: '1.25rem', color: 'var(--muted)' }}>
          <li style={{ marginBottom: '0.5rem' }}>
            <strong style={{ color: 'var(--text)' }}>Index your code</strong> — On the <Link to="/qa">Q&A</Link> page, either upload a ZIP of your codebase or paste a public GitHub repo URL and click &quot;Index from GitHub&quot;.
          </li>
          <li style={{ marginBottom: '0.5rem' }}>
            <strong style={{ color: 'var(--text)' }}>Ask questions</strong> — Type a question about the code. Answers are generated using only the retrieved code snippets, with file paths and line ranges as proof.
          </li>
          <li style={{ marginBottom: '0.5rem' }}>
            <strong style={{ color: 'var(--text)' }}>Check status</strong> — Use the <Link to="/status">Status</Link> page to verify backend, vector DB, and LLM connectivity.
          </li>
          <li>
            <strong style={{ color: 'var(--text)' }}>View history</strong> — The last 10 Q&As are available under <Link to="/history">History</Link>.
          </li>
        </ol>
      </section>

      <p>
        <Link to="/qa" style={{
          display: 'inline-block',
          padding: '0.6rem 1.2rem',
          background: 'var(--accent)',
          color: 'var(--bg)',
          borderRadius: 6,
          fontWeight: 600,
          textDecoration: 'none',
        }}>
          Go to Q&A →
        </Link>
      </p>
    </div>
  )
}
