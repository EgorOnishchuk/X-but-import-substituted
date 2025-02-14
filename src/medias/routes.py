from fastapi import APIRouter, UploadFile, status

from src.medias.dependencies import Service
from src.medias.schemas import PydanticMedia
from src.schemas import PydanticError
from src.users.dependencies import CurrentUser

router = APIRouter(prefix="/medias", tags=["Изображения"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка изображения.",
    response_description="Изображение загружено.",
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
async def upload(
    file: UploadFile, service: Service, user: CurrentUser
) -> PydanticMedia:
    """
    Загрузка изображения. Является предварительным этапом для последующего создания публикации. Для получения
    загруженного изображения см. раздел «Статические файлы».
    """
    return await service.save(file)
