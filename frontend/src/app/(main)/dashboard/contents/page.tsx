'use client'
import { useState } from 'react'
import { Plus, FileText } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { PostFilterBar } from '@/features/contents/components/post/PostFilterBar'
import { PostTable } from '@/features/contents/components/post/PostTable'
import { usePosts } from '@/features/contents/hooks'
import type { PostStatus, PlatformType } from '@/features/contents/types'

export default function ContentsPage() {
  const router = useRouter()
  const [filters, setFilters] = useState<{
    status?: PostStatus
    platform_type?: PlatformType
    search?: string
  }>({})

  const { posts, loading } = usePosts(filters)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">Quản lý nội dung</h1>
          <p className="text-sm text-fg-muted mt-1">Tạo, chỉnh sửa và quản lý bài viết</p>
        </div>
        <Button size="sm" onClick={() => router.push('/dashboard/contents/new')}>
          <Plus size={16} />
          Tạo bài viết
        </Button>
      </div>

      <PostFilterBar
        currentStatus={filters.status}
        onFilterChange={(next) => setFilters((prev) => ({ ...prev, ...next }))}
      />

      <div className="mt-4">
        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : posts.length === 0 ? (
          <EmptyState
            icon={<FileText size={40} strokeWidth={1.5} />}
            title="Chưa có bài viết nào"
            description="Tạo bài viết đầu tiên để bắt đầu"
            actionLabel="Tạo bài viết"
            onAction={() => router.push('/dashboard/contents/new')}
          />
        ) : (
          <PostTable posts={posts} />
        )}
      </div>
    </div>
  )
}
