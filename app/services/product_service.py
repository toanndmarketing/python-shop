from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.product import Product, Category
from ..schemas.product import ProductCreate, ProductUpdate, ProductList

def get_product(db: Session, id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == id).first()

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
) -> ProductList:
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search),
                Product.description.ilike(search)
            )
        )
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return ProductList(
        items=products,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

def create_product(db: Session, obj_in: ProductCreate) -> Product:
    db_obj = Product(
        name=obj_in.name,
        description=obj_in.description,
        price=obj_in.price,
        stock=obj_in.stock,
        category_id=obj_in.category_id,
        image_url=obj_in.image_url,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_product(db: Session, db_obj: Product, obj_in: ProductUpdate) -> Product:
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_product(db: Session, id: int) -> None:
    db_obj = db.query(Product).filter(Product.id == id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()

def get_category(db: Session, id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    print("[SERVICE] Querying categories from DB...")
    categories_from_db = db.query(Category).offset(skip).limit(limit).all()
    print(f"[SERVICE] Categories from DB: {type(categories_from_db)}")
    if isinstance(categories_from_db, list):
        print(f"[SERVICE] Number of categories found: {len(categories_from_db)}")
        # for i, cat in enumerate(categories_from_db):
        #      print(f"[SERVICE] Category {i}: ID={cat.id}, Name={cat.name}")
    # else:
    #     print(f"[SERVICE] Data from DB is NOT a list: {categories_from_db}")
    return categories_from_db 