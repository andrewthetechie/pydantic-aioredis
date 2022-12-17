from typing import List

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic_aioredis import Model as PAModel
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.ext.FastAPI import PydanticAioredisCRUDRouter
from pydantic_aioredis.store import Store


class Model(PAModel):
    _primary_key_field = "name"
    name: str
    value: int


class ModelNoSync(PAModel):
    _primary_key_field = "name"
    name: str
    value: int
    _auto_sync = False


@pytest_asyncio.fixture()
async def test_app(redis_store):
    redis_store.register_model(Model)

    app = FastAPI()

    router = PydanticAioredisCRUDRouter(schema=Model, store=redis_store)
    app.include_router(router)
    yield redis_store, app, Model
    await redis_store.redis_store.close()


@pytest_asyncio.fixture()
def test_models():
    return [Model(name=f"test{i}", value=i) for i in range(1, 10)]


async def test_crudrouter_get_many_200_empty(test_app):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/model")

    assert response.status_code == 200
    assert response.json() == []


async def test_crudrouter_get_one_404(test_app):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/model/test")

    assert response.status_code == 404


async def test_crudrouter_get_many_200(test_app, test_models):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    await test_app[2].insert(test_models)
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/model")

    assert response.status_code == 200
    result = response.json()
    assert len(result) == len(test_models)


async def test_crudrouter_get_many_200_pagination(test_app, test_models):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    await test_app[2].insert(test_models)
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/model", params={"skip": 2, "limit": 5})

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 5


async def test_crudrouter_get_many_200(test_app, test_models):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    await test_app[2].insert(test_models)
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/model")

    assert response.status_code == 200
    result = response.json()
    assert len(result) == len(test_models)


async def test_crudrouter_get_one_200(test_app, test_models):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    await test_app[2].insert(test_models)
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get(f"/model/{test_models[0].name}")

    assert response.status_code == 200
    result = response.json()
    assert result["name"] == test_models[0].name


async def test_crudrouter_post_200(test_app, test_models):
    """Tests that crudrouter will post properly"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.post(f"/model", json=test_models[0].dict())

    assert response.status_code == 200
    result = response.json()
    assert result["name"] == test_models[0].name


async def test_crudrouter_post_422(test_app, test_models):
    """Tests that crudrouter post will 422 with invalid data"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.post(f"/model", json={"invalid": "stuff"})

    assert response.status_code == 422


async def test_crudrouter_put_404(test_app, test_models):
    """Tests that crudrouter put will 404 when no instance exists"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.put(f"/model/test", json=test_models[0].dict())

    assert response.status_code == 404


async def test_crudrouter_put_200(test_app, test_models):
    """Tests that crudrouter put will 200 on a successful update"""
    await test_app[2].insert(test_models)
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.put(
            f"/model/{test_models[0].name}",
            json={"name": test_models[0].name, "value": 100},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["name"] == test_models[0].name
    assert result["value"] == 100


async def test_crudrouter_put_200_no_autosync(redis_store):
    """Tests that crudrouter put will 404 when no instance exists"""

    redis_store.register_model(ModelNoSync)

    app = FastAPI()

    router = PydanticAioredisCRUDRouter(schema=ModelNoSync, store=redis_store)
    app.include_router(router)
    await ModelNoSync.insert(ModelNoSync(name="test", value=20))
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/modelnosync/test",
            json={"name": "test", "value": 100},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "test"
    assert result["value"] == 100


async def test_crudrouter_put_404(test_app, test_models):
    """Tests that crudrouter put will 404 when no instance exists"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.put(
            f"/model/{test_models[0].name}", json=test_models[0].dict()
        )

    assert response.status_code == 404


async def test_crudrouter_delete_200(test_app, test_models):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    await test_app[2].insert(test_models)
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.delete(f"/model/{test_models[0].name}")

    assert response.status_code == 200
    result = response.json()
    assert result["name"] == test_models[0].name

    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.delete(f"/model")

    assert response.status_code == 200


async def test_crudrouter_delete_404(test_app, test_models):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.delete(f"/model/{test_models[0].name}")

    assert response.status_code == 404
