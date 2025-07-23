# 🍎 E-commerce API (Django + DRF)

Hệ thống **Backend cho website thương mại điện tử**, xây dựng bằng **Django REST Framework**, hỗ trợ đầy đủ các chức năng: người dùng, sản phẩm, đơn hàng, xác thực, lưu trữ ảnh, API docs,...

---

## 🚀 Công nghệ sử dụng

| Công nghệ             | Mục đích                       |
| --------------------- | ------------------------------ |
| Django                | Backend framework chính        |
| Django REST Framework | Xây dựng RESTful API           |
| Simple JWT            | Xác thực người dùng với JWT    |
| PostgreSQL            | Cơ sở dữ liệu chính            |
| Redis                 | Lưu cache hoặc notification    |
| Cloudinary            | Lưu trữ ảnh sản phẩm           |
| drf-spectacular       | Tạo tài liệu Swagger tự động   |
| python-decouple       | Quản lý cấu hình với `.env`    |
| Docker + Compose      | Đóng gói & triển khai ứng dụng |

---

## 📂 Cấu trúc thư mục

```
E-commerce-API/
├── apps/
│   ├── users/        # Đăng ký, đăng nhập, hồ sơ, địa chỉ
│   ├── products/     # Danh mục & sản phẩm
│   └── orders/       # Đơn hàng & mục trong đơn
├── config/           # Cấu hình Django (settings, urls, wsgi,...)
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.dev
└── README.md
```

---

## ✅ Tính năng chính

### 🔐 Authentication

* Đăng ký / đăng nhập bằng email
* Đăng xuất và cập nhật `last_login`
* Quên mật khẩu qua OTP gửi email
* Đổi mật khẩu
* JWT Token xác thực

### 🤵‍♂️ Users

* Xem và cập nhật thông tin cá nhân
* Danh sách địa chỉ giao hàng (mỗi user có nhiều địa chỉ)
* Phân quyền user và admin

### 📦 Products

* CRUD sản phẩm và danh mục
* Upload ảnh sản phẩm lên Cloudinary
* Sắp xếp, phân trang

### 📬 Orders

* Tạo đơn hàng với nhiều sản phẩm
* Tự động trừ kho khi đặt hàng
* Tính tổng tiền đơn hàng
* Cập nhật trạng thái đơn hàng:

  * Admin: Confirmed, Shipped, Delivered
  * User: Canceled, Returned
* Hủy đơn hàng khi trạng thái vẫn là PENDING
* Gửi notification sau khi tạo đơn

---

## 📣 Chạy với Docker

```bash
docker compose --env-file .env.dev up --build
```

Truy cập: [http://localhost:8000/](http://localhost:8000/)

---

## 📘 Tài liệu API

* Swagger UI:

```bash
http://localhost:8000/api/v1/schema/swagger-ui/
```

---

## ⚙️ Cài đặt thủ công (không dùng Docker)

```bash
# Clone project
git clone https://github.com/your-username/e-commerce-api.git
cd e-commerce-api

# Tạo virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env.dev
touch .env.dev

# Migrate
python manage.py migrate

# Chạy server
APP_ENV=dev python manage.py runserver
```
