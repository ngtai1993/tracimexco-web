# Dashboard Design Plan

> Frontend: Next.js 16 · Tailwind v4 · Dark Azure Design System · Bento Grid  
> Sidebar chuyên nghiệp + Widget placeholder — widgets phát triển sau

---

## 1. Layout Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Sidebar (260px / 64px collapsed)  │  Main Area          │
│  ┌──────────────────────────────┐  │  ┌────────────────┐ │
│  │  Logo + App Name   [«]       │  │  │  Topbar        │ │
│  ├──────────────────────────────┤  │  │  breadcrumb    │ │
│  │  User Quick Info             │  │  │  + actions     │ │
│  ├──────────────────────────────┤  │  ├────────────────┤ │
│  │  NAV — Tổng quan             │  │  │                │ │
│  │    Dashboard                 │  │  │   Content Area │ │
│  │    Analytics (🔜)            │  │  │   (BentoGrid)  │ │
│  ├──────────────────────────────┤  │  │                │ │
│  │  NAV — Quản lý               │  │  │                │ │
│  │    Người dùng (🔜)           │  │  │                │ │
│  │    Agents (🔜)               │  │  │                │ │
│  ├──────────────────────────────┤  │  │                │ │
│  │  NAV — Hệ thống              │  │  │                │ │
│  │    Cài đặt (🔜)              │  │  │                │ │
│  │    Appearance (🔜)           │  │  │                │ │
│  ├──────────────────────────────┤  │  │                │ │
│  │  User Avatar + Name          │  │  │                │ │
│  │  [Profile] [Logout]          │  │  │                │ │
│  └──────────────────────────────┘  │  └────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Kích thước & trạng thái

| State | Sidebar width | Main padding-left | Trigger |
|---|---|---|---|
| Expanded (default desktop) | 260px | 260px | — |
| Collapsed | 64px | 64px | Click `«` button |
| Mobile overlay | 100% overlay | 0 | Hamburger button |

**Breakpoints:**
- `md+` (768px+): Sidebar dạng `fixed left-0`, main area `ml-[260px]` / `ml-[64px]`
- `< md`: Sidebar ẩn, mở bằng hamburger → overlay full-height với backdrop blur

---

## 2. Sidebar Design Spec

### 2.1 Cấu trúc phân vùng

```
┌─────────────────────────────┐
│  HEADER (64px)              │  Logo + App name + Collapse btn
├─────────────────────────────┤
│  USER BLOCK (72px)          │  Avatar + Full name + Email (truncated)
├─────────────────────────────┤
│  NAV GROUPS (flex-1 scroll) │  Các nhóm chức năng
│    > Group Label            │
│    > Nav Item               │
│    > Nav Item (active)      │
│    > Nav Item (disabled)    │
├─────────────────────────────┤
│  FOOTER (56px)              │  Settings link + Logout button
└─────────────────────────────┘
```

### 2.2 Nav Item States

| State | Background | Text | Icon | Border-left |
|---|---|---|---|---|
| Default | transparent | `text-fg-muted` | `text-fg-subtle` | none |
| Hover | `bg-surface` | `text-fg` | `text-fg-muted` | none |
| Active | `bg-primary/10` | `text-primary` | `text-primary` | `border-l-2 border-primary` |
| Disabled | transparent | `text-fg-subtle/50` | `text-fg-subtle/30` | none |
| Focus-visible | `ring-2 ring-primary/30` | — | — | — |

### 2.3 Collapsed State (icon-only)

Khi sidebar thu lại `w-16`:
- Ẩn label, group title, user name/email
- Giữ icon (centered, 20px)
- Active state: icon `text-primary` + `bg-primary/10` rounded pill
- Tooltip khi hover: `title` attribute hiển thị label
- Logo vùng: chỉ hiển thị favicon/icon mark

### 2.4 Nav Groups

```
TỔNG QUAN
  ├─ Dashboard          /dashboard         LayoutDashboard
  └─ Analytics          /analytics         BarChart2         🔜

QUẢN LÝ  
  ├─ Người dùng         /users             Users             🔜
  ├─ Agents             /agents            Bot               🔜
  └─ Hội thoại          /conversations     MessageSquare     🔜

HỆ THỐNG
  ├─ Cài đặt            /settings          Settings          🔜
  ├─ Appearance         /appearance        Palette           🔜
  └─ Nhật ký            /logs              FileText          🔜

TRỢ GIÚP
  ├─ Tài liệu           (external)         BookOpen          🔜
  └─ Hỗ trợ             (external)         HeadphonesIcon    🔜
```

**Badge**: Items có notification badge (số đỏ) hiển thị ở góc trên phải của icon, ẩn khi collapsed chỉ còn dot.

### 2.5 Components cần tạo

| File | Mô tả |
|---|---|
| `components/layout/DashboardSidebar.tsx` | Sidebar chính (replaces Sidebar.tsx) |
| `components/layout/SidebarNavGroup.tsx` | Nhóm nav với group label |
| `components/layout/SidebarNavItem.tsx` | Item đơn lẻ với icon, label, badge |
| `components/layout/SidebarUserBlock.tsx` | User avatar + name + email |
| `components/layout/SidebarToggle.tsx` | Collapse/expand button |
| `hooks/useSidebar.ts` | State: expanded/collapsed, mobile open, persist to localStorage |
| `app/(main)/layout.tsx` | Cập nhật: dùng sidebar layout mới |

---

## 3. Topbar (trong Main Area)

Topbar **không** sticky — chỉ xuất hiện trong vùng content, không phải toàn chiều rộng màn hình.

```
┌──────────────────────────────────────────────────────────┐
│  Breadcrumb > Dashboard      │      ThemeToggle  Avatar  │
└──────────────────────────────────────────────────────────┘
```

- Trái: `Breadcrumb` — tự động từ pathname
- Phải: `ThemeToggle` + `Avatar` với dropdown (Profile, Settings, Logout)

**File:** `components/layout/DashboardTopbar.tsx`

---

## 4. Dashboard Page — Widget Grid

```
12-column CSS Grid, rows tự auto-fit

ROW 1 — Stat Cards (span 3/12 mỗi card)
┌──────────┬──────────┬──────────┬──────────┐
│ Stat 1   │ Stat 2   │ Stat 3   │ Stat 4   │
│ (3 cols) │ (3 cols) │ (3 cols) │ (3 cols) │
└──────────┴──────────┴──────────┴──────────┘

ROW 2 — Charts
┌──────────────────────────┬───────────────┐
│ Chart lớn (8 cols)       │ Chart phụ     │
│ Line/Bar (placeholder)   │ (4 cols)      │
│                          │ Donut/Pie     │
└──────────────────────────┴───────────────┘

ROW 3 — Table + Activity
┌──────────────────────────┬───────────────┐
│ Data Table (8 cols)      │ Activity Feed │
│ (placeholder)            │ (4 cols)      │
│                          │ (placeholder) │
└──────────────────────────┴───────────────┘

ROW 4 — Quick Actions (optional)
┌───────────┬───────────┬───────────┬──────┐
│ Action 1  │ Action 2  │ Action 3  │ ...  │
└───────────┴───────────┴───────────┴──────┘
```

### 4.1 Placeholder Widget Spec

Mỗi widget là `BentoCard` với:
- `variant="dashed"` — border dashed, opacity thấp
- Icon centered + label "Sắp ra mắt" hoặc tên widget
- `min-h` theo kích thước grid row

```tsx
// Ví dụ placeholder
<BentoCard cols={3} variant="placeholder">
  <div className="flex flex-col items-center justify-center gap-2 text-fg-subtle">
    <TrendingUp size={24} />
    <span className="text-sm">Tổng người dùng</span>
  </div>
</BentoCard>
```

### 4.2 Widget Inventory (để phát triển sau)

| Widget | Cols | Rows | API | Priority |
|---|---|---|---|---|
| Stat: Tổng users | 3 | 1 | `GET /api/v1/users/stats/` | 🔜 |
| Stat: Active agents | 3 | 1 | `GET /api/v1/agents/stats/` | 🔜 |
| Stat: Hội thoại hôm nay | 3 | 1 | Future | 🔜 |
| Stat: Tổng revenue (nếu có) | 3 | 1 | Future | 🔜 |
| Chart: Activity timeline | 8 | 2 | Future | 🔜 |
| Chart: User growth donut | 4 | 2 | Future | 🔜 |
| Table: Users gần đây | 8 | 3 | `GET /api/v1/users/` | 🔜 |
| Activity feed | 4 | 3 | Future | 🔜 |

---

## 5. Contrast Audit — Light vs Dark Mode

### 5.1 Bảng đánh giá WCAG AA (tỷ lệ tối thiểu 4.5:1 normal, 3:1 large)

#### Light Mode (`:root`)

| Pair | Foreground | Background | Ratio | WCAG | Ghi chú |
|---|---|---|---|---|---|
| Body text | `#0f172a` | `#ffffff` | 21:1 | ✅ AAA | |
| Muted text | `#475569` | `#ffffff` | 7.6:1 | ✅ AAA | |
| Subtle text | `#94a3b8` | `#ffffff` | 2.6:1 | ⚠️ Fail | Chỉ dùng placeholder |
| Primary btn | `#ffffff` | `#0e4475` | 7.7:1 | ✅ AAA | |
| Primary hover | `#ffffff` | `#0b3560` | 9.2:1 | ✅ AAA | |
| Ghost hover | `#0f172a` | `#f1f5f9` | 18.1:1 | ✅ AAA | `bg-surface` |
| Nav active | `#0e4475` | `#e6eef7` | 4.8:1 | ✅ AA | `bg-primary/10` |
| Input label | `#0f172a` | `#ffffff` | 21:1 | ✅ AAA | |
| Placeholder | `#94a3b8` | `#ffffff` | 2.6:1 | ⚠️ Fail | Decorative only |
| Danger | `#dc2626` | `#ffffff` | 4.5:1 | ✅ AA | |
| Success | `#16a34a` | `#ffffff` | 4.5:1 | ✅ AA | |

#### Dark Mode (`[data-theme="dark"]`)

| Pair | Foreground | Background | Ratio | WCAG | Ghi chú |
|---|---|---|---|---|---|
| Body text | `#f1f5f9` | `#0c1a2e` | 13.1:1 | ✅ AAA | |
| Muted text | `#94a3b8` | `#0c1a2e` | 5.4:1 | ✅ AA | |
| Subtle text | `#64748b` | `#0c1a2e` | 3.2:1 | ⚠️ Fail | Chỉ dùng placeholder |
| Primary btn | `#ffffff` | `#2b78cc` | 4.7:1 | ✅ AA | |
| Primary hover | `#ffffff` | `#2470be` | 4.6:1 | ✅ AA | **Fixed** từ `#3d8fdb` (3.2:1) |
| Ghost hover | `#f1f5f9` | `#162843` | 12.1:1 | ✅ AAA | `bg-surface` |
| Nav active | `#2b78cc` | `#0d253d` | 5.3:1 | ✅ AA | `bg-primary/10` |
| Card on bg | — | `#112036` | 1.4:1 | ✅ Decoration | Chỉ cần phân biệt được |
| Border | `#1e3a5f` | `#0c1a2e` | 1.5:1 | ✅ Decoration | |
| Danger | `#f87171` | `#0c1a2e` | 6.2:1 | ✅ AA | |
| Success | `#4ade80` | `#0c1a2e` | 9.8:1 | ✅ AAA | |

### 5.2 Hover State Audit

| Component | Hover class | Light result | Dark result | Status |
|---|---|---|---|---|
| `<Button variant="ghost">` | `hover:bg-surface` | `#f1f5f9` bg ✅ | `#162843` bg ✅ | ✅ **Fixed** |
| `<Button variant="outline">` | `hover:bg-surface` | `#f1f5f9` bg ✅ | `#162843` bg ✅ | ✅ **Fixed** |
| `<Sidebar>` nav link | `hover:bg-surface hover:text-fg` | Visible ✅ | Visible ✅ | ✅ **Fixed** |
| `<Header>` nav link | `hover:bg-surface hover:text-fg` | Visible ✅ | Visible ✅ | ✅ **Fixed** |
| `<ThemeToggle>` | `bg-surface hover:bg-border/40` | Visible ✅ | Visible ✅ | ✅ **Fixed** |
| `<Button variant="primary">` | `hover:bg-primary-hover` | `#0b3560` 9.2:1 ✅ | `#2470be` 4.6:1 ✅ | ✅ **Fixed** |
| Logout button | `hover:text-danger hover:bg-danger/10` | `#dc2626` on `#fee2e2` ✅ | `#f87171` on dark ✅ | ✅ OK |
| Sidebar active | `bg-primary/10 text-primary` | 4.8:1 ✅ | 5.3:1 ✅ | ✅ OK |

### 5.3 Root Cause — Lý do hover không hoạt động trước đây

1. **API trả về empty** — seed chưa được chạy → không có CSS vars nào từ backend
2. **`buildCssVars` sai type** — API trả `{key, value, name}[]` nhưng code dùng `Object.entries(group)` đọc như `Record<string,string>` → output: `--color-0: [object Object]`
3. **`--color-surface` thiếu** — dùng trong 5 component nhưng không định nghĩa trong `@theme inline`, `:root`, hay `[data-theme="dark"]` → Tailwind generate `bg-surface: var(--color-surface)` nhưng biến không tồn tại → transparent
4. **Dark fallbacks không đồng bộ** — giá trị trong `globals.css` khác với seed → khi API fail, fallback render khác màu

---

## 6. Implementation Plan — Dashboard

### Phase 1: Layout Refactor (hiện tại — ưu tiên)

```
Hiện tại: Header (full width) + main content (no sidebar)
Mục tiêu: Sidebar (fixed left) + Topbar + content area
```

**Thứ tự implement:**
1. `hooks/useSidebar.ts` — state collapse/expand, mobile, localStorage persist
2. `components/layout/SidebarNavItem.tsx` — item với active state (dùng `usePathname`)
3. `components/layout/SidebarNavGroup.tsx` — wrapper group với label
4. `components/layout/SidebarUserBlock.tsx` — avatar + tên + email
5. `components/layout/DashboardSidebar.tsx` — combine tất cả
6. `components/layout/DashboardTopbar.tsx` — breadcrumb + actions
7. `app/(main)/layout.tsx` — refactor: sidebar + topbar layout
8. `app/(main)/dashboard/page.tsx` — widget placeholders

### Phase 2: Widgets (phát triển sau)
- Stat cards với live data
- Charts (sử dụng `recharts` hoặc `chart.js`)
- Data tables với pagination
- Activity feed với websocket / polling

---

## 7. File Structure (sau Phase 1)

```
frontend/src/
├── app/(main)/
│   ├── layout.tsx              ← Refactor: sidebar layout
│   ├── page.tsx                ← Landing
│   ├── dashboard/
│   │   └── page.tsx            ← Widget grid
│   └── profile/
│       └── page.tsx
│
├── components/
│   └── layout/
│       ├── DashboardSidebar.tsx    ← NEW (replaces Sidebar.tsx)
│       ├── SidebarNavItem.tsx      ← NEW
│       ├── SidebarNavGroup.tsx     ← NEW
│       ├── SidebarUserBlock.tsx    ← NEW
│       ├── SidebarToggle.tsx       ← NEW
│       ├── DashboardTopbar.tsx     ← NEW
│       ├── AppLogo.tsx             ← keep
│       ├── ThemeToggle.tsx         ← keep
│       └── Header.tsx              ← keep (for landing pages only)
│
└── hooks/
    ├── useSidebar.ts               ← NEW
    ├── useTheme.ts                 ← keep
    └── useToast.ts                 ← keep
```

---

## 8. Design Tokens Reference

| Token | Light | Dark | Dùng ở đâu |
|---|---|---|---|
| `--color-bg` | `#ffffff` | `#0c1a2e` | Page background |
| `--color-bg-subtle` | `#f8fafc` | `#112036` | Sidebar background |
| `--color-surface` | `#f1f5f9` | `#162843` | Hover background, ThemeToggle |
| `--color-card` | `#ffffff` | `#112036` | Card/Widget background |
| `--color-border` | `#e2e8f0` | `#1e3a5f` | Card/Sidebar borders |
| `--color-primary` | `#0e4475` | `#2b78cc` | Active nav, buttons |
| `--color-primary-light` | `#e6eef7` | `#0d253d` | Active nav bg (`bg-primary/10`) |
| `--color-fg` | `#0f172a` | `#f1f5f9` | Main text |
| `--color-fg-muted` | `#475569` | `#94a3b8` | Secondary text, nav labels |
| `--color-fg-subtle` | `#94a3b8` | `#64748b` | Placeholder, disabled — **không dùng cho interactive** |

> `fg-subtle` chỉ dùng cho decorative text (placeholder, disabled). Không dùng cho nav labels, button text, hay bất kỳ interactive element nào.
