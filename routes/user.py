from fastapi import APIRouter
from fastapi import HTTPException
from config.database import SessionLocal
from models.user import User
from schemas.user import UserCreate
from schemas.login import LoginUser
from utils.security import hash_password
from utils.security import verify_password
from utils.jwt import create_access_token
from fastapi import Depends
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
def login(data: LoginUser):

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not verify_password(data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        return {
            "status": True,
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        db.close()

# Profile Section

@router.get("/profile")
def profile(user=Depends(get_current_user)):
    return {
        "status": True,
        "user": user
    }

# Logout Section

@router.post("/logout")
def logout(user=Depends(get_current_user)):
    return {
        "status": True,
        "message": "Logout successful"
    }
