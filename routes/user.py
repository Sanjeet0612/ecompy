from fastapi import APIRouter, HTTPException, Depends, Response, Request
from config.database import SessionLocal
from models.user import User
from schemas.user import UserCreate
from schemas.login import LoginUser
from utils.security import hash_password, verify_password
from utils.jwt import create_access_token
from utils.auth import get_current_user



router = APIRouter(prefix="/user", tags=["User"])

# Signup Section
@router.post("/api/signup")
def signup(user: UserCreate):

    db = SessionLocal()

    try:
        # duplicate email check
        existing = db.query(User).filter(User.email == user.email).first()

        if existing:
            return {"status": False, "message": "Email already exists"}

        hashed_pw = hash_password(user.password)

        new_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=hashed_pw
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"status": True, "message": "Signup successful ✔️"}

    except Exception as e:
        db.rollback()
        return {"status": False, "error": str(e)}

    finally:
        db.close()

# Login Section

@router.post("/api/login")
def login(data: LoginUser, response: Response):

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == data.email).first()

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        # 🔥 COOKIE SET
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax"
        )

        return {
            "status": True,
            "message": "Login successful"
        }

    finally:
        db.close()

# Profile Section

@router.get("/profile")
def profile(user=Depends(get_current_user)):

    return {
        "status": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "created_at": user.created_at
        }
    }

# Logout Section

@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        path="/"
    )

    return {
        "status": True,
        "message": "Logged out successfully"
    }
