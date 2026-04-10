 'use client'
import { useState } from 'react'
import { Trash2, Eye, FileText, ImageIcon, Globe, Type, File } from 'lucide-react'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useDocuments, useDeleteDocument } from '../hooks'
import { formatDateTime } from '@/lib/utils'
import type { Document } from '../types'

interface DocumentTableProps {
  kbSlug: string
  onViewChunks: (doc: Document) => void
  onAdd: () => void
  refreshKey?: number
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

const sourceIcon = {
  file: File,
  text: Type,
  url: Globe,
}

export function DocumentTable({ kbSlug, onViewChunks, onAdd, refreshKey, onToast }: DocumentTableProps) {
  const [deleteTarget, setDeleteTarget] = useState<Document | null>(null)
  const { documents, loading, error, refetch } = useDocuments(kbSlug)
  const { remove, loading: deleting } = useDeleteDocument()

  useState(() => { if (refreshKey) refetch() })

  const handleDelete = async () => {
    if (!deleteTarget) return
    const ok = await remove(deleteTarget.id)
    if (ok) {
      onToast(`Đã xóa "${deleteTarget.title}"`, 'success')
      refetch()
    } else {
      onToast('Xóa tài liệu thất bại', 'danger')
    }
    setDeleteTarget(null)
  }

  if (loading) return <SkeletonTable rows={4} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>
  if (documents.length === 0) {
    return (
      <EmptyState
        icon={<FileText size={40} strokeWidth={1.5} />}
        title="Chưa có tài liệu nào"
        description="Tải lên tài liệu để bắt đầu xây dựng knowledge base"
        actionLabel="Thêm tài liệu"
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
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Tài liệu</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Loại</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Trạng thái</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Chunks</th>
              <th className="text-center px-4 py-3 font-medium text-fg-muted">Tokens</th>
              <th className="text-left px-4 py-3 font-medium text-fg-muted">Ngày tạo</th>
              <th className="text-right px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => {
              const Icon = sourceIcon[doc.source_type] ?? FileText
              return (
                <tr
                  key={doc.id}
                  className="border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {doc.is_image ? <ImageIcon size={14} className="text-info shrink-0" /> : <Icon size={14} className="text-fg-muted shrink-0" />}
                      <div>
                        <p className="font-medium text-fg truncate max-w-[200px]">{doc.title}</p>
                        {doc.description && (
                          <p className="text-xs text-fg-muted truncate max-w-[200px]">{doc.description}</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-xs capitalize text-fg-muted">{doc.source_type}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <StatusBadge status={doc.processing_status} />
                  </td>
                  <td className="px-4 py-3 text-center text-fg-muted">{doc.chunk_count}</td>
                  <td className="px-4 py-3 text-center text-fg-muted">
                    {doc.token_count.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-xs text-fg-muted">
                    {formatDateTime(doc.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      {doc.processing_status === 'completed' && (
                        <button
                          onClick={() => onViewChunks(doc)}
                          className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors"
                          title="Xem chunks"
                        >
                          <Eye size={14} />
                        </button>
                      )}
                      <button
                        onClick={() => setDeleteTarget(doc)}
                        className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa tài liệu"
        message={`Bạn chắc chắn muốn xóa "${deleteTarget?.title}"? Tất cả chunks sẽ bị xóa.`}
        confirmLabel="Xóa"
      />
    </>
  )
}
