from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models.product import Category, Product
from app.models.user import User # Import User model
from app.core.security import get_password_hash # Import password hashing utility

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def init_db(db: Session):
    # Check if data already exists to prevent duplicates
    if db.query(Category).first():
        print("Database already has category data. Skipping initialization.")
    else:
        # Create categories
        categories_data = [
            {"name": "Quần Áo Bóng Đá", "description": "Áo đấu, quần, vớ cho bóng đá"},
            {"name": "Giày Chạy Bộ", "description": "Giày chuyên dụng cho chạy bộ các cự ly"},
            {"name": "Vợt Tennis", "description": "Các loại vợt tennis cho mọi cấp độ"},
            {"name": "Đồ Bơi Lội", "description": "Quần áo bơi, kính bơi, mũ bơi"},
            {"name": "Dụng Cụ Tập Gym", "description": "Tạ, thảm tập, dây kháng lực"}
        ]
        
        categories_db = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
            categories_db.append(category)
        db.commit()
        print("Categories created.")

        # Create products
        products_data = [
            # Quần Áo Bóng Đá
            {"name": "Áo Đấu Real Madrid 2024", "description": "Áo đấu sân nhà chính hãng Real Madrid mùa giải 2024.", "price": 1800000, "stock": 50, "category_name": "Quần Áo Bóng Đá", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Ao+Real+2024"},
            {"name": "Quần Short Tập Luyện Nike", "description": "Quần short nhẹ, thoáng khí cho tập luyện.", "price": 750000, "stock": 100, "category_name": "Quần Áo Bóng Đá", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Quan+Nike"},
            
            # Giày Chạy Bộ
            {"name": "Giày Nike Pegasus 40", "description": "Phiên bản mới nhất của dòng giày chạy bộ Pegasus.", "price": 3200000, "stock": 30, "category_name": "Giày Chạy Bộ", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Pegasus+40"},
            {"name": "Giày Adidas Adizero Boston 12", "description": "Giày chạy tốc độ, nhẹ và linh hoạt.", "price": 3500000, "stock": 25, "category_name": "Giày Chạy Bộ", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Adizero+Boston"},

            # Vợt Tennis
            {"name": "Vợt Babolat Pure Drive", "description": "Vợt mạnh mẽ, phổ biến cho người chơi phong trào.", "price": 4500000, "stock": 15, "category_name": "Vợt Tennis", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Pure+Drive"},
            {"name": "Vợt Wilson Blade 98", "description": "Vợt kiểm soát tốt, dành cho người chơi có kỹ thuật.", "price": 4800000, "stock": 10, "category_name": "Vợt Tennis", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Wilson+Blade"},

            # Đồ Bơi Lội
            {"name": "Quần Bơi Speedo Endurance+", "description": "Quần bơi nam chất liệu bền bỉ.", "price": 900000, "stock": 40, "category_name": "Đồ Bơi Lội", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Quan+Boi+Speedo"},
            {"name": "Kính Bơi Arena Cobra Ultra", "description": "Kính bơi thi đấu, tầm nhìn rộng.", "price": 1200000, "stock": 20, "category_name": "Đồ Bơi Lội", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Kinh+Boi+Arena"},

            # Dụng Cụ Tập Gym
            {"name": "Tạ Tay Dumbbell 5kg (Cặp)", "description": "Tạ tay bọc cao su, trọng lượng 5kg mỗi quả.", "price": 500000, "stock": 50, "category_name": "Dụng Cụ Tập Gym", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Ta+Tay+5kg"},
            {"name": "Thảm Tập Yoga TPE 6mm", "description": "Thảm tập yoga chống trượt, dày 6mm.", "price": 350000, "stock": 60, "category_name": "Dụng Cụ Tập Gym", "image_url": "https://placehold.co/600x400/E8E8E8/AAAAAA?text=Tham+Yoga"}
        ]

        for prod_data in products_data:
            category_name = prod_data.pop("category_name")
            category = db.query(Category).filter(Category.name == category_name).first()
            if category:
                product = Product(**prod_data, category_id=category.id)
                db.add(product)
            else:
                print(f"Category {category_name} not found for product {prod_data['name']}")
        db.commit()
        print("Products created.")

    # Check if admin user already exists
    if db.query(User).filter(User.username == "admin").first():
        print("Admin user already exists. Skipping admin creation.")
    else:
        # Create a default admin user
        admin_user = User(
            email="admin@sportsshop.com",
            username="admin",
            hashed_password=get_password_hash("adminpass"), # PLEASE CHANGE THIS PASSWORD!
            full_name="Admin User",
            is_active=True,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("Default admin user created (username: admin, password: adminpass)")

if __name__ == "__main__":
    print("Initializing database with demo data...")
    db = SessionLocal()
    try:
        init_db(db)
        print("Database initialization complete.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
    finally:
        db.close() 