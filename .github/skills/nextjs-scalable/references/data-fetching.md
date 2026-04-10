# Data Fetching — Next.js 15

## Nguyên Tắc Cốt Lõi

Next.js 15 mở rộng `fetch` API và thêm `cache()` của React để kiểm soát caching/revalidation. Quyết định caching xảy ra **tại nơi fetch dữ liệu**, không phải ở route level.

---

## 1. Fetch với Caching Options

```ts
// Sử dụng trong Server Components hoặc queries/

// a) Static — cache vĩnh viễn (mặc định khi deploy)
const data = await fetch('https://api.example.com/data')

// b) ISR — revalidate sau N giây
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 },
})

// c) Dynamic — luôn fetch mới, không cache
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store',
})

// d) On-demand revalidation theo tag
const data = await fetch('https://api.example.com/users', {
  next: { tags: ['users'] },
})
// Sau khi mutation: revalidateTag('users') sẽ xóa cache này
```

---

## 2. React `cache()` — Deduplicate trong cùng render

```ts
// features/users/queries/userQueries.ts
import { cache } from 'react'

// cache() đảm bảo: nhiều component gọi getUser(same id) trong 1 render
// → chỉ thực sự gọi 1 lần
export const getUser = cache(async (id: string): Promise<User | null> => {
  const res = await fetch(`${process.env.API_URL}/users/${id}`, {
    next: { tags: [`user-${id}`] },
  })
  if (!res.ok) return null
  return res.json()
})

export const getUsers = cache(async (): Promise<User[]> => {
  const res = await fetch(`${process.env.API_URL}/users`, {
    next: { revalidate: 30, tags: ['users'] },
  })
  if (!res.ok) throw new Error('Failed to fetch users')
  return res.json()
})
```

---

## 3. Parallel Fetching — Tránh waterfall

```tsx
// ❌ Waterfall: chờ từng request
export default async function Page() {
  const user = await getUser('1')    // chờ...
  const posts = await getPosts('1')  // sau đó mới fetch
}

// ✅ Parallel: fetch đồng thời
export default async function Page() {
  const [user, posts] = await Promise.all([
    getUser('1'),
    getPosts('1'),
  ])
}
```

---

## 4. Streaming với Suspense

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>
      {/* Các Suspense boundaries stream độc lập */}
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<UserListSkeleton />}>
        <UserList />
      </Suspense>
    </main>
  )
}

// Stats và UserList là async Server Components
async function Stats() {
  const stats = await getStats()  // fetch của riêng nó
  return <StatsDisplay data={stats} />
}
```

---

## 5. On-Demand Revalidation

```ts
// Revalidate theo path
import { revalidatePath } from 'next/cache'
revalidatePath('/dashboard/users')           // Trang cụ thể
revalidatePath('/dashboard/users', 'layout') // Layout và tất cả pages bên dưới

// Revalidate theo tag (khuyến nghị — linh hoạt hơn)
import { revalidateTag } from 'next/cache'
revalidateTag('users')       // Xóa mọi fetch có tag 'users'
revalidateTag(`user-${id}`)  // Xóa cache của 1 user cụ thể
```

---

## 6. Dynamic Rendering

Route tự động trở thành dynamic khi:
- Dùng `cookies()`, `headers()`, `searchParams`
- Fetch với `cache: 'no-store'`
- Gọi `noStore()` tường minh

```ts
import { unstable_noStore as noStore } from 'next/cache'

export async function getDashboardData() {
  noStore()  // Tường minh opt-out static rendering
  // ...
}
```

---

## 7. Error Handling trong Fetch

```ts
// Pattern chuẩn cho query functions
export async function getUsers(): Promise<User[]> {
  const res = await fetch(`${process.env.API_URL}/users`, {
    next: { tags: ['users'] },
  })

  if (!res.ok) {
    // next/navigation notFound() → kích hoạt not-found.tsx
    // throw new Error() → kích hoạt error.tsx

    if (res.status === 404) notFound()
    throw new Error(`API error: ${res.status}`)
  }

  return res.json()
}
```

---

## Bảng Quyết Định Caching

| Dữ liệu | Chiến lược | Code |
|---------|-----------|------|
| Marketing page, docs | Static | mặc định |
| Blog posts, products | ISR | `next: { revalidate: 3600 }` |
| Dashboard, user data | Dynamic | `cache: 'no-store'` |
| Sau user action | On-demand | `revalidateTag('tag')` |
| Realtime | Dynamic + SWR client | `cache: 'no-store'` + client polling |
