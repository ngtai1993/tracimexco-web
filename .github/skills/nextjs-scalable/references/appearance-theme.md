# Appearance & Theme Colors — Reference

> **Quy tắc bất biến:** Không hardcode màu hex trong bất kỳ file nào của dự án.
> Toàn bộ màu sắc đến từ backend qua `GET /api/v1/appearance/config/`.

---

## Backend API

| Endpoint | Auth | Mô tả |
|----------|------|-------|
| `GET /api/v1/appearance/config/` | Public | JSON với `colors.light`, `colors.dark`, `media` |
| `GET /api/v1/appearance/config/css/` | Public | CSS text `:root {}` + `[data-theme="dark"] {}` |

**Response structure:**
```json
{
  "data": {
    "colors": {
      "light": {
        "brand":    { "primary": "#0e4475", "secondary": "#1a5fa8", "accent": "#2980d4" },
        "semantic": { "danger": "#c0392b", "warning": "#e67e22", "success": "#27ae60", "info": "#2980d4" },
        "neutral":  { "bg": "#f0f4f8", "surface": "#ffffff", "border": "#c6d4e3", "fg": "#0c1a2e", "fg-muted": "#3d5a80" }
      },
      "dark": {
        "brand":    { "primary": "#2b78cc", "secondary": "#1a5fa8", "accent": "#5ba3e8" },
        "semantic": { "danger": "#e74c3c", "warning": "#f39c12", "success": "#2ecc71", "info": "#5ba3e8" },
        "neutral":  { "bg": "#0c1a2e", "surface": "#0e2040", "border": "#1e3a5f", "fg": "#e8f0f7", "fg-muted": "#8fafc8" }
      }
    },
    "media": {
      "logo": "/media/appearance/logo.png",
      "favicon": "/media/appearance/favicon.ico"
    }
  }
}
```

**CSS var naming convention:** `--color-{key}` (e.g. `--color-primary`, `--color-fg-muted`)

---

## Cài đặt

### 1. `lib/appearance.ts` — Fetch & helpers

```ts
export interface ColorGroups {
  brand:    Record<string, string>
  semantic: Record<string, string>
  neutral:  Record<string, string>
  [group: string]: Record<string, string>
}

export interface AppearanceConfig {
  colors: {
    light: ColorGroups
    dark:  ColorGroups
  }
  media: Record<string, string | null>
}

/**
 * Server-side fetch — dùng INTERNAL_API_URL để tránh round-trip qua internet.
 * Có tag 'appearance' để on-demand revalidation.
 */
export async function fetchAppearanceConfig(): Promise<AppearanceConfig | null> {
  const url = `${process.env.INTERNAL_API_URL}/api/v1/appearance/config/`
  try {
    const res = await fetch(url, {
      next: { tags: ['appearance'], revalidate: 3600 },
    })
    if (!res.ok) return null
    const json = await res.json()
    return (json.data as AppearanceConfig) ?? null
  } catch {
    return null
  }
}

/**
 * Chuyển grouped color tokens thành CSS custom properties string.
 * Ví dụ: buildCssVars(config.colors.light, ':root')
 */
export function buildCssVars(
  tokens: ColorGroups,
  selector: string
): string {
  const lines = Object.values(tokens)
    .flatMap(group => Object.entries(group))
    .map(([key, value]) => `  --color-${key}: ${value};`)
  return `${selector} {\n${lines.join('\n')}\n}`
}
```

---

### 2. `app/layout.tsx` — Inject CSS vars (Server Component)

```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { fetchAppearanceConfig, buildCssVars } from '@/lib/appearance'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' })

export const metadata: Metadata = {
  title: 'MyApp',
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const config = await fetchAppearanceConfig()

  const lightCss = config ? buildCssVars(config.colors.light, ':root') : ''
  const darkCss  = config ? buildCssVars(config.colors.dark, '[data-theme="dark"]') : ''
  const themeCss = [lightCss, darkCss].filter(Boolean).join('\n\n')

  return (
    <html lang="vi" className={inter.variable}>
      <head>
        {themeCss && (
          <style dangerouslySetInnerHTML={{ __html: themeCss }} />
        )}
      </head>
      <body className="bg-bg text-fg font-sans">
        {children}
      </body>
    </html>
  )
}
```

> **Lưu ý:** `dangerouslySetInnerHTML` ở đây an toàn vì nội dung CSS được tạo từ
> dữ liệu server-controlled (backend API), không từ user input.

---

### 3. `tailwind.config.ts` — Map CSS vars vào Tailwind tokens

```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: ['attribute', 'data-theme'],   // toggle bằng data-theme="dark" trên <html>
  theme: {
    extend: {
      colors: {
        // Brand
        primary:   'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent:    'var(--color-accent)',
        // Semantic
        danger:    'var(--color-danger)',
        warning:   'var(--color-warning)',
        success:   'var(--color-success)',
        info:      'var(--color-info)',
        // Neutral
        bg:        'var(--color-bg)',
        surface:   'var(--color-surface)',
        border:    'var(--color-border)',
        fg:        'var(--color-fg)',
        'fg-muted': 'var(--color-fg-muted)',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
```

---

### 4. `hooks/useTheme.ts` — Dark mode toggle (Client)

```ts
'use client'
import { useEffect, useState, useCallback } from 'react'

type Theme = 'light' | 'dark'
const STORAGE_KEY = 'theme'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('light')

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as Theme | null
    const preferred: Theme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
    apply(saved ?? preferred)
  }, [])

  const apply = useCallback((next: Theme) => {
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem(STORAGE_KEY, next)
    setTheme(next)
  }, [])

  const toggleTheme = useCallback(() => {
    apply(theme === 'light' ? 'dark' : 'light')
  }, [theme, apply])

  return { theme, toggleTheme, setTheme: apply }
}
```

**Dùng trong component:**
```tsx
'use client'
import { useTheme } from '@/hooks/useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  return (
    <button
      onClick={toggleTheme}
      aria-label={theme === 'light' ? 'Bật dark mode' : 'Bật light mode'}
      className="p-2 rounded-lg bg-surface border border-border text-fg"
    >
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  )
}
```

---

### 5. Revalidate khi admin cập nhật token

```ts
// features/appearance/actions/revalidateAppearance.ts
'use server'
import { revalidateTag } from 'next/cache'

export async function revalidateAppearanceCache() {
  revalidateTag('appearance')
}
```

Gọi sau khi admin lưu thay đổi color token qua admin panel / API.

---

### 6. `.env` — Biến môi trường

```env
# Server-side (không prefix NEXT_PUBLIC_)
INTERNAL_API_URL=http://backend:8000   # Docker internal network

# Client-side (nếu cần fetch từ browser)
NEXT_PUBLIC_API_URL=https://api.example.com
```

---

## Checklist

- [ ] Không có hex color (`#xxxxxx`) hardcode trong source code
- [ ] `lib/appearance.ts` có `fetchAppearanceConfig()` + `buildCssVars()`
- [ ] `app/layout.tsx` inject CSS vars từ backend vào `<style>`
- [ ] `tailwind.config.ts` dùng `var(--color-*)` cho tất cả màu
- [ ] `darkMode: ['attribute', 'data-theme']` trong Tailwind config
- [ ] `useTheme` hook persist lựa chọn vào `localStorage`
- [ ] Fallback graceful khi `/api/v1/appearance/config/` trả lỗi
- [ ] `revalidateTag('appearance')` sau khi admin cập nhật token
