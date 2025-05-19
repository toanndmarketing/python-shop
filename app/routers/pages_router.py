from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..core.security import get_current_active_user # Optional: for protected pages
from ..schemas.user import User as UserSchema # Optional: for type hinting
from ..services import product_service # Thêm import này
from ..database import get_db # Thêm import này

router = APIRouter(
    tags=["pages"],
    include_in_schema=False # We don't want these in API docs
)
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse, name="register_page")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse, name="profile_page")
async def profile_page(request: Request):
    # This page will fetch data client-side using JavaScript and token
    # No specific data needs to be passed from server initially for this setup
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/", response_class=HTMLResponse, name="home_page")
async def serve_home_page(request: Request, db: Session = Depends(get_db)):
    featured_products = product_service.get_products(db, skip=0, limit=3).items
    return templates.TemplateResponse("home.html", {"request": request, "featured_products": featured_products})

@router.get("/products", response_class=HTMLResponse, name="products_page")
async def serve_products_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

@router.get("/cart", response_class=HTMLResponse, name="cart_page")
async def serve_cart_page(request: Request):
    # Giả sử trang giỏ hàng yêu cầu người dùng đăng nhập
    # current_user: UserSchema = Depends(get_current_active_user) # Bỏ comment nếu cần bảo vệ route
    return templates.TemplateResponse("cart.html", {"request": request})

@router.get("/checkout", response_class=HTMLResponse, name="checkout_page") # Sẽ tạo file HTML sau
async def serve_checkout_page(request: Request):
    # current_user: UserSchema = Depends(get_current_active_user) # Bỏ comment nếu cần bảo vệ route
    return templates.TemplateResponse("checkout.html", {"request": request, "error": "Trang đang được xây dựng"})

@router.get("/order-confirmation/{order_id}", response_class=HTMLResponse, name="order_confirmation_page")
async def serve_order_confirmation_page(request: Request, order_id: str):
    # current_user: UserSchema = Depends(get_current_active_user) # Bỏ comment nếu cần bảo vệ route
    return templates.TemplateResponse("order_confirmation.html", {"request": request, "order_id": order_id})

@router.get("/order-history", response_class=HTMLResponse, name="order_history_page") # Sẽ tạo file HTML sau
async def serve_order_history_page(request: Request):
    # current_user: UserSchema = Depends(get_current_active_user) # Bỏ comment nếu cần bảo vệ route
    return templates.TemplateResponse("order_history.html", {"request": request, "error": "Trang đang được xây dựng"})

# Add a logout route/link logic in base.html or JS
# For now, client-side will just remove the token 