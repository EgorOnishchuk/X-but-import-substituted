from fastapi import APIRouter, status

from src.schemas import ID, PydanticError
from src.users.dependencies import CurrentUser, Service
from src.users.schemas import (
    PydanticUserDetailed,
    PydanticUserNotDetailed,
    PydanticUserPersonal,
)

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get(
    "/me",
    summary="Получение своего профиля.",
    response_description="Профиль получен.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Неверные данные аутентификации.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def get_profile(user: CurrentUser) -> PydanticUserDetailed:
    """
    Получение подробной информации о текущем аутентифицированном пользователе (самом себе).
    """
    return user


@router.get(
    "/{id}",
    summary="Получение профиля другого пользователя.",
    response_description="Пользователь получен.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Пользователь не найден.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def get_by_id(
    id_: ID, service: Service, user: CurrentUser
) -> PydanticUserDetailed:
    """
    Получение подробной информации о другом пользователе по его ID.
    """
    return await service.find_by_id(id_)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя.",
    response_description="Пользователь зарегистрирован.",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Такой пользователь уже был зарегистрирован.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def sign_up(
    service: Service, user: PydanticUserPersonal
) -> PydanticUserNotDetailed:
    """
    Регистрация нового пользователя. Автоматической аутентификации не производится.
    """
    return await service.sign_up(user)


@router.post(
    "/{id}/follows",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отслеживание пользователя.",
    response_description="Пользователь отслеживается.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Попытка отслеживать самого себя.",
            "model": PydanticError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Пользователь не найден.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def follow(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Добавление пользователя в отслеживаемые (подписка, фолловинг). Попытка создать уже существующее отношение
    отслеживания не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому — отношение присутствует.
    """
    await service.follow(id_, user.id)


@router.delete(
    "/{id}/follows",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена отслеживания пользователя.",
    response_description="Пользователей перестал отслеживаться.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Пользователь не найден.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def unfollow(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Удаление пользователя из отслеживаемых (отписка, анфолловинг). Попытка удалить несуществующее отношение
    отслеживания не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому — отношение отсутствует.
    """
    await service.unfollow(id_, user.id)
