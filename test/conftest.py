import pytest
import pytest_asyncio
import redislite
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.model import Model
from pydantic_aioredis.store import Store


@pytest_asyncio.fixture()
def redis_server(unused_tcp_port):
    """Sets up a fake redis server we can use for tests"""
    instance = redislite.Redis(serverconfig={"port": unused_tcp_port})

    yield unused_tcp_port

    instance.close()
    instance.shutdown()


@pytest_asyncio.fixture()
async def redis_store(redis_server):
    """Sets up a redis store using the redis_server fixture and adds the book model to it"""
    store = Store(
        name="sample",
        redis_config=RedisConfig(port=redis_server, db=1),  # nosec
        life_span_in_seconds=3600,
    )
    yield store
    await store.redis_store.flushall()


def pytest_configure(config):
    """Configure our markers"""
    config.addinivalue_line("markers", "union_test: Tests for union types")
