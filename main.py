from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from config.settings import APP_NAME, SECRET_KEY

from routes.web import router as web_router
from routes.user import router as user_router
from middleware.auth_middleware import AuthMiddleware

app = FastAPI(title=APP_NAME)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

# Custom Auth Middleware
app.add_middleware(AuthMiddleware)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(web_router)
app.include_router(user_router)