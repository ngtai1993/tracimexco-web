---
name: react-scalable
description: "Tạo React component, hook, feature, hoặc cấu trúc dự án theo chuẩn scalable và reusable. Use when: tạo react component, viết custom hook, cấu trúc folder react, react scalable, react reusable, tái sử dụng component, react typescript, compound component, react query, tanstack query, api layer react, react performance, react 19, react router, vite react, tailwind react, react feature folder, react architecture, design system, design token, đồng bộ thiết kế, nhất quán UI, cva, class-variance-authority, color token, typography scale, spacing, vỡ design, consistent design."
argument-hint: "Mô tả component/feature/hook bạn muốn tạo (vd: UserCard component, useAuth hook, trang Dashboard)"
---

# React Scalable & Reusable — Chuẩn Kiến Trúc React 19 + TypeScript

Skill này hướng dẫn tạo React code theo kiến trúc **feature-based**, dễ mở rộng và tái sử dụng tốt nhất.

**Stack mặc định:** React 19 · TypeScript · Vite · TanStack Query · React Router · Tailwind CSS

---

## Khi Nào Dùng

- Tạo component mới (UI, page, layout, form)
- Viết custom hook tái sử dụng logic
- Thiết lập cấu trúc folder cho feature/module mới
- Xây dựng API layer với TanStack Query
- Tối ưu performance (memo, lazy loading)
- Áp dụng compound component, HOC, render props

---

## Quy Trình Thực Hiện

### Bước 1 — Phân loại yêu cầu

Xác định loại task:

| Yêu cầu | Pattern |
|---------|---------|
| Component UI đơn giản | [→ Atomic Component](#atomic-component) |
| Component phức tạp có sub-parts | [→ Compound Component](#compound-component) |
| Tái sử dụng logic stateful | [→ Custom Hook](#custom-hook) |
| Tái sử dụng behavior (auth, permissions) | [→ HOC](#hoc) |
| Gọi API + cache + loading/error state | [→ API Layer](#api-layer) |
| Tạo feature/module mới | [→ Folder Structure](#folder-structure) |
| Tối ưu re-render | [→ Performance](#performance) |
| Form với validation | [→ Form Handling](#form-handling) |
| Đồng bộ màu / spacing / font / variant | [→ Design System](#design-system) |

---

### Bước 2 — Áp dụng pattern phù hợp

#### Folder Structure

Xem chi tiết: [references/folder-structure.md](./references/folder-structure.md)

**Nguyên tắc cốt lõi:** Feature-based, không layer-based.

```
src/
├── features/           # Mỗi feature tự đóng gói
│   └── <feature>/
│       ├── components/ # UI chỉ dùng trong feature này
│       ├── hooks/      # Logic riêng của feature
│       ├── api/        # API calls của feature
│       ├── types.ts    # Types của feature
│       └── index.ts    # Public API (re-export có chọn lọc)
├── components/         # Shared UI components (Button, Modal, etc.)
│   └── ui/
├── hooks/              # Shared custom hooks
├── lib/                # Setup thư viện (queryClient, axios, router)
├── types/              # Global types
└── utils/              # Pure utility functions
```

#### Atomic Component

```tsx
// components/ui/Button/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
}

export const Button = React.memo(({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...props}
    >
      {isLoading ? <Spinner size={size} /> : children}
    </button>
  )
})

Button.displayName = 'Button'
```

**Quy tắc atomic component:**
- Luôn dùng `React.memo` cho shared components
- Extend HTML props gốc bằng `React.XxxHTMLAttributes`
- Dùng `cn()` (clsx + tailwind-merge) để merge classNames
- Export từ `index.ts` của folder
- **Variants dùng `cva()` — không viết className ad-hoc theo màu** (xem [Design System](#design-system))

#### Compound Component

Xem chi tiết: [references/component-patterns.md](./references/component-patterns.md)

```tsx
// Dùng khi component có nhiều sub-parts liên quan
// vd: <Select>, <Modal>, <Tabs>, <Accordion>

const SelectContext = React.createContext<SelectContextValue | null>(null)

function Select({ children, value, onChange }: SelectProps) {
  return (
    <SelectContext value={{ value, onChange }}>
      <div className="relative">{children}</div>
    </SelectContext>
  )
}

function SelectTrigger({ children }: { children: React.ReactNode }) {
  const ctx = use(SelectContext)  // React 19: use() hook
  // ...
}

Select.Trigger = SelectTrigger
Select.Options = SelectOptions
Select.Option = SelectOption

// Usage: <Select><Select.Trigger /><Select.Options /></Select>
```

#### Custom Hook

```tsx
// hooks/useDebounce.ts — Reusable, generic
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = React.useState(value)

  React.useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}
```

**Quy tắc custom hook:**
- Tên bắt đầu bằng `use`
- Return object `{}` (không array) khi có nhiều giá trị
- Generic type khi logic không phụ thuộc kiểu dữ liệu
- Tách logic phức tạp thành hook nhỏ hơn, compose lại

#### API Layer

Xem chi tiết: [references/hooks-and-api.md](./references/hooks-and-api.md)

```tsx
// features/users/api/userApi.ts — Pure API functions
import { apiClient } from '@/lib/apiClient'
import type { User, CreateUserDto } from '../types'

export const userApi = {
  getAll: () => apiClient.get<User[]>('/users'),
  getById: (id: string) => apiClient.get<User>(`/users/${id}`),
  create: (data: CreateUserDto) => apiClient.post<User>('/users', data),
  update: (id: string, data: Partial<CreateUserDto>) =>
    apiClient.patch<User>(`/users/${id}`, data),
  delete: (id: string) => apiClient.delete(`/users/${id}`),
}

// features/users/hooks/useUsers.ts — TanStack Query hooks
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  detail: (id: string) => [...userKeys.all, 'detail', id] as const,
}

export function useUsers() {
  return useQuery({
    queryKey: userKeys.lists(),
    queryFn: userApi.getAll,
  })
}

export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: userApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: userKeys.lists() }),
  })
}
```

#### HOC

```tsx
// HOC cho cross-cutting concerns (auth, permissions, logging)
function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  requiredRole?: string
) {
  const WithAuth = (props: P) => {
    const { user, isLoading } = useAuth()
    if (isLoading) return <PageSkeleton />
    if (!user) return <Navigate to="/login" replace />
    if (requiredRole && !user.roles.includes(requiredRole)) return <Forbidden />
    return <WrappedComponent {...props} />
  }

  WithAuth.displayName = `WithAuth(${WrappedComponent.displayName ?? WrappedComponent.name})`
  return WithAuth
}
```

#### Design System

Xem chi tiết: [references/design-system.md](./references/design-system.md)

> **Quy tắc số 1:** Không bao giờ hardcode màu, font-size, spacing trong JSX.
> Tất cả phải đến từ design tokens (CSS variables → Tailwind classes).

```tsx
// ✅ Đúng — dùng token + cva variant
const buttonVariants = cva('...base...', {
  variants: {
    variant: {
      primary: 'bg-primary text-primary-fg hover:bg-primary-hover',
      danger:  'bg-danger text-white',
    },
  },
})

// ❌ Sai — hardcode màu ad-hoc
<button className="bg-blue-600 text-white hover:bg-blue-700">  // lần sau lại dùng blue-500
<div className="text-[#6b6375] p-[13px]">                        // không theo scale
```

**Token đang dùng trong project (`src/index.css`):**
- Colors: `primary`, `fg`, `fg-muted`, `fg-subtle`, `border`, `bg-subtle`, `bg-muted`
- Semantic: `success`, `warning`, `danger`, `info` (mỗi cái có `-light` variant)
- Radius: `rounded-sm/md/lg/xl`
- Spacing: bội số 4px (`p-1`=4px … `p-16`=64px)

#### Performance

Xem chi tiết: [references/performance.md](./references/performance.md)

**Checklist nhanh:**
- [ ] Dùng `React.memo` cho shared components nhận props primitive
- [ ] `useMemo` chỉ khi computation thực sự nặng (>1ms)
- [ ] `useCallback` khi function là dependency của `useEffect` hoặc truyền vào memoized component
- [ ] Lazy load routes: `const Page = React.lazy(() => import('./Page'))`
- [ ] Virtual list khi render >50 items (dùng `@tanstack/react-virtual`)
- [ ] Tránh anonymous object/array trong JSX props

#### Form Handling

Xem chi tiết: [references/form-handling.md](./references/form-handling.md)

**Pattern cốt lõi:**
```ts
// 1. Định nghĩa schema Zod (single source of truth)
const schema = z.object({ name: z.string().min(2), email: z.string().email() })
type FormDto = z.infer<typeof schema>  // ← infer type từ schema

// 2. Dùng với RHF
const { register, handleSubmit, formState: { errors } } = useForm<FormDto>({
  resolver: zodResolver(schema),
})
```

---

### Bước 3 — Cấu trúc file chuẩn

Mỗi component/hook cần có:

```
ComponentName/
├── ComponentName.tsx      # Implementation
├── ComponentName.test.tsx # Tests (vitest + testing-library)
└── index.ts               # Re-export: export { ComponentName } from './ComponentName'
```

---

### Bước 4 — TypeScript patterns bắt buộc

```tsx
// ✅ Discriminated union cho state phức tạp
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error }

// ✅ Props mở rộng HTML element
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'outlined'
}

// ✅ Generic component
function List<T extends { id: string }>({
  items,
  renderItem,
}: {
  items: T[]
  renderItem: (item: T) => React.ReactNode
}) {
  return <ul>{items.map((item) => <li key={item.id}>{renderItem(item)}</li>)}</ul>
}
```

---

### Bước 5 — Kiểm tra trước khi hoàn thành

- [ ] Component/hook có single responsibility không?
- [ ] Props interface có được export không?
- [ ] `displayName` đã set cho memoized/HOC component?
- [ ] `index.ts` đã re-export?
- [ ] Query keys đã được tách thành `queryKeys` object?
- [ ] Không có `any` type?
- [ ] Component có thể test độc lập không cần mock quá nhiều?
- [ ] Form: schema Zod tách file riêng, DTO infer từ schema?
- [ ] Form: API errors được map về đúng field bằng `setError`?
- [ ] **Design: không có hardcode màu/spacing/font-size trong JSX?**
- [ ] **Design: variants dùng `cva()`, tên theo intent không phải màu?**
- [ ] **Design: màu semantic đúng ngữ nghĩa (`text-danger` cho lỗi)?**
