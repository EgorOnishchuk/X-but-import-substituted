from fastapi import UploadFile

from src.medias.repositories import MediaRepository
from src.medias.schemas import PydanticMedia


class MediaService:
    def __init__(self, repository: MediaRepository) -> None:
        self._repository: MediaRepository = repository

    async def save(self, file: UploadFile) -> PydanticMedia:
        return await self._repository.save(file)
