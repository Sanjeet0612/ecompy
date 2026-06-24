from fastapi import APIRouter
from config.database import SessionLocal
from models.user import User
from schemas.user import UserCreate
from utils.security import hash_password

router = APIRouter(prefix="/user", tags=["User"])


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