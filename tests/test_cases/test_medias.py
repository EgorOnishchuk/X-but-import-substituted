from pathlib import Path
from random import randint
from tempfile import SpooledTemporaryFile
from typing import Type

import pytest
from faker import Faker
from fastapi import UploadFile
from PIL import Image

from src.medias.services import FileSystemMediaRepository, MediaService
from tests.test_cases.test_model import TestModel


class TestMedias(TestModel):
    service: Type[MediaService] = MediaService
    repository: Type[FileSystemMediaRepository] = FileSystemMediaRepository

    @pytest.fixture(autouse=True)
    def set_service(self, tmp_path: Path) -> None:
        self.test_service = self.service(self.repository(tmp_path))

    @pytest.fixture
    def img(self) -> UploadFile:
        img_ = Image.new(
            "RGB", (randint(100, 1000), randint(100, 1000)), Faker().color_rgb()
        )

        file = SpooledTemporaryFile()
        img_.save(file, "PNG")
        file.seek(0)

        return UploadFile(file=file, filename=Faker().file_name("image"))

    @pytest.mark.asyncio
    async def test_save(self, img: UploadFile) -> None:
        await self.test_service.save(img)
