'use client'
import { useState } from 'react'
import { Pencil, Trash2, Star, StarOff, ToggleLeft, ToggleRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { useConfigs, useDeleteConfig, useUpdateConfig } from '../hooks'
import type { AgentConfig } from '../types'

interface ConfigTableProps {
  providerSlug: string
  onEdit: (config: AgentConfig) => void
  onAdd: () => void
  refreshKey?: number
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

export function ConfigTable({ providerSlug, onEdit, onAdd, refreshKey, onToast }: ConfigTableProps) {
  const [deleteTarget, setDeleteTarget] = useState<AgentConfig | null>(null)
  const { configs, loading, error, refetch } = useConfigs(providerSlug)
  const { remove, loading: deleting } = useDeleteConfig()
  const { update } = useUpdateConfig()

  useState(() => { if (refreshKey) refetch() })

  const handleDelete = async () => {
    if (!deleteTarget) return
    const ok = await remove(providerSlug, deleteTarget.id)
    if (ok) {
      onToast(`Đã xóa config "${deleteTarget.name}"`, 'success')
      refetch()
    } else {
      onToast('Xóa config thất bại', 'danger')
    }
    setDeleteTarget(null)
  }

  const handleSetDefault = async (config: AgentConfig) => {
    const result = await update(providerSlug, config.id, { is_default: true })
    if (result) {
      onToast(`"${config.name}" đã được đặt là default`, 'success')
      refetch()
    } else {
      onToast('Cập nhật thất bại', 'danger')
    }
  }

  const handleToggle = async (config: AgentConfig) => {
    const result = await update(providerSlug, config.id, { is_active: !config.is_active })
    if (result) {
      onToast(`Config "${config.name}" đã ${result.is_active ? 'bật' : 'tắt'}`, 'success')
      refetch()
    } else {
      onToast('Cập nhật thất bại', 'danger')
    }
  }

  if (loading) return <SkeletonTable rows={3} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (configs.length === 0) {
    return (
      <EmptyState
        title="Chưa có config nào"
        description="Thêm config để cấu hình model AI"
        actionLabel="Thêm Config"
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
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Model</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Default</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Active</th>
              <th className="text-right px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {configs.map((config) => (
              <tr
                key={config.id}
                className={cn(
                  'border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors',
                  !config.is_active && 'opacity-50'
                )}
              >
                <td className="px-4 py-3 font-medium text-fg">{config.name}</td>
                <td className="px-4 py-3 font-mono text-xs text-fg-muted">{config.model_name}</td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => !config.is_default && handleSetDefault(config)}
                    className={cn(
                      'transition-colors',
                      config.is_default ? 'text-warning' : 'text-fg-subtle hover:text-warning'
                    )}
                    disabled={config.is_default}
                  >
                    {config.is_default ? <Star size={18} fill="currentColor" /> : <StarOff size={18} />}
                  </button>
                </td>
                <td className="px-4 py-3 text-center">
                  <button onClick={() => handleToggle(config)} className="text-fg-muted hover:text-primary transition-colors">
                    {config.is_active
                      ? <ToggleRight size={20} className="text-success" />
                      : <ToggleLeft size={20} />}
                  </button>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-2">
                    <button onClick={() => onEdit(config)} className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors">
                      <Pencil size={14} />
                    </button>
                    <button onClick={() => setDeleteTarget(config)} className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors">
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
        title="Xóa Config"
        message={`Bạn chắc chắn muốn xóa config "${deleteTarget?.name}"?`}
        confirmLabel="Xóa"
      />
    </>
  )
}
