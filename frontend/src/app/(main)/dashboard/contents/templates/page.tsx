'use client'
import { useState } from 'react'
import { Tabs } from '@/components/ui/Tabs'
import { FileText, Layout } from 'lucide-react'
import { PostTemplateGrid } from '@/features/contents/components/templates/PostTemplateGrid'
import { LayoutTemplateGrid } from '@/features/contents/components/templates/LayoutTemplateGrid'

const TABS = [
  { key: 'posts', label: 'Bài viết', icon: <FileText size={14} /> },
  { key: 'layouts', label: 'Banner Layout', icon: <Layout size={14} /> },
]

export default function TemplatesPage() {
  const [tab, setTab] = useState('posts')

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-fg">Templates</h1>
        <p className="text-sm text-fg-muted mt-1">Mẫu nội dung và layout có sẵn</p>
      </div>

      <Tabs tabs={TABS} active={tab} onChange={setTab} className="mb-6" />

      {tab === 'posts' && <PostTemplateGrid />}
      {tab === 'layouts' && <LayoutTemplateGrid />}
    </div>
  )
}
