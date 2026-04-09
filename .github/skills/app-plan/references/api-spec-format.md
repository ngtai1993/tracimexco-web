# Format Kiến Trúc & Đặc Tả API

## 1. Format Kiến Trúc Hệ Thống

```
## Kiến Trúc Hệ Thống

### Django Apps
| App | Domain | Mô tả |
|-----|--------|-------|
| `users` | Người dùng | Đăng ký, đăng nhập, phân quyền |
| `products` | Sản phẩm | Quản lý sản phẩm, danh mục, tồn kho |
| `orders` | Đơn hàng | Tạo đơn, trạng thái, lịch sử |
| `payments` | Thanh toán | Ghi nhận giao dịch, hoàn tiền |
| `notifications` | Thông báo | Email, push notification |
| `core` | Dùng chung | BaseModel, utilities, permissions |

### Models Chính & Quan Hệ

User
├── có nhiều → Order (1 user có nhiều đơn hàng)
└── có nhiều → Address (1 user có nhiều địa chỉ)

Product
├── thuộc về → Category (nhiều-1)
├── có nhiều → ProductImage (1 sản phẩm, nhiều ảnh)
└── có 1 → Inventory (tồn kho)

Order
├── thuộc về → User (nhiều-1)
├── có nhiều → OrderItem (danh sách sản phẩm trong đơn)
├── có 1 → Payment (thông tin thanh toán)
└── có nhiều → OrderStatusHistory (lịch sử trạng thái)

OrderItem
├── thuộc về → Order (nhiều-1)
└── thuộc về → Product (nhiều-1)
```

---

## 2. Format Đặc Tả API Endpoint

Mỗi endpoint mô tả đầy đủ theo mẫu sau **(không viết code)**:

```
### [Tên tính năng]

**[METHOD] /api/v1/[resource]/[path]**

- **Mục đích:** Mô tả một câu endpoint này làm gì
- **Permission:** Ai được gọi (ví dụ: Đã đăng nhập | Chỉ Admin | Công khai)
- **Input:**
  - `field_name` (kiểu dữ liệu, bắt buộc/tuỳ chọn): Mô tả ý nghĩa
- **Output thành công:** Mô tả dữ liệu trả về, status code
- **Output lỗi:** Các trường hợp lỗi có thể xảy ra
- **Logic chính:**
  1. Bước 1 hệ thống làm gì
  2. Bước 2 hệ thống làm gì
  3. ...
```

---

## 3. Ví Dụ Đặc Tả Đầy Đủ

### Nhóm: Xác Thực (Authentication)

---

**POST /api/v1/auth/register/**

- **Mục đích:** Đăng ký tài khoản mới bằng email và mật khẩu
- **Permission:** Công khai (không cần đăng nhập)
- **Input:**
  - `email` (string, bắt buộc): Địa chỉ email — phải là email hợp lệ và chưa được dùng
  - `password` (string, bắt buộc): Mật khẩu — tối thiểu 8 ký tự, có chữ hoa và số
  - `full_name` (string, bắt buộc): Họ tên đầy đủ
- **Output thành công:** `201 Created` — thông tin user vừa tạo (không trả password), kèm access token
- **Output lỗi:**
  - `400` — email đã tồn tại
  - `400` — mật khẩu không đủ độ mạnh
  - `400` — thiếu trường bắt buộc
- **Logic chính:**
  1. Validate format email và độ mạnh password
  2. Kiểm tra email chưa được dùng trong hệ thống
  3. Hash mật khẩu trước khi lưu
  4. Tạo tài khoản với role mặc định là `customer`
  5. Gửi email xác thực đến địa chỉ đã nhập
  6. Trả về thông tin user và access token

---

**POST /api/v1/auth/login/**

- **Mục đích:** Đăng nhập bằng email và mật khẩu, nhận JWT token
- **Permission:** Công khai
- **Input:**
  - `email` (string, bắt buộc): Địa chỉ email
  - `password` (string, bắt buộc): Mật khẩu
- **Output thành công:** `200 OK` — `access_token`, `refresh_token`, thông tin user cơ bản
- **Output lỗi:**
  - `401` — sai email hoặc mật khẩu
  - `403` — tài khoản bị khóa hoặc chưa xác thực email
- **Logic chính:**
  1. Tìm user theo email
  2. Kiểm tra mật khẩu khớp
  3. Kiểm tra tài khoản đang active
  4. Tạo và trả về JWT access token + refresh token

---

### Nhóm: Đơn Hàng (Orders)

---

**GET /api/v1/orders/**

- **Mục đích:** Lấy danh sách đơn hàng của người dùng hiện tại
- **Permission:** Đã đăng nhập
- **Input (query params, tuỳ chọn):**
  - `status` (string): Lọc theo trạng thái — `pending`, `processing`, `shipped`, `delivered`, `cancelled`
  - `from_date` (date): Lọc từ ngày
  - `to_date` (date): Lọc đến ngày
  - `page` (int): Số trang, mặc định 1
  - `page_size` (int): Số item/trang, mặc định 20, tối đa 100
- **Output thành công:** `200 OK` — danh sách đơn hàng có phân trang, mỗi item gồm: mã đơn, ngày tạo, trạng thái, tổng tiền, số lượng sản phẩm
- **Output lỗi:**
  - `401` — chưa đăng nhập
- **Logic chính:**
  1. Lấy danh sách đơn hàng thuộc về user hiện tại
  2. Áp dụng filter nếu có query params
  3. Sắp xếp theo ngày tạo mới nhất
  4. Phân trang và trả về

---

**POST /api/v1/orders/**

- **Mục đích:** Tạo đơn hàng mới
- **Permission:** Đã đăng nhập
- **Input:**
  - `items` (array, bắt buộc): Danh sách sản phẩm
    - `product_id` (int, bắt buộc): ID sản phẩm
    - `quantity` (int, bắt buộc): Số lượng — tối thiểu 1
  - `shipping_address_id` (int, bắt buộc): ID địa chỉ giao hàng đã lưu
  - `payment_method` (string, bắt buộc): Phương thức thanh toán — `cod`, `vnpay`, `momo`
  - `note` (string, tuỳ chọn): Ghi chú cho đơn hàng
  - `voucher_code` (string, tuỳ chọn): Mã giảm giá
- **Output thành công:** `201 Created` — thông tin đơn hàng vừa tạo đầy đủ, kèm link thanh toán nếu dùng online payment
- **Output lỗi:**
  - `400` — sản phẩm không tồn tại hoặc đã ngừng bán
  - `400` — tồn kho không đủ
  - `400` — mã giảm giá không hợp lệ hoặc hết hạn
  - `400` — địa chỉ giao hàng không thuộc về user này
- **Logic chính:**
  1. Validate tất cả sản phẩm trong items còn active và đủ tồn kho
  2. Validate địa chỉ giao hàng thuộc về user hiện tại
  3. Validate voucher nếu có
  4. Tính tổng tiền: giá gốc + phí ship - giảm giá
  5. Tạo Order và các OrderItem trong một transaction
  6. Trừ tồn kho của từng sản phẩm (dùng select_for_update tránh race condition)
  7. Tạo Payment record với trạng thái `pending`
  8. Nếu COD: chuyển trạng thái order sang `confirmed`
  9. Nếu online payment: tạo payment URL và trả về để redirect
  10. Gửi email xác nhận đơn hàng

---

**PATCH /api/v1/orders/{id}/cancel/**

- **Mục đích:** Hủy đơn hàng — chỉ hủy được khi đơn đang ở trạng thái có thể hủy
- **Permission:** Đã đăng nhập + là chủ đơn hàng đó
- **Input:**
  - `reason` (string, tuỳ chọn): Lý do hủy đơn
- **Output thành công:** `200 OK` — thông tin đơn hàng sau khi hủy
- **Output lỗi:**
  - `403` — không phải đơn của user này
  - `404` — không tìm thấy đơn hàng
  - `409` — đơn đã giao, đã hủy, hoặc đang vận chuyển — không thể hủy
- **Logic chính:**
  1. Kiểm tra đơn hàng thuộc về user hiện tại
  2. Kiểm tra trạng thái cho phép hủy (`pending`, `confirmed`)
  3. Cập nhật trạng thái thành `cancelled`
  4. Hoàn lại tồn kho cho từng sản phẩm trong đơn
  5. Nếu đã thanh toán online: tạo yêu cầu hoàn tiền
  6. Ghi lý do hủy vào lịch sử trạng thái
  7. Gửi email thông báo hủy đơn

---

## 4. Bảng Tổng Hợp Endpoints

Sau khi đặc tả xong, tổng hợp thành bảng:

```
## Bảng Tổng Hợp API

| Method | Endpoint | Mục đích | Permission |
|--------|----------|----------|------------|
| POST | /api/v1/auth/register/ | Đăng ký tài khoản | Công khai |
| POST | /api/v1/auth/login/ | Đăng nhập | Công khai |
| POST | /api/v1/auth/logout/ | Đăng xuất | Đã đăng nhập |
| GET | /api/v1/auth/me/ | Thông tin user hiện tại | Đã đăng nhập |
| GET | /api/v1/products/ | Danh sách sản phẩm | Công khai |
| GET | /api/v1/products/{id}/ | Chi tiết sản phẩm | Công khai |
| POST | /api/v1/products/ | Tạo sản phẩm | Admin |
| PUT | /api/v1/products/{id}/ | Cập nhật sản phẩm | Admin |
| DELETE | /api/v1/products/{id}/ | Xóa sản phẩm | Admin |
| GET | /api/v1/orders/ | Danh sách đơn hàng | Đã đăng nhập |
| POST | /api/v1/orders/ | Tạo đơn hàng | Đã đăng nhập |
| GET | /api/v1/orders/{id}/ | Chi tiết đơn hàng | Đã đăng nhập + chủ đơn |
| PATCH | /api/v1/orders/{id}/cancel/ | Hủy đơn | Đã đăng nhập + chủ đơn |
| PATCH | /api/v1/orders/{id}/status/ | Cập nhật trạng thái | Admin / Nhân viên |
```
