'use client'
import { cn } from '@/lib/utils'
import { useMyAccess } from '../hooks'

interface QuotaIndicatorProps {
  instanceSlug: string
  className?: string
}

export function QuotaIndicator({ instanceSlug, className }: QuotaIndicatorProps) {
  const { access, loading } = useMyAccess(instanceSlug)

  if (loading || !access || !access.has_access) return null

  const queryPct = access.daily_queries_used && access.daily_query_limit
    ? (access.daily_queries_used / access.daily_query_limit) * 100
    : 0

  const tokenPct = access.monthly_tokens_used && access.monthly_token_limit
    ? (access.monthly_tokens_used / access.monthly_token_limit) * 100
    : 0

  return (
    <div className={cn('flex items-center gap-4 text-[10px] text-fg-subtle', className)}>
      <div className="flex items-center gap-1.5">
        <span>Queries:</span>
        <div className="w-16 h-1.5 rounded-full bg-border overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all',
              queryPct > 80 ? 'bg-danger' : queryPct > 50 ? 'bg-warning' : 'bg-success'
            )}
            style={{ width: `${Math.min(queryPct, 100)}%` }}
          />
        </div>
        <span>{access.daily_queries_used}/{access.daily_query_limit}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <span>Tokens:</span>
        <div className="w-16 h-1.5 rounded-full bg-border overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all',
              tokenPct > 80 ? 'bg-danger' : tokenPct > 50 ? 'bg-warning' : 'bg-success'
            )}
            style={{ width: `${Math.min(tokenPct, 100)}%` }}
          />
        </div>
        <span>{((access.monthly_tokens_used ?? 0) / 1000).toFixed(0)}k</span>
      </div>
    </div>
  )
}
