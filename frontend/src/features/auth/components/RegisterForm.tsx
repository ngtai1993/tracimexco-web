'use client'
import { useActionState } from 'react'
import { registerAction } from '../actions/authActions'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { authClient } from '../lib/authClient'

export function RegisterForm() {
  const [state, action, isPending] = useActionState(registerAction, null)
  const router = useRouter()

  useEffect(() => {
    if (!state?.success || !state.data) return
    authClient.setTokens(state.data.access, state.data.refresh)
    router.replace('/dashboard')
  }, [router, state])

  return (
    <form action={action} className="flex flex-col gap-4">
      <Input
        label="Họ và tên"
        name="full_name"
        type="text"
        autoComplete="name"
        placeholder="Nguyễn Văn A"
        error={state?.fieldErrors?.full_name?.[0]}
        required
      />
      <Input
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        placeholder="example@email.com"
        error={state?.fieldErrors?.email?.[0]}
        required
      />
      <Input
        label="Mật khẩu"
        name="password"
        type="password"
        autoComplete="new-password"
        placeholder="Tối thiểu 8 ký tự"
        error={state?.fieldErrors?.password?.[0]}
        required
      />
      <Input
        label="Xác nhận mật khẩu"
        name="password_confirm"
        type="password"
        autoComplete="new-password"
        placeholder="••••••••"
        error={state?.fieldErrors?.password_confirm?.[0]}
        required
      />

      {state?.error && !state.fieldErrors && (
        <p className="text-sm text-danger text-center bg-danger/10 border border-danger/30 rounded-bento px-4 py-2">
          {state.error}
        </p>
      )}

      <Button type="submit" variant="gradient" size="lg" loading={isPending} className="w-full mt-2">
        {isPending ? 'Đang tạo tài khoản...' : 'Tạo tài khoản'}
      </Button>
    </form>
  )
}
