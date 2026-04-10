'use server'
import { cookies } from 'next/headers'
import { z } from 'zod'
import type { ActionResult } from '@/types/api'

const API = process.env.INTERNAL_API_URL

const ChangePasswordSchema = z.object({
  old_password: z.string().min(1, 'Vui lòng nhập mật khẩu hiện tại'),
  new_password: z.string().min(8, 'Mật khẩu mới tối thiểu 8 ký tự'),
  new_password_confirm: z.string().min(1, 'Vui lòng xác nhận mật khẩu mới'),
})

export async function changePasswordAction(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const raw = {
    old_password: formData.get('old_password') as string,
    new_password: formData.get('new_password') as string,
    new_password_confirm: formData.get('new_password_confirm') as string,
  }

  const parsed = ChangePasswordSchema.safeParse(raw)
  if (!parsed.success) {
    return { success: false, fieldErrors: parsed.error.flatten().fieldErrors }
  }

  if (parsed.data.new_password !== parsed.data.new_password_confirm) {
    return {
      success: false,
      fieldErrors: { new_password_confirm: ['Mật khẩu xác nhận không khớp'] },
    }
  }

  const jar = await cookies()
  const access = jar.get('access_token')?.value
  if (!access) {
    return { success: false, error: 'Phiên đăng nhập đã hết hạn' }
  }

  try {
    const res = await fetch(`${API}/api/v1/auth/password/change/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${access}`,
      },
      body: JSON.stringify(parsed.data),
    })

    const json = await res.json()

    if (!res.ok) {
      return {
        success: false,
        error: json.message ?? 'Đổi mật khẩu thất bại',
        fieldErrors: json.errors ?? undefined,
      }
    }

    return { success: true }
  } catch {
    return { success: false, error: 'Không thể kết nối đến máy chủ' }
  }
}
