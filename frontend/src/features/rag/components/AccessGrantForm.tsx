'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { useGrantAccess } from '../hooks'
import type { GrantAccessInput } from '../types'

interface AccessGrantFormProps {
  instanceSlug: string
  onSuccess: () => void
  onCancel: () => void
}

export function AccessGrantForm({ instanceSlug, onSuccess, onCancel }: AccessGrantFormProps) {
  const [form, setForm] = useState<GrantAccessInput>({
    user_id: '',
    access_level: 'use',
    daily_query_limit: 100,
    monthly_token_limit: 1000000,
    expires_at: null,
  })

  const { grant, loading, error } = useGrantAccess()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await grant(instanceSlug, form)
    if (result) onSuccess()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="User ID"
        placeholder="ID của người dùng"
        value={form.user_id}
        onChange={(e) => setForm({ ...form, user_id: e.target.value })}
        required
      />
      <Select
        label="Quyền truy cập"
        value={form.access_level ?? 'use'}
        onChange={(e) => setForm({ ...form, access_level: e.target.value })}
        options={[
          { value: 'use', label: 'Use (Chỉ sử dụng)' },
          { value: 'manage', label: 'Manage (Quản lý)' },
        ]}
      />
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Query/Ngày"
          type="number"
          value={String(form.daily_query_limit ?? 100)}
          onChange={(e) => setForm({ ...form, daily_query_limit: Number(e.target.value) })}
          min={1}
        />
        <Input
          label="Token/Tháng"
          type="number"
          value={String(form.monthly_token_limit ?? 1000000)}
          onChange={(e) => setForm({ ...form, monthly_token_limit: Number(e.target.value) })}
          min={1000}
        />
      </div>
      <Input
        label="Hết hạn (tùy chọn)"
        type="datetime-local"
        value={form.expires_at ?? ''}
        onChange={(e) => setForm({ ...form, expires_at: e.target.value || null })}
      />

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
          Hủy
        </Button>
        <Button type="submit" size="sm" loading={loading}>
          Cấp quyền
        </Button>
      </div>
    </form>
  )
}
