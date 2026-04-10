'use client'
import { use } from 'react'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { PostDetailTabs } from '@/features/contents/components/post/PostDetailTabs'
import { usePost } from '@/features/contents/hooks'

export default function PostDetailPage({ params }: { params: Promise<{ postId: string }> }) {
  const { postId } = use(params)
  const { post, loading, refetch } = usePost(postId)

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner size={32} />
      </div>
    )
  }

  if (!post) {
    return (
      <div className="text-center py-20">
        <p className="text-fg-muted">Không tìm thấy bài viết</p>
        <Link href="/dashboard/contents">
          <Button variant="ghost" size="sm" className="mt-4">
            <ArrowLeft size={16} />
            Quay lại
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Link href="/dashboard/contents">
          <Button variant="ghost" size="sm">
            <ArrowLeft size={16} />
          </Button>
        </Link>
      </div>

      <PostDetailTabs
        post={post}
        onUpdate={refetch}
      />
    </div>
  )
}
