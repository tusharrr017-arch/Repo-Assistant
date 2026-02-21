/** Fix LLM fenced code blocks where language is on the next line (e.g. ``` \npython -> ```python). */
export function normalizeMarkdownForDisplay(text: string): string {
  if (!text || typeof text !== 'string') return text;
  return text
    .replace(/^```\s*\n(\w+)\s*\n/gm, '```$1\n')
    .replace(/^```\s*\n+\s*(\w+)\s*\n/gm, '```$1\n');
}
