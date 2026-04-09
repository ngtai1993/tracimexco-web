# Design System — Design Tokens & Consistency Rules

## 1. Nguyên Tắc Cốt Lõi

> **Không bao giờ hardcode màu, font size, spacing trực tiếp trong JSX.**
> Tất cả giá trị visual phải đến từ **design tokens** — CSS variables được map vào Tailwind.

```tsx
// ❌ Hardcode gây vỡ design
<div className="text-[#6b6375] text-[14px] p-[12px] rounded-[8px]">

// ✅ Dùng token
<div className="text-muted text-sm p-3 rounded-md">
```

---

## 2. Định Nghĩa Design Tokens (CSS Variables)

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  /* ── Color Palette ────────────────────────────────────────────── */
  /* Primary */
  --color-primary:         #2563eb;   /* blue-600 */
  --color-primary-hover:   #1d4ed8;   /* blue-700 */
  --color-primary-light:   #eff6ff;   /* blue-50  */
  --color-primary-fg:      #ffffff;   /* text trên primary bg */

  /* Neutral */
  --color-bg:              #ffffff;
  --color-bg-subtle:       #f9fafb;   /* gray-50  */
  --color-bg-muted:        #f3f4f6;   /* gray-100 */

  --color-fg:              #111827;   /* gray-900 — default text */
  --color-fg-muted:        #6b7280;   /* gray-500 — secondary text */
  --color-fg-subtle:       #9ca3af;   /* gray-400 — placeholder */
  --color-fg-disabled:     #d1d5db;   /* gray-300 */

  /* Border */
  --color-border:          #e5e7eb;   /* gray-200 */
  --color-border-strong:   #d1d5db;   /* gray-300 */

  /* Semantic */
  --color-success:         #16a34a;   /* green-600 */
  --color-success-light:   #f0fdf4;   /* green-50  */
  --color-warning:         #d97706;   /* amber-600 */
  --color-warning-light:   #fffbeb;   /* amber-50  */
  --color-danger:          #dc2626;   /* red-600   */
  --color-danger-light:    #fef2f2;   /* red-50    */
  --color-info:            #0891b2;   /* cyan-600  */
  --color-info-light:      #ecfeff;   /* cyan-50   */

  /* ── Typography ───────────────────────────────────────────────── */
  --font-sans:  'Inter', ui-sans-serif, system-ui, sans-serif;

  /* ── Border Radius ────────────────────────────────────────────── */
  --radius-sm:  0.25rem;    /* 4px  */
  --radius-md:  0.5rem;     /* 8px  */
  --radius-lg:  0.75rem;    /* 12px */
  --radius-xl:  1rem;       /* 16px */
  --radius-full: 9999px;

  /* ── Shadow ──────────────────────────────────────────────────── */
  --shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
```

---

## 3. Component Variants Nhất Quán (CVA)

```tsx
// components/ui/Button/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/utils/cn'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 font-medium rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:   'bg-primary text-primary-fg hover:bg-primary-hover',
        secondary: 'bg-bg-muted text-fg hover:bg-border',
        outline:   'border border-border text-fg hover:bg-bg-subtle',
        ghost:     'text-fg hover:bg-bg-muted',
        danger:    'bg-danger text-white hover:bg-danger/90',
        link:      'text-primary underline-offset-4 hover:underline p-0 h-auto',
      },
      size: {
        sm:  'h-8 px-3 text-sm',
        md:  'h-10 px-4 text-sm',
        lg:  'h-11 px-6 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean
}

export const Button = React.memo(
  ({ variant, size, isLoading, className, children, disabled, ...props }: ButtonProps) => (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...props}
    >
      {isLoading && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  )
)
Button.displayName = 'Button'

export { buttonVariants }
```

---

## 4. Badge / Status Chip — Semantic Colors

```tsx
// components/ui/Badge/Badge.tsx
const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium',
  {
    variants: {
      intent: {
        default: 'bg-bg-muted text-fg',
        primary: 'bg-primary-light text-primary',
        success: 'bg-success-light text-success',
        warning: 'bg-warning-light text-warning',
        danger:  'bg-danger-light text-danger',
        info:    'bg-info-light text-info',
      },
    },
    defaultVariants: { intent: 'default' },
  }
)

// Usage:
// <Badge intent="success">Hoạt động</Badge>
// <Badge intent="danger">Bị khoá</Badge>
```

---

## 5. Spacing — Quy Tắc Sử Dụng

```
KHÔNG dùng:  p-[12px], m-[24px], gap-[16px]
LUÔN dùng:   p-3,      m-6,      gap-4

Scale 4px:
  p-1 = 4px   (icon gap, tight spacing)
  p-2 = 8px   (badge padding, chip)
  p-3 = 12px  (button sm, input sm)
  p-4 = 16px  (card padding, button md)
  p-6 = 24px  (section padding, card lg)
  p-8 = 32px  (page section)
  p-12 = 48px (large section gap)
  p-16 = 64px (hero spacing)
```

---

## 6. Checklist Design Consistency

Trước khi commit component, kiểm tra:

- [ ] Không có màu hardcode (`#hex`, `rgb(...)`) trong className
- [ ] Không có arbitrary values cho spacing (`p-[13px]`, `m-[7px]`)
- [ ] Font size dùng scale chuẩn (`text-sm`, `text-base`, không dùng `text-[15px]`)
- [ ] Variant mới được thêm vào `cva()` — không tạo className riêng lẻ
- [ ] Semantic color đúng ngữ nghĩa: `text-danger` cho lỗi, `text-success` cho OK
- [ ] Spacing dùng bội số 4px
- [ ] Border radius dùng token: `rounded-sm/md/lg/xl` (không dùng `rounded-[6px]`)

---

## 7. Quy Tắc Mở Rộng

**Khi cần thêm variant mới:**
1. Thêm vào `cva()` của component — **không** tạo className ad-hoc
2. Đặt tên theo intent (primary/secondary/danger) — **không** theo màu (blue/red)
3. Nếu cần màu mới → thêm CSS variable vào `@theme` trước

**Tuyệt đối không:**
```tsx
// ❌ Tạo class ad-hoc theo context
<div className="bg-blue-100 text-blue-700">

// ❌ Dùng tên màu thay tên role
<Badge className="bg-green-100 text-green-800">

// ✅ Luôn dùng token semantic
<div className="bg-info-light text-info">
<Badge intent="success">
```
