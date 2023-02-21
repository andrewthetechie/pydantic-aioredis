import pytest_asyncio
import redislite


@pytest_asyncio.fixture()
def redis_server(unused_tcp_port):
    """Sets up a fake redis server we can use for tests"""
    try:
        instance = redislite.Redis(serverconfig={"port": unused_tcp_port})
        yield unused_tcp_port
    finally:
        instance.close()
        instance.shutdown()
