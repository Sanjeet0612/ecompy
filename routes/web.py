# routes/web.py

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from utils.auth import get_current_user
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from config.database import get_db
from models.user import User
from pydantic import EmailStr
import re

import os
import shutil
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")



def redirect_with_error(request: Request, message: str):
    request.session["error"] = message

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

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
def blog(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="blog.html",
        context={}
    )

@router.get("/dashboard")
def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):

    return templates.TemplateResponse(
        request=request,
        name="user_profile.html",
        context={
            "user": current_user,
            "error": request.session.pop("error", None),
            "success": request.session.pop("success", None)
        }
    )

@router.post("/profile/update")
async def update_profile(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    bio: str = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    UPLOAD_DIR = "static/uploads/profile"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # ------------------------
    # Name Validation
    # ------------------------

    if len(name.strip()) < 3:
        return redirect_with_error(
            request,
            "Name must be at least 3 characters."
        )

    # ------------------------
    # Phone Validation
    # ------------------------

    if not phone.isdigit():
        return redirect_with_error(
            request,
            "Phone number must contain digits only."
        )

    if len(phone) != 10:
        return redirect_with_error(
            request,
            "Phone number must be exactly 10 digits."
        )

    # ------------------------
    # Email Validation
    # ------------------------

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return redirect_with_error(
            request,
            "Please enter a valid email address."
        )

    # ------------------------
    # Email Exists
    # ------------------------

    email_exists = (
        db.query(User)
        .filter(
            User.email == email,
            User.id != current_user.id
        )
        .first()
    )

    if email_exists:
        return redirect_with_error(
            request,
            "Email already exists."
        )

    # ------------------------
    # Image Upload
    # ------------------------

    if profile_image and profile_image.filename:

        allowed_extensions = ["jpg","jpeg","png","webp"]

        extension = profile_image.filename.split(".")[-1].lower()

        if extension not in allowed_extensions:
            return redirect_with_error(
                request,
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        MAX_SIZE = 500 * 1024

        contents = await profile_image.read()

        if len(contents) > MAX_SIZE:
            return redirect_with_error(
                request,
                "Image size must be less than 500 KB."
            )

        profile_image.file.seek(0)

        # Delete Old Image

        if user.profile_image:

            old_image = user.profile_image.replace(
                "/static/uploads/profile/",
                ""
            )

            old_path = os.path.join(
                UPLOAD_DIR,
                old_image
            )

            if os.path.exists(old_path):
                os.remove(old_path)

        filename = f"{uuid.uuid4()}.{extension}"

        filepath = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(
                profile_image.file,
                buffer
            )

        user.profile_image = f"/static/uploads/profile/{filename}"

    # ------------------------
    # Update
    # ------------------------

    #user.name = name.strip()
    #user.phone = phone
    #user.email = email
    user.bio = bio

    db.commit()
    db.refresh(user)

    request.session["success"] = "Profile updated successfully."

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )