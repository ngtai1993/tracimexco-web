'use client'
import { useState } from 'react'
import { Plus, Trash2, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { useDeleteConversation } from '../hooks'
import type { RAGConversation } from '../types'

interface ChatSidebarProps {
  conversations: RAGConversation[]
  selectedId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  instanceSlug: string
  onDeleted: () => void
}

export function ChatSidebar({
  conversations,
  selectedId,
  onSelect,
  onNew,
  instanceSlug,
  onDeleted,
}: ChatSidebarProps) {
  const [deleteTarget, setDeleteTarget] = useState<RAGConversation | null>(null)
  const { remove, loading: deleting } = useDeleteConversation()

  const handleDelete = async () => {
    if (!deleteTarget) return
    const ok = await remove(instanceSlug, deleteTarget.id)
    if (ok) onDeleted()
    setDeleteTarget(null)
  }

  return (
    <div className="w-64 border-r border-border bg-card flex flex-col h-full">
      <div className="p-3 border-b border-border">
        <button
          onClick={onNew}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium rounded-bento border border-border text-fg hover:bg-surface transition-colors"
        >
          <Plus size={14} />
          Cuộc trò chuyện mới
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-2">
        {conversations.length === 0 ? (
          <p className="text-xs text-fg-subtle text-center py-8">Chưa có cuộc trò chuyện nào</p>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={cn(
                'group flex items-start gap-2 px-3 py-2.5 mx-2 rounded-md cursor-pointer transition-colors',
                selectedId === conv.id
                  ? 'bg-primary/10 text-primary'
                  : 'text-fg hover:bg-surface'
              )}
              onClick={() => onSelect(conv.id)}
            >
              <MessageSquare size={14} className="shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{conv.title}</p>
                {conv.last_message && (
                  <p className="text-[10px] text-fg-muted truncate mt-0.5">{conv.last_message}</p>
                )}
                <p className="text-[10px] text-fg-subtle mt-0.5">
                  {conv.message_count} tin nhắn
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setDeleteTarget(conv)
                }}
                className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-danger/10 text-fg-subtle hover:text-danger transition-all"
              >
                <Trash2 size={12} />
              </button>
            </div>
          ))
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa cuộc trò chuyện"
        message={`Bạn chắc chắn muốn xóa "${deleteTarget?.title}"?`}
        confirmLabel="Xóa"
      />
    </div>
  )
}
