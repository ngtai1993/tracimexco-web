---
name: app-plan
description: 'Lập kế hoạch tạo app mới từ ý tưởng: liệt kê tính năng, kiến trúc, API, luồng hoạt động, và thiết kế UX/UI frontend. Use when: lên kế hoạch app, plan app, thiết kế tính năng, app idea, liệt kê tính năng, phân tích API, thiết kế hệ thống, lên kế hoạch dự án, brainstorm app, thiết kế UX, thiết kế UI, luồng người dùng, user flow, màn hình, page, component nào cần tạo, frontend plan.'
argument-hint: 'Mô tả ngắn về app bạn muốn xây dựng (vd: hệ thống quản lý đơn hàng)'
---

# App Plan — Lập Kế Hoạch App Mới Từ Ý Tưởng

Skill này giúp chuyển một ý tưởng thô thành một bản kế hoạch kỹ thuật đầy đủ: danh sách tính năng, kiến trúc hệ thống, luồng hoạt động, đặc tả API, và **thiết kế UX/UI frontend** — **không viết code**, chỉ phân tích và mô tả.

## Khi Nào Dùng
- Có ý tưởng về app/tính năng mới và muốn lên kế hoạch trước khi code
- Muốn liệt kê tất cả tính năng có thể có rồi chọn lọc lại
- Cần phân tích rõ các API endpoint trước khi bắt đầu implement
- Muốn xác định MVP (phiên bản tối thiểu) so với full features
- Muốn thiết kế luồng UX và các màn hình frontend cần xây dựng

---

## Quy Trình 6 Bước

### Bước 1 — Thu Thập Ý Tưởng

Hỏi người dùng để hiểu rõ app:
- App này giải quyết vấn đề gì?
- Ai là người dùng chính (admin, khách hàng, nhân viên...)?
- Dùng trên nền tảng nào (web, mobile API, cả hai)?
- Có tích hợp với hệ thống nào khác không?

### Bước 2 — Liệt Kê Toàn Bộ Tính Năng (Brainstorm)

Liệt kê **tất cả** tính năng có thể có, chia theo nhóm chức năng. Không lọc ở bước này — mục tiêu là bao quát tối đa.

Xem format tại [references/feature-checklist.md](./references/feature-checklist.md)

### Bước 3 — Người Dùng Lọc & Chọn Tính Năng

Trình bày danh sách tính năng theo dạng có thể lựa chọn. Người dùng đánh dấu:
- ✅ **Giữ** — cần thiết cho MVP
- 🔜 **Sau** — muốn nhưng chưa cần ngay
- ❌ **Bỏ** — không cần

**Chỉ tiếp tục sang bước 4 sau khi người dùng đã xác nhận danh sách tính năng cuối.**

### Bước 4 — Thiết Kế Kiến Trúc & Luồng Hoạt Động

Dựa trên tính năng đã chọn, mô tả:
1. **Các Django app cần tạo** (mỗi app ứng với một domain)
2. **Các model chính** và quan hệ giữa chúng
3. **Luồng hoạt động** của các tính năng cốt lõi

Xem format tại [references/api-spec-format.md](./references/api-spec-format.md)

### Bước 5 — Đặc Tả API Endpoints

Mô tả **từng API endpoint** cần xây dựng theo format chuẩn. Không viết code — chỉ mô tả rõ:
- Method + URL
- Mục đích
- Input cần gì
- Output trả về gì
- Ai được phép gọi (permission)
- Logic xử lý chính là gì

### Bước 6 — Thiết Kế UX/UI Frontend

Dựa trên tính năng đã chọn và API đã đặc tả, mô tả frontend cần xây dựng:

#### 6.1 — Danh Sách Màn Hình (Pages/Routes)

Liệt kê từng route cần có:
```
Route       | Mô tả                      | Ai truy cập được
/login      | Trang đăng nhập            | Khách
/register   | Trang đăng ký              | Khách
/dashboard  | Trang tổng quan            | User đã đăng nhập
/profile    | Trang hồ sơ cá nhân        | User đã đăng nhập
/admin/...  | Trang quản trị             | Admin
```

#### 6.2 — Luồng Người Dùng (User Flows)

Mô tả hành trình người dùng qua từng tính năng chính:
```
Đăng nhập:
  Vào /login → Nhập email+password → Submit → Lưu token → Redirect /dashboard
  Sai password → Hiện lỗi trên form
  Đã đăng nhập → Redirect /dashboard

Quản lý X:
  Vào /admin/x → Thấy bảng danh sách → Nhấn "Thêm" → Mở form → Submit → Cập nhật bảng
  Nhấn "Sửa" → Mở form có sẵn dữ liệu → Submit → Cập nhật
  Nhấn "Xóa" → Hiện confirm dialog → Xác nhận → Xóa khỏi danh sách
```

#### 6.3 — Shared UI Components Cần Tạo

Dựa trên các màn hình, xác định components tái sử dụng:
```
Component   | Dùng ở đâu
Button      | Mọi nơi — variants: primary/ghost/danger/outline
Input       | Tất cả form
Avatar      | Header, profile, danh sách user
Badge       | Status, role, label
Modal       | Confirm xóa, xem chi tiết, form popup
Table       | Danh sách admin
```

#### 6.4 — Features Frontend Cần Tạo

Tổ chức theo feature-based folder structure (từ react-scalable skill):
```
features/
├── auth/       → LoginForm, RegisterForm, useLogin, useRegister, useCurrentUser
├── profile/    → ProfileForm, ChangePasswordForm, useProfile
└── admin/
    └── users/  → UserTable, EditUserForm, useAdminUsers
```

#### 6.5 — UX Considerations

Cho từng tính năng chính, mô tả:
- **Loading state**: Hiện spinner/skeleton khi đang fetch
- **Empty state**: Hiện gì khi danh sách trống
- **Error state**: Hiện lỗi API ở đâu (trên form field, toast, hay alert)
- **Success feedback**: Thông báo khi thao tác thành công
- **Optimistic update**: Cập nhật UI ngay trước khi API respond (nếu áp dụng)
- **Form validation**: Client-side (Zod) và server-side error mapping

Tham khảo thêm: [react-scalable skill](../react-scalable/SKILL.md)

---

## Output Cuối Cùng

Sau khi hoàn thành, bản kế hoạch bao gồm:

```
📋 Tên App — Bản Kế Hoạch

1. Tổng Quan
   - Mục đích app
   - Người dùng hệ thống
   - Nền tảng

2. Danh Sách Tính Năng (đã lọc)
   - Nhóm A: [tên nhóm]
     ✅ Tính năng 1
     ✅ Tính năng 2
     🔜 Tính năng 3 (sau)

3. Kiến Trúc Hệ Thống
   - Danh sách Django apps
   - Models và quan hệ
   - Luồng hoạt động chính

4. Đặc Tả API
   - Danh sách endpoints theo nhóm
   - Mỗi endpoint: method, url, mục đích, input, output, permission

5. Thiết Kế UX/UI Frontend
   - Danh sách routes/pages
   - User flows cho tính năng chính
   - Shared UI components cần tạo
   - Features folder structure
   - UX considerations (loading/empty/error states)
```
     🔜 Tính năng 3 (sau)

3. Kiến Trúc Hệ Thống
   - Danh sách Django apps
   - Models và quan hệ
   - Luồng hoạt động chính

4. Đặc Tả API
   - Danh sách endpoints theo nhóm
   - Mỗi endpoint: method, url, mục đích, input, output, permission
```

---

## Nguyên Tắc Khi Lập Kế Hoạch

- **Không vội code** — hiểu rõ toàn bộ trước khi bắt đầu bất kỳ dòng code nào
- **Liệt kê tối đa, lọc có chủ đích** — brainstorm rộng rồi mới thu hẹp
- **Mỗi app = một domain** — đừng nhồi nhiều domain vào một app
- **Mỗi API = một mục đích duy nhất** — đừng làm một endpoint làm nhiều việc
- **Nghĩ đến permission ngay từ đầu** — ai được làm gì là quyết định kiến trúc, không phải afterthought
- **Mỗi tính năng = một user flow** — luôn mô tả hành trình người dùng từ đầu đến cuối
- **UX trước, UI sau** — xác định luồng và trạng thái trước khi nghĩ đến giao diện cụ thể
- **Reuse components** — nhận biết sớm components nào dùng nhiều nơi để tách ra shared
