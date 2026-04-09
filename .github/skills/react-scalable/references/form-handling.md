# Form Handling — React Hook Form + Zod

## 1. Setup

```bash
npm install react-hook-form zod @hookform/resolvers
```

---

## 2. Schema-First Pattern (Zod + RHF)

```ts
// features/users/schemas/createUser.schema.ts
import { z } from 'zod'

export const createUserSchema = z.object({
  name: z.string().min(2, 'Tên tối thiểu 2 ký tự').max(100),
  email: z.string().email('Email không hợp lệ'),
  password: z
    .string()
    .min(8, 'Mật khẩu tối thiểu 8 ký tự')
    .regex(/[A-Z]/, 'Cần ít nhất 1 chữ hoa')
    .regex(/[0-9]/, 'Cần ít nhất 1 chữ số'),
  confirmPassword: z.string(),
  role: z.enum(['admin', 'user', 'moderator']),
}).refine(
  (data) => data.password === data.confirmPassword,
  { message: 'Mật khẩu không khớp', path: ['confirmPassword'] }
)

// Infer DTO type từ schema — single source of truth
export type CreateUserDto = z.infer<typeof createUserSchema>
```

---

## 3. Form Component Chuẩn

```tsx
// features/users/components/CreateUserForm/CreateUserForm.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { createUserSchema, type CreateUserDto } from '../../schemas/createUser.schema'
import { useCreateUser } from '../../hooks/useUsers'
import { Input, Button } from '@/components/ui'

interface CreateUserFormProps {
  onSuccess?: () => void
}

export function CreateUserForm({ onSuccess }: CreateUserFormProps) {
  const createUser = useCreateUser()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    setError,
  } = useForm<CreateUserDto>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { role: 'user' },
  })

  const onSubmit = async (data: CreateUserDto) => {
    try {
      await createUser.mutateAsync(data)
      reset()
      onSuccess?.()
    } catch (error: any) {
      // Map API errors về form fields
      const apiErrors = error?.response?.data?.errors
      if (apiErrors) {
        Object.entries(apiErrors).forEach(([field, message]) => {
          setError(field as keyof CreateUserDto, { message: message as string })
        })
      } else {
        setError('root', {
          message: error?.response?.data?.detail ?? 'Đã có lỗi xảy ra',
        })
      }
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
      <Input
        label="Họ tên"
        error={errors.name?.message}
        {...register('name')}
      />
      <Input
        label="Email"
        type="email"
        error={errors.email?.message}
        {...register('email')}
      />
      <Input
        label="Mật khẩu"
        type="password"
        error={errors.password?.message}
        {...register('password')}
      />

      {/* Lỗi chung của form (từ API) */}
      {errors.root && (
        <p className="text-sm text-danger">{errors.root.message}</p>
      )}

      <Button
        type="submit"
        isLoading={isSubmitting || createUser.isPending}
        className="mt-2"
      >
        Tạo tài khoản
      </Button>
    </form>
  )
}
```

---

## 4. Common Zod Patterns

```ts
const schema = z.object({
  // Optional với giá trị mặc định khi empty string
  bio: z.string().optional().or(z.literal('')),

  // Phone VN
  phone: z.string().regex(/^(0|\+84)[0-9]{9}$/, 'Số điện thoại không hợp lệ'),

  // File upload
  avatar: z
    .instanceof(File)
    .refine((f) => f.size < 2 * 1024 * 1024, 'File tối đa 2MB')
    .refine(
      (f) => ['image/jpeg', 'image/png', 'image/webp'].includes(f.type),
      'Chỉ chấp nhận JPG, PNG, WEBP'
    )
    .optional(),

  // Conditional validation
  companyName: z.string().optional(),
  isCompany: z.boolean(),
}).refine(
  (data) => !data.isCompany || (data.isCompany && data.companyName),
  { message: 'Tên công ty là bắt buộc', path: ['companyName'] }
)
```

---

## 5. useFormWithMutation — Tái sử dụng

```ts
// hooks/useFormWithMutation.ts
import { useForm, type UseFormProps, type FieldValues, type DefaultValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import type { UseMutationResult } from '@tanstack/react-query'
import type { ZodSchema } from 'zod'

interface Options<TSchema extends FieldValues, TResponse> {
  schema: ZodSchema<TSchema>
  mutation: UseMutationResult<TResponse, unknown, TSchema>
  defaultValues?: DefaultValues<TSchema>
  onSuccess?: (data: TResponse) => void
  resetOnSuccess?: boolean
}

export function useFormWithMutation<TSchema extends FieldValues, TResponse>({
  schema,
  mutation,
  defaultValues,
  onSuccess,
  resetOnSuccess = true,
}: Options<TSchema, TResponse>) {
  const form = useForm<TSchema>({
    resolver: zodResolver(schema),
    defaultValues,
  })

  const onSubmit = form.handleSubmit(async (data) => {
    try {
      const result = await mutation.mutateAsync(data)
      if (resetOnSuccess) form.reset()
      onSuccess?.(result)
    } catch (error: any) {
      const apiErrors = error?.response?.data?.errors
      if (apiErrors) {
        Object.entries(apiErrors).forEach(([field, message]) => {
          form.setError(field as any, { message: message as string })
        })
      } else {
        form.setError('root', {
          message: error?.response?.data?.detail ?? 'Đã có lỗi xảy ra',
        })
      }
    }
  })

  return { ...form, onSubmit, isPending: mutation.isPending }
}
```

---

## Checklist Form

- [ ] Schema Zod được tách ra file riêng `.schema.ts`
- [ ] DTO type infer từ schema (`z.infer<typeof schema>`)
- [ ] `noValidate` trên `<form>` để RHF kiểm soát validation
- [ ] API errors được map về đúng field bằng `setError`
- [ ] `errors.root` hiển thị lỗi chung của form
- [ ] Loading state dùng `isSubmitting || mutation.isPending`
- [ ] `reset()` sau khi submit thành công (nếu phù hợp)
