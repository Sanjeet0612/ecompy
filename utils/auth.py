from fastapi import Header, HTTPException
from utils.jwt import verify_token

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        token = authorization.split(" ")[1]
        user = verify_token(token)
        return user

    except:
        raise HTTPException(status_code=401, detail="Invalid token")