"""
Исключения и их обработчики уровня приложения.
"""

from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from src.schemas import Error


class NotFoundError(HTTPException):
    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class AlreadyExistsError(HTTPException):
    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, headers)


class SelfActionError(HTTPException):
    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Возвращает ответ клиенту напрямую на основании перехваченного HTTP исключения.
    :param request: Запрос.
    :param exc: Ошибка, связанная с определённым кодом состояния HTTP.
    :return: Исключение, сериализованное в JSON.
    """
    content = Error(msg=exc.detail).model_dump(mode="json")

    return JSONResponse(
        content,
        exc.status_code,
    )


async def validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Возвращает ответ клиенту напрямую на основании перехваченных исключений валидации Pydantic.
    :param request: Запрос.
    :param exc: Ошибка запроса. Ошибки ответа не перехватываются, т.к. являются внутренними ошибками сервера.
    :return: Список ошибок, сериализованных в JSON.
    """
    content = [
        Error(msg=error["msg"]).model_dump(mode="json") for error in exc.errors()
    ]

    return JSONResponse(
        content,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
