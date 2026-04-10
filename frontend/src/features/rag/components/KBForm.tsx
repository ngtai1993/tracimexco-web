'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { useCreateKB } from '../hooks'
import type { KBInput } from '../types'

interface KBFormProps {
  onSuccess: () => void
  onCancel: () => void
}

export function KBForm({ onSuccess, onCancel }: KBFormProps) {
  const [form, setForm] = useState<KBInput>({
    name: '',
    slug: '',
    description: '',
    chunk_strategy: 'recursive',
    chunk_size: 1000,
    chunk_overlap: 200,
    embedding_model: 'text-embedding-3-small',
  })

  const { create, loading, error } = useCreateKB()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await create(form)
    if (result) onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tên Knowledge Base"
        placeholder="Tài liệu nội bộ"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        required
      />
      <Input
        label="Slug"
        placeholder="tai-lieu-noi-bo"
        value={form.slug}
        onChange={(e) => setForm({ ...form, slug: e.target.value })}
        required
        hint="Dùng để định danh URL"
      />
      <Input
        label="Mô tả"
        placeholder="Mô tả knowledge base..."
        value={form.description ?? ''}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
      />
      <Select
        label="Chunking Strategy"
        value={form.chunk_strategy ?? 'recursive'}
        onChange={(e) => setForm({ ...form, chunk_strategy: e.target.value })}
        options={[
          { value: 'fixed', label: 'Fixed Size' },
          { value: 'recursive', label: 'Recursive' },
          { value: 'semantic', label: 'Semantic' },
        ]}
      />
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Chunk Size"
          type="number"
          value={String(form.chunk_size ?? 1000)}
          onChange={(e) => setForm({ ...form, chunk_size: Number(e.target.value) })}
          min={100}
          max={10000}
        />
        <Input
          label="Chunk Overlap"
          type="number"
          value={String(form.chunk_overlap ?? 200)}
          onChange={(e) => setForm({ ...form, chunk_overlap: Number(e.target.value) })}
          min={0}
          max={5000}
        />
      </div>
      <Input
        label="Embedding Model"
        placeholder="text-embedding-3-small"
        value={form.embedding_model ?? ''}
        onChange={(e) => setForm({ ...form, embedding_model: e.target.value })}
      />

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          Tạo Knowledge Base
        </Button>
      </div>
    </form>
  )
}
