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
