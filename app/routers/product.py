from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from ..database import get_db
from ..schemas import product as product_schema
from ..schemas import user as user_schema
from ..services import product_service
from ..core import security

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=product_schema.ProductList)
def list_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
) -> Any:
    """
    Lấy danh sách sản phẩm với các bộ lọc.
    """
    products = product_service.get_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        search=search,
    )
    return products

@router.get("/categories/")
def list_categories(
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Lấy danh sách tất cả các danh mục.
    """
    print("[ROUTER] list_categories called (NO DB DEPENDENCY). Returning MOCK DATA.")
    return [
        {"id": 1, "name": "Áo Thể Thao (Mock)", "description": "Các loại áo thể thao", "created_at": "2023-01-01T10:00:00"},
        {"id": 2, "name": "Quần Thể Thao (Mock)", "description": "Các loại quần thể thao", "created_at": "2023-01-02T11:00:00"},
        {"id": 3, "name": "Giày Chạy Bộ (Mock)", "description": "Các loại giày chạy bộ", "created_at": "2023-01-03T12:00:00"}
    ]

@router.get("/{product_id}", response_model=product_schema.Product)
def get_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Lấy thông tin chi tiết sản phẩm.
    """
    product = product_service.get_product(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return product

@router.post("/", response_model=product_schema.Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: product_schema.ProductCreate,
    current_user: user_schema.User = Depends(security.get_current_active_admin),
) -> Any:
    """
    Tạo sản phẩm mới (chỉ admin).
    """
    product = product_service.create_product(db, obj_in=product_in)
    return product

@router.put("/{product_id}", response_model=product_schema.Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: product_schema.ProductUpdate,
    current_user: user_schema.User = Depends(security.get_current_active_admin),
) -> Any:
    """
    Cập nhật thông tin sản phẩm (chỉ admin).
    """
    product = product_service.get_product(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    product = product_service.update_product(db, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{product_id}")
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: user_schema.User = Depends(security.get_current_active_admin),
) -> Any:
    """
    Xóa sản phẩm (chỉ admin).
    """
    product = product_service.get_product(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    product_service.delete_product(db, id=product_id)
    return {"message": "Đã xóa sản phẩm thành công"} 