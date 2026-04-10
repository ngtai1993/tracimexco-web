# Folder Structure — Next.js 15 App Router

## Cấu trúc đầy đủ

```
src/
├── app/                              # App Router — CHỈ routing, không business logic
│   ├── (auth)/                       # Route group: không tạo URL segment
│   │   ├── layout.tsx                # Layout riêng cho auth pages (no sidebar)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/                  # Route group cho dashboard
│   │   ├── layout.tsx                # Layout với sidebar, header
│   │   ├── page.tsx                  # → /
│   │   ├── users/
│   │   │   ├── page.tsx              # → /users
│   │   │   └── [id]/
│   │   │       └── page.tsx          # → /users/:id
│   │   └── settings/
│   │       └── page.tsx
│   ├── api/                          # Route Handlers
│   │   ├── auth/
│   │   │   └── [...nextauth]/route.ts
│   │   └── webhooks/
│   │       └── route.ts
│   ├── layout.tsx                    # Root layout (html, body, providers)
│   ├── not-found.tsx                 # Global 404
│   └── globals.css
│
├── features/                         # Feature modules — tự đóng gói
│   ├── users/
│   │   ├── components/
│   │   │   ├── UserList.tsx          # async Server Component
│   │   │   ├── UserCard.tsx          # Server Component
│   │   │   ├── UserForm.tsx          # 'use client'
│   │   │   └── UserListSkeleton.tsx  # Loading skeleton
│   │   ├── actions/
│   │   │   └── userActions.ts        # 'use server'
│   │   ├── queries/
│   │   │   └── userQueries.ts        # Server-only fetch / DB calls
│   │   ├── hooks/                    # Client hooks (nếu cần)
│   │   │   └── useUserSearch.ts      # 'use client' hooks
│   │   ├── types.ts
│   │   └── index.ts                  # Public exports
│   └── auth/
│       ├── components/
│       ├── actions/
│       └── types.ts
│
├── components/                       # Shared components dùng nhiều feature
│   ├── ui/                           # Primitives (Button, Input, Badge…)
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   └── index.ts
│   │   └── Modal/
│   └── layouts/                      # Structural: Sidebar, Header, Footer
│       ├── Sidebar.tsx
│       └── Header.tsx
│
├── lib/                              # Third-party setup, singletons
│   ├── db.ts                         # Prisma client (hoặc DB connection)
│   ├── auth.ts                       # Auth config (NextAuth, Lucia…)
│   └── validations.ts                # Shared Zod schemas
│
├── hooks/                            # Shared client-only hooks
│   └── useMediaQuery.ts
│
├── types/                            # Global TypeScript types
│   ├── index.ts
│   └── api.ts
│
└── utils/                            # Pure functions (không side effects)
    ├── cn.ts                         # clsx + tailwind-merge
    └── format.ts
```

## Nguyên Tắc

### 1. `app/` chỉ là routing layer
- Page components gọi feature components, không chứa business logic trực tiếp
- Nếu logic > 5 dòng trong page.tsx → trích ra `features/`

### 2. Ranh giới Server / Client rõ ràng
- `features/*/queries/` → server-only (DB, internal API)
- `features/*/actions/` → server-only (`'use server'`)
- `features/*/hooks/` → client-only hooks

### 3. Route Groups `(name)`
- Dùng để nhóm routes có chung layout mà không thêm URL segment
- Ví dụ: `(auth)/login` → URL là `/login`, không phải `/auth/login`

### 4. Colocation
- Test files đặt cạnh file được test: `UserList.test.tsx` cùng folder `UserList.tsx`
- Stories (Storybook): `UserList.stories.tsx` cùng folder

### 5. Barrel exports (`index.ts`)
```ts
// features/users/index.ts — chỉ export những gì public
export { UserList } from './components/UserList'
export { UserCard } from './components/UserCard'
export type { User } from './types'
// KHÔNG export internal implementation
```
