"""Entry point for pydantic-aioredis"""
from .config import RedisConfig  # noqa: F401
from .model import Model  # noqa: F401
from .store import Store  # noqa: F401

__version__ = "0.1.0"