from fastapi import Header, HTTPException
from utils.jwt import verify_token
from config.database import SessionLocal
from models.user import User

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        token   = authorization.split(" ")[1]
        payload = verify_token(token)
        db      = SessionLocal()
        user    = db.query(User).filter(User.id == payload["user_id"]).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    finally:
        db.close()