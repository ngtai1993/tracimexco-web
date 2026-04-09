# Folder Structure — Feature-Based Architecture

## Cấu Trúc Toàn Bộ Dự Án (Vite + React 19)

```
src/
├── app/                    # App-level setup (providers, router root)
│   ├── App.tsx
│   ├── providers.tsx       # Wrap tất cả providers (Query, Router, Theme...)
│   └── router.tsx          # Route definitions (React Router v7)
│
├── features/               # ★ Core: mỗi domain là 1 folder tự đóng gói
│   ├── auth/
│   │   ├── components/     # LoginForm, RegisterForm, AuthGuard
│   │   ├── hooks/          # useAuth, useLogin, useRegister
│   │   ├── api/            # authApi.ts
│   │   ├── store/          # authStore.ts (nếu dùng Zustand)
│   │   ├── types.ts        # User, AuthState, LoginDto...
│   │   ├── constants.ts    # AUTH_ROUTES, TOKEN_KEY...
│   │   └── index.ts        # export { useAuth, AuthGuard, ... }
│   │
│   ├── users/
│   │   ├── components/
│   │   │   ├── UserCard/
│   │   │   │   ├── UserCard.tsx
│   │   │   │   ├── UserCard.test.tsx
│   │   │   │   └── index.ts
│   │   │   └── UserList/
│   │   ├── hooks/
│   │   │   ├── useUsers.ts
│   │   │   └── useUserDetail.ts
│   │   ├── api/
│   │   │   └── userApi.ts
│   │   ├── types.ts
│   │   └── index.ts
│   │
│   └── dashboard/
│       ├── components/
│       ├── hooks/
│       └── index.ts
│
├── pages/                  # Route-level components (thin, delegate to features)
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   └── UsersPage.tsx
│
├── components/             # Shared UI (không chứa business logic)
│   └── ui/
│       ├── Button/
│       ├── Modal/
│       ├── Form/
│       ├── Table/
│       ├── Skeleton/
│       └── index.ts        # Re-export tất cả UI components
│
├── hooks/                  # Shared hooks (không liên quan feature cụ thể)
│   ├── useDebounce.ts
│   ├── useLocalStorage.ts
│   ├── useMediaQuery.ts
│   └── useIntersectionObserver.ts
│
├── lib/                    # Cấu hình & khởi tạo thư viện bên ngoài
│   ├── queryClient.ts      # TanStack Query client
│   ├── apiClient.ts        # Axios instance + interceptors
│   └── router.ts           # createBrowserRouter config
│
├── types/                  # Global TypeScript types
│   ├── api.ts              # ApiResponse<T>, PaginatedResponse<T>
│   └── common.ts           # ID, Timestamp, etc.
│
└── utils/                  # Pure functions (không side effects)
    ├── format.ts           # formatDate, formatCurrency
    ├── cn.ts               # clsx + tailwind-merge helper
    └── validators.ts       # Zod schemas dùng chung
```

## Quy Tắc Import

```tsx
// ✅ Dùng path alias (cấu hình trong vite.config.ts)
import { Button } from '@/components/ui'
import { useAuth } from '@/features/auth'
import { userApi } from '@/features/users/api/userApi'  // import trực tiếp trong cùng feature

// ❌ Không dùng relative path dài
import { Button } from '../../../components/ui/Button'

// ❌ Không cross-import giữa features
// Trong features/dashboard KHÔNG import từ features/users trực tiếp
// Thay vào đó, expose qua index.ts và import từ đó
import { UserCard } from '@/features/users'  // ✅ dùng public API
```

## vite.config.ts — Path Alias

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

## tsconfig.json — Path Mapping

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

## Feature index.ts — Public API Pattern

```ts
// features/users/index.ts
// Chỉ export những gì cần thiết cho bên ngoài — không export internals

export { UserCard } from './components/UserCard'
export { UserList } from './components/UserList'
export { useUsers, useUserDetail } from './hooks/useUsers'
export type { User, CreateUserDto } from './types'
// KHÔNG export: userApi, internal helpers, etc.
```

## Page Component — Thin Layer

```tsx
// pages/UsersPage.tsx — Chỉ layout + compose features, không có business logic
import { UserList } from '@/features/users'
import { PageHeader } from '@/components/ui'

export default function UsersPage() {
  return (
    <div className="container mx-auto py-8">
      <PageHeader title="Quản lý người dùng" />
      <UserList />
    </div>
  )
}
```

## Naming Conventions

| Loại | Convention | Ví dụ |
|------|-----------|-------|
| Component file | PascalCase | `UserCard.tsx` |
| Hook file | camelCase | `useUsers.ts` |
| Utility file | camelCase | `formatDate.ts` |
| Type file | camelCase | `types.ts` |
| Constant | SCREAMING_SNAKE | `MAX_PAGE_SIZE = 20` |
| Interface/Type | PascalCase | `interface UserCardProps` |
| Generic type param | Single uppercase | `<T>`, `<TData>`, `<TError>` |
