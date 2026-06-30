from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse

from utils.jwt import verify_token


class AdminAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        path = request.url.path.rstrip("/")

        public_routes = [
            "/admin",
            "/admin/api/login"
        ]

        if path in public_routes:
            return await call_next(request)

        if path.startswith("/admin"):

            token = request.cookies.get("admin_token")

            if not token:
                return RedirectResponse("/admin/", 302)

            try:
                payload = verify_token(token)
            except:
                payload = None

            if not payload or payload.get("type") != "admin":
                response = RedirectResponse("/admin/", 302)
                response.delete_cookie("admin_token")
                return response

            request.state.admin = payload

        return await call_next(request)