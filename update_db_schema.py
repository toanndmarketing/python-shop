import sqlite3

DB_NAME = "sports_shop.db" # Đảm bảo đây là tên tệp DB chính xác của bạn

def add_columns_to_orders_table():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Kiểm tra xem cột 'recipient_name' đã tồn tại chưa
        cursor.execute("PRAGMA table_info(orders)")
        columns = [info[1] for info in cursor.fetchall()]

        if 'recipient_name' not in columns:
            print("Đang thêm cột 'recipient_name' vào bảng 'orders'...")
            cursor.execute("ALTER TABLE orders ADD COLUMN recipient_name TEXT") # TEXT tương đương String, nullable mặc định
            print("Đã thêm cột 'recipient_name'.")
        else:
            print("Cột 'recipient_name' đã tồn tại trong bảng 'orders'.")

        if 'notes' not in columns:
            print("Đang thêm cột 'notes' vào bảng 'orders'...")
            cursor.execute("ALTER TABLE orders ADD COLUMN notes TEXT") # TEXT tương đương String, nullable mặc định
            print("Đã thêm cột 'notes'.")
        else:
            print("Cột 'notes' đã tồn tại trong bảng 'orders'.")

        conn.commit()
        print("Cập nhật schema cơ sở dữ liệu thành công!")

    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_columns_to_orders_table() 