from fastapi import status
from fastapi.requests import Request
from starlette.responses import JSONResponse

from src.errors import ServerError, handle


class UnauthenticatedError(ServerError):
    def __init__(self, msg: str = "Invalid credentials.") -> None:
        """
        При переопределении базового сообщения об ошибке не рекомендуется указывать, какая именно часть данных
        указана неверно: взлом усложняется, если злоумышленник получает меньше конкретики.
        """
        super().__init__(msg)


class UnauthorizedError(ServerError):
    def __init__(self, msg: str = "Not found.") -> None:
        """
        Базовый вариант сообщения об ошибке намеренно искажает её сущность: недоступные ресурсы маскируются под
        «несуществующие» для усложнения доступа злоумышленниками.
        """
        super().__init__(msg)


async def unauthenticated_handler(
    request: Request, exc: UnauthenticatedError
) -> JSONResponse:
    return handle(msg=exc.args[0], status_code=status.HTTP_401_UNAUTHORIZED)


async def unauthorized_handler(
    request: Request, exc: UnauthorizedError
) -> JSONResponse:
    """
    Код состояния намеренно искажает сущность ошибки: недоступные ресурсы маскируются под «несуществующие» для
    усложнения доступа злоумышленниками.
    """
    return handle(msg=exc.args[0], status_code=status.HTTP_404_NOT_FOUND)
