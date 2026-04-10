'use client'
import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { useCreateSkill, useUpdateSkill } from '../hooks'
import type { RAGSkill, RAGSkillInput } from '../types'

interface SkillFormProps {
  skill?: RAGSkill
  onSuccess: () => void
  onCancel: () => void
}

const SKILL_TYPE_OPTIONS = [
  { value: 'builtin', label: 'Built-in' },
  { value: 'api_call', label: 'External API Call' },
  { value: 'custom', label: 'Custom Implementation' },
]

const stringify = (v: unknown) => {
  if (!v || (typeof v === 'object' && Object.keys(v as object).length === 0)) return '{}'
  return JSON.stringify(v, null, 2)
}

export function SkillForm({ skill, onSuccess, onCancel }: SkillFormProps) {
  const isEdit = !!skill

  const [form, setForm] = useState<RAGSkillInput>({
    name: skill?.name ?? '',
    slug: skill?.slug ?? '',
    description: skill?.description ?? '',
    skill_type: (skill?.skill_type as RAGSkillInput['skill_type']) ?? 'builtin',
    is_active: skill?.is_active ?? true,
    implementation_path: skill?.implementation_path ?? '',
    api_endpoint: skill?.api_endpoint ?? '',
    api_method: skill?.api_method ?? 'POST',
  })
  const [configText, setConfigText] = useState(stringify(skill?.config))
  const [inputSchemaText, setInputSchemaText] = useState(stringify(skill?.input_schema))
  const [outputSchemaText, setOutputSchemaText] = useState(stringify(skill?.output_schema))
  const [apiHeadersText, setApiHeadersText] = useState('{}')
  const [jsonError, setJsonError] = useState<string | null>(null)

  const { create, loading: creating, error: createError } = useCreateSkill()
  const { update, loading: updating, error: updateError } = useUpdateSkill()
  const loading = creating || updating
  const error = createError || updateError

  const isApiSkill = form.skill_type === 'api_call'
  const isCustomSkill = form.skill_type === 'custom'

  const submitError = useMemo(() => jsonError ?? error, [jsonError, error])

  const parseJsonField = (value: string, label: string): Record<string, unknown> | null => {
    const trimmed = value.trim()
    if (!trimmed) return {}
    try {
      const parsed = JSON.parse(trimmed)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return parsed as Record<string, unknown>
      }
      setJsonError(`${label} phải là JSON object`) 
      return null
    } catch {
      setJsonError(`${label} không phải JSON hợp lệ`)
      return null
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setJsonError(null)

    const config = parseJsonField(configText, 'Config')
    if (!config) return

    const inputSchema = parseJsonField(inputSchemaText, 'Input schema')
    if (!inputSchema) return

    const outputSchema = parseJsonField(outputSchemaText, 'Output schema')
    if (!outputSchema) return

    const apiHeaders = parseJsonField(apiHeadersText, 'API headers')
    if (!apiHeaders) return

    const payload: RAGSkillInput = {
      ...form,
      config,
      input_schema: inputSchema,
      output_schema: outputSchema,
      api_headers: apiHeaders,
      implementation_path: form.implementation_path?.trim() || '',
      api_endpoint: form.api_endpoint?.trim() || '',
      api_method: (form.api_method || 'POST').toUpperCase(),
    }

    if (!isApiSkill) {
      payload.api_endpoint = ''
      payload.api_method = 'POST'
      payload.api_headers = {}
    }

    if (!isCustomSkill) {
      payload.implementation_path = ''
    }

    const result = isEdit
      ? await update(skill!.id, payload)
      : await create(payload)
    if (result) onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Tên Skill"
          placeholder="Web Search"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
        />
        <Input
          label="Slug"
          placeholder="web-search"
          value={form.slug}
          onChange={(e) => setForm({ ...form, slug: e.target.value })}
          required
        />
      </div>

      <Textarea
        label="Mô tả"
        placeholder="Mô tả cho LLM biết khi nào skill này cần được dùng"
        value={form.description}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
        required
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select
          label="Loại Skill"
          value={form.skill_type}
          onChange={(e) => setForm({ ...form, skill_type: e.target.value as RAGSkillInput['skill_type'] })}
          options={SKILL_TYPE_OPTIONS}
        />
        <Select
          label="Trạng thái"
          value={form.is_active ? 'true' : 'false'}
          onChange={(e) => setForm({ ...form, is_active: e.target.value === 'true' })}
          options={[
            { value: 'true', label: 'Đang bật' },
            { value: 'false', label: 'Đang tắt' },
          ]}
        />
      </div>

      <Textarea
        label="Config (JSON)"
        value={configText}
        onChange={(e) => setConfigText(e.target.value)}
        className="font-mono text-xs"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Textarea
          label="Input Schema (JSON)"
          value={inputSchemaText}
          onChange={(e) => setInputSchemaText(e.target.value)}
          className="font-mono text-xs"
        />
        <Textarea
          label="Output Schema (JSON)"
          value={outputSchemaText}
          onChange={(e) => setOutputSchemaText(e.target.value)}
          className="font-mono text-xs"
        />
      </div>

      {isCustomSkill && (
        <Input
          label="Implementation Path"
          placeholder="apps.graph_rag.skills.web_search.WebSearchSkill"
          value={form.implementation_path ?? ''}
          onChange={(e) => setForm({ ...form, implementation_path: e.target.value })}
        />
      )}

      {isApiSkill && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="API Endpoint"
              placeholder="https://api.example.com/search"
              value={form.api_endpoint ?? ''}
              onChange={(e) => setForm({ ...form, api_endpoint: e.target.value })}
            />
            <Select
              label="API Method"
              value={form.api_method ?? 'POST'}
              onChange={(e) => setForm({ ...form, api_method: e.target.value })}
              options={[
                { value: 'GET', label: 'GET' },
                { value: 'POST', label: 'POST' },
                { value: 'PUT', label: 'PUT' },
                { value: 'PATCH', label: 'PATCH' },
                { value: 'DELETE', label: 'DELETE' },
              ]}
            />
          </div>
          <Textarea
            label="API Headers (JSON)"
            value={apiHeadersText}
            onChange={(e) => setApiHeadersText(e.target.value)}
            className="font-mono text-xs"
          />
        </>
      )}

      {submitError && <p className="text-sm text-danger">{submitError}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Cập nhật' : 'Tạo Skill'}
        </Button>
      </div>
    </form>
  )
}
