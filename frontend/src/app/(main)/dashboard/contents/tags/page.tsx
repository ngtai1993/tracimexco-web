'use client'
import { TagManager } from '@/features/contents/components/taxonomy/TagManager'

export default function TagsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-fg">Quản lý tags</h1>
        <p className="text-sm text-fg-muted mt-1">Thêm và quản lý tags cho bài viết</p>
      </div>

      <TagManager />
    </div>
  )
}
