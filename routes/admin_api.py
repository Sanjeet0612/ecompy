from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from config.database import get_db
from repositories.admin_repository import AdminRepository
from schemas.admin import AdminLogin
from utils.security import verify_password
from utils.jwt import create_access_token


router = APIRouter(prefix="/admin")

@router.post("/api/login")
def admin_login(data: AdminLogin, response: Response, db: Session = Depends(get_db)):

    admin = AdminRepository.get_by_email(db, data.email)

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, admin.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if admin.status == 0:
        raise HTTPException(
            status_code=403,
            detail="Your account is inactive"
        )
    
    token = create_access_token({
            "admin_id": admin.id,
            "email": admin.email,
            "role": admin.role,
            "type": "admin"
        })
    
    # Store JWT in HTTP Only Cookie

    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        secure=False,          # True when using HTTPS in production
        samesite="lax",
        #max_age=60 * 60 * 24,  # 1 Day
        path="/"
    )


    return {
        "status": True,
        "message": "Login successful",
        "token": token,
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role
        }
    }

# Logout Section Start

@router.post("/api/logout")
def logout(response: Response):

    response.delete_cookie("admin_token")

    return {
        "status": True,
        "message": "Logout successful"
    }