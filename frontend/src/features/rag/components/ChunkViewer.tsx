'use client'
import { useState } from 'react'
import { ChevronDown, ChevronRight, Hash, FileText } from 'lucide-react'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { useDocumentChunks } from '../hooks'
import type { DocumentChunk } from '../types'

interface ChunkViewerProps {
  docId: string
  docTitle: string
}

export function ChunkViewer({ docId, docTitle }: ChunkViewerProps) {
  const { chunks, loading, error } = useDocumentChunks(docId)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  if (loading) return <SkeletonTable rows={5} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (chunks.length === 0) {
    return <EmptyState title="Không có chunks" description="Tài liệu chưa được xử lý" />
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-fg-muted mb-3">
        <FileText size={14} className="inline mr-1" />
        {docTitle} — {chunks.length} chunks
      </p>
      {chunks.map((chunk) => (
        <ChunkItem
          key={chunk.id}
          chunk={chunk}
          expanded={expandedId === chunk.id}
          onToggle={() => setExpandedId(expandedId === chunk.id ? null : chunk.id)}
        />
      ))}
    </div>
  )
}

function ChunkItem({
  chunk,
  expanded,
  onToggle,
}: {
  chunk: DocumentChunk
  expanded: boolean
  onToggle: () => void
}) {
  return (
    <div className="rounded-bento border border-border overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-surface/60 transition-colors"
      >
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <div className="flex items-center gap-2 text-sm flex-1 min-w-0">
          <Hash size={12} className="text-fg-subtle shrink-0" />
          <span className="font-medium text-fg">Chunk {chunk.chunk_index + 1}</span>
          <span className="text-fg-muted">• {chunk.token_count} tokens</span>
          {chunk.is_image_chunk && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-info/15 text-info">Image</span>
          )}
        </div>
      </button>
      {expanded && (
        <div className="px-4 pb-4 border-t border-border/50">
          <pre className="text-sm text-fg whitespace-pre-wrap bg-surface rounded-md p-3 mt-2 max-h-[300px] overflow-y-auto">
            {chunk.content}
          </pre>
          {Object.keys(chunk.metadata).length > 0 && (
            <details className="mt-2">
              <summary className="text-xs text-fg-subtle cursor-pointer">Metadata</summary>
              <pre className="text-xs text-fg-muted mt-1 bg-surface rounded p-2">
                {JSON.stringify(chunk.metadata, null, 2)}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  )
}
