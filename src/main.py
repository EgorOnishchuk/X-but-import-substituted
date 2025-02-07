"""
Точка входа в приложение. Применение и монтирование всех настроек, модулей и подприложений происходит здесь.
"""

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.dependencies import lifespan
from src.errors import http_exception_handler, validation_handler
from src.medias.routes import router as medias
from src.settings import STATIC, api_settings, cors_settings
from src.tweets.routes import router as tweets
from src.users.routes import router as users

app = FastAPI(**api_settings.model_dump(by_alias=True), lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC))

app.add_middleware(CORSMiddleware, **cors_settings.model_dump(by_alias=True))

for exc, handler in (
    (HTTPException, http_exception_handler),
    (RequestValidationError, validation_handler),
):
    app.add_exception_handler(exc, handler)  # type: ignore


for router in (users, tweets, medias):
    app.include_router(router)
