'use client'
import Link from 'next/link'
import { Database, ToggleLeft, ToggleRight, Settings2, ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { RAGInstance } from '../types'

interface InstanceCardProps {
  instance: RAGInstance
}

export function InstanceCard({ instance }: InstanceCardProps) {
  return (
    <Link
      href={`/dashboard/rag/instances/${instance.slug}`}
      className={cn(
        'group block rounded-bento border border-border bg-card p-5',
        'hover:border-primary/40 hover:shadow-lg transition-all duration-200',
        !instance.is_active && 'opacity-60'
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-base font-semibold text-fg group-hover:text-primary transition-colors">
          {instance.name}
        </h3>
        {instance.is_active ? (
          <ToggleRight size={20} className="text-success shrink-0" />
        ) : (
          <ToggleLeft size={20} className="text-fg-subtle shrink-0" />
        )}
      </div>

      {instance.description && (
        <p className="text-sm text-fg-muted mb-3 line-clamp-2">{instance.description}</p>
      )}

      <div className="flex items-center gap-3 mb-3 text-xs text-fg-muted">
        <div className="flex items-center gap-1.5">
          <Database size={13} />
          <span>{instance.provider_name}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Settings2 size={13} />
          <span>{instance.retrieval_config.search_strategy}</span>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3 text-xs text-fg-muted">
        <span>Top-K: {instance.retrieval_config.top_k_final}</span>
        <span>•</span>
        <span>Temp: {instance.generation_config.temperature}</span>
        <span>•</span>
        <span>{instance.generation_config.language.toUpperCase()}</span>
      </div>

      <div className="flex items-center gap-2 pt-3 border-t border-border/50">
        <StatusBadge status={instance.is_active ? 'active' : 'inactive'} />
        {instance.is_public && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-info/15 text-info font-medium">
            Public
          </span>
        )}
        {instance.retrieval_config.images_enabled && (
          <div className="ml-auto flex items-center gap-1 text-xs text-fg-subtle">
            <ImageIcon size={12} />
            <span>Images</span>
          </div>
        )}
      </div>
    </Link>
  )
}
