# Custom Hooks & API Layer

## 1. API Client Setup (Axios + Interceptors)

```ts
// lib/apiClient.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach access token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor — unwrap data, handle 401
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

## 2. TanStack Query Setup

```ts
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,   // 5 phút
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
})
```

---

## 3. Query Keys Factory Pattern

```ts
// features/users/api/queryKeys.ts
// Centralized query key factory — prevents key collisions
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: UserFilters) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
}

// Usage: queryClient.invalidateQueries({ queryKey: userKeys.lists() })
//        queryClient.setQueryData(userKeys.detail(id), updatedUser)
```

---

## 4. API Function Layer

```ts
// features/users/api/userApi.ts
import { apiClient } from '@/lib/apiClient'
import type { User, CreateUserDto, UpdateUserDto, UserFilters } from '../types'
import type { PaginatedResponse } from '@/types/api'

export const userApi = {
  // ── Queries ──────────────────────────────────────────────────────────────
  getAll: (filters?: UserFilters) =>
    apiClient.get<User[]>('/users', { params: filters }),

  getPaginated: (page: number, filters?: UserFilters) =>
    apiClient.get<PaginatedResponse<User>>('/users', {
      params: { page, ...filters },
    }),

  getById: (id: string) =>
    apiClient.get<User>(`/users/${id}`),

  // ── Mutations ────────────────────────────────────────────────────────────
  create: (data: CreateUserDto) =>
    apiClient.post<User>('/users', data),

  update: (id: string, data: UpdateUserDto) =>
    apiClient.patch<User>(`/users/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<void>(`/users/${id}`),
}
```

---

## 5. TanStack Query Hooks

```ts
// features/users/hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userApi } from '../api/userApi'
import { userKeys } from '../api/queryKeys'
import type { UserFilters, UpdateUserDto } from '../types'

// ── Query hooks ───────────────────────────────────────────────────────────
export function useUsers(filters?: UserFilters) {
  return useQuery({
    queryKey: userKeys.list(filters ?? {}),
    queryFn: () => userApi.getAll(filters),
  })
}

export function useUserDetail(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => userApi.getById(id),
    enabled: Boolean(id),  // Không fetch nếu id rỗng
  })
}

// ── Mutation hooks ────────────────────────────────────────────────────────
export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: userApi.create,
    onSuccess: (newUser) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      queryClient.setQueryData(userKeys.detail(newUser.id), newUser)
    },
  })
}

export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserDto }) =>
      userApi.update(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: userKeys.detail(id) })
      const previous = queryClient.getQueryData(userKeys.detail(id))
      queryClient.setQueryData(userKeys.detail(id), (old: any) => ({ ...old, ...data }))
      return { previous }
    },
    onError: (_err, { id }, ctx) => {
      queryClient.setQueryData(userKeys.detail(id), ctx?.previous)
    },
    onSettled: (_data, _err, { id }) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(id) })
    },
  })
}

export function useDeleteUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: userApi.delete,
    onSuccess: (_, deletedId) => {
      queryClient.removeQueries({ queryKey: userKeys.detail(deletedId) })
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
    },
  })
}
```

---

## 6. Custom Hooks Pattern Library

### useDebounce — Generic

```ts
export function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}
```

### useLocalStorage — Type-safe

```ts
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key)
      return item ? (JSON.parse(item) as T) : initialValue
    } catch {
      return initialValue
    }
  })

  const setStoredValue = useCallback((newValue: T | ((prev: T) => T)) => {
    setValue((prev) => {
      const resolved = typeof newValue === 'function'
        ? (newValue as (prev: T) => T)(prev)
        : newValue
      localStorage.setItem(key, JSON.stringify(resolved))
      return resolved
    })
  }, [key])

  return [value, setStoredValue] as const
}
```

### useDisclosure — Modal/Drawer control

```ts
export function useDisclosure(defaultOpen = false) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  return {
    isOpen,
    open: useCallback(() => setIsOpen(true), []),
    close: useCallback(() => setIsOpen(false), []),
    toggle: useCallback(() => setIsOpen((v) => !v), []),
    onOpenChange: setIsOpen,
  }
}
// Usage: const modal = useDisclosure()
//        <Modal open={modal.isOpen} onOpenChange={modal.onOpenChange} />
```

### usePagination

```ts
export function usePagination(totalItems: number, pageSize = 20) {
  const [page, setPage] = useState(1)
  const totalPages = Math.ceil(totalItems / pageSize)

  return {
    page,
    pageSize,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
    goTo: (p: number) => setPage(Math.min(Math.max(1, p), totalPages)),
    next: () => setPage((p) => Math.min(p + 1, totalPages)),
    prev: () => setPage((p) => Math.max(p - 1, 1)),
    reset: () => setPage(1),
  }
}
```

---

## 7. Global Types

```ts
// types/api.ts
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  hasNextPage: boolean
}

export type ID = string
```
