"""Module containing the store classes"""
from typing import Any
from typing import Dict
from typing import Optional

from pydantic_aioredis.abstract import _AbstractStore
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.model import Model
from redis import asyncio as aioredis


class Store(_AbstractStore):
    """
    A store that allows a declarative way of querying for data in redis
    """

    models: Dict[str, type(Model)] = {}

    def __init__(
        self,
        name: str,
        redis_config: RedisConfig,
        redis_store: Optional[aioredis.Redis] = None,
        life_span_in_seconds: Optional[int] = None,
        **data: Any,
    ):
        super().__init__(
            name=name,
            redis_config=redis_config,
            redis_store=redis_store,
            life_span_in_seconds=life_span_in_seconds,
            **data,
        )
        self.redis_store = aioredis.from_url(
            self.redis_config.redis_url,
            encoding=self.redis_config.encoding,
            decode_responses=True,
        )

    def register_model(self, model_class: type(Model)):
        """Registers the model to this store"""
        if not isinstance(model_class.get_primary_key_field(), str):
            raise NotImplementedError(
                f"{model_class.__name__} should have a _primary_key_field"
            )

        model_class._store = self
        self.models[model_class.__name__.lower()] = model_class

    def model(self, name: str) -> Model:
        """Gets a model by name: case insensitive"""
        return self.models[name.lower()]
