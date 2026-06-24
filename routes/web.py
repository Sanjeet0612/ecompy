# routes/web.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@router.get("/about-us")
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={}
    )

@router.get("/contact-us")
def contact(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={}
    )

@router.get("/blog")
def contact(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="blog.html",
        context={}
    )