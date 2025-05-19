from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from ..database import get_db
from ..schemas import order as order_schema
from ..schemas import user as user_schema
from ..services import order_service, cart_service
from ..core import security

router = APIRouter(prefix="/orders", tags=["orders"])

# Cart endpoints
@router.get("/cart", response_model=order_schema.Cart)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    return cart_service.get_cart(db, user_id=current_user.id)

@router.post("/cart/items", response_model=order_schema.CartItem)
def add_item_to_cart(
    *,
    db: Session = Depends(get_db),
    item_in: order_schema.CartItemCreate,
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    try:
        return cart_service.add_to_cart(db, user_id=current_user.id, item_in=item_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/cart/items/{item_id}", response_model=Optional[order_schema.CartItem])
def update_cart_item_quantity(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    quantity: int = Query(..., ge=0),
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    try:
        updated_item = cart_service.update_cart_item(db, user_id=current_user.id, item_id=item_id, quantity=quantity)
        if updated_item is None and quantity <=0:
             return {"message": "Sản phẩm đã được xóa khỏi giỏ hàng."}
        return updated_item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/cart/items/{item_id}")
def remove_item_from_cart(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    try:
        cart_service.remove_from_cart(db, user_id=current_user.id, item_id=item_id)
        return {"message": "Đã xóa sản phẩm khỏi giỏ hàng"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# Order endpoints
@router.post("/", response_model=order_schema.Order)
def create_new_order(
    *,
    db: Session = Depends(get_db),
    order_in: order_schema.OrderCreate,
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    try:
        cart = cart_service.get_cart(db, user_id=current_user.id)
        if not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Giỏ hàng trống. Không thể tạo đơn hàng.")
        
        return order_service.create_order(db, user_id=current_user.id, order_payload=order_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=order_schema.OrderList)
def list_user_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100, 
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    return order_service.get_orders(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=order_schema.Order)
def get_specific_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    order = order_service.get_order(db, id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đơn hàng")
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập đơn hàng này")
    return order

# Admin endpoints
@router.get("/admin/all", response_model=order_schema.OrderList, dependencies=[Depends(security.get_current_active_admin)])
def list_all_orders_admin(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return order_service.get_all_orders(db, skip=skip, limit=limit)

@router.put("/admin/{order_id}", response_model=order_schema.Order, dependencies=[Depends(security.get_current_active_admin)])
def update_order_status_admin(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: order_schema.OrderUpdate,
) -> Any:
    order = order_service.get_order(db, id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đơn hàng")
    return order_service.update_order(db, db_obj=order, obj_in=order_in) 