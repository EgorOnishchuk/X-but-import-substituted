from typing import Annotated

from fastapi import Depends

from src.medias.repositories import FileSystemMediaRepository
from src.medias.services import MediaService
from src.settings import source_settings


def get_media_service() -> MediaService:
    return MediaService(FileSystemMediaRepository(source_settings.medias))


Service = Annotated[MediaService, Depends(get_media_service)]
