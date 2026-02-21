const API_BASE = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || '/api');

function errFromResponse(text: string): string {
  try {
    const j = JSON.parse(text);
    const msg = j.detail ?? j.message ?? text;
    return Array.isArray(msg) ? msg[0]?.msg ?? msg[0] : String(msg);
  } catch {
    return text;
  }
}

async function request<T>(path: string, options: RequestInit & { body?: unknown } = {}): Promise<T> {
  const { body, ...rest } = options;
  const headers: HeadersInit = { ...(rest.headers as Record<string, string>) };
  if (body !== undefined && body !== null && typeof body === 'object' && !(body instanceof FormData)) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers,
    body: body instanceof FormData ? body : body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) throw new Error(errFromResponse(text));
  if (!text) return undefined as T;
  try {
    return JSON.parse(text) as T;
  } catch {
    return text as T;
  }
}

export interface HealthResp {
  status: string;
  backend: { status: string; message?: string };
  vector_db: { status: string; message?: string; chunk_count?: number };
  llm: { status: string; message?: string };
}

export interface QAResponse {
  answer: string;
  references: { file_path: string; start_line: number; end_line: number }[];
  retrieved_snippets: { file_path: string; start_line: number; end_line: number; text: string }[];
}

export type HistoryEntry = QAResponse & { question: string };

export interface RefactorResponse {
  suggestions: { title: string; description: string; file_path?: string; start_line?: number; end_line?: number }[];
  retrieved_snippets: { file_path: string; start_line: number; end_line: number; text: string }[];
  message?: string;
}

export const api = {
  health: () => request<HealthResp>('/health'),
  indexZip: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<{ status: string; message: string; chunks: number }>('/index/zip', { method: 'POST', body: form });
  },
  indexGithub: (repoUrl: string) =>
    request<{ status: string; message: string; chunks: number }>('/index/github', {
      method: 'POST',
      body: { repo_url: repoUrl },
    }),
  qa: (question: string) => request<QAResponse>('/qa', { method: 'POST', body: { question } }),
  refactor: () => request<RefactorResponse>('/refactor', { method: 'POST' }),
  history: () => request<{ history: HistoryEntry[] }>('/history'),
};
