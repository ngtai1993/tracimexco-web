# Server Actions — Next.js 15

## Khái Niệm

Server Actions là **async functions chạy trên server**, được gọi từ Client Components hoặc form HTML. Thay thế hoàn toàn API route riêng cho mutations.

---

## 1. Định nghĩa

```ts
// features/users/actions/userActions.ts
'use server'  // ← Tất cả exports trong file này đều là Server Actions

import { revalidatePath, revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod'

// Schema định nghĩa 1 lần, dùng lại cho type inference
const UpdateUserSchema = z.object({
  id: z.string().cuid(),
  name: z.string().min(2).max(100),
  email: z.string().email(),
})

type UpdateUserInput = z.infer<typeof UpdateUserSchema>

// Kiểu trả về chuẩn để dùng với useActionState
type ActionResult =
  | { success: true }
  | { success: false; error: string | Record<string, string[]> }

export async function updateUser(
  _prevState: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const parsed = UpdateUserSchema.safeParse({
    id: formData.get('id'),
    name: formData.get('name'),
    email: formData.get('email'),
  })

  if (!parsed.success) {
    return { success: false, error: parsed.error.flatten().fieldErrors }
  }

  try {
    // await db.user.update({ where: { id: parsed.data.id }, data: parsed.data })
    revalidateTag('users')
    revalidateTag(`user-${parsed.data.id}`)
    return { success: true }
  } catch {
    return { success: false, error: 'Đã có lỗi xảy ra, vui lòng thử lại.' }
  }
}

export async function deleteUser(id: string): Promise<ActionResult> {
  try {
    // await db.user.delete({ where: { id } })
    revalidateTag('users')
    redirect('/dashboard/users')  // redirect() throw nội bộ, KHÔNG cần try/catch xung quanh
  } catch (error) {
    // Phân biệt redirect error với lỗi thực sự
    if (error instanceof Error && error.message === 'NEXT_REDIRECT') throw error
    return { success: false, error: 'Xóa thất bại.' }
  }
}
```

---

## 2. Dùng với Form + `useActionState`

```tsx
// features/users/components/UpdateUserForm.tsx
'use client'

import { useActionState } from 'react'
import { updateUser } from '../actions/userActions'
import type { User } from '../types'

interface UpdateUserFormProps {
  user: User
}

export function UpdateUserForm({ user }: UpdateUserFormProps) {
  const [state, action, isPending] = useActionState(updateUser, null)

  return (
    <form action={action} className="space-y-4">
      <input type="hidden" name="id" value={user.id} />

      <div>
        <label htmlFor="name">Tên</label>
        <input
          id="name"
          name="name"
          defaultValue={user.name}
          aria-describedby={state?.success === false ? 'name-error' : undefined}
        />
        {state?.success === false && typeof state.error === 'object' && (
          <p id="name-error" className="text-destructive text-sm">
            {state.error.name?.[0]}
          </p>
        )}
      </div>

      {state?.success === false && typeof state.error === 'string' && (
        <p className="text-destructive">{state.error}</p>
      )}

      {state?.success === true && (
        <p className="text-success">Cập nhật thành công!</p>
      )}

      <button type="submit" disabled={isPending}>
        {isPending ? 'Đang lưu...' : 'Lưu thay đổi'}
      </button>
    </form>
  )
}
```

---

## 3. Gọi trực tiếp từ Event Handler

```tsx
'use client'

import { deleteUser } from '../actions/userActions'
import { useTransition } from 'react'

export function DeleteUserButton({ userId }: { userId: string }) {
  const [isPending, startTransition] = useTransition()

  return (
    <button
      onClick={() => startTransition(() => deleteUser(userId))}
      disabled={isPending}
      className="text-destructive"
    >
      {isPending ? 'Đang xóa...' : 'Xóa'}
    </button>
  )
}
```

---

## 4. Server Action trong Server Component

```tsx
// Inline action trong Server Component (form đơn giản)
// app/contact/page.tsx

async function sendMessage(formData: FormData) {
  'use server'  // ← Khai báo inline
  const message = formData.get('message') as string
  // await sendEmail(message)
  revalidatePath('/contact')
}

export default function ContactPage() {
  return (
    <form action={sendMessage}>
      <textarea name="message" />
      <button type="submit">Gửi</button>
    </form>
  )
}
```

---

## 5. Bảo mật

```ts
'use server'

import { getSession } from '@/lib/auth'
import { redirect } from 'next/navigation'

export async function adminOnlyAction(data: FormData) {
  // ✅ LUÔN xác thực quyền trong Server Action
  const session = await getSession()
  if (!session) redirect('/login')
  if (session.user.role !== 'admin') {
    return { success: false, error: 'Không có quyền thực hiện.' }
  }

  // ... proceed
}
```

**Quy tắc bắt buộc:**
- Không tin tưởng dữ liệu từ `formData` — luôn validate bằng Zod
- Luôn kiểm tra authentication/authorization ở đầu action
- Không expose sensitive data trong return value

---

## 6. Checklist Server Action

- [ ] File có `'use server'` ở dòng đầu?
- [ ] Input validate bằng Zod `safeParse` trước khi xử lý?
- [ ] Auth/permission check ở đầu function?
- [ ] Gọi `revalidatePath` hoặc `revalidateTag` sau mutation?
- [ ] Trả về error state thay vì throw (để UI hiển thị)?
- [ ] Nếu dùng `redirect()`: đặt ngoài `try/catch` hoặc re-throw redirect error?
- [ ] Kiểu trả về tương thích với `useActionState`?
