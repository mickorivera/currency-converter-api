import logging
from functools import lru_cache

from pydantic import BaseSettings


class EnvSettings(BaseSettings):
    env: str


class AppSettings(BaseSettings):
    exchange_rate_host: str
    exchange_rate_decimal_places: int = 2

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level: int = logging.INFO


class DevAppSettings(AppSettings):
    class Config:
        env_file = ".dev.env"

    log_level: int = logging.DEBUG


class StgAppSettings(AppSettings):
    class Config:
        env_file = ".stg.env"


class ProdAppSettings(AppSettings):
    class Config:
        env_file = ".prod.env"


@lru_cache
def get_app_settings() -> AppSettings:
    env_settings = EnvSettings()

    return {
        "dev": DevAppSettings,
        "stg": StgAppSettings,
        "prod": ProdAppSettings,
    }.get(env_settings.env.lower(), DevAppSettings)()
