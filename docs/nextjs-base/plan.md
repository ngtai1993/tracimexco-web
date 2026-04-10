# Kế Hoạch Frontend — Next.js Base

> **Thư mục dự án:** `frontend/`
> **Mục tiêu:** Xây dựng nền tảng frontend chuẩn cho toàn bộ dự án, tích hợp `appearance` API, thiết kế theo phong cách **Bento Grid Layout** + **Dark Mode mặc định** + **Vivid Gradients**.

---

## 1. Tổng Quan

### 1.1 Mục Đích

Frontend base cung cấp:
- **Hệ thống màu sắc động** — toàn bộ màu lấy từ backend `appearance` API, không hardcode hex.
- **Bento Grid UI system** — layout linh hoạt dạng ô lưới bất đối xứng, mỗi ô là một card tự đóng gói.
- **Dark Mode mặc định** — tiêu chuẩn bắt buộc; light mode là lựa chọn thứ hai.
- **Vivid Gradients** — gradient dọc theo palette Dark Azure (`#0e4475` → `#2b78cc`) tạo chiều sâu trên card, text, border.
- **Auth flow** — đăng nhập / đăng ký / JWT refresh tích hợp sẵn.

### 1.2 Người Dùng Hệ Thống

| Vai trò | Mô tả |
|---------|-------|
| **Visitor** | Khách vãng lai — truy cập trang chủ, landing |
| **User** | Đã đăng nhập — xem dashboard, hồ sơ cá nhân |
| **Admin** | Quản trị viên — truy cập khu vực admin (nếu mở rộng) |

### 1.3 Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript (strict mode) |
| Styling | Tailwind CSS v4 |
| State | React `useState` / `useContext` (không dùng thư viện nặng) |
| Auth storage | `httpOnly` cookie (access token) + `localStorage` (refresh) |
| HTTP client | native `fetch` (server-side) + `axios` (client-side) |
| Validation | Zod |
| Animation | CSS Transition + Tailwind `animate-*` |
| Icons | `lucide-react` |

---

## 2. Design System

### 2.1 Dark Mode — Tiêu Chuẩn Bắt Buộc

- Dark mode là **trạng thái mặc định** khi user mới truy cập lần đầu.
- Khi không có lựa chọn trong `localStorage`, dùng `prefers-color-scheme: dark` của hệ điều hành.
- Toggle dùng `data-theme="dark"` / `data-theme="light"` trên thẻ `<html>`.
- Tất cả màu sắc đến từ backend `appearance` API — CSS vars được inject trong root layout.

```
Mặc định (lần đầu vào):
  prefers-color-scheme: dark  → dark mode
  prefers-color-scheme: light → light mode

Sau khi toggle:
  Lưu vào localStorage["theme"] → khôi phục lần sau
```

### 2.2 Color System

> Toàn bộ màu là CSS variables từ `GET /api/v1/appearance/config/`. **Không hardcode hex.**

| Token | Light | Dark | Vai trò |
|-------|-------|------|---------|
| `--color-primary` | `#0e4475` | `#2b78cc` | Màu chủ đạo Dark Azure |
| `--color-secondary` | `#1565c0` | `#42a5f5` | Màu phụ |
| `--color-accent` | `#0288d1` | `#29b6f6` | Điểm nhấn |
| `--color-bg` | `#ffffff` | `#0c1a2e` (Dark Navy) | Nền trang |
| `--color-surface` | `#f8fafc` | `#0e2040` | Nền card |
| `--color-border` | `#e2e8f0` | `#1e3a5f` | Viền |
| `--color-fg` | `#0f172a` | `#e8f0f7` | Chữ chính |
| `--color-fg-muted` | `#475569` | `#8fafc8` | Chữ phụ |
| `--color-danger` | `#dc2626` | `#f87171` | Lỗi |
| `--color-success` | `#16a34a` | `#4ade80` | Thành công |

### 2.3 Vivid Gradients

Gradient sử dụng CSS variables của Tailwind, không hardcode hex:

| Gradient | Tailwind class | Mô tả |
|----------|---------------|-------|
| **Primary gradient** | `bg-gradient-to-br from-primary to-accent` | Nền hero, CTA card |
| **Deep gradient** | `bg-gradient-to-b from-primary to-bg` | Nền section tối |
| **Subtle surface** | `bg-gradient-to-b from-surface to-bg` | Nền card nhẹ |
| **Accent gradient** | `bg-gradient-to-r from-accent to-secondary` | Badge, highlight |
| **Border gradient** | CSS custom (pseudo-element) | Viền gradient cho Bento card |

**Gradient text** (tiêu đề lớn):
```css
.gradient-text {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Gradient border** (Bento card featured):
```css
.gradient-border {
  position: relative;
  border-radius: 1rem;
  background: var(--color-surface);
}
.gradient-border::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  z-index: -1;
}
```

### 2.4 Bento Grid System

**Bento Grid** là layout dạng lưới CSS Grid với các card có kích thước bất đối xứng, tạo cảm giác "tờ báo hiện đại".

**Grid container:**
```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);   /* 12 cột */
  grid-auto-rows: minmax(120px, auto);
  gap: 1rem;
}
```

**Card size variants:**

| Variant | cols | rows | Dùng cho |
|---------|------|------|---------|
| `1x1` | 3 cột | 2 rows | Stat card nhỏ |
| `2x1` | 6 cột | 2 rows | Feature card ngang |
| `1x2` | 3 cột | 4 rows | Feature card dọc |
| `2x2` | 6 cột | 4 rows | Chart / Hero card |
| `3x1` | 9 cột | 2 rows | Wide card |
| `4x2` | 12 cột | 4 rows | Full-width hero |
| `full` | 12 cột | auto | Banner, CTA |

**Responsive:**
- `md:` (768px): 12-col grid
- `sm:` (640px): 6-col grid — mỗi card tối đa 6 cột
- Mobile (< 640px): 1-col — tất cả card full width, stack dọc

**Bento Card structure:**
```
BentoCard
├── Inner glow (box-shadow gradient)
├── Gradient border (featured cards)
├── Background (surface + subtle gradient)
├── Content slot (header / body / footer)
└── Hover effect (scale + border brightness)
```

### 2.5 Typography

| Role | Class | Font |
|------|-------|------|
| Heading XL | `text-5xl font-bold tracking-tight` | `var(--font-inter)` |
| Heading L | `text-3xl font-semibold` | `var(--font-inter)` |
| Heading M | `text-xl font-semibold` | `var(--font-inter)` |
| Body | `text-base font-normal` | `var(--font-inter)` |
| Caption | `text-sm text-fg-muted` | `var(--font-inter)` |
| Code | `text-sm font-mono` | `var(--font-mono)` |

---

## 3. Kiến Trúc Thư Mục

```
frontend/
├── src/
│   ├── app/                              # App Router — chỉ routing
│   │   ├── (auth)/                       # Route group — trang auth (không header/sidebar)
│   │   │   ├── layout.tsx                # Auth layout — centered, gradient background
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (main)/                       # Route group — trang chính
│   │   │   ├── layout.tsx                # Main layout — header + sidebar
│   │   │   ├── page.tsx                  # Landing page (Bento Grid showcase)
│   │   │   └── dashboard/
│   │   │       └── page.tsx              # Dashboard Bento Grid
│   │   ├── profile/
│   │   │   └── page.tsx
│   │   ├── api/
│   │   │   └── revalidate/
│   │   │       └── route.ts              # Webhook: revalidateTag('appearance')
│   │   ├── layout.tsx                    # Root layout — inject appearance CSS vars
│   │   ├── globals.css
│   │   ├── not-found.tsx
│   │   └── error.tsx
│   │
│   ├── features/                         # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── actions/
│   │   │   │   └── authActions.ts        # Server Actions: login, register, logout
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts            # Client: current user, token state
│   │   │   ├── lib/
│   │   │   │   └── authClient.ts         # Token storage (cookie / localStorage)
│   │   │   └── types.ts
│   │   ├── dashboard/
│   │   │   ├── components/
│   │   │   │   ├── DashboardBento.tsx    # Bento Grid container
│   │   │   │   ├── StatsCard.tsx         # 1x1 stat card
│   │   │   │   ├── ChartCard.tsx         # 2x2 chart card (placeholder)
│   │   │   │   └── QuickActionsCard.tsx  # full-width CTA card
│   │   │   ├── queries/
│   │   │   │   └── dashboardQueries.ts
│   │   │   └── types.ts
│   │   ├── profile/
│   │   │   ├── components/
│   │   │   │   ├── ProfileCard.tsx
│   │   │   │   └── ChangePasswordForm.tsx
│   │   │   ├── actions/
│   │   │   │   └── profileActions.ts
│   │   │   └── types.ts
│   │   └── landing/
│   │       ├── components/
│   │       │   ├── HeroBento.tsx         # Hero — full-width gradient card
│   │       │   ├── FeaturesBento.tsx     # Bento grid features showcase
│   │       │   └── CTASection.tsx
│   │       └── types.ts
│   │
│   ├── components/                       # Shared UI components
│   │   ├── ui/
│   │   │   ├── Button.tsx                # variants: primary/ghost/danger/outline/gradient
│   │   │   ├── Input.tsx
│   │   │   ├── Textarea.tsx
│   │   │   ├── Badge.tsx                 # variants: brand/semantic/outline/gradient
│   │   │   ├── Avatar.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── Spinner.tsx
│   │   ├── bento/
│   │   │   ├── BentoGrid.tsx             # Grid container (12-col CSS Grid)
│   │   │   ├── BentoCard.tsx             # Individual bento cell — size variants
│   │   │   └── types.ts                  # BentoSize, BentoCardProps
│   │   ├── gradient/
│   │   │   ├── GradientText.tsx          # Gradient text wrapper
│   │   │   ├── GradientBorder.tsx        # Card với gradient border
│   │   │   └── GradientBackground.tsx    # Section background gradient
│   │   └── layout/
│   │       ├── Header.tsx                # Logo + nav + ThemeToggle + Avatar
│   │       ├── Sidebar.tsx
│   │       ├── ThemeToggle.tsx           # Client Component
│   │       └── AppLogo.tsx               # Logo từ appearance media.logo
│   │
│   ├── lib/
│   │   ├── appearance.ts                 # fetchAppearanceConfig, buildCssVars
│   │   ├── api.ts                        # Base fetch wrapper (auth header, error handling)
│   │   └── utils.ts                      # cn() (clsx + twMerge), formatDate, etc.
│   │
│   ├── hooks/
│   │   ├── useTheme.ts                   # Dark mode toggle, localStorage persist
│   │   └── useToast.ts                   # Toast notification state
│   │
│   └── types/
│       ├── appearance.ts                 # AppearanceConfig, ColorGroups
│       ├── auth.ts                       # User, LoginPayload, RegisterPayload
│       └── api.ts                        # ApiResponse<T>, PaginatedResponse<T>
│
├── public/
│   └── og-fallback.png                   # OG image fallback
├── .env.local
├── .env.example
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

---

## 4. Pages & Routes

| Route | Layout | Truy cập | Mô tả |
|-------|--------|----------|-------|
| `/` | Main | Visitor + User | Landing page — Bento Grid showcase |
| `/login` | Auth | Visitor | Form đăng nhập |
| `/register` | Auth | Visitor | Form đăng ký |
| `/dashboard` | Main | User (auth) | Dashboard Bento Grid |
| `/profile` | Main | User (auth) | Hồ sơ cá nhân + đổi mật khẩu |
| `*` | None | Tất cả | 404 not-found page |

---

## 5. User Flows

### 5.1 Đăng Nhập

```
Visitor vào /login
  → Nhập email + password
  → Submit (Server Action: login)
  → Gọi POST /api/v1/auth/login/
    → Thành công: lưu access vào cookie httpOnly, refresh vào localStorage
               → redirect /dashboard
    → Lỗi 401: hiện lỗi "Email hoặc mật khẩu không đúng" trên form
    → Lỗi validation: hiện lỗi trên từng field
  → Đã đăng nhập → middleware redirect /dashboard
```

### 5.2 Đăng Ký

```
Visitor vào /register
  → Nhập email + full_name + password + password_confirm
  → Submit (Server Action: register)
  → Gọi POST /api/v1/auth/register/
    → 201: tự động đăng nhập → redirect /dashboard
    → 400: hiện lỗi field (email đã tồn tại, mật khẩu yếu...)
```

### 5.3 Đăng Xuất

```
User nhấn "Đăng xuất" (Header)
  → Server Action: logout
  → Gọi POST /api/v1/auth/logout/ (blacklist refresh token)
  → Xóa cookie access token
  → Xóa localStorage refresh token
  → redirect /login
```

### 5.4 Refresh Token (tự động)

```
Client gọi API → nhận 401
  → Tự động gọi POST /api/v1/auth/token/refresh/
    → Thành công: cập nhật access token trong cookie → retry request gốc
    → Thất bại: redirect /login
```

### 5.5 Dashboard

```
User vào /dashboard
  → Server Component fetch data (nếu có) với access token từ cookie
  → Hiển thị Bento Grid:
      [Stats 1][Stats 2][Stats 3]
      [     Chart 2x2    ][Recent 1x2]
      [    Quick Actions — full    ]
  → Mỗi card có gradient nền + hover effect
```

### 5.6 Appearance Bootstrap

```
App khởi động (Root Layout — Server Component):
  → fetchAppearanceConfig() → GET /api/v1/appearance/config/
    → OK: buildCssVars(light, ':root') + buildCssVars(dark, '[data-theme="dark"]')
        → inject <style> vào <head>
    → Lỗi/timeout: app vẫn render (CSS vars trống — browser dùng fallback)
  → Client hydration: useTheme() đọc localStorage / prefers-color-scheme
      → setAttribute('data-theme', ...) trên <html>
  → Logo: lấy config.media.logo → inject vào AppLogo component
```

---

## 6. Shared UI Components

### 6.1 `BentoGrid` & `BentoCard`

```tsx
// Dùng:
<BentoGrid cols={12} gap={4}>
  <BentoCard size="2x2" variant="featured">   {/* gradient border */}
    ...
  </BentoCard>
  <BentoCard size="1x1">
    ...
  </BentoCard>
</BentoGrid>
```

| Prop | Type | Mô tả |
|------|------|-------|
| `size` | `'1x1' \| '2x1' \| '1x2' \| '2x2' \| '3x1' \| 'full'` | Grid span |
| `variant` | `'default' \| 'featured' \| 'gradient' \| 'ghost'` | Visual style |
| `gradient` | `'primary' \| 'accent' \| 'surface'` | Gradient background |
| `hover` | `boolean` | Scale + border brightness on hover |

### 6.2 `Button`

| Variant | Style |
|---------|-------|
| `primary` | `bg-primary text-primary-fg` |
| `gradient` | `bg-gradient-to-r from-primary to-accent text-white` |
| `ghost` | `bg-transparent hover:bg-surface` |
| `outline` | `border border-border` |
| `danger` | `bg-danger text-white` |

### 6.3 `GradientText`

```tsx
<GradientText from="primary" to="accent" size="5xl" weight="bold">
  Tiêu đề lớn
</GradientText>
```

Wrap text trong `<span>` với CSS gradient clip.

### 6.4 `AppLogo`

```tsx
// Server Component
// Nhận AppearanceConfig.media.logo từ parent layout
// Fallback về text logo nếu media.logo = null
<AppLogo src={config?.media?.logo} alt="Logo" />
```

### 6.5 `ThemeToggle`

```tsx
// Client Component
// useTheme() → toggleTheme()
// Icon: Moon (dark) / Sun (light) từ lucide-react
<ThemeToggle />
```

---

## 7. Tích Hợp Backend APIs

### 7.1 Appearance Config (Root Layout)

```
GET /api/v1/appearance/config/
  → Không cần auth
  → Cache tag: 'appearance', revalidate: 3600s
  → Inject CSS vars vào <head>
  → Lấy logo URL cho AppLogo
```

**Revalidation webhook** — khi admin cập nhật token trên backend:
```
POST /api/revalidate?secret=REVALIDATE_SECRET
  → Route Handler: revalidateTag('appearance')
  → Response: { revalidated: true }
```

### 7.2 Auth APIs

| Action | Endpoint |
|--------|----------|
| Đăng nhập | `POST /api/v1/auth/login/` |
| Đăng ký | `POST /api/v1/auth/register/` |
| Đăng xuất | `POST /api/v1/auth/logout/` |
| Refresh token | `POST /api/v1/auth/token/refresh/` |
| Đổi mật khẩu | `POST /api/v1/auth/password/change/` |

### 7.3 Truyền Auth Token

- **Server Component**: đọc cookie `access_token` → đính vào `Authorization: Bearer <token>`
- **Client Component**: axios interceptor tự đính access token; tự refresh khi 401

---

## 8. Environment Variables

```env
# .env.local

# Server-side (không prefix NEXT_PUBLIC_)
INTERNAL_API_URL=http://backend:8000          # Docker internal network

# Client-side
NEXT_PUBLIC_API_URL=http://localhost:8000     # Development
# NEXT_PUBLIC_API_URL=https://api.example.com  # Production

# Revalidation secret (dùng cho webhook từ backend)
REVALIDATE_SECRET=your-secret-key-here
```

---

## 9. Tailwind Config

```ts
// tailwind.config.ts
const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: ['attribute', 'data-theme'],
  theme: {
    extend: {
      colors: {
        // Brand
        primary:         'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        'primary-light': 'var(--color-primary-light)',
        'primary-fg':    'var(--color-primary-fg)',
        secondary:       'var(--color-secondary)',
        accent:          'var(--color-accent)',
        // Semantic
        danger:          'var(--color-danger)',
        'danger-light':  'var(--color-danger-light)',
        warning:         'var(--color-warning)',
        success:         'var(--color-success)',
        info:            'var(--color-info)',
        // Neutral
        bg:              'var(--color-bg)',
        'bg-subtle':     'var(--color-bg-subtle)',
        'bg-muted':      'var(--color-bg-muted)',
        surface:         'var(--color-surface)',
        border:          'var(--color-border)',
        card:            'var(--color-card)',
        fg:              'var(--color-fg)',
        'fg-muted':      'var(--color-fg-muted)',
        'fg-subtle':     'var(--color-fg-subtle)',
      },
      fontFamily: {
        sans:  ['var(--font-inter)', 'sans-serif'],
        mono:  ['var(--font-mono)', 'monospace'],
      },
      borderRadius: {
        bento: '1.25rem',  // Corner radius chuẩn cho Bento card
      },
    },
  },
}
```

---

## 10. UX Considerations

### Loading States

| Component | Loading pattern |
|-----------|----------------|
| Page toàn trang | `loading.tsx` — BentoGrid skeleton (pulse animation) |
| Stat card | Skeleton `animate-pulse` với màu `bg-muted` |
| Form submit | Button `disabled` + Spinner |
| Logo | Skeleton box kích thước cố định |

### Empty States

| Tình huống | UI |
|------------|-----|
| Dashboard không có data | Bento card với icon + text "Chưa có dữ liệu" |
| Danh sách rỗng | Empty state illustration + CTA button |

### Error States

| Loại lỗi | Xử lý |
|----------|-------|
| Lỗi field (validation) | Hiện dưới field với `text-danger text-sm` |
| Lỗi chung API | Toast notification (top-right, auto dismiss 4s) |
| 401 Unauthorized | Redirect `/login` (middleware + axios interceptor) |
| 500 Server Error | `error.tsx` — hiện thông báo + nút "Thử lại" |
| Appearance API lỗi | Tiếp tục render với CSS vars trống (graceful fallback) |

### Dark Mode UX

- Không có flash khi load (CSS vars được inject server-side trong `<style>`)
- `useTheme` đọc `localStorage` sau hydration → áp dụng ngay, không phụ thuộc JS load
- Tất cả gradient và shadow được thiết kế để đẹp trên **cả dark lẫn light**

### Hover & Animation

- Bento card: `transition-transform duration-200 hover:scale-[1.02]`
- Gradient border: `hover:brightness-110`
- Button: `active:scale-95 transition-transform`
- Tất cả animation: `prefers-reduced-motion: reduce` → disable transition

---

## 11. Kế Hoạch Triển Khai

### Phase 1 — Nền Tảng (Ưu tiên đầu)

| # | Task |
|---|------|
| 1 | Khởi tạo Next.js 15 project vào `frontend/` với TypeScript + Tailwind |
| 2 | Cấu hình `tailwind.config.ts` với CSS vars mapping |
| 3 | Tạo `lib/appearance.ts` — `fetchAppearanceConfig()` + `buildCssVars()` |
| 4 | Root layout `app/layout.tsx` — inject appearance CSS vars |
| 5 | `hooks/useTheme.ts` — dark mode toggle + localStorage persist |
| 6 | Tạo `globals.css` — CSS custom properties fallback (khi appearance API chưa có response) |
| 7 | Cấu hình Font (Inter qua `next/font`) |

### Phase 2 — Bento Grid System

| # | Task |
|---|------|
| 8 | `components/bento/BentoGrid.tsx` — 12-col grid container |
| 9 | `components/bento/BentoCard.tsx` — size variants + visual variants |
| 10 | `components/gradient/GradientText.tsx` — gradient text clip |
| 11 | `components/gradient/GradientBorder.tsx` — pseudo-element gradient border |
| 12 | `components/gradient/GradientBackground.tsx` — section nền |
| 13 | Landing page `/` — lắp ráp Bento Grid showcase |

### Phase 3 — Auth Flow

| # | Task |
|---|------|
| 14 | `features/auth/` — LoginForm, RegisterForm |
| 15 | Server Actions: `authActions.ts` — login, register, logout |
| 16 | `features/auth/lib/authClient.ts` — token storage |
| 17 | Middleware `middleware.ts` — bảo vệ route `/dashboard`, `/profile` |
| 18 | Axios client với refresh token interceptor |

### Phase 4 — Layout & Navigation

| # | Task |
|---|------|
| 19 | `components/layout/Header.tsx` — logo + nav + ThemeToggle + avatar |
| 20 | `components/layout/AppLogo.tsx` — logo từ appearance media API |
| 21 | `components/layout/ThemeToggle.tsx` — client toggle |
| 22 | Auth layout (centered) + Main layout (header + sidebar) |

### Phase 5 — Dashboard & Profile

| # | Task |
|---|------|
| 23 | `features/dashboard/` — DashboardBento, StatsCard, QuickActionsCard |
| 24 | `/dashboard` page |
| 25 | `features/profile/` — ProfileCard, ChangePasswordForm |
| 26 | `/profile` page |

### Phase 6 — Polish & Production Ready

| # | Task |
|---|------|
| 27 | `app/api/revalidate/route.ts` — webhook revalidateTag('appearance') |
| 28 | `loading.tsx` + `error.tsx` cho mỗi route segment |
| 29 | SEO: metadata, og:image từ `appearance` media |
| 30 | Dockerfile cho `frontend/` |

---

## 12. Ghi Chú Kỹ Thuật

### Bento Grid Responsive Strategy

```
Desktop  (lg ≥ 1024px): 12-col grid, cards dùng đúng size variant
Tablet   (md  768-1023): 6-col grid, 2x* cards thu lại, 1x* giữ nguyên
Mobile   (< 768px):       1-col, tất cả stack dọc, bỏ gradient border
```

### CSS Vars Fallback

Khi appearance API chưa trả về kịp (error/timeout), `globals.css` định nghĩa fallback tối giản:
```css
/* globals.css — fallback chỉ để app không bị vỡ màu */
:root {
  --color-bg: #0c1a2e;
  --color-fg: #e8f0f7;
  --color-primary: #2b78cc;
  --color-surface: #0e2040;
  --color-border: #1e3a5f;
}
```
Khi appearance API load xong (server-side), `<style>` được inject sẽ override toàn bộ.

### Security Notes

- Access token trong `httpOnly` cookie — không đọc được từ JavaScript.
- Refresh token trong `localStorage` — chỉ dùng để gọi `/token/refresh/`, không dùng trực tiếp cho auth.
- Revalidation webhook dùng `REVALIDATE_SECRET` query param — validate server-side trước khi `revalidateTag()`.
- CSP header: không dùng `unsafe-inline` — `<style>` inject từ server là nonce-based nếu bật CSP.
