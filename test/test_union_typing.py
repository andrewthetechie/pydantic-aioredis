"""Tests from https://github.com/andrewthetechie/pydantic-aioredis/issues/379"""
from typing import Union

import pytest
from pydantic import BaseModel
from pydantic_aioredis.model import Model


class FloatIntTest(Model):
    _primary_key_field: str = "key"

    key: str
    float_int: Union[float, int]  # fails
    # float_int: Optional[Union[float,int]] # passes
    # float_int: Union[Optional[float],Optional[int]] # fails


class IntFloatTest(Model):
    _primary_key_field: str = "key"

    key: str
    int_float: Union[int, float]  # fails
    # int_float: Optional[Union[int,float]] # fails
    # int_float: Union[Optional[int],Optional[float]] # fails


"""Integers gets cast into floats unintentionally"""


@pytest.mark.asyncio
@pytest.mark.union_test
@pytest.mark.xfail
async def test_float_int_assign_inside(redis_store):
    redis_store.register_model(FloatIntTest)
    key = "test_float_int"
    instance = FloatIntTest(
        key=key,
        float_int=2,  # gets cast to 2.0
    )
    await instance.save()  # this operation doesn't affect the test outcome
    # Fails !
    assert isinstance(instance.float_int, int)


@pytest.mark.asyncio
@pytest.mark.union_test
@pytest.mark.xfail
async def test_float_int_assign_inside_pydantic_only():
    class FloatIntTestPydantic(BaseModel):

        key: str
        float_int: Union[float, int]  # fails
        # float_int: Optional[Union[float,int]] # passes
        # float_int: Union[Optional[float],Optional[int]] # fails

    key = "test_float_int"
    instance = FloatIntTestPydantic(
        key=key,
        float_int=2,  # gets cast to 2.0
    )
    assert isinstance(instance.float_int, int)


@pytest.mark.asyncio
@pytest.mark.union_test
async def test_float_int_assign_after(redis_store):
    key = "test_float_int_assign_after"
    instance = FloatIntTest(
        key=key,
        float_int=2,  # gets cast to 2.0
    )
    print(f"{instance.float_int=}")  # is float here
    instance.float_int = 1
    # Passes !
    assert isinstance(instance.float_int, int)


"""Floats gets cast (and truncated) into integers unintentionally"""


@pytest.mark.asyncio
@pytest.mark.union_test
@pytest.mark.xfail
async def test_int_float_assign_inside(redis_store):
    key = "test_int_float_assign_inside"
    redis_store.register_model(IntFloatTest)
    instance = IntFloatTest(
        key=key,
        int_float=2.9,  # gets cast into and truncated to 2
    )
    await instance.save()  # this operation doesn't affect the test outcome
    # Fails !
    assert isinstance(instance.int_float, float)


@pytest.mark.asyncio
@pytest.mark.union_test
@pytest.mark.xfail
async def test_int_float_assign_inside_pydantic_only():
    class IntFloatTestPydantic(BaseModel):
        key: str
        int_float: Union[int, float]  # fails
        # int_float: Optional[Union[int,float]] # fails
        # int_float: Union[Optional[int],Optional[float]] # fails

    key = "test_int_float_assign_inside"
    instance = IntFloatTestPydantic(
        key=key,
        int_float=2.9,  # gets cast into and truncated to 2
    )
    # Fails !
    assert isinstance(instance.int_float, float)


@pytest.mark.asyncio
@pytest.mark.union_test
async def test_int_float_assign_after(redis_store):
    key = "test_int_float_assign_after"
    instance = IntFloatTest(
        key=key,
        int_float=2.9,
    )
    print(f"{instance.int_float=}")
    instance.int_float = 1.9
    # Passes !
    assert isinstance(instance.int_float, float)
