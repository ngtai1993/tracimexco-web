'use client'
import { useState } from 'react'
import { Layout, Check, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { EmptyState } from '@/components/ui/EmptyState'
import { Spinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { useBannerLayouts } from '../../hooks'
import type { BannerLayout, BannerLayoutJson } from '../../types'

interface BannerLayoutGridProps {
  postId: string
}

export function BannerLayoutGrid({ postId }: BannerLayoutGridProps) {
  const { layouts, loading, generating, generate, update, approve } = useBannerLayouts(postId)
  const [showGenerate, setShowGenerate] = useState(false)
  const [genRagInstance, setGenRagInstance] = useState('')
  const [genVariants, setGenVariants] = useState(2)
  const [editLayout, setEditLayout] = useState<BannerLayout | null>(null)

  const handleGenerate = () => {
    generate(genRagInstance || undefined, genVariants)
    setShowGenerate(false)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-fg flex items-center gap-2">
          <Layout size={18} />
          Banner Layouts
        </h3>
        <Button size="sm" onClick={() => setShowGenerate(true)} loading={generating}>
          <Sparkles size={14} />
          Sinh banner tự động
        </Button>
      </div>

      {generating && (
        <div className="flex flex-col items-center gap-3 py-8 rounded-bento border border-border bg-surface/50">
          <Spinner size={24} />
          <p className="text-sm text-fg-muted animate-pulse">Đang tạo layout...</p>
        </div>
      )}

      {!generating && layouts.length === 0 ? (
        <EmptyState
          title="Chưa có banner layout"
          description="Sinh banner tự động để tạo bố cục cho bài viết."
          actionLabel="Sinh banner"
          onAction={() => setShowGenerate(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {layouts.map((layout) => (
            <BannerLayoutCard
              key={layout.id}
              layout={layout}
              onEdit={() => setEditLayout(layout)}
              onApprove={() => approve(layout.id)}
            />
          ))}
        </div>
      )}

      {/* Generate Modal */}
      <Modal open={showGenerate} onClose={() => setShowGenerate(false)} title="Sinh banner layout">
        <div className="space-y-4">
          <Input
            label="RAG Instance ID (không bắt buộc)"
            value={genRagInstance}
            onChange={(e) => setGenRagInstance(e.target.value)}
            placeholder="Bỏ trống để dùng mặc định"
          />
          <Input
            label="Số variants"
            type="number"
            min={1}
            max={5}
            value={genVariants}
            onChange={(e) => setGenVariants(Number(e.target.value))}
          />
          <div className="flex justify-end gap-2">
            <Button size="sm" variant="ghost" onClick={() => setShowGenerate(false)}>
              Hủy
            </Button>
            <Button size="sm" onClick={handleGenerate}>
              Tạo
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit Modal */}
      {editLayout && (
        <BannerLayoutEditor
          layout={editLayout}
          onClose={() => setEditLayout(null)}
          onSave={async (json) => {
            await update(editLayout.id, json)
            setEditLayout(null)
          }}
        />
      )}
    </div>
  )
}

// ── Banner Card ───────────────────────────────────────────────

interface BannerLayoutCardProps {
  layout: BannerLayout
  onEdit: () => void
  onApprove: () => void
}

function BannerLayoutCard({ layout, onEdit, onApprove }: BannerLayoutCardProps) {
  const json = layout.layout_json
  const bgValue = json.background?.value ?? '#1F2937'

  return (
    <div className="rounded-bento border border-border overflow-hidden bg-card">
      {/* Visual Preview */}
      <div
        className="relative h-36 flex items-center justify-center p-4"
        style={{
          background: json.background?.type === 'gradient'
            ? json.background.value
            : json.background?.type === 'color'
            ? bgValue
            : '#1F2937',
        }}
      >
        <div className={cn(
          'text-center',
          json.title_position === 'bottom-left' && 'text-left self-end',
          json.title_position === 'top-center' && 'self-start',
        )}>
          <p className="text-white text-lg font-bold" style={{ fontFamily: json.font_family }}>
            {json.title || 'Tiêu đề banner'}
          </p>
          {json.tagline && (
            <p className="text-white/80 text-sm mt-1">{json.tagline}</p>
          )}
        </div>
        {json.accent_color && (
          <div
            className="absolute bottom-0 left-0 right-0 h-1"
            style={{ backgroundColor: json.accent_color }}
          />
        )}
      </div>

      {/* Info */}
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-fg">Variant #{layout.variant_index}</span>
          {layout.is_approved ? (
            <Badge color="success">Đã duyệt</Badge>
          ) : (
            <Badge color="neutral">Chờ duyệt</Badge>
          )}
        </div>

        <div className="flex flex-wrap gap-1.5 text-xs text-fg-muted">
          {json.layout_style && <span className="px-1.5 py-0.5 bg-surface rounded">{json.layout_style}</span>}
          {json.font_family && <span className="px-1.5 py-0.5 bg-surface rounded">{json.font_family}</span>}
        </div>

        <div className="flex gap-2 pt-2">
          <Button size="sm" variant="outline" onClick={onEdit} className="flex-1">
            Chỉnh sửa
          </Button>
          {!layout.is_approved && (
            <Button size="sm" onClick={onApprove} className="flex-1">
              <Check size={14} />
              Duyệt
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Banner Editor ─────────────────────────────────────────────

interface BannerLayoutEditorProps {
  layout: BannerLayout
  onClose: () => void
  onSave: (json: BannerLayoutJson) => void
}

function BannerLayoutEditor({ layout, onClose, onSave }: BannerLayoutEditorProps) {
  const [json, setJson] = useState<BannerLayoutJson>({ ...layout.layout_json })

  const updateField = <K extends keyof BannerLayoutJson>(key: K, value: BannerLayoutJson[K]) => {
    setJson((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <Modal open onClose={onClose} title={`Chỉnh sửa Variant #${layout.variant_index}`} className="max-w-lg">
      <div className="space-y-3">
        <Input
          label="Title"
          value={json.title ?? ''}
          onChange={(e) => updateField('title', e.target.value)}
        />
        <Input
          label="Tagline"
          value={json.tagline ?? ''}
          onChange={(e) => updateField('tagline', e.target.value)}
        />
        <Input
          label="Background Color"
          type="color"
          value={json.background?.value ?? '#1F2937'}
          onChange={(e) => updateField('background', { type: 'color', value: e.target.value })}
        />
        <Input
          label="Accent Color"
          type="color"
          value={json.accent_color ?? '#FF5733'}
          onChange={(e) => updateField('accent_color', e.target.value)}
        />
        <Input
          label="Font Family"
          value={json.font_family ?? ''}
          onChange={(e) => updateField('font_family', e.target.value)}
          placeholder="Montserrat, Arial..."
        />
        <Select
          label="Layout Style"
          options={[
            { value: 'bold', label: 'Bold' },
            { value: 'minimal', label: 'Minimal' },
            { value: 'elegant', label: 'Elegant' },
            { value: 'playful', label: 'Playful' },
          ]}
          value={json.layout_style ?? 'bold'}
          onChange={(e) => updateField('layout_style', e.target.value as BannerLayoutJson['layout_style'])}
        />
        <Select
          label="Logo Placement"
          options={[
            { value: 'top-left', label: 'Trên trái' },
            { value: 'top-right', label: 'Trên phải' },
            { value: 'none', label: 'Không có' },
          ]}
          value={json.logo_placement ?? 'top-left'}
          onChange={(e) => updateField('logo_placement', e.target.value as BannerLayoutJson['logo_placement'])}
        />
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <Button size="sm" variant="ghost" onClick={onClose}>
          Hủy
        </Button>
        <Button size="sm" onClick={() => onSave(json)}>
          Lưu
        </Button>
      </div>
    </Modal>
  )
}
