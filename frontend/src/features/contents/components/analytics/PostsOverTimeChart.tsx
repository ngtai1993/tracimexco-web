'use client'
import { useState } from 'react'
import { BarChart3 } from 'lucide-react'
import { Select } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useAnalyticsPosts } from '../../hooks'

const GROUP_OPTIONS = [
  { value: 'day', label: 'Theo ngày' },
  { value: 'week', label: 'Theo tuần' },
  { value: 'month', label: 'Theo tháng' },
]

export function PostsOverTimeChart() {
  const [groupBy, setGroupBy] = useState<'day' | 'week' | 'month'>('day')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  const { dataPoints, loading } = useAnalyticsPosts({
    group_by: groupBy,
    ...(from && { from }),
    ...(to && { to }),
  })

  const max = Math.max(...dataPoints.map((d) => d.count), 1)

  return (
    <div className="rounded-bento border border-border bg-card p-4 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h4 className="text-sm font-semibold text-fg flex items-center gap-2">
          <BarChart3 size={16} className="text-primary" />
          Bài viết theo thời gian
        </h4>

        <div className="flex items-center gap-2">
          <Input
            type="date"
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            className="w-36 text-xs"
          />
          <span className="text-xs text-fg-muted">→</span>
          <Input
            type="date"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            className="w-36 text-xs"
          />
          <Select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value as 'day' | 'week' | 'month')}
            options={GROUP_OPTIONS}
            className="w-32 text-xs"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner size={24} />
        </div>
      ) : dataPoints.length === 0 ? (
        <EmptyState title="Không có dữ liệu" description="Thay đổi khoảng thời gian để xem dữ liệu." />
      ) : (
        <div className="flex items-end gap-1 h-48">
          {dataPoints.map((d) => (
            <div key={d.period} className="flex-1 flex flex-col items-center gap-1 min-w-0">
              <span className="text-xs font-medium text-fg">{d.count}</span>
              <div
                className="w-full bg-primary/80 rounded-t transition-all"
                style={{ height: `${(d.count / max) * 100}%`, minHeight: d.count > 0 ? 4 : 0 }}
              />
              <span className="text-[10px] text-fg-muted truncate w-full text-center">
                {d.period}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
