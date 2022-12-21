"""Module containing the model classes"""
import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
from sys import version_info
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import nest_asyncio
from pydantic_aioredis.abstract import _AbstractModel
from pydantic_aioredis.utils import bytes_to_string


class Model(_AbstractModel):
    """
    The section in the store that saves rows of the same kind

    Model has some custom fields you can set in your models that alter the behavior of how this is stored in redis

    _primary_key_field -- The field of your model that is the primary key
    _redis_prefix -- If set, will be added to the beginning of the keys we store in redis
    _redis_separator -- Defaults to :, used to separate prefix, table_name, and primary_key
    _table_name -- Defaults to the model's name, can set a custom name in redis


    If your model was named ThisModel, the primary key was "key", and prefix and separator were left at default (not set), the
    keys stored in redis would be
    thismodel:key
    """

    _auto_sync = False
    _auto_save = False

    def __init__(self, **data: Any) -> None:
        auto_save = (
            data.pop("auto_save")
            if "auto_save" in data.keys()
            else getattr(self, "_auto_save", False)
        )
        auto_sync = (
            data.pop("auto_sync")
            if "auto_sync" in data.keys()
            else getattr(self, "_auto_sync", False)
        )
        super().__init__(**data)
        # set _auto_save and _auto_sync to the class defaults in the Config
        self.Config.auto_sync = auto_sync
        self.Config.auto_save = auto_save
        # If this instance is _auto_save, save it
        if self.auto_save and getattr(self, "_store", None) is not None:
            self.__save_from_sync()

    def __setattr__(self, name: str, value: Any):
        """
        This overrides __setattr__ to allow for auto_sync
        because __setattr__ has be to sync, this uses a hack to call the async save method

        """
        super().__setattr__(name, value)
        if self._auto_sync and getattr(self, "_store", None) is not None:
            self.__save_from_sync()

    def __save_from_sync(self):
        """Calls the async save coroutine from a sync context, used with _auto_save and _auto_sync"""
        if version_info.minor < 10:  # pragma: no cover
            # less than 3.10.0
            io_loop = asyncio.get_event_loop()
        else:  # pragma: no cover
            # equal or greater than 3.10.0
            try:
                io_loop = asyncio.get_running_loop()
                # https://github.com/erdewit/nest_asyncio
                # Use nest_asyncio so we can call the async save
            except RuntimeError:
                io_loop = asyncio.new_event_loop()
        nest_asyncio.apply()
        io_loop.run_until_complete(self.save())

    @asynccontextmanager
    async def update(self):
        """
        Async Context manager to allow for updating multiple fields without syncing to redis until the end
        """
        auto_sync = self.auto_sync
        if auto_sync:
            self.set_auto_sync(False)
        yield self
        if getattr(self, "_store", None) is not None:
            await self.save()
        if auto_sync != self.auto_sync:
            self.set_auto_sync(auto_sync)

    @property
    def auto_sync(self) -> bool:
        return getattr(self.Config, "auto_sync", False)

    def set_auto_sync(self, auto_sync: bool = True) -> None:
        """Change this instance of a model's _auto_sync setting"""
        self.Config.auto_sync = auto_sync

    @property
    def auto_save(self) -> bool:
        return getattr(self.Config, "auto_save", False)

    def set_auto_save(self, auto_save: bool = True) -> None:
        """Change this instance of a model's _auto_save setting"""
        self.Config.auto_save = auto_save

    @classmethod
    @lru_cache(1)
    def _get_prefix(cls) -> str:
        prefix_str = getattr(cls, "_redis_prefix", "").lower()
        return f"{prefix_str}{cls._get_separator()}" if prefix_str != "" else ""

    @classmethod
    @lru_cache(1)
    def _get_separator(cls):
        return getattr(cls, "_redis_separator", ":").lower()

    @classmethod
    @lru_cache(1)
    def _get_tablename(cls):
        return cls.__name__.lower() if cls._table_name is None else cls._table_name

    @classmethod
    @lru_cache(1)
    def __get_primary_key(cls, primary_key_value: Any):
        """
        Uses _table_name, _table_refix, and _redis_separator from the model to build our primary key.

        _table_name defaults to the name of the model class if it is not set
        _redis_separator defualts to : if it is not set
        _prefix defaults to nothing if it is not set

        The key is contructed as {_prefix}{_redis_separator}{_table_name}{_redis_separator}{primary_key_value}
        So a model named ThisModel with a primary key of id, by default would result in a key of thismodel:id
        """

        return f"{cls._get_prefix()}{cls._get_tablename()}{cls._get_separator()}{primary_key_value}"

    @classmethod
    def get_table_index_key(cls):
        """Returns the key in which the primary keys of the given table have been saved"""
        return f"{cls._get_prefix()}{cls._get_tablename()}{cls._get_separator()}__index"

    @classmethod
    async def _ids_to_primary_keys(
        cls, ids: Optional[Union[Any, List[Any]]] = None
    ) -> Tuple[List[Optional[str]], str]:
        """Turn passed in ids into primary key values"""
        table_index_key = cls.get_table_index_key()
        if ids is None:
            keys_generator = cls._store.redis_store.sscan_iter(name=table_index_key)
            keys = [key async for key in keys_generator]
        else:
            if not isinstance(ids, list):
                ids = [ids]
            keys = [
                cls.__get_primary_key(primary_key_value=primary_key_value)
                for primary_key_value in ids
            ]
        keys.sort()
        return keys, table_index_key

    @classmethod
    async def insert(
        cls,
        data: Union[List[_AbstractModel], _AbstractModel],
        life_span_seconds: Optional[int] = None,
    ):
        """
        Inserts a given row or sets of rows into the table
        """
        life_span = (
            life_span_seconds
            if life_span_seconds is not None
            else cls._store.life_span_in_seconds
        )
        async with cls._store.redis_store.pipeline(transaction=True) as pipeline:
            data_list = []

            data_list = [data] if not isinstance(data, list) else data

            for record in data_list:
                primary_key_value = getattr(record, cls._primary_key_field)
                name = cls.__get_primary_key(primary_key_value=primary_key_value)
                mapping = cls.serialize_partially(record.dict())
                pipeline.hset(name=name, mapping=mapping)

                if life_span is not None:
                    pipeline.expire(name=name, time=life_span)
                # save the primary key in an index
                table_index_key = cls.get_table_index_key()
                pipeline.sadd(table_index_key, name)
                if life_span is not None:
                    pipeline.expire(table_index_key, time=life_span)
            response = await pipeline.execute()

        return response

    async def save(self):
        await self.insert(self)

    @classmethod
    async def delete(
        cls, ids: Optional[Union[Any, List[Any]]] = None
    ) -> Optional[List[int]]:
        """
        deletes a given row or sets of rows in the table
        """
        keys, table_index_key = await cls._ids_to_primary_keys(ids)
        if len(keys) == 0:
            return None
        async with cls._store.redis_store.pipeline(transaction=True) as pipeline:
            pipeline.delete(*keys)
            # remove the primary keys from the index
            pipeline.srem(table_index_key, *keys)
            response = await pipeline.execute()
        return response

    @classmethod
    async def select(
        cls,
        columns: Optional[List[str]] = None,
        ids: Optional[List[Any]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Optional[List[Any]]:
        """
        Selects given rows or sets of rows in the table

        Pagination is accomplished by using the below variables
            skip: Optional[int]
            limit: Optional[int]
        """
        all_keys, _ = await cls._ids_to_primary_keys(ids)
        if limit is not None and skip is not None:
            limit = limit + skip
        keys = all_keys[skip:limit]
        async with cls._store.redis_store.pipeline() as pipeline:
            for key in keys:
                if columns is None:
                    pipeline.hgetall(name=key)
                else:
                    pipeline.hmget(name=key, keys=columns)

            response = await pipeline.execute()

        if len(response) == 0:
            return None

        if response[0] == {}:
            return None

        if isinstance(response, list) and columns is None:
            result = [
                cls(**cls.deserialize_partially(record))
                for record in response
                if record != {}
            ]
        else:
            result = [
                cls.deserialize_partially(
                    {
                        field: bytes_to_string(record[index])
                        for index, field in enumerate(columns)
                    }
                )
                for record in response
                if record != {}
            ]
        return result


class AutoModel(Model):
    """A model that automatically saves to redis on creation and syncs changing fields to redis"""

    _auto_sync: bool = True
    _auto_save: bool = True
