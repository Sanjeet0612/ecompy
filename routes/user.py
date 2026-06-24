from fastapi import APIRouter
from config.database import SessionLocal
from models.user import User
from schemas.user import UserCreate

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/api/signup")
def signup(user: UserCreate):

    db = SessionLocal()

    try:
        # duplicate email check
        existing = db.query(User).filter(User.email == user.email).first()

        if existing:
            return {"status": False, "message": "Email already exists"}

        new_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=user.password
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