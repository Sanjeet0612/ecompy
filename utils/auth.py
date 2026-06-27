from fastapi import Request, HTTPException
from utils.jwt import verify_token
from config.database import SessionLocal
from models.user import User

def get_current_user(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    payload = verify_token(token)

    db = SessionLocal()
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user