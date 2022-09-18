"""Tests for the redis orm"""
import asyncio
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
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.model import Model
from pydantic_aioredis.store import Store


class Book(Model):
    _primary_key_field: str = "title"
    title: str
    author: str
    published_on: date
    in_stock: bool = True


books = [
    Book(
        title="Oliver Twist",
        author="Charles Dickens",
        published_on=date(year=1215, month=4, day=4),
        in_stock=False,
    ),
    Book(
        title="Great Expectations",
        author="Charles Dickens",
        published_on=date(year=1220, month=4, day=4),
    ),
    Book(
        title="Jane Eyre",
        author="Charles Dickens",
        published_on=date(year=1225, month=6, day=4),
        in_stock=False,
    ),
    Book(
        title="Wuthering Heights",
        author="Jane Austen",
        published_on=date(year=1600, month=4, day=4),
    ),
]

editions = ["first", "second", "third", "hardbound", "paperback", "ebook"]


class ExtendedBook(Book):
    editions: List[Optional[str]]


class ModelWithNone(Model):
    _primary_key_field = "name"
    name: str
    optional_field: Optional[str]


class ModelWithIP(Model):
    _primary_key_field = "name"
    name: str
    ip_network: IPv4Network


class ModelWithPrefix(Model):
    _primary_key_field = "name"
    _redis_prefix = "prefix"
    name: str


class ModelWithSeparator(Model):
    _primary_key_field = "name"
    _redis_separator = "!!"
    name: str


class ModelWithTableName(Model):
    _primary_key_field = "name"
    _table_name = "tablename"
    name: str


class ModelWithFullCustomKey(Model):
    _primary_key_field = "name"
    _redis_prefix = "prefix"
    _redis_separator = "!!"
    _table_name = "custom"
    name: str


extended_books = [
    ExtendedBook(**book.dict(), editions=sample(editions, randint(0, len(editions))))
    for book in books
]
extended_books[0].editions = list()

test_models = [
    ModelWithNone(name="test", optional_field="test"),
    ModelWithNone(name="test2"),
]

test_ip_models = [
    ModelWithIP(name="test", ip_network=ip_network("10.10.0.0/24")),
    ModelWithIP(name="test2", ip_network=ip_network("192.168.0.0/16")),
]

test_models_with_prefix = [
    ModelWithPrefix(name="test"),
    ModelWithPrefix(name="test2"),
]

test_models_with_separator = [
    ModelWithSeparator(name="test"),
    ModelWithSeparator(name="test2"),
]


test_models_with_tablename = [
    ModelWithTableName(name="test"),
    ModelWithTableName(name="test2"),
]

test_models_with_fullcustom = [
    ModelWithFullCustomKey(name="test"),
    ModelWithFullCustomKey(name="test2"),
]


@pytest_asyncio.fixture()
async def redis_store(redis_server):
    """Sets up a redis store using the redis_server fixture and adds the book model to it"""
    store = Store(
        name="sample",
        redis_config=RedisConfig(port=redis_server, db=1),  # nosec
        life_span_in_seconds=3600,
    )
    store.register_model(Book)
    store.register_model(ExtendedBook)
    store.register_model(ModelWithNone)
    store.register_model(ModelWithIP)
    store.register_model(ModelWithPrefix)
    store.register_model(ModelWithSeparator)
    store.register_model(ModelWithTableName)
    store.register_model(ModelWithFullCustomKey)
    yield store
    await store.redis_store.flushall()


parameters = [
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        books,
        Book,
        "book:",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        extended_books,
        ExtendedBook,
        "extendedbook:",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        test_models,
        ModelWithNone,
        "modelwithnone:",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        test_ip_models,
        ModelWithIP,
        "modelwithip:",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        test_models_with_prefix,
        ModelWithPrefix,
        "prefix:modelwithprefix:",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        test_models_with_separator,
        ModelWithSeparator,
        "modelwithseparator!!",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        test_models_with_tablename,
        ModelWithTableName,
        "tablename:",
    ),
    (
        pytest.lazy_fixture("redis_store"),
        pytest.lazy_fixture("aio_benchmark"),
        test_models_with_fullcustom,
        ModelWithFullCustomKey,
        "prefix!!custom!!",
    ),
]


@pytest_asyncio.fixture
async def aio_benchmark(benchmark, event_loop):
    def _wrapper(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):

            @benchmark
            def _():
                return event_loop.run_until_complete(func(*args, **kwargs))

        else:
            benchmark(func, *args, **kwargs)

    return _wrapper


async def import_benchmark(rs, model_class, models):
    await model_class.insert(models)


@pytest.mark.parametrize("rs, ab, models, model_class, key_prefix", parameters)
def test_bulk_insert(rs, ab, models, model_class, key_prefix):
    ab(import_benchmark, rs, model_class, models)
