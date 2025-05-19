from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import uvicorn

from . import models
from .database import engine
from .routers import auth, product, order, pages_router
from .routers.admin import auth as admin_auth_router
from .routers.admin import dashboard as admin_dashboard_router
from .routers.admin import products as admin_products_router
from .routers.admin import orders as admin_orders_router
from .routers.admin import customers as admin_customers_router

# Create database tables if they don't exist
# This should ideally be handled by Alembic migrations in a production app
models.user.Base.metadata.create_all(bind=engine)
models.product.Base.metadata.create_all(bind=engine)
models.order.Base.metadata.create_all(bind=engine)
models.admin_activity_log.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Shop")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(product.router, prefix="/api/v1")
app.include_router(order.router, prefix="/api/v1")
app.include_router(pages_router.router)

# Admin routers
app.include_router(admin_auth_router.router)
app.include_router(admin_dashboard_router.router)
app.include_router(admin_products_router.router)
app.include_router(admin_orders_router.router)
app.include_router(admin_customers_router.router)

# @app.get("/", response_class=HTMLResponse, name="home_page")
# async def home(request: Request):
#     return templates.TemplateResponse("home.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 