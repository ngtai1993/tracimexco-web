# Performance Optimization

## 1. Khi Nào Cần Optimize

> **Quy tắc vàng:** Đừng optimize sớm. Profile trước, optimize sau.

| Triệu chứng | Nguyên nhân thường gặp | Giải pháp |
|------------|----------------------|-----------|
| Re-render nhiều không cần thiết | Props object/array mới mỗi render | `useMemo`, `useCallback` |
| Danh sách lớn chậm | Render quá nhiều DOM nodes | Virtual list |
| Bundle lớn, load chậm | Import tất cả vào main chunk | Code splitting + lazy |
| Tính toán nặng trong render | Expensive computation | `useMemo` |
| Component con re-render khi parent state thay đổi | Props không stable | `React.memo` + stable props |

---

## 2. React.memo — Đúng Cách

```tsx
// ✅ Có ích: component nhận props thay đổi không đều
const UserCard = React.memo(({ user, onEdit }: UserCardProps) => {
  return (
    <div className="rounded-lg border border-border p-4">
      <h3>{user.name}</h3>
      <button onClick={() => onEdit(user.id)}>Sửa</button>
    </div>
  )
})

// ❌ Không có ích: component luôn nhận props mới
// memo chỉ so sánh shallow — object/array mới mỗi render vẫn trigger re-render
```

---

## 3. useMemo & useCallback — Khi Nào Thực Sự Cần

```tsx
function ProductList({ products, categoryId }: Props) {
  // ✅ useMemo: filter/sort list lớn — expensive computation
  const filteredProducts = useMemo(
    () => products.filter((p) => p.categoryId === categoryId).sort(byPrice),
    [products, categoryId]
  )

  // ✅ useCallback: function truyền vào memoized component
  const handleDelete = useCallback(
    (id: string) => {
      deleteProduct(id)
      queryClient.invalidateQueries({ queryKey: productKeys.lists() })
    },
    [deleteProduct, queryClient]
  )

  // ❌ Không cần: tính toán đơn giản
  // const total = products.length  // Đừng bọc useMemo ở đây

  return <MemoizedGrid items={filteredProducts} onDelete={handleDelete} />
}
```

---

## 4. Code Splitting & Lazy Loading

```tsx
// lib/router.tsx — Lazy load tất cả pages
import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'

const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const UsersPage = lazy(() => import('@/pages/UsersPage'))

function PageLoader() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        path: 'dashboard',
        element: <Suspense fallback={<PageLoader />}><DashboardPage /></Suspense>
      },
      {
        path: 'users',
        element: <Suspense fallback={<PageLoader />}><UsersPage /></Suspense>
      },
    ],
  },
])
```

---

## 5. Virtual List (>50 items)

```tsx
// Dùng @tanstack/react-virtual cho danh sách dài
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualUserList({ users }: { users: User[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: users.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 72,
    overscan: 5,
  })

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <UserCard user={users[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 6. Tránh Common Pitfalls

### Anti-pattern: Object/Array trong JSX props

```tsx
// ❌ Tạo object mới mỗi render → UserCard luôn re-render dù memo
<UserCard style={{ margin: 8 }} filters={['active', 'verified']} />

// ✅ Tách ra ngoài component hoặc dùng useMemo
const CARD_STYLE = { margin: 8 }
const DEFAULT_FILTERS = ['active', 'verified']
<UserCard style={CARD_STYLE} filters={DEFAULT_FILTERS} />
```

### Anti-pattern: Context gây re-render rộng

```tsx
// ❌ Một context chứa tất cả → mọi consumer re-render khi bất kỳ giá trị thay đổi
const AppContext = createContext({ user, theme, notifications })

// ✅ Tách thành nhiều context theo domain
const AuthContext = createContext<AuthContextValue | null>(null)
const ThemeContext = createContext<ThemeContextValue | null>(null)
```

### Anti-pattern: Inline function trong render

```tsx
// ❌ Tạo function mới mỗi render
{items.map((item) => (
  <Item key={item.id} onClick={() => handleClick(item.id)} />
))}

// ✅ Dùng data attribute nếu không cần performance cao
{items.map((item) => (
  <Item key={item.id} data-id={item.id} onClick={handleItemClick} />
))}
```
