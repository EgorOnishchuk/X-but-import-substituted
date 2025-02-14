"""
Точка входа в приложение. Применение и монтирование всех настроек, модулей и подприложений происходит здесь.
"""

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.dependencies import lifespan
from src.errors import (
    AlreadyExistsError,
    NotFoundError,
    SelfActionError,
    already_exists_handler,
    http_exception_handler,
    not_found_handler,
    self_action_handler,
    validation_handler,
)
from src.medias.routes import router as medias
from src.settings import api_settings, cors_settings, source_settings
from src.tweets.routes import router as tweets
from src.users.errors import (
    UnauthenticatedError,
    UnauthorizedError,
    unauthenticated_handler,
    unauthorized_handler,
)
from src.users.routes import router as users

app = FastAPI(
    **api_settings.model_dump(by_alias=True),
    openapi_tags=[
        {
            "name": "Статические файлы",
            "description": "Доступны по «/static/<категория>/<файл>». Поддерживаются «templates» (HTML), "
            "«styles» (CSS), «scripts» (JS) и «medias» (изображения).",
        }
    ],
    lifespan=lifespan,
)

for static in (
    source_settings.templates,
    source_settings.styles,
    source_settings.scripts,
    source_settings.medias,
):
    app.mount(
        f"/{source_settings.static.name}/{static.name}",
        StaticFiles(directory=static),
        name=static.name,
    )

app.add_middleware(CORSMiddleware, **cors_settings.model_dump(by_alias=True))

for exc, handler in (
    (RequestValidationError, validation_handler),
    (NotFoundError, not_found_handler),
    (AlreadyExistsError, already_exists_handler),
    (SelfActionError, self_action_handler),
    (UnauthenticatedError, unauthenticated_handler),
    (UnauthorizedError, unauthorized_handler),
    (HTTPException, http_exception_handler),
):
    app.add_exception_handler(exc, handler)  # type: ignore


for router in (users, tweets, medias):
    app.include_router(router, prefix="/api")
