'use client'
import { useState } from 'react'
import { Tabs } from '@/components/ui/Tabs'
import { FileText, Image as ImageIcon, Layout, Sparkles, History, MessageSquare } from 'lucide-react'
import { PostForm } from './PostForm'
import { PostActionBar } from './PostActionBar'
import { MediaGallery } from '../media/MediaGallery'
import { AIGenerationPanel } from '../ai/AIGenerationPanel'
import { BannerLayoutGrid } from '../banner/BannerLayoutGrid'
import { VersionTimeline } from '../versions/VersionTimeline'
import { PostCommentSection } from '../comments/PostCommentSection'
import { PostStatusBadge } from './PostStatusBadge'
import { useUpdatePost } from '../../hooks'
import { PLATFORM_LABELS, PLATFORM_ICONS } from '../../constants'
import type { PostDetail, PostInput } from '../../types'

interface PostDetailTabsProps {
  post: PostDetail
  onUpdate: () => void
}

const TABS = [
  { key: 'content', label: 'Nội dung', icon: <FileText size={15} /> },
  { key: 'media', label: 'Media', icon: <ImageIcon size={15} /> },
  { key: 'banner', label: 'Banner', icon: <Layout size={15} /> },
  { key: 'ai', label: 'AI', icon: <Sparkles size={15} /> },
  { key: 'versions', label: 'Lịch sử', icon: <History size={15} /> },
  { key: 'comments', label: 'Bình luận', icon: <MessageSquare size={15} /> },
]

export function PostDetailTabs({ post, onUpdate }: PostDetailTabsProps) {
  const [activeTab, setActiveTab] = useState('content')
  const { updatePost, loading: saving } = useUpdatePost()

  const isDraft = post.status === 'draft'

  const handleSave = async (data: PostInput) => {
    const result = await updatePost(post.id, data)
    if (!result.error) onUpdate()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-fg">{post.title}</h1>
          <div className="flex items-center gap-3 mt-2">
            <PostStatusBadge status={post.status} />
            <span className="text-sm text-fg-muted">
              {PLATFORM_ICONS[post.platform_type]} {PLATFORM_LABELS[post.platform_type]}
            </span>
            <span className="text-sm text-fg-muted">
              bởi {post.author_name}
            </span>
          </div>
        </div>
        <PostActionBar post={post} onUpdate={onUpdate} />
      </div>

      {/* Tabs */}
      <Tabs tabs={TABS} active={activeTab} onChange={setActiveTab} />

      {/* Tab Content */}
      <div>
        {activeTab === 'content' && (
          <PostForm
            initialData={{
              title: post.title,
              content: post.content,
              platform_type: post.platform_type,
              category: post.category?.id ?? null,
              tags: post.tags.map((t) => t.id),
              hashtags: post.hashtags,
            }}
            onSubmit={handleSave}
            loading={saving}
            disabled={!isDraft}
          />
        )}

        {activeTab === 'media' && (
          <MediaGallery postId={post.id} disabled={!isDraft} />
        )}

        {activeTab === 'banner' && (
          <BannerLayoutGrid postId={post.id} />
        )}

        {activeTab === 'ai' && (
          <AIGenerationPanel
            postId={post.id}
            platformType={post.platform_type}
          />
        )}

        {activeTab === 'versions' && (
          <VersionTimeline postId={post.id} />
        )}

        {activeTab === 'comments' && (
          <PostCommentSection postId={post.id} />
        )}
      </div>
    </div>
  )
}
