'use client'
import { useActionState } from 'react'
import { changePasswordAction } from '../actions/profileActions'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export function ChangePasswordForm() {
  const [state, action, isPending] = useActionState(changePasswordAction, null)

  return (
    <div className="bg-surface border border-border rounded-bento p-6">
      <h3 className="font-semibold text-fg mb-5">Đổi mật khẩu</h3>

      {state?.success && (
        <div className="mb-4 px-4 py-2.5 rounded-bento text-sm bg-success/10 border border-success/30 text-success">
          Đổi mật khẩu thành công!
        </div>
      )}

      <form action={action} className="flex flex-col gap-4">
        <Input
          label="Mật khẩu hiện tại"
          name="old_password"
          type="password"
          autoComplete="current-password"
          error={state?.fieldErrors?.old_password?.[0]}
        />
        <Input
          label="Mật khẩu mới"
          name="new_password"
          type="password"
          autoComplete="new-password"
          hint="Tối thiểu 8 ký tự"
          error={state?.fieldErrors?.new_password?.[0]}
        />
        <Input
          label="Xác nhận mật khẩu mới"
          name="new_password_confirm"
          type="password"
          autoComplete="new-password"
          error={state?.fieldErrors?.new_password_confirm?.[0]}
        />

        {state?.error && !state.fieldErrors && (
          <p className="text-sm text-danger">{state.error}</p>
        )}

        <div className="flex justify-end pt-2">
          <Button type="submit" variant="primary" loading={isPending}>
            {isPending ? 'Đang lưu...' : 'Lưu mật khẩu mới'}
          </Button>
        </div>
      </form>
    </div>
  )
}
