from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db # Adjusted import path
from app.models.product import Product # Adjusted import path
from app.models.order import Order # Adjusted import path
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

@router.get("/", response_class=RedirectResponse)
async def admin_root(request: Request, admin_user: dict = Depends(get_admin_user_or_redirect)):
    """Redirects to dashboard if logged in, otherwise get_admin_user_or_redirect handles redirect to login."""
    return RedirectResponse(url="/admin/dashboard")

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), admin_user: dict = Depends(get_admin_user_or_redirect)):
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    
    stats = {
        "total_products": total_products,
        "total_orders": total_orders
    }

    # Lấy 10 hoạt động gần nhất của admin
    recent_activities = db.query(AdminActivityLog).order_by(AdminActivityLog.timestamp.desc()).limit(10).all()

    return TEMPLATES_ADMIN.TemplateResponse(
        "dashboard.html", 
        {"request": request, "stats": stats, "admin_user": admin_user, "recent_activities": recent_activities, "active_page": "dashboard"}
    ) 