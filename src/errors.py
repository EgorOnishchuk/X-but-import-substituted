from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from src.schemas import PydanticError


class ServerError(Exception):
    """
    Исключение логики предметной области, не относится к транспортному уровню.
    """

    def __init__(self, msg: str = "Something went wrong.") -> None:
        super().__init__(msg)


class NotFoundError(ServerError):
    def __init__(self, msg: str = "Not found.") -> None:
        super().__init__(msg)


class AlreadyExistsError(ServerError):
    def __init__(self, msg: str = "Already exists.") -> None:
        super().__init__(msg)


class SelfActionError(ServerError):
    def __init__(self, msg: str = "Unable to perform self action") -> None:
        super().__init__(msg)


def handle(msg: str, status_code: int) -> JSONResponse:
    return JSONResponse(PydanticError(msg=msg).to_dict(mode="json"), status_code)


async def validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    content = [
        PydanticError(msg=error["msg"]).to_dict(mode="json") for error in exc.errors()
    ]

    return JSONResponse(content, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return handle(msg=exc.args[0], status_code=status.HTTP_404_NOT_FOUND)


async def already_exists_handler(
    request: Request, exc: AlreadyExistsError
) -> JSONResponse:
    return handle(msg=exc.args[0], status_code=status.HTTP_409_CONFLICT)


async def self_action_handler(request: Request, exc: SelfActionError) -> JSONResponse:
    return handle(msg=exc.args[0], status_code=status.HTTP_403_FORBIDDEN)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    «Шаблонный ответ» на ошибки, которые не были перехвачены другими обработчиками.
    """
    return handle(msg=exc.detail, status_code=exc.status_code)
