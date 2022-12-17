"""Tests for the AutoModel"""
from datetime import date
from enum import Enum
from ipaddress import ip_network
from ipaddress import IPv4Network
from random import randint
from random import sample
from typing import List
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.model import AutoModel
from pydantic_aioredis.store import Store


class Book(AutoModel):
    _primary_key_field: str = "title"
    title: str
    author: str
    published_on: date
    in_stock: bool = True


@pytest_asyncio.fixture()
async def redis_store():
    """Sets up a redis store using the redis_server fixture and adds the book model to it"""
    store = Store(
        name="sample",
        redis_config=RedisConfig(port=1024, db=1),  # nosec
        life_span_in_seconds=3600,
    )
    store.redis_store = FakeRedis(decode_responses=True)
    store.register_model(Book)
    yield store
    await store.redis_store.flushall()


async def test_auto_save(redis_store):
    """Tests that the auto save feature works"""
    book = Book(
        title="Oliver Twist",
        author="Charles Dickens",
        published_on=date(year=1215, month=4, day=4),
        in_stock=False,
    )
    key = f"book:{getattr(book, type(book)._primary_key_field)}"

    book_in_redis = await redis_store.redis_store.hgetall(name=key)
    book_deser = Book(**Book.deserialize_partially(book_in_redis))
    assert book == book_deser


async def test_auto_sync(redis_store):
    """Tests that the auto sync feature works"""
    book = Book(
        title="Oliver Twist",
        author="Charles Dickens",
        published_on=date(year=1215, month=4, day=4),
        in_stock=False,
    )
    key = f"book:{getattr(book, type(book)._primary_key_field)}"

    book_in_redis = await redis_store.redis_store.hgetall(name=key)
    book_deser = Book(**Book.deserialize_partially(book_in_redis))
    assert book == book_deser

    book.in_stock = True
    book_in_redis = await redis_store.redis_store.hgetall(name=key)
    book_deser = Book(**Book.deserialize_partially(book_in_redis))
    assert book_deser.in_stock
