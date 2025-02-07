"""
Слой логики операций с медиафайлами.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from src.medias.models import DataMedia, FileSystemMedia


class MediaRepository(ABC):
    """
    Выполняет операции с файлами в отношении какого-либо хранилища.
    """

    @abstractmethod
    async def save(self, file: UploadFile) -> DataMedia:
        """
        Сохраняет файл в хранилище.
        :param file: Файл.
        :return: Сохранённый файл.
        """


class FileSystemMediaRepository(MediaRepository):
    def __init__(self, dir_: Path) -> None:
        self._dir: Path = dir_

    async def save(self, file: UploadFile) -> FileSystemMedia:
        id_ = uuid4()
        path = (self._dir / str(id_)).with_suffix(Path(file.filename).suffix)

        async with aiofiles.open(path, "wb") as out_file:
            await out_file.write(await file.read())

        return FileSystemMedia(id_)


class MediaService:
    """
    Сервис для работы с медиафайлами.
    """

    def __init__(self, repository: MediaRepository):
        self._repository: MediaRepository = repository

    async def save(self, file: UploadFile) -> DataMedia:
        """
        Сохраняет файл в хранилище.
        :param file: Файл.
        :return: Сохранённый файл.
        """
        return await self._repository.save(file)
