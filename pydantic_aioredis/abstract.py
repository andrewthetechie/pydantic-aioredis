"""Module containing the main base classes"""
import json
from datetime import date
from datetime import datetime
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv6Address
from ipaddress import IPv6Network
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import aioredis
from pydantic import BaseModel
from pydantic.fields import SHAPE_DEFAULTDICT
from pydantic.fields import SHAPE_DICT
from pydantic.fields import SHAPE_FROZENSET
from pydantic.fields import SHAPE_LIST
from pydantic.fields import SHAPE_MAPPING
from pydantic.fields import SHAPE_SEQUENCE
from pydantic.fields import SHAPE_SET
from pydantic.fields import SHAPE_TUPLE
from pydantic.fields import SHAPE_TUPLE_ELLIPSIS

from pydantic_aioredis.config import RedisConfig

JSON_DUMP_SHAPES = [
    SHAPE_LIST,
    SHAPE_SET,
    SHAPE_MAPPING,
    SHAPE_TUPLE,
    SHAPE_TUPLE_ELLIPSIS,
    SHAPE_SEQUENCE,
    SHAPE_FROZENSET,
    SHAPE_DICT,
    SHAPE_DEFAULTDICT,
]


class _AbstractStore(BaseModel):
    """
    An abstract class of a store
    """

    name: str
    redis_config: RedisConfig
    redis_store: aioredis.Redis = None
    life_span_in_seconds: int = None

    class Config:
        """Pydantic schema config for _AbstractStore"""

        arbitrary_types_allowed = True
        orm_mode = True


class _AbstractModel(BaseModel):
    """
    An abstract class to help with typings for Model class
    """

    _store: _AbstractStore
    _primary_key_field: str
    _table_name: Optional[str] = None

    @staticmethod
    def json_default(obj: Any) -> str:
        """
        JSON serializer for objects not serializable by default json library
        Currently handles: datetimes -> obj.isoformat, ipaddress and ipnetwork -> str
        """

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, (IPv4Network, IPv4Address, IPv6Network, IPv6Address)):
            return str(obj)

        raise TypeError("Type %s not serializable" % type(obj))

    @classmethod
    def serialize_partially(cls, data: Dict[str, Any]):
        """Converts data types that are not compatible with Redis into json strings
        by looping through the models fields and inspecting its types.

            str, float, int - will be stored in redis as a string field
            None - will be converted to the string "None"
            More complex data types will be json dumped.

        The json dumper uses class.json_serial as its default serializer.
        Users can override json_serial with a custom json serializer if they chose to.
        Users can override serialze paritally and deserialze partially
        """
        columns = data.keys()
        for field in cls.__fields__:
            # if we're updating a few columns, we might not have all fields, skip ones we dont have
            if field not in columns:
                continue
            if cls.__fields__[field].type_ not in [str, float, int]:
                data[field] = json.dumps(data[field], default=cls.json_default)
            if getattr(cls.__fields__[field], "shape", None) in JSON_DUMP_SHAPES:
                data[field] = json.dumps(data[field], default=cls.json_default)
            if getattr(cls.__fields__[field], "allow_none", False):
                if data[field] is None:
                    data[field] = "None"
        return data

    @classmethod
    def deserialize_partially(cls, data: Dict[bytes, Any]):
        """Converts model fields back from json strings into python data types.

        Users can override serialze paritally and deserialze partially
        """
        columns = data.keys()
        for field in cls.__fields__:
            # if we're selecting a few columns, we might not have all fields, skip ones we dont have
            if field not in columns:
                continue
            if cls.__fields__[field].type_ not in [str, float, int]:
                data[field] = json.loads(data[field])
            if getattr(cls.__fields__[field], "shape", None) in JSON_DUMP_SHAPES:
                data[field] = json.loads(data[field])
            if getattr(cls.__fields__[field], "allow_none", False):
                if data[field] == "None":
                    data[field] = None
        return data

    @classmethod
    def get_primary_key_field(cls):
        """Gets the protected _primary_key_field"""
        return cls._primary_key_field

    @classmethod
    async def insert(
        cls,
        data: Union[List["_AbstractModel"], "_AbstractModel"],
        life_span_seconds: Optional[int] = None,
    ):  # pragma: no cover
        """Insert into the redis store"""
        raise NotImplementedError("insert should be implemented")

    @classmethod
    async def update(
        cls, _id: Any, data: Dict[str, Any], life_span_seconds: Optional[int] = None
    ):  # pragma: no cover
        """Update an existing key in the redis store"""
        raise NotImplementedError("update should be implemented")

    @classmethod
    async def delete(cls, ids: Union[Any, List[Any]]):  # pragma: no cover
        """Delete a key from the redis store"""
        raise NotImplementedError("delete should be implemented")

    @classmethod
    async def select(
        cls, columns: Optional[List[str]] = None, ids: Optional[List[Any]] = None
    ):  # pragma: no cover
        """Select one or more object from the redis store"""
        raise NotImplementedError("select should be implemented")

    class Config:
        """Pydantic schema config for _AbstractModel"""

        arbitrary_types_allowed = True
