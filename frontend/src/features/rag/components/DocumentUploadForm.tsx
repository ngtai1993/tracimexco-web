'use client'
import { useState } from 'react'
import { Upload, Type, Globe, FileUp } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useUploadDocument, useAddTextDocument, useAddURLDocument } from '../hooks'

interface DocumentUploadFormProps {
  kbSlug: string
  onSuccess: () => void
  onCancel: () => void
}

type UploadTab = 'file' | 'text' | 'url'

export function DocumentUploadForm({ kbSlug, onSuccess, onCancel }: DocumentUploadFormProps) {
  const [tab, setTab] = useState<UploadTab>('file')

  return (
    <div className="space-y-4">
      {/* Tab Switcher */}
      <div className="flex gap-1 p-1 rounded-bento bg-surface border border-border">
        {([
          { key: 'file' as const, label: 'Upload File', icon: FileUp },
          { key: 'text' as const, label: 'Nhập Text', icon: Type },
          { key: 'url' as const, label: 'URL', icon: Globe },
        ]).map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm rounded-md transition-colors ${
              tab === key
                ? 'bg-primary text-white font-medium'
                : 'text-fg-muted hover:text-fg'
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {tab === 'file' && <FileUploadForm kbSlug={kbSlug} onSuccess={onSuccess} onCancel={onCancel} />}
      {tab === 'text' && <TextForm kbSlug={kbSlug} onSuccess={onSuccess} onCancel={onCancel} />}
      {tab === 'url' && <URLForm kbSlug={kbSlug} onSuccess={onSuccess} onCancel={onCancel} />}
    </div>
  )
}

function FileUploadForm({ kbSlug, onSuccess, onCancel }: { kbSlug: string; onSuccess: () => void; onCancel: () => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const { upload, loading, error } = useUploadDocument()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title || file.name)
    if (description) formData.append('description', description)
    const result = await upload(kbSlug, formData)
    if (result) onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div>
        <label className="block text-sm font-medium text-fg mb-1">File</label>
        <div className="border-2 border-dashed border-border rounded-bento p-6 text-center hover:border-primary/40 transition-colors">
          <input
            type="file"
            onChange={(e) => {
              const f = e.target.files?.[0] ?? null
              setFile(f)
              if (f && !title) setTitle(f.name.replace(/\.[^.]+$/, ''))
            }}
            className="hidden"
            id="file-upload"
            accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.png,.jpg,.jpeg,.gif,.webp"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload size={24} className="mx-auto mb-2 text-fg-muted" />
            <p className="text-sm text-fg-muted">
              {file ? file.name : 'Kéo file vào đây hoặc click để chọn'}
            </p>
            <p className="text-xs text-fg-subtle mt-1">
              PDF, DOC, TXT, MD, CSV, XLSX, PNG, JPG...
            </p>
          </label>
        </div>
      </div>
      <Input
        label="Tiêu đề"
        placeholder="Tên tài liệu"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Input
        label="Mô tả (tùy chọn)"
        placeholder="Mô tả ngắn gọn..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>Hủy</Button>
        <Button type="submit" size="sm" loading={loading} disabled={!file}>Upload</Button>
      </div>
    </form>
  )
}

function TextForm({ kbSlug, onSuccess, onCancel }: { kbSlug: string; onSuccess: () => void; onCancel: () => void }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [description, setDescription] = useState('')
  const { add, loading, error } = useAddTextDocument()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await add(kbSlug, { title, content_text: content, description: description || undefined })
    if (result) onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tiêu đề"
        placeholder="Tên tài liệu"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <div>
        <label className="block text-sm font-medium text-fg mb-1">Nội dung</label>
        <textarea
          className="w-full rounded-bento border border-border bg-surface px-3 py-2 text-sm text-fg placeholder:text-fg-subtle focus:border-primary focus:ring-1 focus:ring-primary/30 min-h-[200px] resize-y"
          placeholder="Nhập nội dung tài liệu..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
      </div>
      <Input
        label="Mô tả (tùy chọn)"
        placeholder="Mô tả ngắn gọn..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>Hủy</Button>
        <Button type="submit" size="sm" loading={loading}>Lưu Text</Button>
      </div>
    </form>
  )
}

function URLForm({ kbSlug, onSuccess, onCancel }: { kbSlug: string; onSuccess: () => void; onCancel: () => void }) {
  const [title, setTitle] = useState('')
  const [url, setURL] = useState('')
  const [description, setDescription] = useState('')
  const { add, loading, error } = useAddURLDocument()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await add(kbSlug, { title, source_url: url, description: description || undefined })
    if (result) onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tiêu đề"
        placeholder="Tên tài liệu"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <Input
        label="URL"
        placeholder="https://example.com/document"
        value={url}
        onChange={(e) => setURL(e.target.value)}
        type="url"
        required
      />
      <Input
        label="Mô tả (tùy chọn)"
        placeholder="Mô tả ngắn gọn..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>Hủy</Button>
        <Button type="submit" size="sm" loading={loading}>Thêm URL</Button>
      </div>
    </form>
  )
}
