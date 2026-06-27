from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config.settings import APP_NAME

from routes.web import router as web_router
from routes.user import router as user_router
from middleware.auth_middleware import AuthMiddleware

app = FastAPI(title=APP_NAME)

# 1. middleware first
app.add_middleware(AuthMiddleware)

# 2. static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. routers
app.include_router(web_router)
app.include_router(user_router)