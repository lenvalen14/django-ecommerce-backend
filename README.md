# 🛒 E-commerce API (Django + DRF)

Đây là hệ thống backend cho một trang web thương mại điện tử, được xây dựng bằng **Django Rest Framework**, hỗ trợ:

- Quản lý người dùng & xác thực bằng JWT
- Danh mục và sản phẩm
- Đơn hàng và các mục trong đơn
- Tích hợp Cloudinary để lưu trữ ảnh sản phẩm
- Tài liệu API với Swagger (drf-spectacular)

---

## 🚀 Công nghệ sử dụng

| Công nghệ           | Mục đích                         |
|---------------------|----------------------------------|
| Django              | Backend framework chính          |
| Django REST Framework | API RESTful                     |
| Simple JWT          | Xác thực người dùng              |
| PostgreSQL          | Cơ sở dữ liệu chính              |
| Cloudinary          | Lưu trữ ảnh                      |
| drf-spectacular     | Tự động tạo Swagger/OpenAPI Docs |
| decouple            | Quản lý cấu hình .env            |

---

## 🗂️ Cấu trúc chính


---

## ✅ Các chức năng chính

### 🔐 Authentication
- Đăng ký (Register)
- Đăng nhập (Login, JWT)
- Cập nhật `last_login` sau khi login
- Xác thực qua email/password

### 🧍‍♂️ Users
- Profile người dùng
- Phân quyền qua custom backend (`EmailAuthBackend`)

### 📦 Products
- CRUD sản phẩm
- Danh mục
- Ảnh sản phẩm dùng Cloudinary

### 📬 Orders
- Tạo đơn hàng kèm danh sách sản phẩm
- Tự động trừ kho khi tạo đơn
- Tính tổng tiền đơn hàng
- Trạng thái đơn hàng (Pending, Confirmed,...)

---

## 📦 Cài đặt

```bash
# Clone repo
git clone https://github.com/your-username/e-commerce-api.git
cd e-commerce-api

# Tạo môi trường ảo
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# Cài gói
pip install -r requirements.txt

# Tạo file .env.dev từ .env.example
cp .env.example .env.dev

# Migrate
python manage.py migrate

# Chạy server
APP_ENV=dev python manage.py runserver

```
---
## Các chức năng chính

### 🔐 Authentication
- Đăng ký (Register)
- Đăng nhập bằng email (Login, JWT)

### 🧍‍♂️ Users
- Profile người dùng
- Địa chỉ người dùng
- Phân quyền

### 📦 Products
- CRUD sản phẩm
- Danh mục
- Ảnh sản phẩm dùng Cloudinary

### 📬 Orders
- Tạo đơn hàng kèm danh sách sản phẩm
- Tự động trừ kho khi tạo đơn
- Tính tổng tiền đơn hàng
- Trạng thái đơn hàng (Pending, Confirmed,...)

---
### 📘 Tài liệu API
Sau khi chạy server, truy cập:

```bash
http://localhost:8000/api/schema/swagger-ui/
```

