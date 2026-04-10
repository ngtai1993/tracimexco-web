'use client'
import { useEffect, useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { PLATFORM_OPTIONS, PLATFORM_CHAR_LIMITS } from '../../constants'
import { useCategories, useTags } from '../../hooks'
import type { PostInput, PlatformType, Category } from '../../types'

interface PostFormProps {
  initialData?: Partial<PostInput>
  onSubmit: (data: PostInput) => void
  loading?: boolean
  disabled?: boolean
}

function buildCategoryTree(categories: Category[]): { value: string; label: string }[] {
  const map = new Map<string | null, Category[]>()
  for (const cat of categories) {
    const parentKey = cat.parent ?? '__root__'
    if (!map.has(parentKey)) map.set(parentKey, [])
    map.get(parentKey)!.push(cat)
  }

  const result: { value: string; label: string }[] = []
  function recurse(parentId: string | null, depth: number) {
    const children = map.get(parentId ?? '__root__') ?? []
    for (const child of children) {
      result.push({ value: child.id, label: '  '.repeat(depth) + child.name })
      recurse(child.id, depth + 1)
    }
  }
  recurse(null, 0)
  return result
}

export function PostForm({ initialData, onSubmit, loading, disabled }: PostFormProps) {
  const [title, setTitle] = useState(initialData?.title ?? '')
  const [content, setContent] = useState(initialData?.content ?? '')
  const [platformType, setPlatformType] = useState<PlatformType>(initialData?.platform_type ?? 'facebook')
  const [categoryId, setCategoryId] = useState(initialData?.category ?? '')
  const [selectedTags, setSelectedTags] = useState<string[]>(initialData?.tags ?? [])
  const [hashtags, setHashtags] = useState(initialData?.hashtags?.join(' ') ?? '')
  const [tagInput, setTagInput] = useState('')

  useEffect(() => {
    setTitle(initialData?.title ?? '')
    setContent(initialData?.content ?? '')
    setPlatformType(initialData?.platform_type ?? 'facebook')
    setCategoryId(initialData?.category ?? '')
    setSelectedTags(initialData?.tags ?? [])
    setHashtags(initialData?.hashtags?.join(' ') ?? '')
  }, [
    initialData?.title,
    initialData?.content,
    initialData?.platform_type,
    initialData?.category,
    initialData?.tags,
    initialData?.hashtags,
  ])

  const { categories } = useCategories()
  const { tags, create: createTag } = useTags()

  const charLimit = PLATFORM_CHAR_LIMITS[platformType]
  const charCount = content.length
  const isOverLimit = charLimit !== Infinity && charCount > charLimit

  const categoryOptions = [
    { value: '', label: 'Không chọn danh mục' },
    ...buildCategoryTree(categories),
  ]

  const filteredTags = tags.filter(
    (t) =>
      !selectedTags.includes(t.id) &&
      t.name.toLowerCase().includes(tagInput.toLowerCase())
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const parsedHashtags = hashtags
      .split(/[\s,]+/)
      .filter(Boolean)
      .map((h) => (h.startsWith('#') ? h : `#${h}`))

    onSubmit({
      title,
      content,
      platform_type: platformType,
      category: categoryId || null,
      tags: selectedTags,
      hashtags: parsedHashtags,
    })
  }

  const addTag = (tagId: string) => {
    setSelectedTags((prev) => [...prev, tagId])
    setTagInput('')
  }

  const removeTag = (tagId: string) => {
    setSelectedTags((prev) => prev.filter((id) => id !== tagId))
  }

  const handleCreateTag = async () => {
    if (!tagInput.trim()) return
    const result = await createTag(tagInput.trim())
    if (!result.error) {
      setTagInput('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        label="Tiêu đề"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Nhập tiêu đề bài viết..."
        required
        disabled={disabled}
      />

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Nền tảng"
          options={PLATFORM_OPTIONS}
          value={platformType}
          onChange={(e) => setPlatformType(e.target.value as PlatformType)}
          disabled={disabled}
        />
        <Select
          label="Danh mục"
          options={categoryOptions}
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          disabled={disabled}
        />
      </div>

      <div>
        <Textarea
          label="Nội dung"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Viết nội dung bài viết..."
          className="min-h-[200px]"
          required
          disabled={disabled}
        />
        {charLimit !== Infinity && (
          <div className="flex justify-end mt-1">
            <span className={`text-xs ${isOverLimit ? 'text-danger font-medium' : 'text-fg-muted'}`}>
              {charCount.toLocaleString()} / {charLimit.toLocaleString()}
            </span>
          </div>
        )}
      </div>

      <Input
        label="Hashtags"
        value={hashtags}
        onChange={(e) => setHashtags(e.target.value)}
        placeholder="#marketing #tracimexco #content"
        hint="Cách nhau bằng dấu cách hoặc phẩy"
        disabled={disabled}
      />

      {/* Tags multi-select */}
      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium text-fg">Tags</label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {selectedTags.map((tagId) => {
            const tag = tags.find((t) => t.id === tagId)
            return tag ? (
              <span
                key={tagId}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium"
              >
                {tag.name}
                {!disabled && (
                  <button type="button" onClick={() => removeTag(tagId)} className="hover:text-danger">
                    ×
                  </button>
                )}
              </span>
            ) : null
          })}
        </div>
        {!disabled && (
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                placeholder="Tìm hoặc tạo tag mới..."
              />
              {tagInput && filteredTags.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-surface border border-border rounded-bento shadow-lg z-10 max-h-40 overflow-y-auto">
                  {filteredTags.slice(0, 8).map((tag) => (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => addTag(tag.id)}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-border/30 transition-colors"
                    >
                      {tag.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {tagInput && !tags.some((t) => t.name.toLowerCase() === tagInput.toLowerCase()) && (
              <Button type="button" size="sm" variant="outline" onClick={handleCreateTag}>
                + Tạo
              </Button>
            )}
          </div>
        )}
      </div>

      {!disabled && (
        <div className="flex justify-end gap-3 pt-4">
          <Button type="submit" loading={loading}>
            Lưu bài viết
          </Button>
        </div>
      )}
    </form>
  )
}
