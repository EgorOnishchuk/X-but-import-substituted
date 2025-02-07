"""
Зависимости медиафайлов.
"""

from typing import Annotated

from fastapi import Depends

from src.medias.services import FileSystemMediaRepository, MediaService
from src.settings import STATIC


def get_media_service() -> MediaService:
    return MediaService(FileSystemMediaRepository(STATIC))


Service = Annotated[MediaService, Depends(get_media_service)]
