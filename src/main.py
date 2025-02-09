"""
Точка входа в приложение. Применение и монтирование всех настроек, модулей и подприложений происходит здесь.
"""

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import src.settings as settings
from src.dependencies import lifespan
from src.errors import http_exception_handler, validation_handler
from src.medias.routes import router as medias
from src.tweets.routes import router as tweets
from src.users.routes import router as users

app = FastAPI(
    **settings.api_settings.model_dump(by_alias=True),
    openapi_tags=[
        {
            "name": "Статические файлы",
            "description": "Доступны по «/static/<категория>/<файл>». Поддерживаются «templates» (HTML), "
            "«styles» (CSS), «scripts» (JS) и «medias» (изображения).",
        }
    ],
    lifespan=lifespan,
)

for static in (settings.TEMPLATES, settings.STYLES, settings.SCRIPTS, settings.MEDIAS):
    app.mount(
        f"/{settings.STATIC.name}/{static.name}",
        StaticFiles(directory=static),
        name=static.name,
    )

app.add_middleware(CORSMiddleware, **settings.cors_settings.model_dump(by_alias=True))

for exc, handler in (
    (HTTPException, http_exception_handler),
    (RequestValidationError, validation_handler),
):
    app.add_exception_handler(exc, handler)  # type: ignore


for router in (users, tweets, medias):
    app.include_router(router, prefix="/api")
