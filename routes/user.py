from fastapi import APIRouter, Form
from config.database import SessionLocal
from models.user import User
from sqlalchemy import select

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/api/signup")
def signup(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    password: str = Form(...)
):

    db = SessionLocal()

    try:
        # check duplicate email
        existing = db.query(User).filter(User.email == email).first()

        if existing:
            return {"status": False, "message": "Email already exists"}

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {"status": True, "message": "Signup successful ✔️"}

    except Exception as e:
        db.rollback()
        return {"status": False, "error": str(e)}

    finally:
        db.close()
    

   