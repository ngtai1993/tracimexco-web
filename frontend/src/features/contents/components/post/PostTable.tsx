'use client'
import Link from 'next/link'
import { Eye } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { PostStatusBadge } from './PostStatusBadge'
import { PLATFORM_LABELS, PLATFORM_ICONS } from '../../constants'
import type { Post } from '../../types'

interface PostTableProps {
  posts: Post[]
  loading?: boolean
}

export function PostTable({ posts, loading }: PostTableProps) {
  if (loading) {
    return (
      <div className="rounded-bento border border-border overflow-hidden">
        <div className="bg-surface/50 px-4 py-3 border-b border-border">
          <Skeleton className="h-4 w-full" />
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="px-4 py-4 border-b border-border/50 flex items-center gap-4">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>
    )
  }

  if (!posts.length) {
    return (
      <EmptyState
        title="Chưa có bài viết nào"
        description="Bắt đầu tạo bài viết đầu tiên của bạn."
        actionLabel="Tạo bài viết"
        onAction={() => window.location.href = '/dashboard/contents/new'}
      />
    )
  }

  return (
    <div className="rounded-bento border border-border overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface/50 border-b border-border text-left">
            <th className="px-4 py-3 font-medium text-fg-muted">Tiêu đề</th>
            <th className="px-4 py-3 font-medium text-fg-muted w-28">Nền tảng</th>
            <th className="px-4 py-3 font-medium text-fg-muted w-28">Trạng thái</th>
            <th className="px-4 py-3 font-medium text-fg-muted w-36">Tác giả</th>
            <th className="px-4 py-3 font-medium text-fg-muted w-36">Ngày tạo</th>
            <th className="px-4 py-3 font-medium text-fg-muted w-10" />
          </tr>
        </thead>
        <tbody>
          {posts.map((post) => (
            <tr
              key={post.id}
              className="border-b border-border/50 hover:bg-surface/30 transition-colors"
            >
              <td className="px-4 py-3">
                <Link
                  href={`/dashboard/contents/${post.id}`}
                  className="font-medium text-fg hover:text-primary transition-colors line-clamp-1"
                >
                  {post.title}
                </Link>
                <div className="flex items-center gap-2 mt-1">
                  {post.category_name && (
                    <span className="text-xs text-fg-muted">{post.category_name}</span>
                  )}
                  {post.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag.id}
                      className="text-[10px] px-1.5 py-0.5 rounded bg-surface text-fg-muted"
                    >
                      {tag.name}
                    </span>
                  ))}
                  {post.is_ai_generated && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-info/15 text-info font-medium">
                      AI
                    </span>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-fg-muted">
                <span className="flex items-center gap-1.5">
                  <span>{PLATFORM_ICONS[post.platform_type]}</span>
                  <span>{PLATFORM_LABELS[post.platform_type]}</span>
                </span>
              </td>
              <td className="px-4 py-3">
                <PostStatusBadge status={post.status} />
              </td>
              <td className="px-4 py-3 text-fg-muted truncate">{post.author_name}</td>
              <td className="px-4 py-3 text-fg-muted text-xs">{formatDateTime(post.created_at)}</td>
              <td className="px-4 py-3">
                <Link
                  href={`/dashboard/contents/${post.id}`}
                  className="p-1 rounded hover:bg-surface transition-colors text-fg-muted hover:text-fg"
                >
                  <Eye size={16} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
