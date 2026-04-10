'use client'
import { useActionState } from 'react'
import { loginAction } from '../actions/authActions'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useEffect } from 'react'
import { authClient } from '../lib/authClient'

export function LoginForm() {
  const [state, action, isPending] = useActionState(loginAction, null)

  // Store refresh token client-side after successful login
  useEffect(() => {
    if (state?.success === false) return
    // On redirect, this effect won't run. This is for future non-redirect flows.
  }, [state])

  return (
    <form action={action} className="flex flex-col gap-4">
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
        autoComplete="current-password"
        placeholder="••••••••"
        error={state?.fieldErrors?.password?.[0]}
        required
      />

      {state?.error && !state.fieldErrors && (
        <p className="text-sm text-danger text-center bg-danger/10 border border-danger/30 rounded-bento px-4 py-2">
          {state.error}
        </p>
      )}

      <Button type="submit" variant="gradient" size="lg" loading={isPending} className="w-full mt-2">
        {isPending ? 'Đang đăng nhập...' : 'Đăng nhập'}
      </Button>
    </form>
  )
}
