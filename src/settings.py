import re
from pathlib import Path
from typing import Annotated, Any, Generic, TypeVar

from faker import Faker
from pydantic import (
    AfterValidator,
    Field,
    HttpUrl,
    MariaDBDsn,
    MySQLDsn,
    NonNegativeInt,
    PositiveInt,
    PostgresDsn,
    RedisDsn,
)
from pydantic_extra_types.semantic_version import SemanticVersion
from pydantic_settings import BaseSettings, SettingsConfigDict

type DBDsn = PostgresDsn | MySQLDsn | MariaDBDsn | RedisDsn
T = TypeVar("T", bound=DBDsn)

ROUTE: re.Pattern[str] = re.compile(r"^/\S*$")

EXAMPLES: Faker = Faker("ru_RU")


def _to_str(value: Any) -> str:
    return str(value)


def _to_strings(values: list[Any]) -> list[str]:
    return list(map(_to_str, values))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


class APISettings(Settings):
    title: Annotated[str, Field(min_length=1, max_length=50)]
    summary: Annotated[str, Field(min_length=5, max_length=100)]
    description: Annotated[str, Field(min_length=5, max_length=500)]
    version: Annotated[SemanticVersion, AfterValidator(_to_str)]

    openapi: Annotated[str | None, AfterValidator(_to_str)] = Field(
        default="/openapi.json", alias="openapi_url", pattern=ROUTE
    )
    docs: Annotated[str | None, AfterValidator(_to_str)] = Field(
        default="/docs", alias="docs_url", pattern=ROUTE
    )
    redoc: Annotated[str | None, AfterValidator(_to_str)] = Field(
        default="/redoc", alias="redoc_url", pattern=ROUTE
    )


class DBSettings(Settings, Generic[T]):
    url: Annotated[T, AfterValidator(_to_str)]
    pool_size: PositiveInt = 100
    max_overflow: NonNegativeInt = 0
    is_pool_pre_ping: bool = False


class SourceSettings(Settings):
    root: Path = Path(__file__).parent.parent

    static: Path = root / "static"
    templates: Path = static / "templates"
    styles: Path = static / "styles"
    scripts: Path = static / "scripts"
    medias: Path = static / "medias"


class CORSSettings(Settings):
    allowed_origins: Annotated[list[HttpUrl], AfterValidator(_to_strings)] = Field(
        default_factory=list, alias="allow_origins"
    )
    allowed_origin_regex: Annotated[str, Field(default="", alias="allow_origin_regex")]
    allowed_methods: Annotated[
        list[str], Field(default_factory=list, alias="allow_methods")
    ]
    allowed_headers: Annotated[
        list[str], Field(default_factory=list, alias="allow_headers")
    ]
    is_credentials: Annotated[bool, Field(default=False, alias="allow_credentials")]
    exposed_headers: Annotated[
        list[str], Field(default_factory=list, alias="expose_headers")
    ]
    cache_time: Annotated[int, Field(default=600, alias="max_age")]


api_settings = APISettings()  # type: ignore
db_settings = DBSettings[PostgresDsn]()  # type: ignore
source_settings = SourceSettings()  # type: ignore
cors_settings = CORSSettings()  # type: ignore
