from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.admin_activity_log import AdminActivityLog

# Setup templates directory
BASE_PATH = Path(__file__).resolve().parent.parent.parent # This should point to the 'app' directory
TEMPLATES_ADMIN = Jinja2Templates(directory=str(BASE_PATH / "templates/admin"))

router = APIRouter(
    prefix="/admin",
    tags=["admin_auth"]
)

# Dummy admin credentials (replace with secure storage and hashing in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123" # NEVER do this in production

# In-memory session (replace with a proper session management like Redis or database-backed sessions)
fake_session_db = {}

def get_current_admin_user(request: Request):
    session_token = request.cookies.get("admin_session_token")
    if session_token and session_token in fake_session_db:
        return fake_session_db[session_token]
    return None

@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    return TEMPLATES_ADMIN.TemplateResponse("login.html", {"request": request})

@router.post("/login", name="login_admin")
async def login_admin(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create a simple session token (insecure, for demo purposes only)
        session_token = "fake_admin_session_token_123" # Generate a real, secure token in production
        fake_session_db[session_token] = {"username": username}
        
        # Log activity
        log_admin_activity(db, admin_username=username, action="Đăng nhập thành công")

        response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="admin_session_token", value=session_token, httponly=True) # httponly for security
        return response
    else:
        return TEMPLATES_ADMIN.TemplateResponse(
            "login.html", 
            {"request": request, "error_message": "Tên đăng nhập hoặc mật khẩu không hợp lệ"}
        )

@router.get("/logout", name="logout_admin")
async def logout_admin(request: Request):
    session_token = request.cookies.get("admin_session_token")
    if session_token and session_token in fake_session_db:
        del fake_session_db[session_token]
    
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("admin_session_token")
    return response

# Dependency to protect routes
async def get_admin_user_or_redirect(request: Request, admin_user: dict = Depends(get_current_admin_user)):
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Chưa xác thực",
            headers={"Location": "/admin/login"},
        )
    return admin_user

# --- Helper function for logging admin activity ---
def log_admin_activity(
    db: Session, 
    admin_username: str, 
    action: str, 
    target_type: Optional[str] = None, 
    target_id: Optional[int] = None, 
    details: Optional[str] = None
):
    log_entry = AdminActivityLog(
        admin_username=admin_username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.add(log_entry)
    db.commit()
    # db.refresh(log_entry) # Không cần thiết refresh ở đây
    print(f"Activity logged: {admin_username} - {action} - {details}") # Ghi log ra console để debug 