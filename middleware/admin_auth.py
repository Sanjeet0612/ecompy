from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse

from utils.jwt import verify_token


class AdminAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        path = request.url.path

        # Public Admin Routes
        public_routes = [
            "/admin/",
            "/admin/api/login"
        ]

        # Public routes ko allow karo
        if path in public_routes:
            return await call_next(request)

        # Sirf /admin routes ko protect karo
        if path.startswith("/admin"):

            token = request.cookies.get("admin_token")

            if not token:
                return RedirectResponse(
                    url="/admin/",
                    status_code=302
                )

            payload = verify_token(token)

            if not payload:
                response = RedirectResponse(
                    url="/admin/",
                    status_code=302
                )
                response.delete_cookie("admin_token")
                return response

            if payload.get("type") != "admin":
                response = RedirectResponse(
                    url="/admin/",
                    status_code=302
                )
                response.delete_cookie("admin_token")
                return response

            # Request me admin data store kar do
            request.state.admin = payload

        return await call_next(request)