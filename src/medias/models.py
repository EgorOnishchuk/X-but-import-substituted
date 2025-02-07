"""
Модели медиафайлов.
"""

from dataclasses import dataclass
from uuid import UUID

from src.models import DataModel


class DataMedia(DataModel):
    readable_name: str = "media"


@dataclass
class FileSystemMedia(DataMedia):
    id: UUID
