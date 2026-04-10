'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useCreateKey, useUpdateKey } from '../hooks'
import type { AgentAPIKey, AgentAPIKeyInput } from '../types'

interface KeyFormProps {
  providerSlug: string
  apiKey?: AgentAPIKey | null
  onSuccess: () => void
  onCancel: () => void
}

export function KeyForm({ providerSlug, apiKey, onSuccess, onCancel }: KeyFormProps) {
  const isEdit = !!apiKey

  const [name, setName] = useState(apiKey?.name ?? '')
  const [rawKey, setRawKey] = useState('')
  const [priority, setPriority] = useState(String(apiKey?.priority ?? 1))
  const [expiresAt, setExpiresAt] = useState(apiKey?.expires_at?.slice(0, 16) ?? '')

  const { create, loading: creating, error: createError } = useCreateKey()
  const { update, loading: updating, error: updateError } = useUpdateKey()

  const loading = creating || updating
  const error = createError || updateError

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (isEdit) {
      const result = await update(providerSlug, apiKey!.id, {
        name,
        priority: Number(priority),
        expires_at: expiresAt || null,
      })
      if (result) onSuccess()
    } else {
      const data: AgentAPIKeyInput = {
        name,
        raw_key: rawKey,
        priority: Number(priority),
        expires_at: expiresAt || null,
      }
      const result = await create(providerSlug, data)
      if (result) onSuccess()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Tên Key"
        placeholder="Main API Key"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      {!isEdit && (
        <Input
          label="API Key"
          placeholder="sk-proj-..."
          value={rawKey}
          onChange={(e) => setRawKey(e.target.value)}
          required
          type="password"
          hint="Key sẽ được mã hóa và không thể xem lại sau khi lưu"
        />
      )}
      <Input
        label="Priority"
        type="number"
        min={1}
        value={priority}
        onChange={(e) => setPriority(e.target.value)}
        hint="1 = ưu tiên cao nhất. Key có priority thấp sẽ được dùng trước"
      />
      <Input
        label="Hết hạn"
        type="datetime-local"
        value={expiresAt}
        onChange={(e) => setExpiresAt(e.target.value)}
        hint="Để trống nếu key không có hạn"
      />

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Cập nhật' : 'Thêm Key'}
        </Button>
      </div>
    </form>
  )
}
