# Test Accounts

> Chỉ dùng cho môi trường **development/staging**. Không commit vào production.

## Danh sách tài khoản

| Email | Password | Role | full_name |
|---|---|---|---|
| `admin@tracimexco.com` | `Admin@123456` | Superuser / Staff | Admin User |
| `manager@tracimexco.com` | `Manager@123456` | Regular user | Nguyen Manager |
| `user1@tracimexco.com` | `User1@123456` | Regular user | Tran User1 |
| `user2@tracimexco.com` | `User2@123456` | Regular user | Le User2 |
| `test@tracimexco.com` | `Test@123456` | Regular user | Test Account |

## Ghi chú

- Tất cả tài khoản được tạo bằng `create_user()` — email verified mặc định theo model.
- Tài khoản `admin@tracimexco.com` có quyền `is_staff=True`, `is_superuser=True` → truy cập được `/admin/`.
- Tạo lại bằng script: `backend/create_test_users.py` (xoá file sau khi dùng xong ở production).

## Tướng dẫn tạo lại

```bash
# Từ thư mục gốc project
Get-Content backend\create_test_users.py | docker exec -i tracimexco-web-web-1 python manage.py shell
```
