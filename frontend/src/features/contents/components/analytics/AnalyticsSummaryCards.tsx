'use client'
import {
  FileText,
  Sparkles,
  CheckCircle,
  Clock,
  Globe,
} from 'lucide-react'
import { useAnalyticsSummary } from '../../hooks'
import { STATUS_LABELS, PLATFORM_LABELS } from '../../constants'
import type { PostStatus, PlatformType } from '../../types'

export function AnalyticsSummaryCards() {
  const { summary, loading } = useAnalyticsSummary()

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="rounded-bento border border-border bg-card p-4 h-20 animate-pulse" />
        ))}
      </div>
    )
  }

  if (!summary) return null

  const topCards = [
    {
      label: 'Tổng bài viết',
      value: summary.total_posts,
      icon: <FileText size={20} />,
      color: 'text-primary',
    },
    {
      label: 'AI tạo',
      value: summary.ai_generated_count,
      icon: <Sparkles size={20} />,
      color: 'text-amber-500',
    },
    {
      label: 'Tỷ lệ xuất bản',
      value:
        summary.publish_success_rate != null
          ? `${Math.round(summary.publish_success_rate)}%`
          : '—',
      icon: <CheckCircle size={20} />,
      color: 'text-emerald-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Top cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {topCards.map((card) => (
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

      {/* Status & platform breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* By Status */}
        <div className="rounded-bento border border-border bg-card p-4 space-y-3">
          <h4 className="text-sm font-semibold text-fg flex items-center gap-2">
            <Clock size={14} className="text-fg-muted" />
            Theo trạng thái
          </h4>
          <div className="space-y-2">
            {Object.entries(summary.by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between text-sm">
                <span className="text-fg-muted">
                  {STATUS_LABELS[status as PostStatus] || status}
                </span>
                <span className="font-medium text-fg">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* By Platform */}
        <div className="rounded-bento border border-border bg-card p-4 space-y-3">
          <h4 className="text-sm font-semibold text-fg flex items-center gap-2">
            <Globe size={14} className="text-fg-muted" />
            Theo nền tảng
          </h4>
          <div className="space-y-2">
            {Object.entries(summary.by_platform).map(([platform, count]) => (
              <div key={platform} className="flex items-center justify-between text-sm">
                <span className="text-fg-muted">
                  {PLATFORM_LABELS[platform as PlatformType] || platform}
                </span>
                <span className="font-medium text-fg">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
