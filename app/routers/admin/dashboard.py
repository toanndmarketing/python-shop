from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db # Adjusted import path
from app.models.product import Product # Adjusted import path
from app.models.order import Order # Adjusted import path
from app.models.user import User # Import User model for customer count
from app.models.admin_activity_log import AdminActivityLog # Import model log
from .auth import get_admin_user_or_redirect # Relative import for auth

# Setup templates directory
BASE_PATH = Path(__file__).resolve().parent.parent.parent # This should point to the 'app' directory
TEMPLATES_ADMIN = Jinja2Templates(directory=str(BASE_PATH / "templates/admin"))

router = APIRouter(
    prefix="/admin",
    tags=["admin_dashboard"],
    dependencies=[Depends(get_admin_user_or_redirect)] # Protect all routes in this router
)

@router.get("/", response_class=RedirectResponse, name="admin_root")
async def admin_root(request: Request, admin_user: dict = Depends(get_admin_user_or_redirect)):
    """Redirects to dashboard if logged in, otherwise get_admin_user_or_redirect handles redirect to login."""
    return RedirectResponse(url="/admin/dashboard")

@router.get("/dashboard", response_class=HTMLResponse, name="admin_dashboard")
async def admin_dashboard(request: Request, db: Session = Depends(get_db), admin_user: dict = Depends(get_admin_user_or_redirect)):
    product_count = db.query(Product).count()
    order_count = db.query(Order).count()
    customer_count = db.query(User).filter(User.is_admin == False).count() # Đếm user không phải admin
    
    # Lấy 10 hoạt động gần nhất của admin
    recent_activities = db.query(AdminActivityLog).order_by(AdminActivityLog.timestamp.desc()).limit(10).all()

    return TEMPLATES_ADMIN.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "product_count": product_count,
            "order_count": order_count,
            "customer_count": customer_count,
            "admin_user": admin_user, 
            "recent_activities": recent_activities, 
            "active_page": "dashboard"
        }
    ) 