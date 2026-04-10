'use client'
import Link from 'next/link'
import { ExternalLink, Key, Settings2, ToggleLeft, ToggleRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'
import type { AgentProvider } from '../types'

interface ProviderCardProps {
  provider: AgentProvider
}

export function ProviderCard({ provider }: ProviderCardProps) {
  return (
    <Link
      href={`/dashboard/agents/${provider.slug}`}
      className={cn(
        'group block rounded-bento border border-border bg-card p-5',
        'hover:border-primary/40 hover:shadow-lg transition-all duration-200',
        !provider.is_active && 'opacity-60'
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-base font-semibold text-fg group-hover:text-primary transition-colors">
          {provider.name}
        </h3>
        {provider.is_active ? (
          <ToggleRight size={20} className="text-success shrink-0" />
        ) : (
          <ToggleLeft size={20} className="text-fg-subtle shrink-0" />
        )}
      </div>

      {provider.description && (
        <p className="text-sm text-fg-muted mb-3 line-clamp-2">{provider.description}</p>
      )}

      <div className="flex items-center gap-3 mb-3">
        <div className="flex items-center gap-1.5 text-xs text-fg-muted">
          <Key size={13} />
          <span>{provider.active_keys_count}/{provider.keys_count} keys active</span>
        </div>
      </div>

      {provider.website_url && (
        <div className="flex items-center gap-1.5 text-xs text-fg-subtle">
          <ExternalLink size={12} />
          <span className="truncate">{provider.website_url}</span>
        </div>
      )}

      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/50">
        <Badge color={provider.is_active ? 'success' : 'neutral'} className="text-[10px]">
          {provider.is_active ? 'Active' : 'Inactive'}
        </Badge>
        <div className="ml-auto flex items-center gap-1 text-xs text-fg-subtle">
          <Settings2 size={12} />
          <span>Configs</span>
        </div>
      </div>
    </Link>
  )
}
