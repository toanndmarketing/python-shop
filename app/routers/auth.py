from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from ..database import get_db
from ..schemas import user as user_schema
from ..services import auth_service
from ..core import security

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=user_schema.User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: user_schema.UserCreate,
) -> Any:
    """
    Đăng ký tài khoản mới.
    """
    user = auth_service.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Tên đăng nhập đã tồn tại",
        )
    user = auth_service.register_user(db, obj_in=user_in)
    return user

@router.post("/login", response_model=user_schema.Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Đăng nhập và nhận access token.
    """
    user = auth_service.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schema.User)
def read_users_me(
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Lấy thông tin người dùng hiện tại.
    """
    return current_user

@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: user_schema.UserUpdate,
    current_user: user_schema.User = Depends(security.get_current_active_user),
) -> Any:
    """
    Cập nhật thông tin người dùng hiện tại.
    """
    user = auth_service.update_user(db, db_obj=current_user, obj_in=user_in)
    return user 