"""Test methods in model.py. Uses hypothesis"""

from typing import Dict
from typing import List

from fakeredis.aioredis import FakeRedis
from pydantic_aioredis.config import RedisConfig
from pydantic_aioredis.model import Model
from pydantic_aioredis.store import Store


class SimpleModel(Model):
    _primary_key_field: str = "test_str"
    test_str: str


async def test_update_sets_autosync_save():
    """Test that update sets autosync to false"""
    model = SimpleModel(test_str="test")
    model.set_auto_sync()
    async with model.update() as cm:
        assert cm._auto_sync is False
    assert model.auto_sync


def test_set_auto_sync():
    """Test that set_auto_sync sets the autosync attribute"""
    model = SimpleModel(test_str="test")
    assert model.auto_sync is False
    model.set_auto_sync()
    assert model.auto_sync
    model.set_auto_sync(False)
    assert model.auto_sync is False


def test_set_auto_save():
    """Test that set_auto_save sets the autosave attribute"""
    model = SimpleModel(test_str="test")
    assert model.auto_save is False
    model.set_auto_save()
    assert model.auto_save
    model.set_auto_save(False)
    assert model.auto_save is False


def test_auto_save_in_init():
    """Test that auto_save is set if set in init"""
    model = SimpleModel(test_str="test", auto_save=True)
    assert model.auto_save
    false_model = SimpleModel(test_str="test", auto_save=False)
    assert false_model.auto_save is False


async def test_update_cm():
    """ """
    test_str = "test"
    test_int = 9
    update_int = 27
    update_int = test_int + update_int

    class UpdateModel(Model):
        _primary_key_field: str = "test_str"
        test_str: str
        test_int: int

    # instead of using a fixture, create it in the function because of hypothesis
    #  Function-scoped fixtures are not reset between examples generated by
    # `@given(...)`, which is often surprising and can cause subtle test bugs.
    redis_store = Store(
        name="sample",
        redis_config=RedisConfig(port=1024, db=1),  # nosec
        life_span_in_seconds=3600,
    )
    redis_store.redis_store = FakeRedis(decode_responses=True)
    redis_store.register_model(UpdateModel)
    this_model = UpdateModel(test_str=test_str, test_int=test_int)
    await UpdateModel.insert(this_model)

    async with this_model.update() as cm:
        cm.test_int = update_int
        redis_model = await UpdateModel.select(ids=[test_str])
        assert redis_model[0].test_int == test_int

    redis_model = await UpdateModel.select(ids=[test_str])
    assert redis_model[0].test_int == update_int


async def test_storing_list(redis_store):
    # https://github.com/andrewthetechie/pydantic-aioredis/issues/403
    class DataTypeTest(Model):
        _primary_key_field: str = "key"

        key: str
        value: List[int]

    redis_store.register_model(DataTypeTest)
    key = "test_list_storage"
    instance = DataTypeTest(
        key=key,
        value=[1, 2, 3],
    )
    await instance.save()

    instance_in_redis = await DataTypeTest.select()
    assert instance_in_redis[0].key == instance.key
    assert len(instance_in_redis[0].value) == len(instance.value)
    for value in instance_in_redis[0].value:
        assert value in instance.value


async def test_storing_dict(redis_store):
    class DataTypeTest(Model):
        _primary_key_field: str = "key"

        key: str
        value: Dict[str, int]

    redis_store.register_model(DataTypeTest)
    key = "test_list_storage"
    instance = DataTypeTest(
        key=key,
        value={"a": 1, "b": 2, "c": 3},
    )
    await instance.save()

    instance_in_redis = await DataTypeTest.select()
    assert instance_in_redis[0].key == instance.key
    assert len(instance_in_redis[0].value.keys()) == len(instance.value.keys())
    for key in instance_in_redis[0].value.keys():
        assert instance.value[key] == instance_in_redis[0].value[key]


async def test_storing_complex_dict(redis_store):
    class DataTypeTest(Model):
        _primary_key_field: str = "key"

        key: str
        value: Dict[str, List[int]]

    redis_store.register_model(DataTypeTest)
    key = "test_list_storage"
    instance = DataTypeTest(
        key=key,
        value={"a": [1], "b": [2, 3], "c": [4, 5, 6]},
    )
    await instance.save()

    instance_in_redis = await DataTypeTest.select()
    assert instance_in_redis[0].key == instance.key
    assert len(instance_in_redis[0].value.keys()) == len(instance.value.keys())
    for key in instance_in_redis[0].value.keys():
        assert instance.value[key] == instance_in_redis[0].value[key]
