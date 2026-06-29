from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

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

    admin = request.state.admin

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "title": "Dashboard",
            "admin": admin
        }
    )

