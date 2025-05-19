from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..schemas.order import OrderCreate, OrderUpdate, OrderList
from ..models.user import User

def get_order(db: Session, id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == id).first()

def get_orders(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> OrderList:
    query = db.query(Order).filter(Order.user_id == user_id)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return OrderList(
        items=orders,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

def get_all_orders(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> OrderList:
    query = db.query(Order)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return OrderList(
        items=orders,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

def create_order(db: Session, user_id: int, order_payload: OrderCreate) -> Order:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Người dùng không tồn tại.")

    cart_items_db = user.cart_items
    if not cart_items_db:
        raise ValueError("Giỏ hàng trống. Không thể tạo đơn hàng.")

    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    db_order = Order(
        user_id=user_id,
        order_number=order_number,
        recipient_name=order_payload.recipient_name,
        shipping_address=order_payload.shipping_address,
        phone=order_payload.phone,
        payment_method=order_payload.payment_method,
        notes=order_payload.notes,
        status="pending",
        payment_status="pending"
    )
    db.add(db_order)
    db.flush()

    total_amount = 0
    order_items_to_add = []

    for cart_item in cart_items_db:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if not product:
            db.rollback()
            raise ValueError(f"Sản phẩm ID {cart_item.product_id} trong giỏ hàng không tồn tại.")
        if product.stock < cart_item.quantity:
            db.rollback()
            raise ValueError(f"Sản phẩm '{product.name}' không đủ số lượng (còn {product.stock}, cần {cart_item.quantity}).")
        
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=product.price
        )
        order_items_to_add.append(order_item)
        total_amount += product.price * cart_item.quantity
        product.stock -= cart_item.quantity
    
    db.add_all(order_items_to_add)
    db_order.total_amount = total_amount
    
    for cart_item in cart_items_db:
        db.delete(cart_item)

    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, db_obj: Order, obj_in: OrderUpdate) -> Order:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Removed Cart service functions as they are now in cart_service.py 