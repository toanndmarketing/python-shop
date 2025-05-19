# Python Shop - Dự Án Thương Mại Điện Tử

Một ứng dụng web thương mại điện tử được xây dựng bằng FastAPI, SQLAlchemy và Jinja2, bao gồm cả giao diện người dùng và trang quản trị viên đầy đủ chức năng.

## Tổng Quan

Dự án này mô phỏng một cửa hàng trực tuyến, cho phép người dùng duyệt sản phẩm, đặt hàng và quản lý tài khoản. Trang quản trị cung cấp các công cụ để quản lý sản phẩm, đơn hàng, khách hàng và theo dõi hoạt động của quản trị viên.

## Tính Năng Chính

### Giao Diện Người Dùng (User-Facing)
*   Đăng ký, đăng nhập, quản lý tài khoản người dùng.
*   Xem danh sách sản phẩm, chi tiết sản phẩm.
*   Tìm kiếm và lọc sản phẩm.
*   Quản lý giỏ hàng.
*   Quy trình thanh toán và đặt hàng.
*   Xem lịch sử đơn hàng.

### Trang Quản Trị (Admin Panel - `/admin`)
*   **Đăng nhập/Đăng xuất Admin:** Giao diện đăng nhập riêng cho quản trị viên.
*   **Bảng Điều Khiển (Dashboard):**
    *   Thống kê nhanh: Tổng sản phẩm, tổng đơn hàng, tổng khách hàng.
    *   Hiển thị 10 hoạt động gần nhất của quản trị viên.
*   **Quản Lý Sản Phẩm (CRUD):**
    *   Xem danh sách sản phẩm (ID, Ảnh, Tên, Danh mục, Giá, Tồn kho).
    *   Thêm sản phẩm mới: Form chi tiết (Tên, Mô tả, Giá, Tồn kho, Danh mục, Tải ảnh lên hoặc URL ảnh).
    *   Sửa thông tin sản phẩm: Pre-fill form, quản lý ảnh hiện tại.
    *   Xóa sản phẩm (có xác nhận, xóa cả file ảnh nếu là ảnh tải lên).
*   **Quản Lý Đơn Hàng:**
    *   Xem danh sách đơn hàng (Mã ĐH, Khách hàng, Ngày đặt, Tổng tiền, Trạng thái).
    *   Xem chi tiết đơn hàng: Thông tin chung, thông tin khách hàng, địa chỉ giao hàng, danh sách sản phẩm trong đơn (kèm ảnh), tổng tiền.
    *   Cập nhật trạng thái đơn hàng (ví dụ: Đang chờ xử lý, Đang giao, Đã giao, Đã hủy).
*   **Quản Lý Khách Hàng:**
    *   Xem danh sách khách hàng (ID, Tên đăng nhập, Email, Họ tên, Điện thoại, Ngày tạo, Trạng thái).
    *   Kích hoạt/Vô hiệu hóa tài khoản khách hàng.
*   **Theo Dõi Hoạt Động Admin:**
    *   Tự động ghi lại các hành động quan trọng của quản trị viên (đăng nhập, thêm/sửa/xóa sản phẩm, cập nhật đơn hàng, thay đổi trạng thái khách hàng) vào database.

## Công Nghệ Sử Dụng
*   **Backend:** Python, FastAPI
*   **Database:** SQLAlchemy (với SQLite cho môi trường phát triển)
*   **Frontend (Templates):** Jinja2, HTML, CSS, (một chút) JavaScript
*   **Server:** Uvicorn

## Cấu Trúc Thư Mục Dự Án

```
python-shop/
├── .git/                     # Thư mục Git
├── .gitignore                # Các file và thư mục được Git bỏ qua
├── app/                      # Thư mục chính chứa mã nguồn ứng dụng
│   ├── __init__.py
│   ├── main.py               # Điểm khởi động chính của FastAPI
│   ├── database.py           # Thiết lập kết nối và session database
│   ├── models/               # Định nghĩa các SQLAlchemy models (ORM)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── admin_activity_log.py
│   ├── routers/              # Xử lý các route (endpoints)
│   │   ├── __init__.py       # (Nên có, trống hoặc import các router con)
│   │   ├── auth.py           # Routes xác thực người dùng
│   │   ├── product.py        # Routes sản phẩm cho người dùng
│   │   ├── order.py          # Routes đơn hàng cho người dùng
│   │   ├── pages_router.py   # Routes cho các trang tĩnh/thông tin chung
│   │   └── admin/            # Routers cho phần quản trị
│   │       ├── __init__.py
│   │       ├── auth.py       # Admin authentication
│   │       ├── dashboard.py
│   │       ├── products.py
│   │       ├── orders.py
│   │       └── customers.py
│   ├── schemas/              # Pydantic schemas (data validation & serialization)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── token.py
│   ├── services/             # (Có thể chứa business logic, nếu tách ra)
│   │   └── ...
│   ├── core/                 # Cấu hình, cài đặt cốt lõi (ví dụ: security)
│   │   └── security.py
│   ├── static/               # Chứa các file tĩnh
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │       └── products/     # Ảnh sản phẩm tải lên
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html         # Template cơ sở cho người dùng
│       ├── home.html
│       ├── login.html        # Login người dùng
│       ├── register.html
│       ├── products.html     # Danh sách sản phẩm người dùng
│       ├── ...               # Các template khác của người dùng
│       └── admin/            # Templates cho trang quản trị
│           ├── layout.html   # Layout chung cho trang admin
│           ├── login.html    # Login admin
│           ├── dashboard.html
│           ├── products.html
│           ├── product_form.html
│           ├── orders.html
│           ├── order_detail.html
│           └── customers.html
├── venv/                     # Thư mục môi trường ảo (được .gitignore bỏ qua)
├── requirements.txt          # Danh sách các thư viện Python cần thiết
├── sports_shop.db            # File database SQLite (có thể ignore nếu chỉ cho local dev)
├── init_db.py                # Script khởi tạo dữ liệu ban đầu (nếu có)
├── update_db_schema.py       # Script tùy chỉnh cập nhật schema (nếu có)
└── README.md                 # Chính là file này
```

## Hướng Dẫn Cài Đặt và Chạy Dự Án

### Yêu Cầu Hệ Thống
*   Python 3.8+
*   pip (Python package installer)
*   Git

### Các Bước Cài Đặt

1.  **Clone Repository:**
    ```bash
    git clone git@github.com:toanndmarketing/python-shop.git
    cd python-shop
    ```

2.  **Tạo và Kích Hoạt Môi Trường Ảo:**
    *   Khuyến khích sử dụng môi trường ảo để quản lý các gói phụ thuộc.
    ```bash
    python -m venv venv
    ```
    *   Kích hoạt môi trường ảo:
        *   Trên Windows (Powershell):
            ```powershell
            .\venv\Scripts\Activate.ps1
            ```
            (Nếu gặp lỗi về execution policy, chạy `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` rồi thử lại)
        *   Trên macOS/Linux (bash/zsh):
            ```bash
            source venv/bin/activate
            ```

3.  **Cài Đặt Các Gói Phụ Thuộc:**
    *   Đảm bảo môi trường ảo đã được kích hoạt.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Khởi Tạo Database (Nếu là lần chạy đầu tiên):**
    *   Ứng dụng sẽ tự động tạo các bảng trong database dựa trên models khi khởi chạy lần đầu tiên (do `models.<model_name>.Base.metadata.create_all(bind=engine)` trong `app/main.py`).
    *   Nếu bạn có một script `init_db.py` để thêm dữ liệu mẫu hoặc thực hiện các thiết lập ban đầu khác, hãy chạy nó:
        ```bash
        python init_db.py 
        ```
        (Lưu ý: Kiểm tra nội dung của `init_db.py` để biết nó làm gì.)

### Chạy Ứng Dụng

1.  **Khởi Động Server Phát Triển:**
    *   Đảm bảo môi trường ảo đã được kích hoạt và bạn đang ở thư mục gốc của dự án (`python-shop`).
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `--reload`: Tự động tải lại server khi có thay đổi trong mã nguồn.
    *   `--host 0.0.0.0`: Cho phép truy cập từ các thiết bị khác trong cùng mạng.
    *   `--port 8000`: Chạy ứng dụng trên cổng 8000.

2.  **Truy Cập Ứng Dụng:**
    *   **Từ máy tính đang chạy server:**
        *   Giao diện người dùng: `http://localhost:8000`
        *   Trang quản trị: `http://localhost:8000/admin`
    *   **Từ các thiết bị khác trong cùng mạng nội bộ (ví dụ: điện thoại, máy tính bảng):**
        1.  **Tìm địa chỉ IP nội bộ của máy chủ:**
            *   Trên máy tính đang chạy server, mở Command Prompt hoặc PowerShell và gõ lệnh:
                ```powershell
                ipconfig
                ```
            *   Tìm dòng "IPv4 Address" trong phần mô tả card mạng đang kết nối (ví dụ: "Wireless LAN adapter Wi-Fi" hoặc "Ethernet adapter Ethernet"). Địa chỉ IP sẽ có dạng như `192.168.1.X` hoặc `10.0.0.X`.
        2.  **Truy cập từ thiết bị khác:**
            *   Đảm bảo thiết bị của bạn (ví dụ: điện thoại) kết nối vào **cùng một mạng Wi-Fi/LAN** với máy chủ.
            *   Mở trình duyệt web trên thiết bị đó và nhập: `http://<ĐỊA_CHỈ_IP_NỘI_BỘ_MÁY_CHỦ>:8000`
                *   Ví dụ: Nếu IP máy chủ là `192.168.1.105`, bạn sẽ nhập `http://192.168.1.105:8000`.
            *   Trang quản trị: `http://<ĐỊA_CHỈ_IP_NỘI_BỘ_MÁY_CHỦ>:8000/admin`
        3.  **Lưu ý về Tường lửa (Firewall):**
            *   Nếu bạn không thể truy cập, tường lửa trên máy tính chạy server có thể đang chặn kết nối.
            *   Bạn có thể cần tạo một quy tắc trong Windows Firewall (hoặc phần mềm tường lửa khác) để cho phép kết nối đến cổng `8000` (hoặc cổng bạn đã chọn) cho ứng dụng Python/Uvicorn. Thông thường, Windows sẽ hỏi khi ứng dụng bắt đầu lắng nghe; hãy chọn cho phép truy cập.

3.  **Tài Liệu API (Swagger & ReDoc):**
    *   FastAPI tự động tạo tài liệu API tương tác.
    *   **Swagger UI:** `http://localhost:8000/docs`
    *   **ReDoc:** `http://localhost:8000/redoc`

## Lưu Ý
*   File `sports_shop.db` là file database SQLite. Nếu bạn muốn reset database, có thể xóa file này (ứng dụng sẽ tự tạo lại file rỗng khi chạy).
*   Để quản lý schema database một cách chuyên nghiệp hơn trong môi trường production, hãy cân nhắc sử dụng các công cụ migration như Alembic.

## Đóng Góp
Mọi ý kiến đóng góp và pull request đều được chào đón! Vui lòng tạo issue để thảo luận về các thay đổi lớn trước. 