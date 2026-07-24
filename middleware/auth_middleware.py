from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
from utils.jwt import verify_token
from config.database import SessionLocal
from models.user import User

class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        path = request.url.path

        public_paths = [
            "/",
            "/about-us",
            "/contact-us",
            "/blog",
            "/user/api/login",
            "/user/api/signup",
            "/login",
            "/static"
        ]
        #print("🔥 MIDDLEWARE HIT:", request.url.path)
        # 🔥 COOKIE se token lo
        token = request.cookies.get("access_token")

        #print("TOKEN:", token)
        user = None

        if token:
            try:
                payload = verify_token(token)

                db = SessionLocal()
                user = db.query(User).filter(User.id == payload["user_id"]).first()
                db.close()

            except:
                user = None

        request.state.user = user

        # BLOCK DASHBOARD (SERVER SIDE SECURITY)
        protected_paths = [
            "/dashboard",
            "/profile",
            "/user/settings"
            
        ]

        if path in protected_paths and not user:
            return RedirectResponse(url="/login", status_code=302)

        return await call_next(request)