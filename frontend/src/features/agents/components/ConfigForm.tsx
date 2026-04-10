'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { useCreateConfig, useUpdateConfig } from '../hooks'
import type { AgentConfig, AgentConfigInput } from '../types'

interface ConfigFormProps {
  providerSlug: string
  config?: AgentConfig | null
  onSuccess: () => void
  onCancel: () => void
}

export function ConfigForm({ providerSlug, config, onSuccess, onCancel }: ConfigFormProps) {
  const isEdit = !!config

  const [name, setName] = useState(config?.name ?? '')
  const [modelName, setModelName] = useState(config?.model_name ?? '')
  const [configJson, setConfigJson] = useState(
    config ? JSON.stringify(config.config_json, null, 2) : '{\n  "temperature": 0.7,\n  "max_tokens": 2048\n}'
  )
  const [isDefault, setIsDefault] = useState(config?.is_default ?? false)
  const [isActive, setIsActive] = useState(config?.is_active ?? true)
  const [jsonError, setJsonError] = useState<string | null>(null)

  const { create, loading: creating, error: createError } = useCreateConfig()
  const { update, loading: updating, error: updateError } = useUpdateConfig()

  const loading = creating || updating
  const error = createError || updateError

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setJsonError(null)

    let parsed: Record<string, unknown>
    try {
      parsed = JSON.parse(configJson)
    } catch {
      setJsonError('JSON không hợp lệ')
      return
    }

    const data: AgentConfigInput = {
      name,
      model_name: modelName,
      config_json: parsed,
      is_default: isDefault,
      is_active: isActive,
    }

    if (isEdit) {
      const result = await update(providerSlug, config!.id, data)
      if (result) onSuccess()
    } else {
      const result = await create(providerSlug, data)
      if (result) onSuccess()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tên Config"
        placeholder="GPT-4o Default"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <Input
        label="Model Name"
        placeholder="gpt-4o"
        value={modelName}
        onChange={(e) => setModelName(e.target.value)}
        required
        hint="Tên model API (vd: gpt-4o, claude-3-opus, gemini-pro)"
      />
      <Textarea
        label="Config JSON"
        value={configJson}
        onChange={(e) => setConfigJson(e.target.value)}
        className="font-mono text-xs min-h-[120px]"
        error={jsonError ?? undefined}
      />
      <div className="flex gap-6">
        <Switch checked={isDefault} onChange={setIsDefault} label="Đặt làm default" />
        <Switch checked={isActive} onChange={setIsActive} label="Kích hoạt" />
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Cập nhật' : 'Tạo Config'}
        </Button>
      </div>
    </form>
  )
}
