'use client'
import { useState, useMemo } from 'react'
import { Trash2, Eye, FileText, ImageIcon, Globe, Type, File, Search } from 'lucide-react'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useDocuments, useDeleteDocument } from '../hooks'
import { formatDateTime } from '@/lib/utils'
import { cn } from '@/lib/utils'
import type { Document } from '../types'

interface DocumentTableProps {
  kbSlug: string
  onViewChunks: (doc: Document) => void
  onSelectDoc: (doc: Document) => void
  selectedDocId?: string | null
  onAdd: () => void
  refreshKey?: number
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

const SOURCE_TYPES = [
  { key: 'all', label: 'Tất cả' },
  { key: 'file_upload', label: 'File' },
  { key: 'text', label: 'Text' },
  { key: 'url', label: 'URL' },
  { key: 'image_upload', label: 'Ảnh' },
] as const

const STATUSES = [
  { key: 'all', label: 'Tất cả' },
  { key: 'completed', label: 'Xong' },
  { key: 'processing', label: 'Đang xử lý' },
  { key: 'pending', label: 'Chờ' },
  { key: 'failed', label: 'Lỗi' },
] as const

const sourceIconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  file_upload: File,
  text: Type,
  url: Globe,
  image_upload: ImageIcon,
  file: File,
}

export function DocumentTable({ kbSlug, onViewChunks, onSelectDoc, selectedDocId, onAdd, refreshKey, onToast }: DocumentTableProps) {
  const [deleteTarget, setDeleteTarget] = useState<Document | null>(null)
  const [search, setSearch] = useState('')
  const [sourceFilter, setSourceFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { documents, loading, error, refetch } = useDocuments(kbSlug)
  const { remove, loading: deleting } = useDeleteDocument()

  useState(() => { if (refreshKey) refetch() })

  const filtered = useMemo(() => {
    return documents.filter((doc) => {
      const matchSearch = search === '' || doc.title.toLowerCase().includes(search.toLowerCase())
      const matchSource = sourceFilter === 'all' || doc.source_type === sourceFilter
      const matchStatus = statusFilter === 'all' || doc.processing_status === statusFilter
      return matchSearch && matchSource && matchStatus
    })
  }, [documents, search, sourceFilter, statusFilter])

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
      {/* Filter bar */}
      <div className="flex flex-col sm:flex-row gap-2 mb-3">
        {/* Search */}
        <div className="relative flex-1 min-w-0">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-fg-subtle pointer-events-none" />
          <input
            type="text"
            placeholder="Tìm tài liệu..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-sm bg-surface border border-border rounded-bento text-fg placeholder:text-fg-subtle focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>
        {/* Source type filter */}
        <div className="flex gap-1 flex-wrap">
          {SOURCE_TYPES.map((s) => (
            <button
              key={s.key}
              onClick={() => setSourceFilter(s.key)}
              className={cn(
                'px-2.5 py-1 text-xs rounded-full border transition-colors',
                sourceFilter === s.key
                  ? 'bg-primary text-primary-fg border-primary'
                  : 'bg-surface text-fg-muted border-border hover:border-primary/50 hover:text-fg'
              )}
            >
              {s.label}
            </button>
          ))}
        </div>
        {/* Status filter */}
        <div className="flex gap-1 flex-wrap">
          {STATUSES.map((s) => (
            <button
              key={s.key}
              onClick={() => setStatusFilter(s.key)}
              className={cn(
                'px-2.5 py-1 text-xs rounded-full border transition-colors',
                statusFilter === s.key
                  ? 'bg-primary text-primary-fg border-primary'
                  : 'bg-surface text-fg-muted border-border hover:border-primary/50 hover:text-fg'
              )}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Result count */}
      {(search || sourceFilter !== 'all' || statusFilter !== 'all') && (
        <p className="text-xs text-fg-muted mb-2">
          {filtered.length} / {documents.length} tài liệu
        </p>
      )}

      {filtered.length === 0 ? (
        <EmptyState
          icon={<Search size={32} strokeWidth={1.5} />}
          title="Không tìm thấy"
          description="Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm"
        />
      ) : (
        <div className="overflow-x-auto rounded-bento border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface">
                <th className="text-left px-4 py-3 font-medium text-fg-muted">Tài liệu</th>
                <th className="text-center px-4 py-3 font-medium text-fg-muted hidden sm:table-cell">Loại</th>
                <th className="text-center px-4 py-3 font-medium text-fg-muted">Trạng thái</th>
                <th className="text-center px-4 py-3 font-medium text-fg-muted hidden md:table-cell">Chunks</th>
                <th className="text-center px-4 py-3 font-medium text-fg-muted hidden md:table-cell">Tokens</th>
                <th className="text-left px-4 py-3 font-medium text-fg-muted hidden lg:table-cell">Ngày tạo</th>
                <th className="text-right px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {filtered.map((doc) => {
                const Icon = sourceIconMap[doc.source_type] ?? FileText
                const isSelected = selectedDocId === doc.id
                return (
                  <tr
                    key={doc.id}
                    onClick={() => onSelectDoc(doc)}
                    className={cn(
                      'border-b border-border/50 last:border-0 cursor-pointer transition-colors',
                      isSelected
                        ? 'bg-primary/8 border-l-2 border-l-primary'
                        : 'hover:bg-surface/60'
                    )}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {doc.is_image
                          ? <ImageIcon size={14} className="text-info shrink-0" />
                          : <Icon size={14} className="text-fg-muted shrink-0" />
                        }
                        <div>
                          <p className="font-medium text-fg truncate max-w-[180px]">{doc.title}</p>
                          {doc.description && (
                            <p className="text-xs text-fg-muted truncate max-w-[180px]">{doc.description}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center hidden sm:table-cell">
                      <span className="text-xs text-fg-muted">{doc.source_type.replace('_', ' ')}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <StatusBadge status={doc.processing_status} />
                    </td>
                    <td className="px-4 py-3 text-center text-fg-muted hidden md:table-cell">{doc.chunk_count}</td>
                    <td className="px-4 py-3 text-center text-fg-muted hidden md:table-cell">
                      {doc.token_count.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-xs text-fg-muted hidden lg:table-cell">
                      {formatDateTime(doc.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      <div
                        className="flex items-center justify-end gap-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {doc.processing_status === 'completed' && (
                          <button
                            onClick={() => onViewChunks(doc)}
                            className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors"
                            title="Xem chunks inline"
                          >
                            <Eye size={14} />
                          </button>
                        )}
                        <button
                          onClick={() => setDeleteTarget(doc)}
                          className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors"
                          title="Xóa"
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
      )}

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
