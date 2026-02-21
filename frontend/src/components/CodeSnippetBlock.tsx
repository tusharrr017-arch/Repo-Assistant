import React from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const codeStyle = {
  ...oneDark,
  'code[class*="language-"]': {
    ...oneDark['code[class*="language-"]'],
    fontSize: '0.8125rem',
    lineHeight: 1.5,
  },
  'pre[class*="language-"]': {
    ...oneDark['pre[class*="language-"]'],
    margin: 0,
    padding: '1rem',
    borderRadius: 0,
  },
}

interface CodeSnippetBlockProps {
  filePath: string
  startLine: number
  endLine: number
  text: string
  language?: string
}

export default function CodeSnippetBlock({
  filePath,
  startLine,
  endLine,
  text,
  language = 'text',
}: CodeSnippetBlockProps) {
  const ext = filePath.split('.').pop()?.toLowerCase()
  const langMap: Record<string, string> = {
    py: 'python',
    js: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    jsx: 'javascript',
    json: 'json',
    md: 'markdown',
    sh: 'bash',
    yaml: 'yaml',
    yml: 'yaml',
    html: 'html',
    css: 'css',
  }
  const resolvedLang = language !== 'text' ? language : (langMap[ext || ''] || 'text')

  return (
    <div className="code-snippet-block">
      <div className="code-snippet-header">
        <span className="code-snippet-path">{filePath}</span>
        <span className="code-snippet-lines">
          Lines {startLine}–{endLine}
        </span>
      </div>
      <SyntaxHighlighter
        style={codeStyle}
        language={resolvedLang}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderTopLeftRadius: 0,
          borderTopRightRadius: 0,
          borderRadius: 8,
        }}
        codeTagProps={{ style: { fontFamily: 'var(--font-mono)' } }}
      >
        {text}
      </SyntaxHighlighter>
    </div>
  )
}
