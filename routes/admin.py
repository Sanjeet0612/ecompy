from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/admin")

templates = Jinja2Templates(directory="templates")


@router.get("/")
def admin_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "title": "Admin Login"
        }
    )


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
                {"name": "Manage Products", "url": "/admin/products"},
                {"name": "Add Product", "url": None}
            ],
            "admin": admin
        }
    )

@router.get("/add-product")
def add_products(request: Request):

    admin = getattr(request.state, "admin", None)

    if not admin:
        return RedirectResponse(url="/admin/", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="admin/add_product.html",
        context={
            "title": "Dashboard",
            "admin": admin
        }
    )

