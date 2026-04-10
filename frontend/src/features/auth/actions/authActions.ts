'use server'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { z } from 'zod'
import type { ActionResult } from '@/types/api'
import type { AuthTokens } from '@/types/auth'

const API = process.env.INTERNAL_API_URL

const LoginSchema = z.object({
  email: z.string().email('Email không hợp lệ'),
  password: z.string().min(1, 'Vui lòng nhập mật khẩu'),
})

const RegisterSchema = z.object({
  email: z.string().email('Email không hợp lệ'),
  full_name: z.string().min(2, 'Họ tên tối thiểu 2 ký tự'),
  password: z.string().min(8, 'Mật khẩu tối thiểu 8 ký tự'),
  password_confirm: z.string().min(1, 'Vui lòng xác nhận mật khẩu'),
})

async function setAuthCookies(tokens: AuthTokens) {
  const jar = await cookies()
  jar.set('access_token', tokens.access, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60, // 1 hour
  })
}

export async function loginAction(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const raw = {
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  }

  const parsed = LoginSchema.safeParse(raw)
  if (!parsed.success) {
    return { success: false, fieldErrors: parsed.error.flatten().fieldErrors }
  }

  try {
    const res = await fetch(`${API}/api/v1/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parsed.data),
    })

    const json = await res.json()

    if (!res.ok) {
      return {
        success: false,
        error: json.message ?? 'Đăng nhập thất bại',
        fieldErrors: json.errors ?? undefined,
      }
    }

    const tokens: AuthTokens = json.data
    await setAuthCookies(tokens)
    // Refresh token stored client-side (done in LoginForm after success)
  } catch {
    return { success: false, error: 'Không thể kết nối đến máy chủ' }
  }

  redirect('/dashboard')
}

export async function registerAction(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const raw = {
    email: formData.get('email') as string,
    full_name: formData.get('full_name') as string,
    password: formData.get('password') as string,
    password_confirm: formData.get('password_confirm') as string,
  }

  const parsed = RegisterSchema.safeParse(raw)
  if (!parsed.success) {
    return { success: false, fieldErrors: parsed.error.flatten().fieldErrors }
  }

  if (parsed.data.password !== parsed.data.password_confirm) {
    return {
      success: false,
      fieldErrors: { password_confirm: ['Mật khẩu xác nhận không khớp'] },
    }
  }

  try {
    const res = await fetch(`${API}/api/v1/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parsed.data),
    })

    const json = await res.json()

    if (!res.ok) {
      return {
        success: false,
        error: json.message ?? 'Đăng ký thất bại',
        fieldErrors: json.errors ?? undefined,
      }
    }

    // Auto-login after register
    const loginRes = await fetch(`${API}/api/v1/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: parsed.data.email, password: parsed.data.password }),
    })

    if (loginRes.ok) {
      const loginJson = await loginRes.json()
      await setAuthCookies(loginJson.data)
    }
  } catch {
    return { success: false, error: 'Không thể kết nối đến máy chủ' }
  }

  redirect('/dashboard')
}

export async function logoutAction(): Promise<void> {
  const jar = await cookies()
  const access = jar.get('access_token')?.value

  if (access) {
    // Best-effort blacklist — ignore failure
    try {
      await fetch(`${API}/api/v1/auth/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${access}`,
        },
        body: JSON.stringify({ refresh: '' }),
      })
    } catch {
      // ignore
    }
  }

  jar.delete('access_token')
  redirect('/login')
}
