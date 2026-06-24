from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config.settings import APP_NAME

from routes.web import router as web_router
from routes.user import router as user_router

app = FastAPI()
app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(web_router)
app.include_router(user_router)