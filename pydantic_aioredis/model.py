"""Module containing the model classes"""
from collections.abc import Generator
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic_aioredis.abstract import _AbstractModel
from pydantic_aioredis.utils import bytes_to_string


class Model(_AbstractModel):
    """
    The section in the store that saves rows of the same kind
    """

    @classmethod
    def __get_primary_key(cls, primary_key_value: Any):
        """
        Returns the primary key value concatenated to the table name for uniqueness
        """
        table_name = cls.__name__.lower()
        return f"{table_name}_%&_{primary_key_value}"

    @classmethod
    def get_table_index_key(cls):
        """Returns the key in which the primary keys of the given table have been saved"""
        table_name = cls.__name__.lower()
        return f"{table_name}__index"

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

            if isinstance(data, list):
                data_list = data
            elif isinstance(data, _AbstractModel):
                data_list = [data]

            for record in data_list:
                primary_key_value = getattr(record, cls._primary_key_field)
                name = cls.__get_primary_key(primary_key_value=primary_key_value)
                mapping = cls.serialize_partially(record.dict())
                print(name)
                print(mapping)
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

    @classmethod
    async def update(
        cls, _id: Any, data: Dict[str, Any], life_span_seconds: Optional[int] = None
    ):
        """
        Updates a given row or sets of rows in the table
        """
        life_span = (
            life_span_seconds
            if life_span_seconds is not None
            else cls._store.life_span_in_seconds
        )
        async with cls._store.redis_store.pipeline(transaction=True) as pipeline:

            if isinstance(data, dict):
                name = cls.__get_primary_key(primary_key_value=_id)
                pipeline.hset(name=name, mapping=cls.serialize_partially(data))
                if life_span is not None:
                    pipeline.expire(name=name, time=life_span)
                # save the primary key in an index
                table_index_key = cls.get_table_index_key()
                pipeline.sadd(table_index_key, name)
                if life_span is not None:
                    pipeline.expire(table_index_key, time=life_span)
            response = await pipeline.execute()
        return response

    @classmethod
    async def delete(cls, ids: Union[Any, List[Any]] = None):
        """
        deletes a given row or sets of rows in the table
        """
        table_index_key = cls.get_table_index_key()
        async with cls._store.redis_store.pipeline(transaction=True) as pipeline:
            if ids is not None:
                if not isinstance(ids, list):
                    ids = [ids]
                keys = [
                    cls.__get_primary_key(primary_key_value=primary_key_value)
                    for primary_key_value in ids
                ]
            if ids is None:
                keys_generator = cls._store.redis_store.sscan_iter(name=table_index_key)
                if isinstance(keys_generator, Generator):
                    keys = [key for key in keys_generator]
                else:
                    keys = [key async for key in keys_generator]

            if len(keys) == 0:
                return None
            pipeline.delete(*keys)
            # remove the primary keys from the index
            pipeline.srem(table_index_key, *keys)
            response = await pipeline.execute()
        return response

    @classmethod
    async def select(
        cls, columns: Optional[List[str]] = None, ids: Optional[List[Any]] = None
    ) -> Optional[List[Any]]:
        """
        Selects given rows or sets of rows in the table
        """
        async with cls._store.redis_store.pipeline() as pipeline:
            if ids is None:
                # get all keys in the table immediately so don't use a pipeline
                table_index_key = cls.get_table_index_key()
                keys = cls._store.redis_store.sscan_iter(name=table_index_key)
            else:
                keys = (
                    cls.__get_primary_key(primary_key_value=primary_key)
                    for primary_key in ids
                )
            if isinstance(keys, Generator):
                for key in keys:
                    if columns is None:
                        pipeline.hgetall(name=key)
                    else:
                        pipeline.hmget(name=key, keys=columns)
            else:
                async for key in keys:
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
            result = [cls(**cls.deserialize_partially(record)) for record in response]
        else:
            result = [
                cls.deserialize_partially(
                    {
                        field: bytes_to_string(record[index])
                        for index, field in enumerate(columns)
                    }
                )
                for record in response
            ]
        return result
