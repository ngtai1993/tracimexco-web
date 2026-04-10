'use client'
import Link from 'next/link'
import { Database, FileText, ImageIcon, ToggleRight, ToggleLeft, Network } from 'lucide-react'
import { cn } from '@/lib/utils'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { KnowledgeBase } from '../types'

interface KBCardProps {
  kb: KnowledgeBase
}

export function KBCard({ kb }: KBCardProps) {
  return (
    <Link
      href={`/dashboard/rag/knowledge-bases/${kb.slug}`}
      className={cn(
        'group block rounded-bento border border-border bg-card p-5',
        'hover:border-primary/40 hover:shadow-lg transition-all duration-200',
        !kb.is_active && 'opacity-60'
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Database size={18} className="text-primary shrink-0" />
          <h3 className="text-base font-semibold text-fg group-hover:text-primary transition-colors">
            {kb.name}
          </h3>
        </div>
        {kb.is_active ? (
          <ToggleRight size={20} className="text-success shrink-0" />
        ) : (
          <ToggleLeft size={20} className="text-fg-subtle shrink-0" />
        )}
      </div>

      {kb.description && (
        <p className="text-sm text-fg-muted mb-3 line-clamp-2">{kb.description}</p>
      )}

      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="flex items-center gap-1.5 text-xs text-fg-muted">
          <FileText size={12} />
          <span>{kb.document_count} docs</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-fg-muted">
          <ImageIcon size={12} />
          <span>{kb.image_count} images</span>
        </div>
        <div className="text-xs text-fg-muted">
          {kb.total_chunks} chunks
        </div>
      </div>

      <div className="text-xs text-fg-subtle mb-3">
        <span className="capitalize">{kb.chunk_strategy}</span>
        <span> • {kb.chunk_size}/{kb.chunk_overlap}</span>
        <span> • {kb.embedding_dimensions}d</span>
      </div>

      <div className="flex items-center gap-2 pt-3 border-t border-border/50">
        <StatusBadge status={kb.is_active ? 'active' : 'inactive'} />
        {kb.graph_status && (
          <StatusBadge status={kb.graph_status} />
        )}
        <div className="ml-auto flex items-center gap-1 text-xs text-fg-subtle">
          <Network size={12} />
          <span>Graph</span>
        </div>
      </div>
    </Link>
  )
}
