---
name: nextjs-scalable
description: "Tạo Next.js component, page, layout, Server Action, Route Handler, hoặc cấu trúc dự án theo chuẩn scalable. Use when: tạo nextjs component, tạo page, tạo layout, server component, client component, server action, route handler, api route, nextjs app router, nextjs folder structure, nextjs typescript, nextjs tailwind, data fetching nextjs, caching nextjs, metadata seo, image optimization, font optimization, loading skeleton, error boundary, not found page, middleware nextjs, nextjs performance, nextjs scalable, nextjs architecture, nextjs feature folder, nextjs reusable, appearance api, màu backend, design token, color token, dark mode, light mode, css variable từ backend, theme colors, màu sắc từ backend, không hardcode màu, backend colors."
argument-hint: "Mô tả component/page/feature bạn muốn tạo (vd: trang Dashboard, UserCard component, form đăng nhập với Server Action)"
---

# Next.js Scalable — Chuẩn Kiến Trúc Next.js 15 + TypeScript

Skill này hướng dẫn xây dựng Next.js 15 theo kiến trúc **feature-based + App Router**, tận dụng tối đa Server Components, Server Actions, và các tính năng rendering hiện đại.

**Stack mặc định:** Next.js 15 · TypeScript · Tailwind CSS · App Router

---

## Khi Nào Dùng

- Tạo page / layout mới trong App Router
- Phân biệt Server Component vs Client Component
- Xây dựng form bằng Server Actions
- Viết Route Handler (API endpoint)
- Thiết lập cấu trúc folder cho feature mới
- Tối ưu caching, image, font, metadata

---

## Quy Trình Thực Hiện

### Bước 1 — Phân loại yêu cầu

Xác định loại task:

| Yêu cầu | Pattern |
|---------|---------|
| Cấu trúc folder project | [→ Folder Structure](#folder-structure) |
| Page / nested layout mới | [→ App Router Conventions](#app-router-conventions) |
| Component thuần UI không tương tác | [→ Server Component](#server-component) |
| Component có state / event / browser API | [→ Client Component](#client-component) |
| Form submit, mutation dữ liệu | [→ Server Action](#server-action) |
| Endpoint trả JSON / webhook | [→ Route Handler](#route-handler) |
| Fetch dữ liệu + cache + revalidate | [→ Data Fetching](#data-fetching) |
| SEO, Open Graph | [→ Metadata API](#metadata-api) |
| Ảnh, font tối ưu | [→ Image & Font](#image--font) |
| Bảo vệ route, redirect | [→ Middleware](#middleware) |
| Loading / Error / Not Found UI | [→ Special Files](#special-files) |
| Màu sắc / theme / dark mode / CSS vars | [→ Appearance & Theme Colors](#appearance--theme-colors) |

---

### Bước 2 — Áp dụng pattern phù hợp

#### Folder Structure

Xem chi tiết: [references/folder-structure.md](./references/folder-structure.md)

**Nguyên tắc cốt lõi:** Feature-based, `app/` chỉ chứa routing.

```
src/
├── app/                        # App Router — chỉ routing
│   ├── (auth)/                 # Route group (không ảnh hưởng URL)
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── dashboard/page.tsx
│   ├── api/                    # Route Handlers
│   │   └── webhooks/route.ts
│   ├── layout.tsx              # Root layout
│   └── globals.css
├── features/                   # Mỗi feature tự đóng gói
│   └── <feature>/
│       ├── components/         # UI chỉ dùng trong feature
│       ├── actions/            # Server Actions của feature
│       ├── queries/            # Data fetching functions (server-side)
│       ├── hooks/              # Client-side hooks
│       ├── types.ts
│       └── index.ts            # Public API
├── components/                 # Shared UI components
│   └── ui/                     # Primitives (Button, Input, Modal…)
├── lib/                        # Setup thư viện (db, auth, validations)
├── hooks/                      # Shared client hooks
├── types/                      # Global types
└── utils/                      # Pure utility functions
```

**Quy tắc routing:**
- Dùng **Route Groups** `(name)` để nhóm layouts mà không thêm segment URL
- Private folders `_folder` để ẩn hoàn toàn khỏi router
- Parallel routes `@slot` cho UI phức tạp (modal, tabs cùng URL)

---

#### App Router Conventions

```
app/
└── dashboard/
    ├── layout.tsx        # Shared layout cho /dashboard/*
    ├── page.tsx          # Route /dashboard
    ├── loading.tsx       # Skeleton khi page đang stream
    ├── error.tsx         # Error boundary (phải là Client Component)
    ├── not-found.tsx     # 404 scope
    └── [id]/
        └── page.tsx      # Dynamic route /dashboard/:id
```

**Template page.tsx (Server Component):**
```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react'
import { UserList } from '@/features/users/components/UserList'
import { UserListSkeleton } from '@/features/users/components/UserListSkeleton'

// Metadata tĩnh hoặc dynamic (xem Metadata API)
export const metadata = { title: 'Dashboard' }

export default async function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>
      <Suspense fallback={<UserListSkeleton />}>
        <UserList />   {/* Async Server Component bên trong Suspense */}
      </Suspense>
    </main>
  )
}
```

---

#### Server Component

> **Mặc định:** Mọi component trong `app/` là Server Component. Chỉ thêm `'use client'` khi thực sự cần.

```tsx
// features/users/components/UserList.tsx — Server Component (không có 'use client')
import { getUsers } from '../queries/userQueries'

export async function UserList() {
  const users = await getUsers()   // Gọi DB / API trực tiếp

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

**Khi nào là Server Component:**
- Fetch dữ liệu từ DB hoặc API nội bộ
- Đọc environment variables nhạy cảm
- Render nội dung không cần tương tác
- Giảm bundle JS gửi về client

---

#### Client Component

```tsx
'use client'  // ← Phải khai báo ở đầu file

// features/users/components/UserSearch.tsx
import { useState } from 'react'

interface UserSearchProps {
  onSearch: (query: string) => void
}

export function UserSearch({ onSearch }: UserSearchProps) {
  const [query, setQuery] = useState('')

  return (
    <input
      value={query}
      onChange={(e) => {
        setQuery(e.target.value)
        onSearch(e.target.value)
      }}
      placeholder="Tìm kiếm..."
    />
  )
}
```

**Khi nào cần `'use client'`:**
- `useState`, `useEffect`, `useReducer`, `useRef`
- Event handlers (`onClick`, `onChange`, `onSubmit`…)
- Browser APIs (`localStorage`, `window`, `navigator`)
- Thư viện chỉ chạy trên client

**Quy tắc vàng:** Đẩy `'use client'` xuống cây component càng thấp càng tốt — chỉ wrap phần tương tác, giữ phần còn lại là Server Component.

---

#### Server Action

Xem chi tiết: [references/server-actions.md](./references/server-actions.md)

```tsx
// features/users/actions/userActions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod'

const CreateUserSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
})

export async function createUser(formData: FormData) {
  const parsed = CreateUserSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  })

  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors }
  }

  // await db.user.create({ data: parsed.data })

  revalidatePath('/dashboard/users')
  redirect('/dashboard/users')
}
```

**Dùng với form (progressive enhancement):**
```tsx
'use client'
import { useActionState } from 'react'
import { createUser } from '../actions/userActions'

export function CreateUserForm() {
  const [state, action, isPending] = useActionState(createUser, null)

  return (
    <form action={action}>
      <input name="name" />
      {state?.error?.name && <p className="text-destructive">{state.error.name[0]}</p>}
      <input name="email" />
      {state?.error?.email && <p className="text-destructive">{state.error.email[0]}</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Đang lưu...' : 'Tạo mới'}
      </button>
    </form>
  )
}
```

---

#### Route Handler

```tsx
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const page = Number(searchParams.get('page') ?? '1')

  // const users = await getUsers({ page })

  return NextResponse.json({ data: [], page })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  // validate + save
  return NextResponse.json({ id: 'new-id' }, { status: 201 })
}

// Dynamic segment: app/api/users/[id]/route.ts
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }   // Next.js 15: params là Promise
) {
  const { id } = await params
  return NextResponse.json({ id })
}
```

---

#### Data Fetching

Xem chi tiết: [references/data-fetching.md](./references/data-fetching.md)

```tsx
// features/users/queries/userQueries.ts — Server-only (gọi DB trực tiếp hoặc internal API)
import { cache } from 'react'

// cache() dedup request trong cùng 1 render
export const getUser = cache(async (id: string) => {
  // return await db.user.findUnique({ where: { id } })
})

export async function getUsers() {
  // Next.js 15 fetch với caching
  const res = await fetch(`${process.env.INTERNAL_API_URL}/users`, {
    next: { revalidate: 60 },     // ISR: revalidate sau 60 giây
    // next: { tags: ['users'] }, // On-demand revalidation theo tag
    // cache: 'no-store',         // Dynamic: luôn fetch mới
  })
  if (!res.ok) throw new Error('Failed to fetch users')
  return res.json()
}
```

**Chiến lược caching:**

| Nhu cầu | Option | Kết quả |
|---------|--------|---------|
| Static (không đổi) | mặc định | Cache vĩnh viễn, build-time |
| ISR (cập nhật định kỳ) | `next: { revalidate: N }` | Cache N giây, nền |
| Dynamic (luôn mới) | `cache: 'no-store'` | Không cache |
| On-demand revalidate | `next: { tags: ['tag'] }` + `revalidateTag('tag')` | Xóa cache theo tag |

**Revalidate theo tag (Server Action):**
```tsx
'use server'
import { revalidateTag } from 'next/cache'

export async function updateUser(id: string, data: unknown) {
  // await db.user.update(...)
  revalidateTag('users')  // Xóa mọi cache có tag 'users'
}
```

---

#### Metadata API

```tsx
// Metadata tĩnh
export const metadata = {
  title: 'Dashboard | MyApp',
  description: 'Quản lý dữ liệu của bạn',
  openGraph: { title: 'Dashboard', images: ['/og.png'] },
}

// Metadata động (async)
export async function generateMetadata(
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  // const user = await getUser(id)
  return {
    title: `User ${id} | MyApp`,
  }
}
```

---

#### Image & Font

```tsx
// Ảnh — luôn dùng next/image
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={630}
  priority           // LCP image: tải trước
  className="object-cover"
/>

// Font — luôn dùng next/font
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',  // CSS variable → dùng trong Tailwind
  display: 'swap',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={inter.variable}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

---

#### Middleware

```tsx
// middleware.ts (root của project)
import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value

  const isAuthRoute = request.nextUrl.pathname.startsWith('/dashboard')
  if (isAuthRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*'], // Chỉ chạy middleware trên các path này
}
```

---

#### Special Files

```tsx
// app/dashboard/loading.tsx — Tự động wrap bằng Suspense
export default function DashboardLoading() {
  return <div className="animate-pulse bg-muted h-48 rounded-lg" />
}

// app/dashboard/error.tsx — Phải là Client Component
'use client'
export default function DashboardError({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <p>Đã có lỗi xảy ra: {error.message}</p>
      <button onClick={reset}>Thử lại</button>
    </div>
  )
}

// app/dashboard/not-found.tsx
import Link from 'next/link'
export default function NotFound() {
  return (
    <div>
      <h2>Không tìm thấy trang</h2>
      <Link href="/dashboard">Quay lại Dashboard</Link>
    </div>
  )
}
```

---

#### Appearance & Theme Colors

> **Quy tắc bắt buộc:** Không bao giờ hardcode màu hex trong JSX, CSS, hoặc Tailwind config. Toàn bộ màu sắc phải đến từ backend qua `GET /api/v1/appearance/config/`.

Xem chi tiết: [references/appearance-theme.md](./references/appearance-theme.md)

**Kiến trúc:**
1. `app/layout.tsx` (Server Component) → fetch appearance config → inject `<style>` với CSS vars
2. `tailwind.config.ts` → map CSS vars vào Tailwind tokens
3. Component dùng class Tailwind (`bg-primary`, `text-fg`) — không dùng hex
4. Dark mode toggle → `document.documentElement.setAttribute('data-theme', 'dark')`

**Type & fetch helper:**
```ts
// lib/appearance.ts
export interface AppearanceConfig {
  colors: {
    light: Record<string, Record<string, string>>  // group → key → hex
    dark: Record<string, Record<string, string>>
  }
  media: Record<string, string | null>             // slug → url
}

export async function fetchAppearanceConfig(): Promise<AppearanceConfig | null> {
  try {
    const res = await fetch(
      `${process.env.INTERNAL_API_URL}/api/v1/appearance/config/`,
      { next: { tags: ['appearance'] } }  // On-demand revalidation
    )
    if (!res.ok) return null
    const json = await res.json()
    return json.data as AppearanceConfig
  } catch {
    return null
  }
}

// Chuyển grouped colors thành CSS var string
export function buildCssVars(
  tokens: Record<string, Record<string, string>>,
  selector: string
): string {
  const vars = Object.values(tokens)
    .flatMap(group => Object.entries(group))
    .map(([key, value]) => `  --color-${key}: ${value};`)
    .join('\n')
  return `${selector} {\n${vars}\n}`
}
```

**Root layout — inject CSS vars:**
```tsx
// app/layout.tsx
import { fetchAppearanceConfig, buildCssVars } from '@/lib/appearance'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const config = await fetchAppearanceConfig()

  const lightCss = config ? buildCssVars(config.colors.light, ':root') : ''
  const darkCss  = config ? buildCssVars(config.colors.dark, '[data-theme="dark"]') : ''

  return (
    <html lang="vi">
      <head>
        {(lightCss || darkCss) && (
          <style dangerouslySetInnerHTML={{ __html: `${lightCss}\n${darkCss}` }} />
        )}
      </head>
      <body>{children}</body>
    </html>
  )
}
```

**Tailwind config — dùng CSS vars:**
```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['attribute', 'data-theme'],  // toggle bằng data-theme="dark"
  theme: {
    extend: {
      colors: {
        primary:    'var(--color-primary)',
        secondary:  'var(--color-secondary)',
        accent:     'var(--color-accent)',
        danger:     'var(--color-danger)',
        warning:    'var(--color-warning)',
        success:    'var(--color-success)',
        bg:         'var(--color-bg)',
        surface:    'var(--color-surface)',
        border:     'var(--color-border)',
        fg:         'var(--color-fg)',
        'fg-muted': 'var(--color-fg-muted)',
        // thêm token khác theo seed data của backend
      },
    },
  },
}

export default config
```

**Dark mode toggle hook:**
```ts
// hooks/useTheme.ts
'use client'
import { useEffect, useState } from 'react'

export function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | null
    const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    applyTheme(saved ?? preferred)
  }, [])

  function applyTheme(next: 'light' | 'dark') {
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem('theme', next)
    setTheme(next)
  }

  return { theme, toggleTheme: () => applyTheme(theme === 'light' ? 'dark' : 'light') }
}
```

**Quan trọng:**
- `INTERNAL_API_URL` — biến môi trường server-side (không `NEXT_PUBLIC_`)
- `NEXT_PUBLIC_API_URL` — dùng ở Client Component nếu cần fetch appearance phía client
- Fallback: nếu API lỗi, app vẫn render — CSS vars sẽ không có giá trị (trình duyệt dùng màu mặc định)
- Revalidate cache khi admin cập nhật token: `revalidateTag('appearance')` trong Server Action

---

### Bước 3 — Cấu trúc file chuẩn

Mỗi feature cần có:

```
features/<feature>/
├── components/
│   ├── FeatureList.tsx        # Server Component (async, fetch data)
│   ├── FeatureCard.tsx        # Server Component (UI thuần)
│   └── FeatureForm.tsx        # Client Component ('use client')
├── actions/
│   └── featureActions.ts      # 'use server' — mutations
├── queries/
│   └── featureQueries.ts      # Server-side data fetching
├── hooks/                     # Client-side hooks (nếu cần)
├── types.ts                   # Types & interfaces
└── index.ts                    # Re-export: export { FeatureList } from './components/FeatureList'
```

---

### Bước 4 — TypeScript patterns bắt buộc

```tsx
// ✅ Next.js 15: params / searchParams là Promise
interface PageProps {
  params: Promise<{ id: string }>
  searchParams: Promise<{ q?: string }>
}

export default async function Page({ params, searchParams }: PageProps) {
  const { id } = await params
  const { q } = await searchParams
}

// ✅ Server Action trả về state (dùng với useActionState)
type ActionState<T = void> =
  | { success: true; data: T }
  | { success: false; error: string | Record<string, string[]> }
  | null

// ✅ Kiểu cho children layout
interface LayoutProps {
  children: React.ReactNode
}

// ✅ Discriminated union cho async state (Client Component)
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string }
```

---

### Bước 5 — Kiểm tra trước khi hoàn thành

**Server / Client boundary:**
- [ ] Chỉ có `'use client'` ở component cần tương tác?
- [ ] Không truyền non-serializable objects (function, class) qua boundary?
- [ ] Async Server Component được bọc trong `<Suspense>`?

**Data fetching:**
- [ ] Dùng `cache()` của React để deduplicate request?
- [ ] Đã chọn đúng caching strategy (static/ISR/dynamic)?
- [ ] `revalidatePath` hoặc `revalidateTag` sau mutation?

**Server Actions:**
- [ ] File có `'use server'` ở đầu?
- [ ] Input được validate bằng Zod trước khi xử lý?
- [ ] Trả về error state thay vì throw (để Client Component handle)?

**Routing:**
- [ ] `params` và `searchParams` được `await` (Next.js 15)?
- [ ] Dùng `notFound()` thay vì return null khi không tìm thấy resource?
- [ ] `error.tsx` có `'use client'` không?

**Performance:**
- [ ] LCP image có `priority` prop?
- [ ] Font dùng `next/font`?
- [ ] Tất cả ảnh dùng `next/image` với đúng `width/height`?
- [ ] Route segment dùng `loading.tsx` để stream UI?

**TypeScript:**
- [ ] Không có `any` type?
- [ ] Props interface được export?
- [ ] `index.ts` re-export đúng public API?

**Appearance & Theme Colors:**
- [ ] Không có màu hex hardcode trong JSX, CSS, hoặc Tailwind config?
- [ ] Màu lấy từ backend qua CSS variable (`--color-*`)?
- [ ] `tailwind.config.ts` dùng `var(--color-*)` thay vì màu cụ thể?
- [ ] Root layout (`app/layout.tsx`) đã inject CSS vars từ `/api/v1/appearance/config/`?
- [ ] Dark mode toggle dùng `data-theme` attribute trên `<html>`?
- [ ] `fetchAppearanceConfig()` có fallback khi API trả lỗi (không crash app)?
