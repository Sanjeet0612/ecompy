from fastapi import APIRouter
from fastapi import HTTPException
from config.database import SessionLocal
from models.user import User
from schemas.user import UserCreate
from schemas.login import LoginUser
from utils.security import hash_password
from utils.security import verify_password


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
        # 1. user find karo
        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Invalid email or password"
            )

        # 2. password verify karo
        if not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Invalid email or password"
            )

        return {
            "status": True,
            "message": "Login successful ✔️",
            "user_id": user.id,
            "name": user.name
        }

    finally:
        db.close()        