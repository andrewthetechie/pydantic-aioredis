from typing import List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.ext.FastAPI import FastAPIModel
from pydantic_aioredis.store import Store


class Model(FastAPIModel):
    _primary_key_field = "name"
    name: str


@pytest.fixture()
async def test_app(redis_server):
    store = Store(
        name="sample",
        redis_config=RedisConfig(port=redis_server, db=1),  # nosec
        life_span_in_seconds=3600,
    )
    store.register_model(Model)

    app = FastAPI()

    @app.get("/", response_model=List[Model])
    async def get_endpoint():
        return await Model.select_or_404()

    yield store, app


@pytest.mark.asyncio
async def test_select_or_404_404(test_app):
    """Tests that select_or_404 will raise a 404 error on an empty return"""
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_select_or_404_200(test_app):
    """Tests that select_or_404 will return a model when that model exists"""
    await Model.insert(Model(name="test"))
    async with AsyncClient(app=test_app[1], base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test"
