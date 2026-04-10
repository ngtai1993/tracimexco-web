'use client'
import { Users, Zap, Clock, ImageIcon, MessageSquare } from 'lucide-react'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { useAnalytics } from '../hooks'

interface AnalyticsDashboardProps {
  instanceSlug: string
  days?: number
}

export function AnalyticsDashboard({ instanceSlug, days = 7 }: AnalyticsDashboardProps) {
  const { analytics, loading, error } = useAnalytics(instanceSlug, days)

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (!analytics) return null

  const cards: { label: string; value: string | number; icon: React.ReactNode; color: string }[] = [
    {
      label: 'Tổng queries',
      value: analytics.total_queries.toLocaleString(),
      icon: <MessageSquare size={18} />,
      color: 'text-primary',
    },
    {
      label: 'Người dùng',
      value: analytics.unique_users,
      icon: <Users size={18} />,
      color: 'text-info',
    },
    {
      label: 'Tokens In',
      value: analytics.total_tokens_in.toLocaleString(),
      icon: <Zap size={18} />,
      color: 'text-warning',
    },
    {
      label: 'Tokens Out',
      value: analytics.total_tokens_out.toLocaleString(),
      icon: <Zap size={18} />,
      color: 'text-success',
    },
    {
      label: 'Avg Latency',
      value: `${analytics.avg_latency_ms.toFixed(0)}ms`,
      icon: <Clock size={18} />,
      color: 'text-fg-muted',
    },
    {
      label: 'Images',
      value: analytics.total_images,
      icon: <ImageIcon size={18} />,
      color: 'text-info',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-bento border border-border bg-card p-4 flex items-start gap-3"
        >
          <div className={card.color}>{card.icon}</div>
          <div>
            <p className="text-2xl font-bold text-fg">{card.value}</p>
            <p className="text-xs text-fg-muted">{card.label}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
