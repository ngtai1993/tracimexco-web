'use client'
import { useState } from 'react'
import { Trash2, UserPlus } from 'lucide-react'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useAccess, useRevokeAccess } from '../hooks'
import { formatDateTime } from '@/lib/utils'
import type { RAGAccessPermission } from '../types'

interface AccessTableProps {
  instanceSlug: string
  onAdd: () => void
  refreshKey?: number
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

export function AccessTable({ instanceSlug, onAdd, refreshKey, onToast }: AccessTableProps) {
  const [revokeTarget, setRevokeTarget] = useState<RAGAccessPermission | null>(null)
  const { permissions, loading, error, refetch } = useAccess(instanceSlug)
  const { revoke, loading: revoking } = useRevokeAccess()

  useState(() => { if (refreshKey) refetch() })

  const handleRevoke = async () => {
    if (!revokeTarget) return
    const ok = await revoke(instanceSlug, revokeTarget.id)
    if (ok) {
      onToast(`Đã thu hồi quyền của ${revokeTarget.user_email}`, 'success')
      refetch()
    } else {
      onToast('Thu hồi quyền thất bại', 'danger')
    }
    setRevokeTarget(null)
  }

  if (loading) return <SkeletonTable rows={3} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (permissions.length === 0) {
    return (
      <EmptyState
        icon={<UserPlus size={40} strokeWidth={1.5} />}
        title="Chưa có ai được cấp quyền"
        description="Cấp quyền cho người dùng để họ sử dụng instance này"
        actionLabel="Cấp quyền"
        onAction={onAdd}
      />
    )
  }

  return (
    <>
      <div className="overflow-x-auto rounded-bento border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface">
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Email</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Quyền</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Query/Ngày</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Token/Tháng</th>
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Hết hạn</th>
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Cấp bởi</th>
              <th className="text-right px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {permissions.map((perm) => (
              <tr
                key={perm.id}
                className="border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors"
              >
                <td className="px-4 py-3 font-medium text-fg">{perm.user_email}</td>
                <td className="px-4 py-3 text-center">
                  <StatusBadge status={perm.access_level === 'manage' ? 'active' : 'pending'} />
                  <span className="text-xs ml-1 capitalize">{perm.access_level}</span>
                </td>
                <td className="px-4 py-3 text-center text-fg-muted">{perm.daily_query_limit}</td>
                <td className="px-4 py-3 text-center text-fg-muted">
                  {perm.monthly_token_limit.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-xs text-fg-muted">
                  {perm.expires_at ? formatDateTime(perm.expires_at) : 'Không giới hạn'}
                </td>
                <td className="px-4 py-3 text-xs text-fg-muted">
                  {perm.granted_by_email ?? '—'}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => setRevokeTarget(perm)}
                    className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors"
                    title="Thu hồi quyền"
                  >
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        open={!!revokeTarget}
        onClose={() => setRevokeTarget(null)}
        onConfirm={handleRevoke}
        loading={revoking}
        title="Thu hồi quyền"
        message={`Bạn chắc chắn muốn thu hồi quyền của "${revokeTarget?.user_email}"?`}
        confirmLabel="Thu hồi"
      />
    </>
  )
}
