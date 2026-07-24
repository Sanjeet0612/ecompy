from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse

from utils.jwt import verify_token


class VendorAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        path = request.url.path.rstrip("/")

        public_routes = [
            "/vendor",
            "/vendor/api/login",
            "/vendor/api/signup",
            "/vendor/api/verify-email"
        ]

        if path in public_routes:
            return await call_next(request)

        if path.startswith("/vendor"):

            token = request.cookies.get("vendor_token")

            if not token:
                return RedirectResponse("/vendor/", 302)

            try:
                payload = verify_token(token)
            except:
                payload = None

            if not payload or payload.get("type") != "vendor":
                response = RedirectResponse("/vendor/", 302)
                response.delete_cookie("vendor_token")
                return response

            request.state.vendor = payload

        return await call_next(request)