'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, FileText, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Tabs } from '@/components/ui/Tabs'
import { PostForm } from '@/features/contents/components/post/PostForm'
import { AIGenerationPanel } from '@/features/contents/components/ai/AIGenerationPanel'
import { useCreatePost } from '@/features/contents/hooks'
import type { PostInput } from '@/features/contents/types'

const CREATION_TABS = [
  { key: 'manual', label: 'Soạn thủ công', icon: <FileText size={14} /> },
  { key: 'ai', label: 'AI hỗ trợ', icon: <Sparkles size={14} /> },
]

export default function NewPostPage() {
  const router = useRouter()
  const { createPost, loading } = useCreatePost()
  const [creationMode, setCreationMode] = useState('manual')
  const [formDraft, setFormDraft] = useState<Partial<PostInput>>({
    title: '',
    platform_type: 'facebook',
    content: '',
    hashtags: [],
    category: null,
    tags: [],
  })

  const handleSubmit = async (data: PostInput) => {
    const result = await createPost(data)
    if (result.data) {
      router.push(`/dashboard/contents/${result.data.id}`)
    }
  }

  const handleApplyContent = (content: string) => {
    setFormDraft((prev) => ({
      ...prev,
      content,
      is_ai_generated: true,
    }))
    setCreationMode('manual')
  }

  const handleApplyHashtags = (hashtags: string[]) => {
    setFormDraft((prev) => ({
      ...prev,
      hashtags,
    }))
    setCreationMode('manual')
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft size={16} />
        </Button>
        <div>
          <h1 className="text-2xl font-semibold text-fg">Tạo bài viết mới</h1>
          <p className="text-sm text-fg-muted mt-1">Điền thông tin bài viết</p>
        </div>
      </div>

      <div className="max-w-3xl">
        <div className="rounded-bento border border-border bg-card p-4 mb-6 space-y-4">
          <div>
            <h2 className="text-base font-semibold text-fg">Bắt đầu bằng AI hoặc nhập tay</h2>
            <p className="text-sm text-fg-muted mt-1">
              Dùng AI để tạo nháp nội dung trước, sau đó quay lại form để chỉnh sửa và lưu bài viết.
            </p>
          </div>

          <Tabs tabs={CREATION_TABS} active={creationMode} onChange={setCreationMode} />

          {creationMode === 'ai' && (
            <AIGenerationPanel
              platformType={formDraft.platform_type}
              onApplyContent={handleApplyContent}
              onApplyHashtags={handleApplyHashtags}
            />
          )}

          {creationMode === 'manual' && (
            <div className="rounded-bento border border-dashed border-border bg-surface/40 px-4 py-3 text-sm text-fg-muted">
              {formDraft.content
                ? 'Nội dung AI đã được đưa vào form bên dưới. Bạn có thể chỉnh sửa trước khi lưu.'
                : 'Bạn có thể chuyển sang tab AI hỗ trợ để tạo nháp nội dung tự động.'}
            </div>
          )}
        </div>

        <PostForm
          initialData={formDraft}
          onSubmit={handleSubmit}
          loading={loading}
          disabled={false}
        />
      </div>
    </div>
  )
}
