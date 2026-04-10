'use client'
import Image from 'next/image'
import { Pencil, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { useToast } from '@/hooks/useToast'
import { ToastContainer } from '@/components/ui/Toast'
import { useAssets, useDeleteAsset, useUpdateAsset } from '../hooks'
import type { MediaAssetAdmin } from '../types'

interface AssetGridProps {
  onEdit: (asset: MediaAssetAdmin) => void
  refreshKey?: number
}

export function AssetGrid({ onEdit, refreshKey }: AssetGridProps) {
  const [includeInactive, setIncludeInactive] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<MediaAssetAdmin | null>(null)

  const { assets, loading, error, refetch } = useAssets({ include_inactive: includeInactive })
  const { remove, loading: deleting } = useDeleteAsset()
  const { update } = useUpdateAsset()
  const { toasts, addToast, removeToast } = useToast()

  useState(() => { if (refreshKey) refetch() })

  const handleDelete = async () => {
    if (!deleteTarget) return
    const ok = await remove(deleteTarget.id)
    if (ok) {
      addToast(`Đã xóa asset "${deleteTarget.key}"`, 'success')
      refetch()
    } else {
      addToast('Xóa asset thất bại', 'danger')
    }
    setDeleteTarget(null)
  }

  const handleToggleActive = async (asset: MediaAssetAdmin) => {
    const result = await update(asset.id, { is_active: !asset.is_active })
    if (result) {
      addToast(`Asset "${asset.key}" đã ${result.is_active ? 'bật' : 'tắt'}`, 'success')
      refetch()
    } else {
      addToast('Cập nhật thất bại', 'danger')
    }
  }

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div className="flex justify-end mb-4">
        <label className="flex items-center gap-2 text-xs text-fg-muted cursor-pointer">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="accent-primary"
          />
          Hiện assets không hoạt động
        </label>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-square rounded-bento bg-surface animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-3 py-12 text-danger">
          <p className="text-sm">{error}</p>
          <button onClick={refetch} className="text-xs text-primary hover:underline">Thử lại</button>
        </div>
      ) : assets.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-12 text-fg-muted">
          <p className="text-sm">Chưa có asset nào</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {assets.map((asset) => (
            <div
              key={asset.id}
              className={cn(
                'group relative rounded-bento border border-border bg-surface overflow-hidden',
                !asset.is_active && 'opacity-50'
              )}
            >
              {/* Thumbnail */}
              <div className="aspect-video bg-bg-subtle flex items-center justify-center">
                {asset.file_url ? (
                  <Image
                    src={asset.file_url}
                    alt={asset.alt_text || asset.name}
                    width={200}
                    height={112}
                    className="object-contain w-full h-full p-2"
                  />
                ) : (
                  <span className="text-xs text-fg-subtle">No image</span>
                )}
              </div>

              {/* Info */}
              <div className="p-3">
                <p className="font-mono text-xs text-primary font-medium">{asset.key}</p>
                <p className="text-sm text-fg truncate mt-0.5">{asset.name}</p>
                {asset.alt_text && (
                  <p className="text-xs text-fg-subtle truncate">{asset.alt_text}</p>
                )}
              </div>

              {/* Actions overlay */}
              <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleToggleActive(asset)}
                  className="p-1.5 rounded-lg bg-surface/90 border border-border text-fg-muted hover:text-primary transition-colors"
                  aria-label={asset.is_active ? 'Tắt' : 'Bật'}
                >
                  {asset.is_active
                    ? <ToggleRight size={14} className="text-success" />
                    : <ToggleLeft size={14} />}
                </button>
                <button
                  onClick={() => onEdit(asset)}
                  className="p-1.5 rounded-lg bg-surface/90 border border-border text-fg-muted hover:text-primary transition-colors"
                  aria-label="Sửa"
                >
                  <Pencil size={14} />
                </button>
                <button
                  onClick={() => setDeleteTarget(asset)}
                  className="p-1.5 rounded-lg bg-surface/90 border border-border text-fg-muted hover:text-danger transition-colors"
                  aria-label="Xóa"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa media asset"
        message={`Bạn chắc chắn muốn xóa asset "${deleteTarget?.key}"?`}
        confirmLabel="Xóa"
      />
    </>
  )
}
