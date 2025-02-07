"""
Маршрутизатор публикаций (твитов).
"""

from fastapi import APIRouter, status

from src.schemas import ID, Error
from src.tweets.dependencies import Service
from src.tweets.models import DataTweet
from src.tweets.schemas import TweetDetailed, TweetID, TweetNotDetailed
from src.users.dependencies import CurrentUser

router: APIRouter = APIRouter(prefix="/tweets", tags=["Публикации"])


@router.get(
    "",
    response_model=list[TweetDetailed],
    summary="Получение всех публикаций.",
    response_description="Публикации получены.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _get_list(service: Service, user: CurrentUser) -> list[DataTweet]:
    """
    Получение полного списка публикаций (твитов) от отслеживаемых пользователей.
    """
    return await service.get_all(user)


@router.post(
    "",
    response_model=TweetID,
    status_code=status.HTTP_201_CREATED,
    summary="Создание публикации.",
    response_description="Публикация создана.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _create(
    tweet: TweetNotDetailed, service: Service, user: CurrentUser
) -> DataTweet:
    """
    Создание новой публикации (твита) от лица текущего пользователя (себя).
    """
    return await service.create(tweet, user.id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление публикации.",
    response_description="Публикация удалена.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Публикация не найдена.",
            "model": Error,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Попытка удалить чужую публикацию.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _remove(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Удаление публикации (твита) текущего пользователя (своей). Попытка удалить несуществующую публикацию не вызывает
    ошибок, т.к. результат в любом случае соответствует ожидаемому — публикация отсутствует.
    """
    await service.delete(id_, user.id)


@router.post(
    "/{id}/likes",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отметка публикации «нравится».",
    response_description="Публикация добавлена в список понравившихся.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Публикация не найдена.",
            "model": Error,
        },
        status.HTTP_403_FORBIDDEN: {"description": "Попытка отметить свою публикацию."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _like(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Добавление публикации (твита) в список понравившихся (лайк) текущего пользователя (себя). Попытка добавить
    уже присутствующую публикацию не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому —
    публикация отмечена.
    """
    await service.create_like(id_, user)


@router.delete(
    "/{id}/likes",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена отметки публикации «нравится».",
    response_description="Публикация удалена из списка понравившихся.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Не передан ключ API.",
            "model": Error,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Публикация не найдена.",
            "model": Error,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Неверные данные запроса.",
            "model": list[Error],
        },
    },
)
async def _unlike(id_: ID, service: Service, user: CurrentUser) -> None:
    """
    Удаление публикации (твита) из списка понравившихся (лайк) текущего пользователя (себя). Попытка удалить
    отсутствующую публикацию не вызывает ошибок, т.к. результат в любом случае соответствует ожидаемому —
    публикация не отмечена.
    """
    await service.delete_like(id_, user)
