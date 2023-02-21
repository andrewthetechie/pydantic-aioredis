import inspect
import os

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from hypothesis import settings
from hypothesis import Verbosity
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.store import Store


@pytest_asyncio.fixture()
async def redis_store():
    """Sets up a redis store using the redis_server fixture and adds the book model to it"""
    store = Store(
        name="sample",
        redis_config=RedisConfig(port=1024, db=1),  # nosec
        life_span_in_seconds=3600,
    )
    store.redis_store = FakeRedis(decode_responses=True)
    yield store
    await store.redis_store.close()


def pytest_configure(config):
    """Configure our markers"""
    config.addinivalue_line("markers", "union_test: Tests for union types")
    config.addinivalue_line("markers", "hypothesis: Tests that use hypothesis")


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Tags all async tests with the asyncio marker"""
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


settings.register_profile("ci", max_examples=5000)
settings.register_profile("dev", max_examples=100)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
