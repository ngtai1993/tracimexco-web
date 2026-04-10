'use client'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { useUsageLogs } from '../hooks'
import { formatDateTime } from '@/lib/utils'

interface UsageLogTableProps {
  instanceSlug: string
  limit?: number
}

export function UsageLogTable({ instanceSlug, limit = 50 }: UsageLogTableProps) {
  const { logs, loading, error } = useUsageLogs(instanceSlug, limit)

  if (loading) return <SkeletonTable rows={5} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (logs.length === 0) return <EmptyState title="Chưa có log nào" description="Chưa có truy vấn nào được ghi nhận" />

  return (
    <div className="overflow-x-auto rounded-bento border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-surface">
            <th className="text-left px-4 py-3 font-medium text-fg-muted">Query</th>
            <th className="text-center px-4 py-3 font-medium text-fg-muted">Strategy</th>
            <th className="text-center px-4 py-3 font-medium text-fg-muted">Tokens</th>
            <th className="text-center px-4 py-3 font-medium text-fg-muted">Latency</th>
            <th className="text-center px-4 py-3 font-medium text-fg-muted">Sources</th>
            <th className="text-left px-4 py-3 font-medium text-fg-muted">Thời gian</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr
              key={log.id}
              className="border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors"
            >
              <td className="px-4 py-3 text-fg max-w-[250px] truncate">{log.query}</td>
              <td className="px-4 py-3 text-center text-xs text-fg-muted capitalize">
                {log.retrieval_strategy}
              </td>
              <td className="px-4 py-3 text-center text-fg-muted">
                <span className="text-xs">{log.tokens_in}→{log.tokens_out}</span>
              </td>
              <td className="px-4 py-3 text-center text-fg-muted">{log.latency_ms}ms</td>
              <td className="px-4 py-3 text-center text-fg-muted">{log.sources_count}</td>
              <td className="px-4 py-3 text-xs text-fg-muted">{formatDateTime(log.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
