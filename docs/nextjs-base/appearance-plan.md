# Appearance Frontend — Kế Hoạch Sử Dụng Đầy Đủ

> Backend: `apps/appearance` · Frontend: Next.js 16 App Router · Tailwind v4

---

## 0. Tổng Quan Kiến Trúc Hiện Tại

```
Backend: GET /api/v1/appearance/config/ (public, cached)
    └─► { colors: { light: {brand, semantic, neutral}, dark: ... }, media: { logo: {url, alt}, ... } }

Frontend Server Layer:
    layout.tsx → fetchAppearanceConfig() → buildCssVars() → <style dangerouslySetInnerHTML>
    Header.tsx → nhận appearance prop → AppLogo (src string)

Frontend Client Layer:  ← THIẾU: không có cách access config từ client components
Admin UI:              ← THIẾU: không có trang CRUD tokens/assets
```

**Vấn đề cần giải quyết:**
1. ❌ Type `AppearanceConfig.media` sai — backend trả `{url, alt}` nhưng type khai báo `string | null`
2. ❌ `Header.tsx` dùng `appearance?.media?.logo` nhận object thay vì `?.logo?.url`
3. ❌ Không có Context/Provider → client components không thể đọc config
4. ❌ Chưa có trang Admin quản lý tokens & assets
5. ❌ Khi admin thay đổi token/asset → Django cache được xóa nhưng Next.js cache chưa được revalidate

---

## 1. Fix Ngay — Type & Header Bug

### 1.1 Fix `types/appearance.ts`

**Vấn đề:** Backend trả `media[key] = {"url": url, "alt": ""}`, nhưng type khai báo `Record<string, string | null>`.

```typescript
// types/appearance.ts

export interface MediaAssetRef {
  url: string | null
  alt: string
}

export interface AppearanceConfig {
  colors: {
    light: ColorGroups
    dark: ColorGroups
  }
  media: Record<string, MediaAssetRef | null>   // ← fix: object thay vì string
}
```

### 1.2 Fix `Header.tsx`

```typescript
// Trước (sai):
const logoSrc = appearance?.media?.logo ?? null

// Sau (đúng):
const logoLogo = appearance?.media?.['logo'] ?? null
const logoSrc = logoLogo?.url ?? null
const logoAlt = logoLogo?.alt ?? 'Logo'
// Truyền cả alt xuống AppLogo
```

### 1.3 Fix `AppLogo` — nhận `MediaAssetRef` thay vì string

```typescript
// AppLogo.tsx props:
interface AppLogoProps {
  asset?: MediaAssetRef | null   // thay src string
  height?: number
}
// Bên trong: src={asset?.url} alt={asset?.alt ?? 'Logo'}
```

---

## 2. Context Provider — Client Components Access Config

Client components như `ThemeToggle`, future `AppFavicon`, admin sidebar logo v.v. cần đọc config mà không cần prop drilling.

### 2.1 File cần tạo

```
src/
  features/
    appearance/
      context.tsx          ← AppearanceContext + AppearanceProvider
      hooks.ts             ← useAppearance(), useMediaAsset(), useAppearanceColor()
      index.ts             ← re-export
```

### 2.2 `AppearanceContext` + `AppearanceProvider`

```typescript
// features/appearance/context.tsx
'use client'
import { createContext, useContext } from 'react'
import type { AppearanceConfig } from '@/types/appearance'

const AppearanceContext = createContext<AppearanceConfig | null>(null)

export function AppearanceProvider({
  config,
  children,
}: {
  config: AppearanceConfig | null
  children: React.ReactNode
}) {
  return (
    <AppearanceContext.Provider value={config}>
      {children}
    </AppearanceContext.Provider>
  )
}

export function useAppearanceContext() {
  return useContext(AppearanceContext)
}
```

### 2.3 `hooks.ts`

```typescript
// features/appearance/hooks.ts
'use client'
import { useAppearanceContext } from './context'
import type { MediaAssetRef } from '@/types/appearance'

/** Toàn bộ config */
export function useAppearance() {
  return useAppearanceContext()
}

/** Lấy một media asset theo key (vd: 'logo', 'favicon', 'banner') */
export function useMediaAsset(key: string): MediaAssetRef | null {
  const config = useAppearanceContext()
  return config?.media?.[key] ?? null
}

/** Lấy giá trị CSS var theo tên token (không cần đọc config — dùng getComputedStyle) */
export function useColorToken(tokenKey: string): string {
  if (typeof window === 'undefined') return ''
  return getComputedStyle(document.documentElement)
    .getPropertyValue(`--color-${tokenKey}`)
    .trim()
}
```

### 2.4 Wire vào `layout.tsx`

```tsx
// app/layout.tsx — thêm AppearanceProvider wrap body
import { AppearanceProvider } from '@/features/appearance'

// Trong return:
<AppearanceProvider config={config}>
  <body>...</body>
</AppearanceProvider>
```

---

## 3. Admin UI — Trang Quản Lý Appearance

### 3.1 Routes cần tạo

| Route | Mô tả | Permission |
|---|---|---|
| `/dashboard/appearance` | Overview: preview màu + danh sách assets | Admin |
| `/dashboard/appearance/tokens` | Bảng CRUD color tokens | Admin |
| `/dashboard/appearance/tokens/new` | Form tạo token mới | Admin |
| `/dashboard/appearance/assets` | Grid CRUD media assets | Admin |

### 3.2 User Flows

**Quản lý Color Tokens:**
```
Vào /dashboard/appearance/tokens
  → Bảng danh sách: key | mode | group | giá trị màu (preview) | order | active
  → Filter: mode (light/dark), group (brand/semantic/neutral)
  → "Thêm token" → Form: name, key, mode, value (color picker + hex input), group, order
  → Submit → Hiện toast "Đã tạo" → Bảng refresh → Backend Django cache bị xóa tự động
  → "Sửa" icon → Form prefilled → PATCH → Cập nhật bảng
  → "Xóa" icon → Confirm dialog → DELETE → Xóa khỏi bảng
  → "Kích hoạt/Tắt" toggle → PATCH is_active → Cập nhật row

Sau khi thay đổi → Nút "Reload màu trang web" → gọi POST /api/revalidate → Next.js cache cleared
```

**Quản lý Media Assets:**
```
Vào /dashboard/appearance/assets
  → Grid dạng card: thumbnail | key | name | alt_text | active toggle
  → "Upload asset" → Form: name, key (slug), file (image), alt_text, description
  → Drag & drop file → Preview ảnh trước khi upload
  → Submit → Hiện toast "Đã upload" → Grid refresh
  → Click card → Form edit prefilled (thay file hoặc sửa metadata)
  → Badge key (vd: logo, favicon) — key cố định không nên đổi sau khi set
  → "Xóa" → Confirm → DELETE
```

**Overview page `/dashboard/appearance`:**
```
Vào trang
  → Panel "Màu sắc hiện tại": Live preview palette light + dark mode
  → Số lượng: X tokens light / Y tokens dark / Z assets
  → Quick links đến /tokens và /assets
  → Nút "Reload cache trang web" → trigger revalidate
```

### 3.3 Folder Structure

```
src/
  features/
    appearance/
      context.tsx
      hooks.ts
      index.ts
      admin/
        api.ts             ← API calls đến backend (CRUD tokens + assets)
        types.ts           ← Types cho admin (ColorTokenAdmin, MediaAssetAdmin)
        components/
          TokenTable.tsx   ← Bảng token với filter
          TokenForm.tsx    ← Form tạo/sửa token
          AssetGrid.tsx    ← Grid media assets
          AssetForm.tsx    ← Form upload/sửa asset
          ColorPreview.tsx ← Ô màu nhỏ hiển thị inline
          PalettePanel.tsx ← Panel preview toàn bộ palette
        hooks.ts           ← useTokens, useAssets, useMutateToken, useMutateAsset

  app/
    (main)/
      dashboard/
        appearance/
          page.tsx         ← Overview
          loading.tsx      ← Skeleton
          tokens/
            page.tsx       ← TokenTable
            new/
              page.tsx     ← TokenForm (create)
          assets/
            page.tsx       ← AssetGrid
```

---

## 4. API Layer (Admin)

**File:** `features/appearance/admin/api.ts`

```typescript
import { apiClient } from '@/lib/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import type { ColorTokenAdmin, MediaAssetAdmin } from './types'

// ─── Tokens ──────────────────────────────────────────────
export const tokenApi = {
  list: (params?: { include_inactive?: boolean }) =>
    apiClient.get<ApiResponse<ColorTokenAdmin[]>>('/api/v1/appearance/tokens/', { params }),

  get: (id: string) =>
    apiClient.get<ApiResponse<ColorTokenAdmin>>(`/api/v1/appearance/tokens/${id}/`),

  create: (data: CreateTokenInput) =>
    apiClient.post<ApiResponse<ColorTokenAdmin>>('/api/v1/appearance/tokens/', data),

  update: (id: string, data: Partial<CreateTokenInput>) =>
    apiClient.patch<ApiResponse<ColorTokenAdmin>>(`/api/v1/appearance/tokens/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/api/v1/appearance/tokens/${id}/`),
}

// ─── Assets ──────────────────────────────────────────────
export const assetApi = {
  list: (params?: { include_inactive?: boolean }) =>
    apiClient.get<ApiResponse<MediaAssetAdmin[]>>('/api/v1/appearance/assets/', { params }),

  get: (id: string) =>
    apiClient.get<ApiResponse<MediaAssetAdmin>>(`/api/v1/appearance/assets/${id}/`),

  create: (data: FormData) =>                        // file upload → FormData
    apiClient.post<ApiResponse<MediaAssetAdmin>>('/api/v1/appearance/assets/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  update: (id: string, data: FormData | Partial<CreateAssetInput>) =>
    apiClient.patch<ApiResponse<MediaAssetAdmin>>(`/api/v1/appearance/assets/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/api/v1/appearance/assets/${id}/`),
}

// ─── Revalidate Next.js cache ─────────────────────────────
export const revalidateAppearance = () =>
  fetch(`/api/revalidate?secret=${process.env.NEXT_PUBLIC_REVALIDATE_SECRET}`, {
    method: 'POST',
  })
```

### Types Admin

```typescript
// features/appearance/admin/types.ts

export interface ColorTokenAdmin {
  id: string
  name: string
  key: string
  mode: 'light' | 'dark'
  value: string               // hex: #rrggbb
  group: 'brand' | 'semantic' | 'neutral' | 'custom'
  description: string
  order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MediaAssetAdmin {
  id: string
  name: string
  key: string
  file_url: string | null
  alt_text: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateTokenInput {
  name: string
  key: string
  mode: 'light' | 'dark'
  value: string
  group: 'brand' | 'semantic' | 'neutral' | 'custom'
  description?: string
  order?: number
  is_active?: boolean
}

export interface CreateAssetInput {
  name: string
  key: string
  alt_text?: string
  description?: string
  is_active?: boolean
  // file: File — chỉ qua FormData
}
```

---

## 5. Admin Hooks (TanStack Query)

**File:** `features/appearance/admin/hooks.ts`

```typescript
// Tokens
export function useTokens(params?: { include_inactive?: boolean })
export function useCreateToken()     // mutation
export function useUpdateToken()     // mutation
export function useDeleteToken()     // mutation

// Assets
export function useAssets(params?: { include_inactive?: boolean })
export function useCreateAsset()     // mutation (FormData)
export function useUpdateAsset()     // mutation
export function useDeleteAsset()     // mutation

// Sau mỗi mutation thành công:
// 1. queryClient.invalidateQueries(['appearance-tokens']) hoặc ['appearance-assets']
// 2. Gọi revalidateAppearance() để xóa Next.js cache → layout reload màu
```

---

## 6. UX Considerations

### Tokens Table

| State | UI |
|---|---|
| Loading | Skeleton rows (10 rows placeholder) |
| Empty | Illustration + "Chưa có token nào. Thêm token đầu tiên." |
| Error | Alert đỏ "Không thể tải danh sách token" + Retry button |
| Xóa thành công | Toast "Đã xóa token" |
| Tạo thành công | Toast "Đã tạo token" + scroll to row mới |

### Assets Grid

| State | UI |
|---|---|
| Loading | Grid skeleton cards (6 placeholder) |
| Upload đang xử lý | Spinner overlay trên form button + disabled |
| File quá lớn | Field error ngay dưới input "Tối đa 5MB" |
| Key đã tồn tại | Field error từ server "key đã tồn tại" |
| Upload thành công | Toast "Đã upload" + card xuất hiện ở grid |

### Color Value Input — `TokenForm`

- Input type `color` (native color picker) + Input type `text` (hex) song song
- Khi thay đổi color picker → sync vào text field
- Khi nhập hex thủ công → validate realtime `/#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/`
- Preview ô màu 24×24px ngay bên cạnh

### Revalidate Flow

```
Admin lưu token/asset
  → API thành công
  → useCreateToken/useUpdateToken onSuccess:
      1. invalidateQueries → refetch bảng
      2. revalidateAppearance() → POST /api/revalidate → revalidateTag('appearance')
      3. Toast "Đã cập nhật. Màu sắc trang chủ sẽ reload."
  → Lần mở trang tiếp theo: layout.tsx fetchAppearanceConfig() → fresh data
```

---

## 7. Revalidation từ Backend (Nâng Cao)

Backend `signals.py` hiện tại chỉ xóa Django cache. Để tự động revalidate Next.js cache sau khi admin dùng Django Admin:

**File:** `apps/appearance/services/nextjs_revalidate_service.py`

```python
import requests
from django.conf import settings

class NextJSRevalidateService:
    @staticmethod
    def revalidate_appearance():
        url = getattr(settings, "NEXTJS_REVALIDATE_URL", None)
        secret = getattr(settings, "NEXTJS_REVALIDATE_SECRET", None)
        if not url or not secret:
            return
        try:
            requests.post(
                f"{url}/api/revalidate",
                params={"secret": secret},
                timeout=3,
            )
        except Exception:
            pass  # không block luồng chính
```

Gọi trong `signals.py` — sau `AppearanceCacheService.invalidate_config()` thêm:
```python
NextJSRevalidateService.revalidate_appearance()
```

Config `.env`:
```
NEXTJS_REVALIDATE_URL=http://frontend:3000
NEXTJS_REVALIDATE_SECRET=your-secret-here
NEXT_PUBLIC_REVALIDATE_SECRET=your-secret-here   # cho admin frontend gọi thủ công
```

---

## 8. Shared UI Components Cần Tạo

| Component | File | Dùng ở đâu |
|---|---|---|
| `ColorSwatch` | `components/ui/ColorSwatch.tsx` | TokenTable, TokenForm preview |
| `FileDropzone` | `components/ui/FileDropzone.tsx` | AssetForm — drag & drop upload |
| `ImagePreview` | `components/ui/ImagePreview.tsx` | AssetGrid card, AssetForm preview |
| `ConfirmDialog` | `components/ui/ConfirmDialog.tsx` | Xác nhận xóa token/asset |

---

## 9. Checklist Triển Khai

### Phase 1 — Fix & Foundation
- [ ] Fix `types/appearance.ts` — `media: Record<string, MediaAssetRef | null>`
- [ ] Fix `Header.tsx` — `appearance?.media?.['logo']?.url`
- [ ] Fix `AppLogo.tsx` — nhận `asset?: MediaAssetRef | null`
- [ ] Tạo `features/appearance/context.tsx`
- [ ] Tạo `features/appearance/hooks.ts`
- [ ] Wire `AppearanceProvider` vào `layout.tsx`

### Phase 2 — Admin API Layer
- [ ] Tạo `features/appearance/admin/types.ts`
- [ ] Tạo `features/appearance/admin/api.ts`
- [ ] Tạo `features/appearance/admin/hooks.ts`

### Phase 3 — Admin UI Components
- [ ] `ColorSwatch`, `FileDropzone`, `ConfirmDialog` shared UI
- [ ] `TokenTable`, `TokenForm`, `ColorPreview`, `PalettePanel`
- [ ] `AssetGrid`, `AssetForm`

### Phase 4 — Admin Pages
- [ ] `app/(main)/dashboard/appearance/page.tsx` — Overview
- [ ] `app/(main)/dashboard/appearance/tokens/page.tsx`
- [ ] `app/(main)/dashboard/appearance/tokens/new/page.tsx`
- [ ] `app/(main)/dashboard/appearance/assets/page.tsx`
- [ ] Thêm "Appearance" vào Sidebar nav

### Phase 5 — Revalidation
- [ ] Thêm `NEXT_PUBLIC_REVALIDATE_SECRET` vào env
- [ ] `revalidateAppearance()` trong admin hooks mutations
- [ ] (Nâng cao) `NextJSRevalidateService` ở backend để Django Admin tự revalidate

---

## 10. Tóm Tắt Dependency Graph

```
Backend appearance API
  ├── GET /config/                → layout.tsx fetchAppearanceConfig()
  │       └── buildCssVars()     → <style> CSS vars → Tailwind tokens hoạt động
  │       └── AppearanceProvider → client components có thể useMediaAsset()
  │
  ├── GET/POST /tokens/           → Admin: useTokens, useCreateToken...
  ├── PATCH/DELETE /tokens/:id/   →         TokenTable, TokenForm
  ├── GET/POST /assets/           → Admin: useAssets, useCreateAsset...
  └── PATCH/DELETE /assets/:id/   →         AssetGrid, AssetForm
          │
          └─ On mutation success → revalidateAppearance() → layout re-fetches fresh colors
```
