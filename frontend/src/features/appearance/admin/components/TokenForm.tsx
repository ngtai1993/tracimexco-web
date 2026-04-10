'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { ColorSwatch } from '@/components/ui/ColorSwatch'
import { useCreateToken, useUpdateToken } from '../hooks'
import type { ColorTokenAdmin, CreateTokenInput } from '../types'

interface TokenFormProps {
  token?: ColorTokenAdmin | null
  onSuccess: (token: ColorTokenAdmin) => void
  onCancel: () => void
}

function toFormValues(token: ColorTokenAdmin | null | undefined): CreateTokenInput {
  if (!token) {
    return { name: '', key: '', mode: 'light', value: '#000000', group: 'brand', description: '', order: 0, is_active: true }
  }
  return {
    name: token.name,
    key: token.key,
    mode: token.mode,
    value: token.value,
    group: token.group,
    description: token.description,
    order: token.order,
    is_active: token.is_active,
  }
}

export function TokenForm({ token, onSuccess, onCancel }: TokenFormProps) {
  const isEdit = !!token
  const [form, setForm] = useState<CreateTokenInput>(() => toFormValues(token))
  const [hexInput, setHexInput] = useState(() => token?.value ?? '#000000')
  const [hexError, setHexError] = useState('')

  const { create, loading: creating, error: createError, fieldErrors: createFieldErrors } = useCreateToken()
  const { update, loading: updating, error: updateError, fieldErrors: updateFieldErrors } = useUpdateToken()

  const loading = creating || updating
  const serverError = createError ?? updateError
  const fieldErrors = createFieldErrors ?? updateFieldErrors

  const set = (field: keyof CreateTokenInput, value: unknown) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const validateHex = (v: string) => /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(v)

  const handleHexChange = (v: string) => {
    setHexInput(v)
    if (validateHex(v)) {
      setHexError('')
      set('value', v)
    } else {
      setHexError('Hex không hợp lệ (vd: #0e4475)')
    }
  }

  const handleColorPicker = (v: string) => {
    setHexInput(v)
    setHexError('')
    set('value', v)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (hexError) return
    if (isEdit && token) {
      const result = await update(token.id, form)
      if (result) onSuccess(result)
    } else {
      const result = await create(form)
      if (result) onSuccess(result)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Tên *"
          value={form.name}
          onChange={(e) => set('name', e.target.value)}
          error={fieldErrors?.name?.[0]}
          required
        />
        <Input
          label="Key (slug) *"
          value={form.key}
          onChange={(e) => set('key', e.target.value)}
          error={fieldErrors?.key?.[0]}
          hint="vd: primary, fg-muted"
          required
        />
      </div>

      {/* Color picker + hex input */}
      <div className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-fg">Giá trị màu *</span>
        <div className="flex items-center gap-3">
          <input
            type="color"
            value={form.value}
            onChange={(e) => handleColorPicker(e.target.value)}
            className="w-10 h-10 rounded border border-border cursor-pointer bg-surface p-0.5"
            title="Chọn màu"
          />
          <ColorSwatch value={form.value} size="lg" />
          <div className="flex-1">
            <Input
              value={hexInput}
              onChange={(e) => handleHexChange(e.target.value)}
              error={hexError || fieldErrors?.value?.[0]}
              placeholder="#0e4475"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Mode */}
        <div className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-fg">Mode *</span>
          <div className="flex gap-2">
            {(['light', 'dark'] as const).map((m) => (
              <label key={m} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="mode"
                  value={m}
                  checked={form.mode === m}
                  onChange={() => set('mode', m)}
                  className="accent-primary"
                />
                <span className="text-sm text-fg-muted">{m}</span>
              </label>
            ))}
          </div>
          {fieldErrors?.mode && <p className="text-xs text-danger">{fieldErrors.mode[0]}</p>}
        </div>

        {/* Group */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-fg" htmlFor="group">Group *</label>
          <select
            id="group"
            value={form.group}
            onChange={(e) => set('group', e.target.value as CreateTokenInput['group'])}
            className="bg-surface border border-border rounded-bento px-3 py-2.5 text-sm text-fg focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            {['brand', 'semantic', 'neutral', 'custom'].map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
          {fieldErrors?.group && <p className="text-xs text-danger">{fieldErrors.group[0]}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Order"
          type="number"
          value={String(form.order ?? 0)}
          onChange={(e) => set('order', parseInt(e.target.value, 10) || 0)}
        />
        <div className="flex flex-col gap-1.5 pt-7">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => set('is_active', e.target.checked)}
              className="accent-primary"
            />
            <span className="text-sm text-fg-muted">Hoạt động</span>
          </label>
        </div>
      </div>

      <Input
        label="Mô tả"
        value={form.description ?? ''}
        onChange={(e) => set('description', e.target.value)}
      />

      {serverError && (
        <p className="text-sm text-danger">{serverError}</p>
      )}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>Hủy</Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Lưu thay đổi' : 'Tạo token'}
        </Button>
      </div>
    </form>
  )
}
