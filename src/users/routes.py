"""
Маршрутизатор пользователей.
"""

from fastapi import APIRouter, status

from src.schemas import ID, Error
from src.users.dependencies import CurrentUser, Service
from src.users.models import DataUser
from src.users.schemas import UserDetailed, UserNotDetailed, UserPersonal

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get(
    "/me",
    response_model=UserDetailed,
    summary="Получение своего профиля.",
    response_description="Профиль получен.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Неверные данные аутентификации.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _get_self(user: CurrentUser) -> DataUser:
    """
    Получение подробной информации о текущем аутентифицированном пользователе (самом себе).
    """
    return user


@router.get(
    "/{id}",
    response_model=UserDetailed,
    summary="Получение профиля другого пользователя.",
    response_description="Пользователь получен.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Пользователь не найден.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _get_by_id(id_: ID, service: Service, user: CurrentUser) -> DataUser:
    """
    Получение подробной информации о другом пользователе по его ID.
    """
    return await service.get_by_id(id_)


@router.post(
    "",
    response_model=UserNotDetailed,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя.",
    response_description="Пользователь зарегистрирован.",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Такой пользователь уже был зарегистрирован.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _sign_up(service: Service, user: UserPersonal) -> DataUser:
    """
    Регистрация нового пользователя. Автоматической аутентификации не производится.
    """
    return await service.create(user)


@router.post(
    "/{id}/follows",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отслеживание пользователя.",
    response_description="Пользователь отслеживается.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Попытка отслеживать самого " "себя.",
            "model": Error,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Пользователь не найден.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _follow(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Добавление пользователя в отслеживаемые (подписка, фолловинг). Попытка создать уже существующее отношение
    отслеживания не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому — отношение присутствует.
    """
    await service.create_follow(id_, user)


@router.delete(
    "/{id}/follows",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена отслеживания пользователя.",
    response_description="Пользователей перестал отслеживаться.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Пользователь не найден.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _unfollow(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Удаление пользователя из отслеживаемых (отписка, анфолловинг). Попытка удалить несуществующее отношение
    отслеживания не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому — отношение отсутствует.
    """
    await service.delete_follow(id_, user)
