'use client'
import { useState } from 'react'
import { Pencil, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { useKeys, useDeleteKey, useUpdateKey } from '../hooks'
import type { AgentAPIKey, AgentAPIKeyUpdate } from '../types'
import { formatDateTime } from '@/lib/utils'

interface KeyTableProps {
  providerSlug: string
  onEdit: (key: AgentAPIKey) => void
  onAdd: () => void
  refreshKey?: number
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

export function KeyTable({ providerSlug, onEdit, onAdd, refreshKey, onToast }: KeyTableProps) {
  const [deleteTarget, setDeleteTarget] = useState<AgentAPIKey | null>(null)
  const { keys, loading, error, refetch } = useKeys(providerSlug)
  const { remove, loading: deleting } = useDeleteKey()
  const { update } = useUpdateKey()

  // Refetch when parent triggers
  useState(() => { if (refreshKey) refetch() })

  const handleDelete = async () => {
    if (!deleteTarget) return
    const ok = await remove(providerSlug, deleteTarget.id)
    if (ok) {
      onToast(`Đã xóa key "${deleteTarget.name}"`, 'success')
      refetch()
    } else {
      onToast('Xóa key thất bại', 'danger')
    }
    setDeleteTarget(null)
  }

  const handleToggle = async (key: AgentAPIKey) => {
    const data: AgentAPIKeyUpdate = { is_active: !key.is_active }
    const result = await update(providerSlug, key.id, data)
    if (result) {
      onToast(`Key "${key.name}" đã ${result.is_active ? 'bật' : 'tắt'}`, 'success')
      refetch()
    } else {
      onToast('Cập nhật thất bại', 'danger')
    }
  }

  if (loading) return <SkeletonTable rows={3} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (keys.length === 0) {
    return (
      <EmptyState
        title="Chưa có API key nào"
        description="Thêm API key để sử dụng provider này"
        actionLabel="Thêm API Key"
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
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Tên</th>
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Key Preview</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Priority</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Active</th>
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Last Used</th>
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Expires</th>
              <th className="text-right px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr
                key={key.id}
                className={cn(
                  'border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors',
                  !key.is_active && 'opacity-50'
                )}
              >
                <td className="px-4 py-3 font-medium text-fg">{key.name}</td>
                <td className="px-4 py-3 font-mono text-xs text-fg-muted">{key.key_preview}</td>
                <td className="px-4 py-3 text-center text-fg-muted">{key.priority}</td>
                <td className="px-4 py-3 text-center">
                  <button onClick={() => handleToggle(key)} className="text-fg-muted hover:text-primary transition-colors">
                    {key.is_active
                      ? <ToggleRight size={20} className="text-success" />
                      : <ToggleLeft size={20} />}
                  </button>
                </td>
                <td className="px-4 py-3 text-xs text-fg-muted">
                  {key.last_used_at ? formatDateTime(key.last_used_at) : 'Chưa dùng'}
                </td>
                <td className="px-4 py-3 text-xs text-fg-muted">
                  {key.expires_at ? formatDateTime(key.expires_at) : '—'}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-2">
                    <button onClick={() => onEdit(key)} className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors">
                      <Pencil size={14} />
                    </button>
                    <button onClick={() => setDeleteTarget(key)} className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa API Key"
        message={`Bạn chắc chắn muốn xóa key "${deleteTarget?.name}"?`}
        confirmLabel="Xóa"
      />
    </>
  )
}
