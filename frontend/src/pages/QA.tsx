import { useState, useCallback } from 'react'
import { api, QAResponse, RefactorResponse } from '../api'
import MarkdownContent from '../components/MarkdownContent'
import CodeSnippetBlock from '../components/CodeSnippetBlock'

export default function QA() {
  const [zipFile, setZipFile] = useState<File | null>(null)
  const [githubUrl, setGithubUrl] = useState('')
  const [indexError, setIndexError] = useState('')
  const [indexSuccess, setIndexSuccess] = useState('')
  const [question, setQuestion] = useState('')
  const [qaResult, setQaResult] = useState<QAResponse | null>(null)
  const [qaError, setQaError] = useState('')
  const [loading, setLoading] = useState(false)
  const [refactorResult, setRefactorResult] = useState<RefactorResponse | null>(null)
  const [refactorError, setRefactorError] = useState('')
  const [refactorLoading, setRefactorLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const doIndexZip = async () => {
    if (!zipFile) {
      setIndexError('Please select or drop a ZIP file')
      return
    }
    setIndexError('')
    setIndexSuccess('')
    setLoading(true)
    try {
      const r = await api.indexZip(zipFile)
      setIndexSuccess(`Indexed ${r.chunks} chunks.`)
      setQaResult(null)
      setQaError('')
    } catch (e) {
      setIndexError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.name?.toLowerCase().endsWith('.zip')) {
      setZipFile(file)
      setIndexError('')
    } else {
      setIndexError('Please drop a .zip file')
    }
  }, [])

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const doIndexGithub = async () => {
    const url = githubUrl.trim()
    if (!url) {
      setIndexError('Please enter a GitHub repo URL')
      return
    }
    setIndexError('')
    setIndexSuccess('')
    setLoading(true)
    try {
      const r = await api.indexGithub(url)
      setIndexSuccess(`Indexed ${r.chunks} chunks.`)
      setQaResult(null)
      setQaError('')
    } catch (e) {
      setIndexError(e instanceof Error ? e.message : 'Invalid GitHub URL or repo not accessible')
    } finally {
      setLoading(false)
    }
  }

  const doQA = async () => {
    const q = question.trim()
    if (!q) {
      setQaError('Please enter a question')
      return
    }
    setQaError('')
    setQaResult(null)
    setLoading(true)
    try {
      const r = await api.qa(q)
      setQaResult(r)
    } catch (e) {
      setQaError(e instanceof Error ? e.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  const doRefactor = async () => {
    setRefactorError('')
    setRefactorResult(null)
    setRefactorLoading(true)
    try {
      const r = await api.refactor()
      setRefactorResult(r)
    } catch (e) {
      setRefactorError(e instanceof Error ? e.message : 'Request failed')
    } finally {
      setRefactorLoading(false)
    }
  }

  return (
    <div>
      <h1 style={{ marginTop: 0, fontWeight: 600 }}>Q&A</h1>

      <section className="section-card">
        <h2>1. Index codebase</h2>
        <label className="section-label">Upload ZIP</label>
        <label
          htmlFor="zip-upload"
          style={{ cursor: 'pointer', display: 'block', marginBottom: '0.75rem' }}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
        >
          <input
            type="file"
            accept=".zip"
            onChange={(e) => {
              setZipFile(e.target.files?.[0] ?? null)
              setIndexError('')
            }}
            style={{ display: 'none' }}
            id="zip-upload"
          />
          <div
            style={{
              border: `2px dashed ${dragOver ? 'var(--accent)' : 'var(--border)'}`,
              borderRadius: 8,
              padding: '1.25rem',
              textAlign: 'center',
              background: dragOver ? 'rgba(91, 141, 239, 0.06)' : 'var(--bg)',
              transition: 'border-color 0.15s, background 0.15s',
            }}
          >
            <span style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
              {zipFile ? (
                <strong style={{ color: 'var(--text)' }}>{zipFile.name}</strong>
              ) : (
                <>Drop a .zip here or click to browse</>
              )}
            </span>
          </div>
        </label>
        <button className="btn-primary" onClick={doIndexZip} disabled={loading} style={{ marginBottom: '1rem' }}>
          {loading ? 'Indexing…' : 'Index ZIP'}
        </button>
        <label className="section-label" style={{ marginTop: '1rem' }}>Or GitHub repo URL</label>
        <input
          type="url"
          placeholder="https://github.com/owner/repo"
          value={githubUrl}
          onChange={(e) => { setGithubUrl(e.target.value); setIndexError('') }}
          className="input-text"
          style={{ maxWidth: 420, marginBottom: '0.5rem' }}
        />
        <button className="btn-primary" onClick={doIndexGithub} disabled={loading}>
          {loading ? 'Cloning…' : 'Index from GitHub'}
        </button>
        {indexError && <p style={{ color: 'var(--error)', marginTop: 8, marginBottom: 0 }}>{indexError}</p>}
        {indexSuccess && <p style={{ color: 'var(--success)', marginTop: 8, marginBottom: 0 }}>{indexSuccess}</p>}
      </section>

      <section className="section-card">
        <h2>2. Ask a question</h2>
        <textarea
          placeholder="e.g. Where is the main entry point? How does authentication work?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          className="input-text"
          style={{ resize: 'vertical', minHeight: 80 }}
        />
        <button className="btn-primary" onClick={doQA} disabled={loading} style={{ marginTop: '0.75rem' }}>
          {loading ? '…' : 'Ask'}
        </button>
        {qaError && <p style={{ color: 'var(--error)', marginTop: 8 }}>{qaError}</p>}
        {qaResult && (
          <div style={{ marginTop: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span className="badge badge-success">Answer</span>
            </div>
            <div className="markdown-content" style={{ marginBottom: '1.25rem' }}>
              <MarkdownContent content={qaResult.answer} />
            </div>
            {qaResult.references?.length > 0 && (
              <>
                <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                  Cited in answer
                </h3>
                <ul style={{ paddingLeft: '1.25rem', marginBottom: '1rem', color: 'var(--muted)', fontSize: '0.875rem' }}>
                  {qaResult.references.map((ref, i) => (
                    <li key={i} style={{ marginBottom: '0.25rem' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>{ref.file_path}</span>
                      {' '}(lines {ref.start_line}–{ref.end_line})
                    </li>
                  ))}
                </ul>
              </>
            )}
            {qaResult.retrieved_snippets?.length > 0 && (
              <>
                <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                  All context sent to the model
                </h3>
                {qaResult.retrieved_snippets.map((s, i) => (
                  <CodeSnippetBlock
                    key={i}
                    filePath={s.file_path}
                    startLine={s.start_line}
                    endLine={s.end_line}
                    text={s.text}
                  />
                ))}
              </>
            )}
          </div>
        )}
      </section>

      <section className="section-card">
        <h2>Refactor suggestions</h2>
        <p style={{ color: 'var(--muted)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
          Generate refactor suggestions with file references from the indexed codebase.
        </p>
        <button className="btn-primary" onClick={doRefactor} disabled={refactorLoading}>
          {refactorLoading ? 'Generating…' : 'Generate refactor suggestions'}
        </button>
        {refactorError && <p style={{ color: 'var(--error)', marginTop: 8 }}>{refactorError}</p>}
        {refactorResult && (
          <div style={{ marginTop: '1rem' }}>
            {refactorResult.message && <p style={{ color: 'var(--muted)' }}>{refactorResult.message}</p>}
            {refactorResult.suggestions?.map((s, i) => (
              <div key={i} style={{ marginBottom: '1.25rem' }}>
                <strong style={{ color: 'var(--text)' }}>{s.title}</strong>
                {s.file_path && (
                  <span style={{ color: 'var(--muted)', marginLeft: 8, fontSize: '0.875rem' }}>
                    {s.file_path} (lines {s.start_line}–{s.end_line})
                  </span>
                )}
                <div style={{ marginTop: 6 }} className="markdown-content">
                  <MarkdownContent content={s.description} />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
