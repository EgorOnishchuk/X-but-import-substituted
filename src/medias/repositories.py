from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from src.medias.schemas import PydanticMedia


class MediaRepository(ABC):
    @abstractmethod
    async def save(self, file: UploadFile) -> PydanticMedia:
        pass


class FileSystemMediaRepository(MediaRepository):
    """
    Концепция репозитория — хранилище, но необязательно БД. В данном случае — ФС.
    """

    def __init__(self, dir_: Path) -> None:
        self._dir: Path = dir_

    async def save(self, file: UploadFile) -> PydanticMedia:
        suffix = Path(file.filename).suffix
        path = (self._dir / str(uuid4())).with_suffix(suffix)

        async with aiofiles.open(path, "wb") as out_file:
            await out_file.write(await file.read())

        return PydanticMedia(name=path.name)
