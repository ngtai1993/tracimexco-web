# Format Liệt Kê & Lọc Tính Năng

## Cách Trình Bày Danh Sách Tính Năng

Sau khi brainstorm, trình bày theo format này để người dùng dễ lựa chọn:

---

### Ví dụ: App Quản Lý Đơn Hàng

```
## Tính Năng Đề Xuất — Vui lòng đánh dấu: ✅ Giữ | 🔜 Sau | ❌ Bỏ

### 👤 Quản Lý Người Dùng
[ ] Đăng ký tài khoản bằng email
[ ] Đăng nhập / đăng xuất
[ ] Đăng nhập bằng Google / Facebook
[ ] Quên mật khẩu, đặt lại qua email
[ ] Xác thực 2 bước (2FA)
[ ] Quản lý thông tin cá nhân
[ ] Phân quyền: Admin / Nhân viên / Khách hàng

### 🛒 Quản Lý Đơn Hàng
[ ] Tạo đơn hàng mới
[ ] Xem danh sách đơn hàng
[ ] Xem chi tiết đơn hàng
[ ] Cập nhật trạng thái đơn hàng
[ ] Hủy đơn hàng
[ ] Hoàn tiền đơn hàng
[ ] Lịch sử thay đổi trạng thái
[ ] In hóa đơn / xuất PDF

### 📦 Quản Lý Sản Phẩm
[ ] Thêm / sửa / xóa sản phẩm
[ ] Phân loại theo danh mục
[ ] Quản lý tồn kho
[ ] Cảnh báo tồn kho thấp
[ ] Ảnh sản phẩm (upload nhiều ảnh)
[ ] Tìm kiếm và lọc sản phẩm

### 💳 Thanh Toán
[ ] Thanh toán COD (tiền mặt khi nhận)
[ ] Thanh toán qua VNPay
[ ] Thanh toán qua MoMo
[ ] Thanh toán qua thẻ ngân hàng
[ ] Lịch sử giao dịch
[ ] Hoàn tiền / refund

### 🔔 Thông Báo
[ ] Email xác nhận đơn hàng
[ ] Email khi trạng thái đơn thay đổi
[ ] Thông báo push (web/app)
[ ] SMS thông báo giao hàng

### 📊 Báo Cáo & Thống Kê
[ ] Doanh thu theo ngày / tháng / năm
[ ] Sản phẩm bán chạy
[ ] Khách hàng thân thiết
[ ] Xuất báo cáo Excel
[ ] Dashboard tổng quan

### ⚙️ Cài Đặt Hệ Thống
[ ] Cấu hình thông tin cửa hàng
[ ] Cấu hình phí vận chuyển
[ ] Quản lý mã giảm giá / voucher
[ ] Cài đặt email template
[ ] Nhật ký hoạt động (audit log)
```

---

## Hướng Dẫn Lọc Tính Năng

Sau khi người dùng lựa chọn, nhóm lại:

```
## Kết Quả Lọc

### ✅ MVP — Xây dựng ngay
- Đăng ký / đăng nhập bằng email
- Quản lý sản phẩm cơ bản (CRUD + tồn kho)
- Tạo và xem đơn hàng
- Cập nhật trạng thái đơn hàng
- Thanh toán COD
- Email xác nhận đơn hàng

### 🔜 Phase 2 — Sau khi MVP xong
- Đăng nhập Google
- Thanh toán VNPay / MoMo
- Báo cáo doanh thu
- Mã giảm giá

### ❌ Không làm
- Đăng nhập Facebook
- 2FA
- SMS thông báo
- Xuất báo cáo Excel
- Audit log
```

---

## Câu Hỏi Gợi Ý Để Lọc

Khi người dùng phân vân, hỏi:

1. **"Nếu thiếu tính năng này, app có dùng được không?"**
   - Có → đưa vào 🔜 hoặc ❌
   - Không → đưa vào ✅ MVP

2. **"Tính năng này phục vụ bao nhiêu % người dùng?"**
   - < 20% → cân nhắc 🔜

3. **"Tính năng này mất bao nhiêu công để làm?"**
   - Nếu phức tạp mà không cốt lõi → 🔜

4. **"Tính năng này có thể làm thủ công tạm thời không?"**
   - Có → 🔜 (ví dụ: báo cáo có thể xuất CSV thay vì dashboard đẹp)
