'use client'
import { useState } from 'react'
import { FileText, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { usePostTemplates } from '../../hooks'
import { PLATFORM_LABELS } from '../../constants'

interface Props {
  onApply?: (content: string) => void
}

export function PostTemplateGrid({ onApply }: Props) {
  const { templates, loading, useTemplate } = usePostTemplates()
  const [applying, setApplying] = useState<string | null>(null)
  const [copied, setCopied] = useState<string | null>(null)

  const handleUse = async (id: string) => {
    setApplying(id)
    const { content } = await useTemplate(id)
    if (content && onApply) {
      onApply(content)
    }
    setApplying(null)
  }

  const handleCopy = async (id: string, text: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  if (templates.length === 0) {
    return <EmptyState title="Chưa có template bài viết" description="Template giúp tạo nội dung nhanh hơn." />
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((t) => (
        <div key={t.id} className="rounded-bento border border-border bg-card p-4 flex flex-col gap-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <FileText size={16} className="text-primary" />
              <h4 className="text-sm font-semibold text-fg">{t.name}</h4>
            </div>
            <span className="text-xs text-fg-muted bg-surface px-2 py-0.5 rounded">
              {PLATFORM_LABELS[t.platform_type]}
            </span>
          </div>

          <p className="text-xs text-fg-muted line-clamp-4 whitespace-pre-wrap flex-1">
            {t.content_template}
          </p>

          <div className="flex items-center gap-2 pt-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleCopy(t.id, t.content_template)}
            >
              {copied === t.id ? <Check size={14} /> : <Copy size={14} />}
              {copied === t.id ? 'Đã sao chép' : 'Sao chép'}
            </Button>
            {onApply && (
              <Button
                size="sm"
                onClick={() => handleUse(t.id)}
                loading={applying === t.id}
              >
                Áp dụng
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
