from datetime import datetime, timedelta
import secrets
from fastapi import Request
from fastapi import (APIRouter, Depends, HTTPException, Response, Form)
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from config.database import get_db
from models.vendor.vendor import Vendor
from repositories.vendor.vendor_repository import VendorRepository
from schemas.vendor.vendor_schema import VendorSignup, VendorLogin

from utils.mail import send_verification_email
from utils.security import verify_password
from utils.jwt import create_access_token

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/vendor/api",tags=["Vendor API"])
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


@router.post("/signup")
async def signup(
    vendor: VendorSignup,
    db: Session = Depends(get_db)
):

    # -----------------------------
    # Check Existing Email
    # -----------------------------
    if VendorRepository.get_by_email(db, vendor.email):

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    # -----------------------------
    # Generate Verification Token
    # -----------------------------
    token = secrets.token_urlsafe(32)

    expiry = datetime.utcnow() + timedelta(hours=24)

    # -----------------------------
    # Create Vendor
    # -----------------------------
    new_vendor = Vendor(
        name=vendor.name,
        email=vendor.email,
        password=pwd_context.hash(vendor.password),
        email_verified=0,
        email_verification_token=token,
        email_verification_expiry=expiry
    )

    VendorRepository.create(
        db,
        new_vendor
    )

    db.commit()
    db.refresh(new_vendor)

    # -----------------------------
    # Verification URL
    # -----------------------------
    verify_url = (
        f"http://127.0.0.1:8000/vendor/api/verify-email"
        f"?token={token}"
    )

    # -----------------------------
    # Send Verification Email
    # -----------------------------
    email_sent = send_verification_email(
        name=new_vendor.name,
        email=new_vendor.email,
        verify_url=verify_url
    )

    # -----------------------------
    # Response
    # -----------------------------
    if email_sent:

        return {
            "status": True,
            "message": "Account created successfully. Please verify your email."
        }

    return {
        "status": True,
        "message": "Account created successfully, but verification email could not be sent."
    }


@router.get("/verify-email")
async def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):

    # -----------------------------------
    # Find Vendor By Token
    # -----------------------------------
    vendor = VendorRepository.get_by_verification_token(
        db=db,
        token=token
    )

    if not vendor:
        return templates.TemplateResponse(
            request=request,
            name="vendor/verification_status.html",
            context={
                "request": request,
                "title": "Invalid Verification Link",
                "message": "This verification link is invalid or has already been used.",
                "icon": "fas fa-times-circle",
                "icon_class": "text-danger"
            }
        )

    # -----------------------------------
    # Already Verified
    # -----------------------------------
    if vendor.email_verified == 1:
        return templates.TemplateResponse(
            request=request,
            name="vendor/verification_status.html",
            context={
                "request": request,
                "title": "Email Already Verified",
                "message": "Your email address has already been verified. You can login to your account.",
                "icon": "fas fa-info-circle",
                "icon_class": "text-primary"
            }
        )

    # -----------------------------------
    # Check Expiry
    # -----------------------------------
    if (
        vendor.email_verification_expiry
        and vendor.email_verification_expiry < datetime.utcnow()
    ):
        return templates.TemplateResponse(
            request=request,
            name="vendor/verification_status.html",
            context={
                "request": request,
                "title": "Verification Link Expired",
                "message": "Your verification link has expired. Please request a new verification email.",
                "icon": "fas fa-clock",
                "icon_class": "text-warning"
            }
        )

    # -----------------------------------
    # Verify Email
    # -----------------------------------
    vendor.email_verified = 1
    vendor.email_verification_token = None
    vendor.email_verification_expiry = None

    VendorRepository.update(
        db=db,
        vendor=vendor
    )

    db.commit()

    # -----------------------------------
    # Success Page
    # -----------------------------------
    return templates.TemplateResponse(
        request=request,
        name="vendor/verification_status.html",
        context={
            "request": request,
            "title": "Email Verified",
            "message": "Your email has been verified successfully. You can now login.",
            "icon": "fas fa-check-circle",
            "icon_class": "text-success"
        }
    )


@router.post("/login")
async def login(
    data: VendorLogin,
    response: Response,
    db: Session = Depends(get_db)
):

    email = data.email
    password = data.password

    # -----------------------------------
    # Find Vendor
    # -----------------------------------
    vendor = VendorRepository.get_by_email(
        db=db,
        email=email
    )

    if not vendor:
        return {
            "status": False,
            "message": "Invalid email or password."
        }

    # -----------------------------------
    # Verify Password
    # -----------------------------------
    if not verify_password(password, vendor.password):
        return {
            "status": False,
            "message": "Invalid email or password."
        }

    # -----------------------------------
    # Email Verification
    # -----------------------------------
    if vendor.email_verified != 1:
        return {
            "status": False,
            "message": "Please verify your email before logging in."
        }

    token = create_access_token({
        "vendor_id": vendor.id,
        "email": vendor.email,
        "type": "vendor"
    })
    
    response.set_cookie(
        key="vendor_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/"
    )
    
    return {
        "status": True,
        "message": "Login successful",
        "token": token,
        "vendor": {
            "id": vendor.id,
            "name": vendor.name,
            "email": vendor.email
        }
    }
