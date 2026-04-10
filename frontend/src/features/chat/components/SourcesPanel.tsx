'use client'
import { useState } from 'react'
import { ChevronDown, ChevronRight, FileText, ExternalLink } from 'lucide-react'
import type { Source } from '../types'

interface SourcesPanelProps {
  sources: Source[]
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  const [expanded, setExpanded] = useState(false)

  if (sources.length === 0) return null

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-fg-muted hover:text-fg transition-colors"
      >
        {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        <FileText size={12} />
        <span>{sources.length} nguồn tham khảo</span>
      </button>
      {expanded && (
        <div className="mt-2 space-y-2">
          {sources.map((source, i) => (
            <div
              key={source.chunk_id}
              className="rounded-md border border-border/50 bg-surface/60 p-3"
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <span className="text-xs font-medium text-fg">
                  [{i + 1}] {source.document_title}
                </span>
                <span className="text-[10px] text-fg-subtle shrink-0">
                  {(source.score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-fg-muted line-clamp-3">{source.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
