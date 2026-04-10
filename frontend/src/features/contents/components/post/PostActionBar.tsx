'use client'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Send, CheckCircle, XCircle, Copy, Trash2 } from 'lucide-react'
import { PLATFORM_OPTIONS } from '../../constants'
import { usePostActions, useDeletePost } from '../../hooks'
import type { PostDetail, PlatformType } from '../../types'

interface PostActionBarProps {
  post: PostDetail
  onUpdate: () => void
}

export function PostActionBar({ post, onUpdate }: PostActionBarProps) {
  const { submitReview, approve, reject, duplicate, loading } = usePostActions()
  const { deletePost, loading: deleting } = useDeletePost()

  const [showReject, setShowReject] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [showDuplicate, setShowDuplicate] = useState(false)
  const [dupPlatform, setDupPlatform] = useState<PlatformType>('facebook')
  const [showDelete, setShowDelete] = useState(false)

  const handleSubmitReview = async () => {
    const result = await submitReview(post.id)
    if (!result.error) onUpdate()
  }

  const handleApprove = async () => {
    const result = await approve(post.id)
    if (!result.error) onUpdate()
  }

  const handleReject = async () => {
    if (!rejectReason.trim()) return
    const result = await reject(post.id, rejectReason)
    if (!result.error) {
      setShowReject(false)
      setRejectReason('')
      onUpdate()
    }
  }

  const handleDuplicate = async () => {
    const result = await duplicate(post.id, dupPlatform)
    if (!result.error && result.data) {
      setShowDuplicate(false)
      window.location.href = `/dashboard/contents/${result.data.id}`
    }
  }

  const handleDelete = async () => {
    const result = await deletePost(post.id)
    if (!result.error) {
      window.location.href = '/dashboard/contents'
    }
  }

  return (
    <>
      <div className="flex items-center gap-2 flex-wrap">
        {post.status === 'draft' && (
          <>
            <Button size="sm" onClick={handleSubmitReview} loading={loading}>
              <Send size={14} />
              Nộp Review
            </Button>
            <Button size="sm" variant="danger" onClick={() => setShowDelete(true)}>
              <Trash2 size={14} />
              Xóa
            </Button>
          </>
        )}

        {post.status === 'review' && (
          <>
            <Button size="sm" onClick={handleApprove} loading={loading}>
              <CheckCircle size={14} />
              Duyệt
            </Button>
            <Button size="sm" variant="outline" onClick={() => setShowReject(true)}>
              <XCircle size={14} />
              Trả về
            </Button>
          </>
        )}

        <Button size="sm" variant="ghost" onClick={() => setShowDuplicate(true)}>
          <Copy size={14} />
          Duplicate
        </Button>
      </div>

      {/* Reject Modal */}
      <Modal open={showReject} onClose={() => setShowReject(false)} title="Trả về bài viết">
        <Textarea
          label="Lý do trả về"
          value={rejectReason}
          onChange={(e) => setRejectReason(e.target.value)}
          placeholder="Nhập lý do..."
        />
        <div className="flex justify-end gap-2 mt-4">
          <Button size="sm" variant="ghost" onClick={() => setShowReject(false)}>
            Hủy
          </Button>
          <Button size="sm" variant="danger" onClick={handleReject} loading={loading} disabled={!rejectReason.trim()}>
            Trả về
          </Button>
        </div>
      </Modal>

      {/* Duplicate Modal */}
      <Modal open={showDuplicate} onClose={() => setShowDuplicate(false)} title="Nhân bản bài viết">
        <Select
          label="Nền tảng mới"
          options={PLATFORM_OPTIONS}
          value={dupPlatform}
          onChange={(e) => setDupPlatform(e.target.value as PlatformType)}
        />
        <div className="flex justify-end gap-2 mt-4">
          <Button size="sm" variant="ghost" onClick={() => setShowDuplicate(false)}>
            Hủy
          </Button>
          <Button size="sm" onClick={handleDuplicate} loading={loading}>
            Nhân bản
          </Button>
        </div>
      </Modal>

      {/* Delete Confirm */}
      <ConfirmDialog
        open={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={handleDelete}
        title="Xóa bài viết"
        message="Bạn có chắc muốn xóa bài viết này? Hành động này không thể hoàn tác."
        confirmLabel="Xóa"
        loading={deleting}
      />
    </>
  )
}
