from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.routers.admin.auth import get_admin_user_or_redirect, log_admin_activity

BASE_PATH = Path(__file__).resolve().parent.parent.parent
TEMPLATES_ADMIN = Jinja2Templates(directory=str(BASE_PATH / "templates/admin"))

router = APIRouter(
    prefix="/admin/customers",
    tags=["admin_customers"],
    dependencies=[Depends(get_admin_user_or_redirect)]
)

@router.get("", response_class=HTMLResponse, name="list_customers")
async def list_customers(request: Request, db: Session = Depends(get_db), message: Optional[str] = None, admin_user: dict = Depends(get_admin_user_or_redirect)):
    # Lấy tất cả user không phải là admin
    customers = db.query(User).filter(User.is_admin == False).order_by(User.created_at.desc()).all()
    
    # Ghi log hành động xem danh sách khách hàng (có thể comment lại nếu không muốn log quá nhiều)
    # log_admin_activity(db, admin_user['username'], action="Xem danh sách khách hàng", target_type="Customer")
    
    return TEMPLATES_ADMIN.TemplateResponse("customers.html", {"request": request, "customers": customers, "message": message, "active_page": "customers"})

@router.post("/toggle_active/{user_id}", name="toggle_customer_active")
async def toggle_customer_active_status(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user_or_redirect)
):
    customer = db.query(User).filter(User.id == user_id, User.is_admin == False).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")

    old_status = customer.is_active
    customer.is_active = not customer.is_active
    db.commit()
    db.refresh(customer)

    action_taken = "Kích hoạt tài khoản" if customer.is_active else "Vô hiệu hóa tài khoản"
    log_admin_activity(
        db,
        admin_username=admin_user['username'],
        action=action_taken,
        target_type="Customer",
        target_id=customer.id,
        details=f"Khách hàng: {customer.username}, Trạng thái cũ: {old_status}, Trạng thái mới: {customer.is_active}"
    )

    message = f"Đã {action_taken.lower()} cho khách hàng {customer.username}."
    return RedirectResponse(url=f"/admin/customers?message={message}", status_code=302) 