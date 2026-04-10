'use client'
import { useState } from 'react'
import { Sparkles, Hash } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useAIGenerate, useSuggestHashtags } from '../../hooks'
import { PLATFORM_OPTIONS } from '../../constants'
import type { PlatformType } from '../../types'

interface AIGenerationPanelProps {
  postId?: string
  platformType?: PlatformType
  onApplyContent?: (content: string) => void
  onApplyHashtags?: (hashtags: string[]) => void
}

export function AIGenerationPanel({
  platformType,
  onApplyContent,
  onApplyHashtags,
}: AIGenerationPanelProps) {
  const [prompt, setPrompt] = useState('')
  const [ragInstance, setRagInstance] = useState('')
  const [platform, setPlatform] = useState<PlatformType>(platformType ?? 'facebook')
  const [variants, setVariants] = useState(1)
  const [language, setLanguage] = useState<'vi' | 'en'>('vi')

  const { generate, generation, loading: generating } = useAIGenerate()
  const { suggest: suggestHashtags, loading: suggestingHashtags } = useSuggestHashtags()

  const [hashtagContent, setHashtagContent] = useState('')
  const [suggestedHashtags, setSuggestedHashtags] = useState<string[]>([])

  const handleGenerate = async () => {
    if (!prompt.trim() || !ragInstance) return
    await generate({
      rag_instance: ragInstance,
      prompt,
      platform_type: platform,
      variants,
      language,
    })
  }

  const handleSuggestHashtags = async () => {
    if (!hashtagContent.trim()) return
    const result = await suggestHashtags(hashtagContent, platform)
    if (result.hashtags) {
      setSuggestedHashtags(result.hashtags)
    }
  }

  const applyResultContent = (content: string) => {
    onApplyContent?.(content)
    setHashtagContent(content)
  }

  const applySuggestedHashtags = () => {
    if (suggestedHashtags.length === 0) return
    onApplyHashtags?.(suggestedHashtags)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left — Generation Form */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-fg flex items-center gap-2">
          <Sparkles size={18} className="text-primary" />
          Tạo nội dung bằng AI
        </h3>

        <Input
          label="RAG Instance ID"
          value={ragInstance}
          onChange={(e) => setRagInstance(e.target.value)}
          placeholder="Nhập ID hoặc chọn RAG Instance..."
        />

        <Textarea
          label="Prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Mô tả chủ đề bài viết bạn muốn AI viết..."
        />

        <div className="grid grid-cols-3 gap-3">
          <Select
            label="Nền tảng"
            options={PLATFORM_OPTIONS}
            value={platform}
            onChange={(e) => setPlatform(e.target.value as PlatformType)}
          />
          <Select
            label="Ngôn ngữ"
            options={[
              { value: 'vi', label: 'Tiếng Việt' },
              { value: 'en', label: 'English' },
            ]}
            value={language}
            onChange={(e) => setLanguage(e.target.value as 'vi' | 'en')}
          />
          <Input
            label="Số variants"
            type="number"
            min={1}
            max={5}
            value={variants}
            onChange={(e) => setVariants(Number(e.target.value))}
          />
        </div>

        <Button onClick={handleGenerate} loading={generating} disabled={!prompt.trim() || !ragInstance}>
          <Sparkles size={14} />
          Tạo nội dung
        </Button>

        {/* Hashtag section */}
        <div className="pt-4 border-t border-border space-y-3">
          <h4 className="text-sm font-medium text-fg flex items-center gap-2">
            <Hash size={15} />
            Gợi ý Hashtags
          </h4>
          <Textarea
            value={hashtagContent}
            onChange={(e) => setHashtagContent(e.target.value)}
            placeholder="Paste nội dung bài viết để AI gợi ý hashtags..."
            className="min-h-[80px]"
          />
          <Button size="sm" variant="outline" onClick={handleSuggestHashtags} loading={suggestingHashtags}>
            Gợi ý
          </Button>
          {suggestedHashtags.length > 0 && (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {suggestedHashtags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium cursor-pointer hover:bg-primary/20 transition-colors"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              {onApplyHashtags && (
                <Button size="sm" variant="ghost" onClick={applySuggestedHashtags}>
                  Dùng hashtags này
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right — Results */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-fg">Kết quả</h3>

        {generating && (
          <div className="flex flex-col items-center gap-3 py-12 rounded-bento border border-border bg-surface/50">
            <Spinner size={28} />
            <p className="text-sm text-fg-muted animate-pulse">
              {generation?.status === 'processing' ? 'AI đang viết...' : 'Đang chuẩn bị...'}
            </p>
          </div>
        )}

        {!generating && !generation && (
          <EmptyState
            title="Chưa có kết quả"
            description="Nhập prompt và nhấn Tạo nội dung để bắt đầu."
          />
        )}

        {!generating && generation?.status === 'failed' && (
          <div className="rounded-bento border border-danger/30 bg-danger/5 p-4">
            <p className="text-sm text-danger font-medium">Tạo nội dung thất bại</p>
            <p className="text-sm text-fg-muted mt-1">{generation.error_message}</p>
          </div>
        )}

        {!generating && generation?.status === 'completed' && (
          <div className="space-y-3">
            {generation.result_variants.length > 0 ? (
              generation.result_variants.map((variant, idx) => (
                <div key={idx} className="rounded-bento border border-border p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-fg-muted">Phiên bản {idx + 1}</span>
                    <div className="flex items-center gap-2">
                      {onApplyContent && (
                        <Button size="sm" variant="outline" onClick={() => applyResultContent(variant)}>
                          Dùng nội dung này
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => navigator.clipboard.writeText(variant)}
                      >
                        Copy
                      </Button>
                    </div>
                  </div>
                  <p className="text-sm text-fg whitespace-pre-wrap">{variant}</p>
                </div>
              ))
            ) : generation.result_content ? (
              <div className="rounded-bento border border-border p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-fg-muted">Kết quả</span>
                  <div className="flex items-center gap-2">
                    {onApplyContent && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => applyResultContent(generation.result_content)}
                      >
                        Dùng nội dung này
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => navigator.clipboard.writeText(generation.result_content)}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-fg whitespace-pre-wrap">{generation.result_content}</p>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  )
}
