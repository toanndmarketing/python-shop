from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload, selectinload
from pathlib import Path
from typing import Optional

from app.database import get_db
from app.models.order import Order, OrderStatus, OrderItem
from app.models.user import User
from app.models.product import Product
from app.routers.admin.auth import get_admin_user_or_redirect, log_admin_activity

BASE_PATH = Path(__file__).resolve().parent.parent.parent
TEMPLATES_ADMIN = Jinja2Templates(directory=str(BASE_PATH / "templates/admin"))

router = APIRouter(
    prefix="/admin/orders",
    tags=["admin_orders"],
    dependencies=[Depends(get_admin_user_or_redirect)]
)

# Định nghĩa các trạng thái có thể chọn, dịch sang tiếng Việt
AVAILABLE_ORDER_STATUSES = {
    OrderStatus.PENDING: "Đang chờ xử lý",
    OrderStatus.PROCESSING: "Đang xử lý",
    OrderStatus.SHIPPED: "Đã giao hàng",
    OrderStatus.DELIVERED: "Đã nhận hàng",
    OrderStatus.CANCELLED: "Đã hủy"
}

@router.get("", response_class=HTMLResponse, name="list_orders")
async def list_orders(request: Request, db: Session = Depends(get_db), message: Optional[str] = None, admin_user: dict = Depends(get_admin_user_or_redirect)):
    orders = db.query(Order).options(joinedload(Order.user)).order_by(Order.created_at.desc()).all()
    # Ghi log hành động xem danh sách đơn hàng
    # log_admin_activity(db, admin_user['username'], action="Xem danh sách đơn hàng", target_type="Order")
    return TEMPLATES_ADMIN.TemplateResponse("orders.html", {"request": request, "orders": orders, "message": message, "active_page": "orders"})

@router.get("/view/{order_id}", response_class=HTMLResponse, name="view_order_detail")
async def view_order_detail(order_id: int, request: Request, db: Session = Depends(get_db), admin_user: dict = Depends(get_admin_user_or_redirect)):
    order = db.query(Order).options(
        joinedload(Order.user),
        selectinload(Order.items).joinedload(OrderItem.product).joinedload(Product.category) # Eager load product and its category
    ).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    # Ghi log hành động xem chi tiết đơn hàng
    log_admin_activity(db, admin_user['username'], action="Xem chi tiết đơn hàng", target_type="Order", target_id=order_id, details=f"Mã ĐH: {order.order_number}")
    
    return TEMPLATES_ADMIN.TemplateResponse(
        "order_detail.html", 
        {
            "request": request, 
            "order": order,
            "available_statuses": AVAILABLE_ORDER_STATUSES,
            "active_page": "orders"
        }
    )

@router.post("/update_status/{order_id}", name="update_order_status")
async def update_order_status(
    order_id: int, 
    request: Request, 
    status: str = Form(...), 
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user_or_redirect)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    if status not in OrderStatus.__members__:
        raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")
    
    old_status = order.status
    order.status = OrderStatus[status] # Gán enum member
    db.commit()
    db.refresh(order)

    # Ghi log hành động cập nhật trạng thái
    log_admin_activity(
        db, 
        admin_username=admin_user['username'], 
        action="Cập nhật trạng thái đơn hàng", 
        target_type="Order", 
        target_id=order_id, 
        details=f"Mã ĐH: {order.order_number}, Trạng thái cũ: {old_status}, Trạng thái mới: {order.status}"
    )

    redirect_url = f"/admin/orders/view/{order_id}?message=Cập nhật trạng thái thành công"
    return RedirectResponse(url=redirect_url, status_code=302) 