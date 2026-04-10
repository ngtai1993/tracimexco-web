'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { Select } from '@/components/ui/Select'
import { useCreateInstance, useUpdateInstance } from '../hooks'
import { useProviders } from '@/features/agents/hooks'
import { useConfigs } from '@/features/agents/hooks'
import type { RAGInstance, RAGInstanceInput } from '../types'

interface InstanceFormProps {
  instance?: RAGInstance | null
  onSuccess: () => void
  onCancel: () => void
}

export function InstanceForm({ instance, onSuccess, onCancel }: InstanceFormProps) {
  const { providers } = useProviders()
  const firstProvider = providers[0]

  const [form, setForm] = useState<RAGInstanceInput>({
    name: instance?.name ?? '',
    slug: instance?.slug ?? '',
    system_prompt: instance?.system_prompt ?? '',
    description: instance?.description ?? '',
    purpose: instance?.purpose ?? '',
    provider_id: '',
    agent_config_id: null,
    is_public: instance?.is_public ?? false,
  })

  const [selectedProviderSlug, setSelectedProviderSlug] = useState(
    instance?.provider_name ? providers.find(p => p.name === instance.provider_name)?.slug ?? '' : ''
  )

  const { configs } = useConfigs(selectedProviderSlug || firstProvider?.slug || '')

  const { create, loading: creating, error: createError } = useCreateInstance()
  const { update, loading: updating, error: updateError } = useUpdateInstance()

  const loading = creating || updating
  const error = createError || updateError
  const isEdit = !!instance

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (isEdit) {
      const result = await update(instance!.slug, form)
      if (result) onSuccess()
    } else {
      const result = await create(form)
      if (result) onSuccess()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tên Instance"
        placeholder="Trợ lý nội bộ"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        required
      />
      <Input
        label="Slug"
        placeholder="tro-ly-noi-bo"
        value={form.slug}
        onChange={(e) => setForm({ ...form, slug: e.target.value })}
        required
        disabled={isEdit}
        hint={isEdit ? 'Slug không thể thay đổi' : 'Dùng để định danh URL'}
      />
      <Input
        label="Mô tả"
        placeholder="RAG instance cho..."
        value={form.description ?? ''}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
      />
      <Input
        label="Mục đích"
        placeholder="Hỗ trợ nhân viên..."
        value={form.purpose ?? ''}
        onChange={(e) => setForm({ ...form, purpose: e.target.value })}
      />

      <Select
        label="Provider"
        value={selectedProviderSlug}
        onChange={(e) => {
          setSelectedProviderSlug(e.target.value)
          const p = providers.find(pr => pr.slug === e.target.value)
          if (p) setForm({ ...form, provider_id: p.id })
        }}
        placeholder="Chọn provider"
        options={providers.map(p => ({ value: p.slug, label: p.name }))}
      />

      <Select
        label="Agent Config"
        value={form.agent_config_id ?? ''}
        onChange={(e) => setForm({ ...form, agent_config_id: e.target.value || null })}
        placeholder="Mặc định"
        options={configs.map(c => ({ value: c.id, label: `${c.name} (${c.model_name})` }))}
      />

      <div>
        <label className="block text-sm font-medium text-fg mb-1">System Prompt</label>
        <textarea
          className="w-full rounded-bento border border-border bg-surface px-3 py-2 text-sm text-fg placeholder:text-fg-subtle focus:border-primary focus:ring-1 focus:ring-primary/30 min-h-[120px] resize-y"
          placeholder="Bạn là trợ lý AI..."
          value={form.system_prompt}
          onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
          required
        />
      </div>

      <Switch
        checked={form.is_public ?? false}
        onChange={(checked) => setForm({ ...form, is_public: checked })}
        label="Công khai (Public)"
      />

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Cập nhật' : 'Tạo Instance'}
        </Button>
      </div>
    </form>
  )
}
