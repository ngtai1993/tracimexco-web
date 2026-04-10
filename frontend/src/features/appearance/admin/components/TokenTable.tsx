'use client'
import { useState } from 'react'
import { Pencil, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ColorSwatch } from '@/components/ui/ColorSwatch'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { useToast } from '@/hooks/useToast'
import { ToastContainer } from '@/components/ui/Toast'
import { useTokens, useDeleteToken, useUpdateToken } from '../hooks'
import type { ColorTokenAdmin } from '../types'

type ModeFilter = 'all' | 'light' | 'dark'
type GroupFilter = 'all' | 'brand' | 'semantic' | 'neutral' | 'custom'

interface TokenTableProps {
  onEdit: (token: ColorTokenAdmin) => void
  refreshKey?: number
}

export function TokenTable({ onEdit, refreshKey }: TokenTableProps) {
  const [modeFilter, setModeFilter] = useState<ModeFilter>('all')
  const [groupFilter, setGroupFilter] = useState<GroupFilter>('all')
  const [includeInactive, setIncludeInactive] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<ColorTokenAdmin | null>(null)

  const { tokens, loading, error, refetch } = useTokens({ include_inactive: includeInactive })
  const { remove, loading: deleting } = useDeleteToken()
  const { update } = useUpdateToken()
  const { toasts, addToast, removeToast } = useToast()

  // Refresh khi parent yêu cầu
  useState(() => { if (refreshKey) refetch() })

  const filtered = tokens.filter((t) => {
    if (modeFilter !== 'all' && t.mode !== modeFilter) return false
    if (groupFilter !== 'all' && t.group !== groupFilter) return false
    return true
  })

  const handleDelete = async () => {
    if (!deleteTarget) return
    const ok = await remove(deleteTarget.id)
    if (ok) {
      addToast(`Đã xóa token "${deleteTarget.key}"`, 'success')
      refetch()
    } else {
      addToast('Xóa token thất bại', 'danger')
    }
    setDeleteTarget(null)
  }

  const handleToggleActive = async (token: ColorTokenAdmin) => {
    const result = await update(token.id, { is_active: !token.is_active })
    if (result) {
      addToast(`Token "${token.key}" đã ${result.is_active ? 'bật' : 'tắt'}`, 'success')
      refetch()
    } else {
      addToast('Cập nhật thất bại', 'danger')
    }
  }

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <div className="flex gap-1 items-center">
          <span className="text-xs text-fg-muted mr-1">Mode:</span>
          {(['all', 'light', 'dark'] as ModeFilter[]).map((m) => (
            <button
              key={m}
              onClick={() => setModeFilter(m)}
              className={cn(
                'px-2.5 py-1 rounded text-xs font-medium transition-colors',
                modeFilter === m
                  ? 'bg-primary text-primary-fg'
                  : 'bg-surface text-fg-muted hover:text-fg border border-border'
              )}
            >
              {m === 'all' ? 'Tất cả' : m}
            </button>
          ))}
        </div>
        <div className="flex gap-1 items-center">
          <span className="text-xs text-fg-muted mr-1">Group:</span>
          {(['all', 'brand', 'semantic', 'neutral', 'custom'] as GroupFilter[]).map((g) => (
            <button
              key={g}
              onClick={() => setGroupFilter(g)}
              className={cn(
                'px-2.5 py-1 rounded text-xs font-medium transition-colors',
                groupFilter === g
                  ? 'bg-primary text-primary-fg'
                  : 'bg-surface text-fg-muted hover:text-fg border border-border'
              )}
            >
              {g === 'all' ? 'Tất cả' : g}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2 text-xs text-fg-muted ml-auto cursor-pointer">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="accent-primary"
          />
          Hiện token không hoạt động
        </label>
      </div>

      {/* Table */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-11 rounded-lg bg-surface animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-3 py-12 text-danger">
          <p className="text-sm">{error}</p>
          <button onClick={refetch} className="text-xs text-primary hover:underline">Thử lại</button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-12 text-fg-muted">
          <p className="text-sm">Chưa có token nào</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-bento border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface">
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Màu</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Key</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Tên</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Mode</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Group</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Giá trị</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Order</th>
                <th className="text-center px-4 py-3 font-medium text-fg-muted">Active</th>
                <th className="text-right px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {filtered.map((token) => (
                <tr
                  key={token.id}
                  className={cn(
                    'border-b border-border/50 last:border-0 transition-colors hover:bg-surface/60',
                    !token.is_active && 'opacity-50'
                  )}
                >
                  <td className="px-4 py-3">
                    <ColorSwatch value={token.value} size="sm" />
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-fg">{token.key}</td>
                  <td className="px-4 py-3 text-fg-muted">{token.name}</td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'inline-block px-2 py-0.5 rounded text-xs font-medium',
                      token.mode === 'light' ? 'bg-warning/15 text-warning' : 'bg-info/15 text-info'
                    )}>
                      {token.mode}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-block px-2 py-0.5 rounded text-xs bg-surface border border-border text-fg-muted">
                      {token.group}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-fg-muted">{token.value}</td>
                  <td className="px-4 py-3 text-fg-muted text-center">{token.order}</td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => handleToggleActive(token)}
                      className="text-fg-muted hover:text-primary transition-colors"
                      aria-label={token.is_active ? 'Tắt' : 'Bật'}
                    >
                      {token.is_active
                        ? <ToggleRight size={20} className="text-success" />
                        : <ToggleLeft size={20} />}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => onEdit(token)}
                        className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors"
                        aria-label="Sửa"
                      >
                        <Pencil size={14} />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(token)}
                        className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors"
                        aria-label="Xóa"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa color token"
        message={`Bạn chắc chắn muốn xóa token "${deleteTarget?.key}" (${deleteTarget?.mode})?`}
        confirmLabel="Xóa"
      />
    </>
  )
}
