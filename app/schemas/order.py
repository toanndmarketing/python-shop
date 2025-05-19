from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .product import Product

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Product

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    recipient_name: Optional[str] = None
    shipping_address: str
    phone: str
    payment_method: str
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None

class Order(OrderBase):
    id: int
    user_id: int
    order_number: str
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True

class OrderList(BaseModel):
    items: List[Order]
    total: int
    page: int
    size: int
    pages: int

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    user_id: int
    product: Product
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Cart(BaseModel):
    items: List[CartItem]
    total_amount: float 