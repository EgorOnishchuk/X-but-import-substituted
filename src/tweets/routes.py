from fastapi import APIRouter, status

from src.schemas import ID, PydanticError
from src.tweets.dependencies import Service
from src.tweets.schemas import (
    PydanticTweetID,
    PydanticTweetNotDetailed,
    PydanticTweetPersonal,
    PydanticTweetsDetailed,
)
from src.users.dependencies import CurrentUser

router: APIRouter = APIRouter(prefix="/tweets", tags=["Публикации"])


@router.get(
    "",
    summary="Получение всех публикаций.",
    response_description="Публикации получены.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def get_list(service: Service, user: CurrentUser) -> PydanticTweetsDetailed:
    """
    Получение полного списка публикаций (твитов) в порядке популярности от отслеживаемых пользователей.
    """
    return await service.get_list(user.id)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание публикации.",
    response_description="Публикация создана.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def publish(
    tweet: PydanticTweetNotDetailed, service: Service, user: CurrentUser
) -> PydanticTweetID:
    """
    Создание новой публикации (твита) от лица текущего пользователя (себя).
    """
    return await service.publish(
        PydanticTweetPersonal(**tweet.to_dict(), author_id=user.id)
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление публикации.",
    response_description="Публикация удалена.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Публикация не найдена.",
            "model": PydanticError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Попытка удалить чужую публикацию.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def remove(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Удаление публикации (твита) текущего пользователя (своей). Попытка удалить несуществующую публикацию не вызывает
    ошибок, т.к. результат в любом случае соответствует ожидаемому — публикация отсутствует.
    """
    await service.remove(id_, user.id)


@router.post(
    "/{id}/likes",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отметка публикации «нравится».",
    response_description="Публикация добавлена в список понравившихся.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Публикация не найдена.",
            "model": PydanticError,
        },
        status.HTTP_403_FORBIDDEN: {"description": "Попытка отметить свою публикацию."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def like(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Добавление публикации (твита) в список понравившихся (лайк) текущего пользователя (себя). Попытка добавить
    уже присутствующую публикацию не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому —
    публикация отмечена.
    """
    await service.like(id_, user.id)


@router.delete(
    "/{id}/likes",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена отметки публикации «нравится».",
    response_description="Публикация удалена из списка понравившихся.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": PydanticError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Публикация не найдена.",
            "model": PydanticError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[PydanticError],
        },
    },
)
async def unlike(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Удаление публикации (твита) из списка понравившихся (лайк) текущего пользователя (себя). Попытка удалить
    отсутствующую публикацию не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому —
    публикация не отмечена.
    """
    await service.unlike(id_, user.id)
