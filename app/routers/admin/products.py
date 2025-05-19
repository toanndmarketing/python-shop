import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Request, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.product import Product, Category # Category is in the same file
from app.routers.admin.auth import get_admin_user_or_redirect, log_admin_activity

# Setup templates directory
BASE_PATH = Path(__file__).resolve().parent.parent.parent # Points to 'app' directory
TEMPLATES_ADMIN = Jinja2Templates(directory=str(BASE_PATH / "templates/admin"))
STATIC_PATH = BASE_PATH / "static"
PRODUCT_IMAGES_PATH = STATIC_PATH / "images/products"
PRODUCT_IMAGES_PATH.mkdir(parents=True, exist_ok=True) # Ensure directory exists

router = APIRouter(
    prefix="/admin/products",
    tags=["admin_products"],
    dependencies=[Depends(get_admin_user_or_redirect)]
)

@router.get("", response_class=HTMLResponse, name="list_products")
async def list_products(request: Request, db: Session = Depends(get_db), message: Optional[str] = None):
    products = db.query(Product).options(joinedload(Product.category)).order_by(Product.id.desc()).all()
    return TEMPLATES_ADMIN.TemplateResponse("products.html", {"request": request, "products": products, "message": message, "active_page": "products"})

@router.get("/add", response_class=HTMLResponse, name="add_product")
async def add_product_form(request: Request, db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.name).all()
    return TEMPLATES_ADMIN.TemplateResponse("product_form.html", {"request": request, "categories": categories, "product": None, "active_page": "products"})

@router.post("/add", name="create_product")
async def add_product(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    image_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin_user: dict = Depends(get_admin_user_or_redirect)
):
    final_image_url = None
    if image and image.filename:
        # Generate a unique filename
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = PRODUCT_IMAGES_PATH / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        final_image_url = f"/static/images/products/{unique_filename}" # Store relative path for serving
    elif image_url:
        final_image_url = image_url

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        image_url=final_image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    # Log activity
    log_admin_activity(
        db, 
        admin_username=admin_user['username'], 
        action="Thêm sản phẩm", 
        target_type="Product", 
        target_id=new_product.id, 
        details=f"Tên: {new_product.name}"
    )
    return RedirectResponse(url="/admin/products?message=Thêm sản phẩm thành công", status_code=302)

@router.get("/edit/{product_id}", response_class=HTMLResponse, name="edit_product")
async def edit_product_form(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    categories = db.query(Category).order_by(Category.name).all()
    return TEMPLATES_ADMIN.TemplateResponse("product_form.html", {"request": request, "product": product, "categories": categories, "active_page": "products"})

@router.post("/edit/{product_id}", name="update_product")
async def edit_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    image_url: Optional[str] = Form(None),
    current_image_url: Optional[str] = Form(None), # Hidden field for existing image
    image: Optional[UploadFile] = File(None),
    admin_user: dict = Depends(get_admin_user_or_redirect)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    final_image_url = product.image_url # Keep current image by default

    if image and image.filename: # New image uploaded
        # Delete old image if it exists and is a local file
        if product.image_url and not product.image_url.startswith('http') and (STATIC_PATH.parent / product.image_url.lstrip('/')).exists():
            try:
                (STATIC_PATH.parent / product.image_url.lstrip('/')).unlink()
            except OSError as e:
                print(f"Lỗi xóa ảnh cũ: {e}") # Log error
        
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = PRODUCT_IMAGES_PATH / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        final_image_url = f"/static/images/products/{unique_filename}"
    elif image_url: # New URL provided, overrides uploaded file
         # Delete old image if it exists and is a local file and new URL is different
        if product.image_url and final_image_url != image_url and not product.image_url.startswith('http') and (STATIC_PATH.parent / product.image_url.lstrip('/')).exists():
            try:
                (STATIC_PATH.parent / product.image_url.lstrip('/')).unlink()
            except OSError as e:
                print(f"Lỗi xóa ảnh cũ: {e}")
        final_image_url = image_url
    elif current_image_url is None and product.image_url : # Explicitly clearing the image by not providing current_image_url (and no new image/url)
        if not product.image_url.startswith('http') and (STATIC_PATH.parent / product.image_url.lstrip('/')).exists():
             try:
                (STATIC_PATH.parent / product.image_url.lstrip('/')).unlink()
             except OSError as e:
                print(f"Lỗi xóa ảnh cũ: {e}")
        final_image_url = None
    # If no new image, no new image_url, and current_image_url is present, final_image_url remains product.image_url (already set)

    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    product.category_id = category_id
    product.image_url = final_image_url
    
    db.commit()
    db.refresh(product)
    # Log activity
    log_admin_activity(
        db, 
        admin_username=admin_user['username'], 
        action="Cập nhật sản phẩm", 
        target_type="Product", 
        target_id=product.id, 
        details=f"Tên: {product.name}"
    )
    return RedirectResponse(url="/admin/products?message=Cập nhật sản phẩm thành công", status_code=302)

@router.get("/delete/{product_id}", name="delete_product")
async def delete_product(product_id: int, request: Request, db: Session = Depends(get_db), admin_user: dict = Depends(get_admin_user_or_redirect)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    # Delete image file if it exists and is locally stored
    if product.image_url and not product.image_url.startswith('http'):
        # Construct absolute path to the image file
        # image_path_to_check = STATIC_PATH.parent / product.image_url.lstrip('/') # app/static/images/products/filename.jpg -> /static/images/products/filename.jpg
        # Correct path construction relative to STATIC_PATH
        actual_image_path = Path(str(STATIC_PATH.parent) + product.image_url)        
        if actual_image_path.exists():
            try:
                actual_image_path.unlink()
            except OSError as e:
                print(f"Lỗi xóa file ảnh {actual_image_path}: {e}") # Log error
        else:
            print(f"Không tìm thấy file ảnh để xóa: {actual_image_path}")

    product_name_for_log = product.name # Lưu tên sản phẩm trước khi xóa
    db.delete(product)
    db.commit()
    # Log activity
    log_admin_activity(
        db, 
        admin_username=admin_user['username'], 
        action="Xóa sản phẩm", 
        target_type="Product", 
        target_id=product_id, # product.id sẽ không còn sau khi xóa
        details=f"Tên: {product_name_for_log}"
    )
    return RedirectResponse(url="/admin/products?message=Xóa sản phẩm thành công", status_code=302) 