'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { useCreateProvider, useUpdateProvider } from '../hooks'
import type { AgentProvider, AgentProviderInput } from '../types'

interface ProviderFormProps {
  provider?: AgentProvider | null
  onSuccess: () => void
  onCancel: () => void
}

export function ProviderForm({ provider, onSuccess, onCancel }: ProviderFormProps) {
  const [form, setForm] = useState<AgentProviderInput>({
    name: provider?.name ?? '',
    slug: provider?.slug ?? '',
    description: provider?.description ?? '',
    website_url: provider?.website_url ?? '',
    is_active: provider?.is_active ?? true,
  })

  const { create, loading: creating, error: createError } = useCreateProvider()
  const { update, loading: updating, error: updateError } = useUpdateProvider()

  const loading = creating || updating
  const error = createError || updateError
  const isEdit = !!provider

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (isEdit) {
      const result = await update(provider!.slug, form)
      if (result) onSuccess()
    } else {
      const result = await create(form)
      if (result) onSuccess()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tên Provider"
        placeholder="OpenAI"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        required
      />
      <Input
        label="Slug"
        placeholder="openai"
        value={form.slug}
        onChange={(e) => setForm({ ...form, slug: e.target.value })}
        required
        disabled={isEdit}
        hint={isEdit ? 'Slug không thể thay đổi' : 'Dùng để định danh URL, viết thường, không dấu'}
      />
      <Input
        label="Mô tả"
        placeholder="Nhà cung cấp AI hàng đầu..."
        value={form.description}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
      />
      <Input
        label="Website URL"
        placeholder="https://openai.com"
        value={form.website_url}
        onChange={(e) => setForm({ ...form, website_url: e.target.value })}
        type="url"
      />
      <Switch
        checked={form.is_active ?? true}
        onChange={(checked) => setForm({ ...form, is_active: checked })}
        label="Kích hoạt"
      />

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Cập nhật' : 'Tạo Provider'}
        </Button>
      </div>
    </form>
  )
}
