# Sports Shop

Ứng dụng web bán đồ thể thao được xây dựng bằng FastAPI và SQLite.

## Tính năng

- Đăng ký và đăng nhập người dùng
- Xem danh sách sản phẩm
- Tìm kiếm và lọc sản phẩm theo danh mục
- Thêm sản phẩm vào giỏ hàng
- Quản lý đơn hàng
- Giao diện responsive với Bootstrap 5

## Yêu cầu hệ thống

- Python 3.8+
- pip (Python package manager)

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd sports-shop
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
```

3. Kích hoạt môi trường ảo:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

1. Khởi động server:
```bash
uvicorn app.main:app --reload
```

2. Truy cập ứng dụng tại địa chỉ: http://localhost:8000

## Cấu trúc dự án

```
app/
├── main.py                   # Điểm khởi động ứng dụng
├── models.py                 # SQLAlchemy models
├── schemas.py                # Pydantic schemas
├── database.py              # Kết nối DB
├── auth.py                  # Xác thực người dùng
├── routes/                  # Các router chia theo chức năng
│   ├── user_routes.py
│   ├── product_routes.py
│   └── order_routes.py
├── templates/               # Jinja2 HTML
│   ├── base.html
│   ├── home.html
│   └── ...
└── static/                  # Bootstrap, ảnh, css/js
    ├── css/
    └── js/
```

## API Documentation

Sau khi chạy ứng dụng, bạn có thể truy cập API documentation tại:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request để đóng góp.

## Giấy phép

MIT License 