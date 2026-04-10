'use client'
import { Clock, User } from 'lucide-react'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useVersions } from '../../hooks'

interface Props {
  postId: string
}

export function VersionTimeline({ postId }: Props) {
  const { versions, loading } = useVersions(postId)

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  if (versions.length === 0) {
    return <EmptyState title="Chưa có phiên bản" description="Các thay đổi sẽ được ghi lại tự động." />
  }

  return (
    <div className="relative pl-6 space-y-6">
      {/* Vertical line */}
      <div className="absolute left-2.5 top-2 bottom-2 w-px bg-border" />

      {versions.map((v, i) => (
        <div key={v.id} className="relative">
          {/* Dot */}
          <div
            className={`absolute -left-6 top-1 w-5 h-5 rounded-full border-2 flex items-center justify-center text-xs font-bold ${
              i === 0
                ? 'bg-primary text-white border-primary'
                : 'bg-surface text-fg-muted border-border'
            }`}
          >
            {v.version_number}
          </div>

          <div className="rounded-bento border border-border bg-card p-4 space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-fg">{v.title}</h4>
              <span className="text-xs text-fg-muted flex items-center gap-1">
                <Clock size={12} />
                {new Date(v.created_at).toLocaleString('vi-VN')}
              </span>
            </div>

            {v.changed_by_name && (
              <p className="text-xs text-fg-muted flex items-center gap-1">
                <User size={12} />
                {v.changed_by_name}
              </p>
            )}

            <div className="text-sm text-fg whitespace-pre-wrap line-clamp-4 bg-surface rounded p-2">
              {v.content}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
