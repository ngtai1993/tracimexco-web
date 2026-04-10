'use client'
import { Layout } from 'lucide-react'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useLayoutTemplates } from '../../hooks'
import { PLATFORM_LABELS } from '../../constants'
import type { LayoutTemplate } from '../../types'

function LayoutPreview({ layout }: { layout: LayoutTemplate }) {
  const json = layout.layout_json
  const backgroundStyle =
    json.background?.type === 'gradient'
      ? { backgroundImage: json.background.value }
      : json.background?.type === 'image'
      ? {
          backgroundImage: `url(${json.background.value})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }
      : { backgroundColor: json.background?.value || '#f5f5f5' }

  return (
    <div
      className="aspect-video rounded border border-border flex items-center justify-center text-xs"
      style={backgroundStyle}
    >
      <div className="text-center p-2" style={{ color: json.accent_color || '#333' }}>
        <p className="font-bold text-sm">{json.title || 'Title'}</p>
        <p className="text-xs opacity-70">{json.tagline || 'Tagline'}</p>
      </div>
    </div>
  )
}

export function LayoutTemplateGrid() {
  const { templates, loading } = useLayoutTemplates()

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  if (templates.length === 0) {
    return <EmptyState title="Chưa có layout template" description="Layout template dùng cho banner." />
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((t) => (
        <div key={t.id} className="rounded-bento border border-border bg-card p-4 space-y-3">
          <LayoutPreview layout={t} />

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layout size={14} className="text-primary" />
              <h4 className="text-sm font-semibold text-fg">{t.name}</h4>
            </div>
            {t.platform_type && (
              <span className="text-xs text-fg-muted bg-surface px-2 py-0.5 rounded">
                {PLATFORM_LABELS[t.platform_type]}
              </span>
            )}
          </div>

          <div className="text-xs text-fg-muted space-y-0.5">
            <p>Style: {t.layout_json.layout_style || '—'}</p>
            <p>Font: {t.layout_json.font_family || '—'}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
