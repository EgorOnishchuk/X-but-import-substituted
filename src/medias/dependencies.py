"""
Зависимости медиафайлов.
"""

from typing import Annotated

from fastapi import Depends

from src.medias.services import FileSystemMediaRepository, MediaService
from src.settings import MEDIAS


def get_media_service() -> MediaService:
    return MediaService(FileSystemMediaRepository(MEDIAS))


Service = Annotated[MediaService, Depends(get_media_service)]
