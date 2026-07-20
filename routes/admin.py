from fastapi import (APIRouter,Request,Depends,Form,File,UploadFile,HTTPException)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from config.database import get_db
from models.category import Category
from models.brand import Brand
from models.attribute import Attribute
from models.blog_category import BlogCategory
from repositories.attribute_repository import AttributeRepository


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

# Edit Product Start
@router.get("/edit-product/{product_id}")
def edit_product(
    request: Request,
    product_id: int,
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
        name="admin/edit_product.html",
        context={
            "title": "Dashboard",
            "product_id": product_id,
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Products", "url": "/admin/products"},
                {"name": "Edit & Update Product", "url": None}
            ],
            "admin": admin,
            "categories": categories,
            "brands": brands,
            "attributes": attributes
            
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

# Attribute Value Section Start
@router.get("/manage-attribute-value")
def manage_attribute_value(
    request: Request,
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)
    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)

    attributes = AttributeRepository().get_active_attributes(db)

    return templates.TemplateResponse(
        request=request,
        name="admin/manage_attribute_value.html",
        context={
            "title": "Manage Attribute Value",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Attribute Value", "url": "/admin/manage-attribute-value"},
                {"name": "Manage Attribute Value", "url": None}
            ],
            "admin": admin,
            "attributes": attributes
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


# Blog Category Section Start
@router.get("/manage-blog-category")
def manage_blog_category(
    request: Request
):
    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_blog_category.html",
        context={
            "title": "Blog Category",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Blog Category", "url": "/admin/manage-blog-category"},
                {"name": "Manage Blog Category", "url": None}
            ],
            "admin": admin
        }
    )

# Blog Section Start
@router.get("/manage-blog")
def manage_blog(
    request: Request
):
    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_blog.html",
        context={
            "title": "Blog",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Blog", "url": "/admin/manage-blog"},
                {"name": "Manage Blog", "url": None}
            ],
            "admin": admin
        }
    )
# Add Blog
@router.get("/add-blog")
def add_blog(
    request: Request,
    db: Session = Depends(get_db)
    ):
    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)

    categories = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.status == 1,
            BlogCategory.deleted_at == None
        )
        .order_by(BlogCategory.name.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/add_blog.html",
        context={
            "title": "Add Blog",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Blog", "url": "/admin/manage-blog"},
                {"name": "Add Blog", "url": None}
            ],
            "admin": admin,
            "categories": categories
        }
    )

# Edit Blog Section Start
@router.get("/blog/edit-blog/{blog_id}")
def edit_blog(
    request:Request,
    blog_id: int,
    db: Session = Depends(get_db)        
):
    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    categories = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.status == 1,
            BlogCategory.deleted_at == None
        )
        .order_by(BlogCategory.name.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/edit_blog.html",
        context={
            "title": "Edit Blog",
            "blog_id": blog_id,
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "Blog", "url": "/admin/manage-blog"},
                {"name": "Edit Blog", "url": None}
            ],
            "admin": admin,
            "categories": categories
        }
    )
    

# AI SETTING SECTION START
@router.get("/manage-ai-setting")
def manage_ai_setting(request: Request):

    admin = getattr(request.state, "admin", None)
    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)
    
    return templates.TemplateResponse(
        request=request,
        name="admin/manage_ai_setting.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Dashboard", "url": "/admin/dashboard"},
                {"name": "AI Setting", "url": "/admin/manage-ai-setting"},
                {"name": "Manage AI Setting", "url": None}
            ],
            "admin": admin
        }

    )