'use client'
import { useState } from 'react'
import {
  X, FileText, Globe, Type, File, ImageIcon,
  Hash, Zap, Calendar, ChevronDown, ChevronRight,
  ExternalLink, Layers, AlertCircle,
} from 'lucide-react'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { formatDateTime } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { useDocumentChunks } from '../hooks'
import type { Document, DocumentChunk } from '../types'

interface DocumentPreviewPanelProps {
  document: Document | null
  onClose: () => void
}

const sourceTypeLabel: Record<string, string> = {
  file_upload: 'File Upload',
  text: 'Văn bản',
  url: 'URL',
  image_upload: 'Hình ảnh',
  api: 'API',
}

const sourceTypeIcon: Record<string, React.ReactNode> = {
  file_upload: <File size={14} />,
  text: <Type size={14} />,
  url: <Globe size={14} />,
  image_upload: <ImageIcon size={14} />,
  api: <Zap size={14} />,
}

// ── Chunk list sub-component ──────────────────────────────────────────────────
function ChunkList({ docId, docTitle }: { docId: string; docTitle: string }) {
  const { chunks, loading, error } = useDocumentChunks(docId)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  if (loading) return <SkeletonTable rows={3} />
  if (error) return <p className="text-xs text-danger py-2">{error}</p>
  if (chunks.length === 0) {
    return <p className="text-xs text-fg-muted py-2">Chưa có chunk nào.</p>
  }

  return (
    <div className="space-y-1 max-h-72 overflow-y-auto pr-1">
      <p className="text-xs text-fg-muted mb-2">
        {docTitle} — {chunks.length} chunks
      </p>
      {chunks.map((chunk: DocumentChunk) => (
        <div
          key={chunk.id}
          className="rounded-lg border border-border bg-surface/60"
        >
          <button
            onClick={() => setExpandedId(expandedId === chunk.id ? null : chunk.id)}
            className="w-full flex items-center justify-between px-3 py-2 text-xs text-left hover:bg-surface transition-colors"
          >
            <span className="flex items-center gap-2 text-fg-muted">
              <Hash size={11} className="shrink-0" />
              Chunk {chunk.chunk_index + 1}
              {chunk.is_image_chunk && (
                <span className="text-info font-medium">· image</span>
              )}
            </span>
            <span className="flex items-center gap-2 text-fg-subtle shrink-0">
              <Zap size={10} /> {chunk.token_count}t
              {expandedId === chunk.id
                ? <ChevronDown size={12} />
                : <ChevronRight size={12} />
              }
            </span>
          </button>
          {expandedId === chunk.id && (
            <div className="px-3 pb-3 pt-1 border-t border-border/50">
              <pre className="text-xs text-fg-muted whitespace-pre-wrap break-words font-mono leading-relaxed max-h-48 overflow-y-auto">
                {chunk.content}
              </pre>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// ── Main panel ────────────────────────────────────────────────────────────────
export function DocumentPreviewPanel({ document: doc, onClose }: DocumentPreviewPanelProps) {
  const [showChunks, setShowChunks] = useState(false)

  if (!doc) return null

  const isComplete = doc.processing_status === 'completed'
  const isFailed = doc.processing_status === 'failed'

  return (
    <div
      className={cn(
        'fixed inset-y-0 right-0 z-40 w-full max-w-md bg-card border-l border-border shadow-2xl',
        'flex flex-col',
        'animate-in slide-in-from-right duration-200',
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between p-5 border-b border-border shrink-0">
        <div className="flex items-start gap-3 min-w-0 pr-2">
          <div className="p-2 rounded-lg bg-surface border border-border shrink-0 mt-0.5">
            {doc.is_image
              ? <ImageIcon size={16} className="text-info" />
              : (sourceTypeIcon[doc.source_type] ?? <FileText size={16} className="text-fg-muted" />)
            }
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-fg text-sm leading-snug break-words">{doc.title}</h3>
            {doc.description && (
              <p className="text-xs text-fg-muted mt-0.5 line-clamp-2">{doc.description}</p>
            )}
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-border/40 text-fg-muted hover:text-fg transition-colors shrink-0"
        >
          <X size={16} />
        </button>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">

        {/* Status + meta row */}
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={doc.processing_status} />
          <span className="inline-flex items-center gap-1 text-xs text-fg-muted bg-surface border border-border rounded-full px-2.5 py-0.5">
            {sourceTypeIcon[doc.source_type]}
            {sourceTypeLabel[doc.source_type] ?? doc.source_type}
          </span>
          {doc.is_image && (
            <span className="inline-flex items-center gap-1 text-xs text-info bg-info/10 rounded-full px-2.5 py-0.5">
              <ImageIcon size={11} /> Hình ảnh
            </span>
          )}
        </div>

        {/* Stats chips */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-surface rounded-bento border border-border p-3 text-center">
            <p className="text-lg font-semibold text-fg">{doc.chunk_count}</p>
            <p className="text-xs text-fg-muted">Chunks</p>
          </div>
          <div className="bg-surface rounded-bento border border-border p-3 text-center">
            <p className="text-lg font-semibold text-fg">{doc.token_count.toLocaleString()}</p>
            <p className="text-xs text-fg-muted">Tokens</p>
          </div>
        </div>

        {/* URL type — clickable link */}
        {doc.source_type === 'url' && doc.source_url && (
          <section>
            <h4 className="text-xs font-semibold text-fg-muted uppercase tracking-wide mb-2">Nguồn URL</h4>
            <a
              href={doc.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-primary hover:underline break-all"
            >
              <ExternalLink size={13} className="shrink-0" />
              {doc.source_url}
            </a>
          </section>
        )}

        {/* Image — caption & tags */}
        {doc.is_image && (
          <section>
            <h4 className="text-xs font-semibold text-fg-muted uppercase tracking-wide mb-2">
              <ImageIcon size={12} className="inline mr-1" />Mô tả hình ảnh
            </h4>
            {doc.image_caption ? (
              <p className="text-sm text-fg bg-surface rounded-lg p-3 border border-border">
                {doc.image_caption}
              </p>
            ) : (
              <p className="text-xs text-fg-subtle italic">Chưa có caption</p>
            )}
            {doc.image_tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {doc.image_tags.map((tag) => (
                  <span key={tag} className="text-xs bg-primary/10 text-primary rounded-full px-2 py-0.5">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Text content preview */}
        {doc.content_text && (
          <section>
            <h4 className="text-xs font-semibold text-fg-muted uppercase tracking-wide mb-2">
              <FileText size={12} className="inline mr-1" />Nội dung
            </h4>
            <div className="relative">
              <pre className="text-xs text-fg-muted whitespace-pre-wrap break-words font-sans leading-relaxed bg-surface rounded-lg p-3 border border-border max-h-56 overflow-y-auto">
                {doc.content_text}
              </pre>
            </div>
          </section>
        )}

        {/* Processing error */}
        {isFailed && doc.processing_error && (
          <section>
            <h4 className="text-xs font-semibold text-danger uppercase tracking-wide mb-2 flex items-center gap-1">
              <AlertCircle size={12} /> Lỗi xử lý
            </h4>
            <p className="text-xs text-danger bg-danger/5 rounded-lg p-3 border border-danger/20">
              {doc.processing_error}
            </p>
          </section>
        )}

        {/* Metadata */}
        {Object.keys(doc.metadata ?? {}).length > 0 && (
          <section>
            <h4 className="text-xs font-semibold text-fg-muted uppercase tracking-wide mb-2">Metadata</h4>
            <div className="bg-surface rounded-lg border border-border p-3 space-y-1">
              {Object.entries(doc.metadata).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-3 text-xs">
                  <span className="text-fg-subtle font-mono">{k}</span>
                  <span className="text-fg truncate max-w-[55%] text-right">{String(v)}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Timestamps */}
        <section className="space-y-1">
          <h4 className="text-xs font-semibold text-fg-muted uppercase tracking-wide mb-2">
            <Calendar size={12} className="inline mr-1" />Thời gian
          </h4>
          <div className="text-xs text-fg-muted space-y-1">
            <div className="flex justify-between">
              <span>Tạo lúc</span>
              <span>{formatDateTime(doc.created_at)}</span>
            </div>
            {doc.processed_at && (
              <div className="flex justify-between">
                <span>Xử lý xong</span>
                <span>{formatDateTime(doc.processed_at)}</span>
              </div>
            )}
          </div>
        </section>

        {/* Chunks section — expandable */}
        {isComplete && (
          <section>
            <button
              onClick={() => setShowChunks((v) => !v)}
              className="flex items-center justify-between w-full text-xs font-semibold text-fg-muted uppercase tracking-wide mb-2 hover:text-fg transition-colors"
            >
              <span className="flex items-center gap-1">
                <Layers size={12} />Chunks ({doc.chunk_count})
              </span>
              {showChunks ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            {showChunks && (
              <ChunkList docId={doc.id} docTitle={doc.title} />
            )}
          </section>
        )}
      </div>
    </div>
  )
}
