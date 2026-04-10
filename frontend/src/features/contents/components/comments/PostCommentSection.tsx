'use client'
import { useState } from 'react'
import { Send, User } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useComments } from '../../hooks'

interface Props {
  postId: string
}

export function PostCommentSection({ postId }: Props) {
  const { comments, loading, addComment } = useComments(postId)
  const [content, setContent] = useState('')
  const [sending, setSending] = useState(false)

  const handleSend = async () => {
    if (!content.trim()) return
    setSending(true)
    await addComment(content.trim())
    setContent('')
    setSending(false)
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
      {/* Add comment form */}
      <div className="rounded-bento border border-border bg-card p-4 space-y-3">
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Viết bình luận..."
          rows={3}
        />
        <div className="flex justify-end">
          <Button size="sm" onClick={handleSend} loading={sending} disabled={!content.trim()}>
            <Send size={14} />
            Gửi
          </Button>
        </div>
      </div>

      {/* Comments list */}
      {comments.length === 0 ? (
        <EmptyState title="Chưa có bình luận" description="Hãy thêm bình luận đầu tiên." />
      ) : (
        <div className="space-y-3">
          {comments.map((c) => (
            <div key={c.id} className="rounded-bento border border-border bg-card p-4 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-fg flex items-center gap-1.5">
                  <User size={14} className="text-fg-muted" />
                  {c.author_name}
                </span>
                <span className="text-xs text-fg-muted">
                  {new Date(c.created_at).toLocaleString('vi-VN')}
                </span>
              </div>
              <p className="text-sm text-fg whitespace-pre-wrap">{c.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
