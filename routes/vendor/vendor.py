from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from config.database import get_db
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/vendor",tags=["Vendor"])

templates = Jinja2Templates(directory="templates")


# Login Section Start
@router.get("/")
def vendor_login(request: Request):

    flash_success = request.session.pop("flash_success", None)

    return templates.TemplateResponse(
        request=request,
        name="vendor/login.html",
        context={
            "request": request,
            "title": "Vendor Login",
            "flash_success": flash_success
        }
    )

# Signup Section Start
@router.get("/sign-up")
def vendor_signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="vendor/signup.html",
        context={
            "title": "Vendor Signup"
        }
    )

# Dashboard Section Start
@router.get("/dashboard")
def dashboard(request: Request):
    vendor = getattr(request.state, "vendor", None)

    if not vendor:
        return RedirectResponse(url="/vendor/", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="vendor/dashboard.html",
        context={
            "title": "Dashboard",
            "breadcrumbs": [
                {"name": "Vendor", "url": None},
                {"name": "Dashboard", "url": "/vendor/dashboard"},
            ],
            "vendor": vendor
        }
    )

# Vendor Logout Section Start

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/vendor", status_code=302)
    response.delete_cookie("vendor_token")
    return response
