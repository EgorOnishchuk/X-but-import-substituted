from pathlib import Path
from random import randint
from tempfile import SpooledTemporaryFile
from typing import Type

import pytest
from fastapi import UploadFile
from PIL import Image

from src.medias.repositories import FileSystemMediaRepository
from src.medias.services import MediaService
from src.settings import EXAMPLES
from tests.test_cases.test_model import TestModel


class TestMedias(TestModel):
    service: Type[MediaService] = MediaService
    repository: Type[FileSystemMediaRepository] = FileSystemMediaRepository

    @pytest.fixture(autouse=True)
    def set_service(self, tmp_path: Path) -> None:
        self.test_service = self.service(self.repository(tmp_path))

    @pytest.fixture
    def img_with_ext(self) -> tuple[UploadFile, str]:
        img_ = Image.new(
            "RGB", (randint(100, 1000), randint(100, 1000)), EXAMPLES.color_rgb()
        )

        file = SpooledTemporaryFile()
        img_.save(file, "PNG")
        file.seek(0)

        name = EXAMPLES.file_name("image")
        return UploadFile(file=file, filename=name), Path(name).suffix

    @pytest.mark.asyncio
    async def test_save(self, img_with_ext: tuple[UploadFile, str]) -> None:
        img, ext = img_with_ext

        assert ext in (await self.test_service.save(img)).name
