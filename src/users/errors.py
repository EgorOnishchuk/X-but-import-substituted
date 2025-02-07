"""
Исключения, связанные с пользователями.
"""

from fastapi import HTTPException, status


class UnauthenticatedError(HTTPException):
    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)
