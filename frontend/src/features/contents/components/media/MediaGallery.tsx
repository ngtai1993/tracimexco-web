'use client'
import { useRef } from 'react'
import Image from 'next/image'
import { Upload, X, Film, FileIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { Spinner } from '@/components/ui/Spinner'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { useState } from 'react'
import { usePostMedia } from '../../hooks'

interface MediaGalleryProps {
  postId: string
  disabled?: boolean
}

export function MediaGallery({ postId, disabled }: MediaGalleryProps) {
  const { media, loading, uploading, upload, remove } = usePostMedia(postId)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const handleFiles = (files: FileList) => {
    Array.from(files).forEach((file) => upload(file))
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (disabled) return
    handleFiles(e.dataTransfer.files)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Upload zone */}
      {!disabled && (
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className={cn(
            'border-2 border-dashed border-border rounded-bento p-8',
            'flex flex-col items-center gap-3 text-center',
            'hover:border-primary/40 transition-colors',
            uploading && 'opacity-60 pointer-events-none'
          )}
        >
          {uploading ? (
            <>
              <Spinner size={28} />
              <p className="text-sm text-fg-muted">Đang tải lên...</p>
            </>
          ) : (
            <>
              <Upload size={28} className="text-fg-subtle" />
              <p className="text-sm text-fg-muted">Kéo thả ảnh/video vào đây hoặc</p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
              >
                Chọn file
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,video/*"
                multiple
                className="hidden"
                onChange={(e) => e.target.files && handleFiles(e.target.files)}
              />
            </>
          )}
        </div>
      )}

      {/* Media grid */}
      {media.length === 0 ? (
        <EmptyState
          title="Chưa có ảnh/video"
          description={disabled ? '' : 'Kéo thả file vào đây để tải lên.'}
        />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {media.map((item) => (
            <div
              key={item.id}
              className="relative group rounded-bento border border-border overflow-hidden bg-surface aspect-square"
            >
              {item.media_type === 'image' ? (
                <Image
                  src={item.file_url ?? item.file}
                  alt={item.caption || 'Media'}
                  fill
                  unoptimized
                  className="object-cover"
                />
              ) : item.media_type === 'video' ? (
                <div className="w-full h-full flex items-center justify-center bg-black/5">
                  <Film size={32} className="text-fg-subtle" />
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <FileIcon size={32} className="text-fg-subtle" />
                </div>
              )}

              {!disabled && (
                <button
                  onClick={() => setDeleteId(item.id)}
                  className={cn(
                    'absolute top-2 right-2 p-1.5 rounded-full',
                    'bg-black/60 text-white opacity-0 group-hover:opacity-100',
                    'hover:bg-danger transition-all'
                  )}
                >
                  <X size={14} />
                </button>
              )}

              {item.caption && (
                <div className="absolute bottom-0 left-0 right-0 bg-black/50 px-2 py-1">
                  <p className="text-xs text-white truncate">{item.caption}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={() => {
          if (deleteId) remove(deleteId)
          setDeleteId(null)
        }}
        title="Xóa media"
        message="Bạn có chắc muốn xóa file này?"
        confirmLabel="Xóa"
      />
    </div>
  )
}
