'use client'
import { CheckCircle, FileText } from 'lucide-react'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { PostTable } from '@/features/contents/components/post/PostTable'
import { usePosts } from '@/features/contents/hooks'

export default function ReviewPage() {
  const { posts, loading } = usePosts({ status: 'review' })

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-fg flex items-center gap-2">
          <CheckCircle size={24} className="text-amber-500" />
          Duyệt bài viết
        </h1>
        <p className="text-sm text-fg-muted mt-1">Các bài viết đang chờ duyệt</p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <EmptyState
          icon={<FileText size={40} strokeWidth={1.5} />}
          title="Không có bài viết nào chờ duyệt"
          description="Tất cả đã được xử lý."
        />
      ) : (
        <PostTable posts={posts} />
      )}
    </div>
  )
}
