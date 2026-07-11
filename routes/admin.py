from fastapi import (APIRouter,Request,Depends,Form,File,UploadFile,HTTPException)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from config.database import get_db
from models.category import Category
from models.brand import Brand
from models.attribute import Attribute

router = APIRouter(prefix="/admin")

templates = Jinja2Templates(directory="templates")

# Login Section Start
@router.get("/")
def admin_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "title": "Admin Login"
        }
    )

# Dashboard Section Start
@router.get("/dashboard")
def dashboard(request: Request):
    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Admin", "url": None},
                {"name": "Dashboard", "url": "/admin/dashboard"},
            ],
            "admin": admin
        }
    )
# Category Section Start
@router.get("/manage-category")
def manage_category(request: Request):

    admin = getattr(request.state, "admin",None)
    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_category.html",
        context={
            "title" : "Dashboard",
            "breadcrumbs":[
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Categories", "url": "/admin/manage-category"},
                {"name": "Manage Category", "url": None}
            ],
            "admin":admin
        }
    )

# Sub Category Section Start
@router.get("/manage-sub-category")
def manage_sub_category(request: Request):
    admin = getattr(request.state, "admin",None)
    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_sub_category.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Products", "url": "/admin/manage-sub-category"},
                {"name": "Manage Sub Category", "url": None}
            ],
            "admin": admin
        }

    )

# Brand Section Start
@router.get("/manage-brand")
def manage_brand(request: Request):
    admin = getattr(request.state, "admin",None)
    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_brand.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Brand", "url": "/admin/manage-brand"},
                {"name": "Manage Brand", "url": None}
            ],
            "admin": admin
        }

    )

# Product Section Start
@router.get("/products")
def products(request: Request):

    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="admin/manage_product.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Products", "url": "/admin/products"},
                {"name": "Manage Product", "url": None}
            ],
            "admin": admin
        }
    )

# Attribute Section Start
@router.get("/manage-attribute")
def manage_attribute(request: Request):
    admin = getattr(request.state, "admin", None)
    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_attribute.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Brand", "url": "/admin/manage-brand"},
                {"name": "Manage Brand", "url": None}
            ],
            "admin": admin
        }

    )


@router.get("/add-product")
def add_products(
    request: Request,
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)

    categories = (
        db.query(Category)
        .filter(
            Category.status == 1,
            Category.deleted_at == None
        )
        .order_by(Category.name.asc())
        .all()
    )

    brands = (
        db.query(Brand)
        .filter(
            Brand.status == 1,
            Brand.deleted_at == None
        )
        .order_by(Brand.name.asc())
        .all()
    )

    attributes = (
        db.query(Attribute)
        .filter(
            Attribute.status == 1,
            Attribute.deleted_at == None
        )
        .order_by(Attribute.name.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/add_product.html",
        context={
            "title": "Add Product",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Products", "url": "/admin/products"},
                {"name": "Add Product", "url": None}
            ],
            "admin": admin,
            "categories": categories,
            "brands": brands,
            "attributes": attributes,
        }
    )

