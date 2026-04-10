'use client'

interface MessageContentProps {
  content: string
}

export function MessageContent({ content }: MessageContentProps) {
  // Simple markdown-like rendering
  // For production, consider using react-markdown
  return (
    <div className="prose prose-sm max-w-none text-fg prose-headings:text-fg prose-strong:text-fg prose-code:text-primary prose-code:bg-surface prose-code:px-1 prose-code:rounded">
      {content.split('\n').map((line, i) => {
        if (!line.trim()) return <br key={i} />

        // Headers
        if (line.startsWith('### '))
          return <h3 key={i} className="text-sm font-bold mt-3 mb-1">{line.slice(4)}</h3>
        if (line.startsWith('## '))
          return <h2 key={i} className="text-base font-bold mt-3 mb-1">{line.slice(3)}</h2>
        if (line.startsWith('# '))
          return <h1 key={i} className="text-lg font-bold mt-3 mb-1">{line.slice(2)}</h1>

        // Lists
        if (line.match(/^[-*] /))
          return <li key={i} className="ml-4 list-disc">{renderInline(line.slice(2))}</li>
        if (line.match(/^\d+\. /))
          return <li key={i} className="ml-4 list-decimal">{renderInline(line.replace(/^\d+\.\s/, ''))}</li>

        // Code blocks
        if (line.startsWith('```'))
          return null // simplified - skip code fence markers

        return <p key={i} className="mb-1">{renderInline(line)}</p>
      })}
    </div>
  )
}

function renderInline(text: string): React.ReactNode {
  // Bold
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i}>{part.slice(2, -2)}</strong>
    if (part.startsWith('`') && part.endsWith('`'))
      return <code key={i} className="text-xs bg-surface px-1 py-0.5 rounded">{part.slice(1, -1)}</code>
    return part
  })
}
