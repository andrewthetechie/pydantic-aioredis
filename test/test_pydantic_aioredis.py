"""Tests for the redis orm"""
from datetime import date
from ipaddress import ip_network
from ipaddress import IPv4Network
from random import randint
from random import sample
from typing import List
from typing import Optional

import pytest

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


@pytest.fixture()
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
    yield store
    await store.redis_store.flushall()


def test_redis_config_redis_url():
    password = "password"
    config_with_no_pass = RedisConfig()
    config_with_ssl = RedisConfig(ssl=True)
    config_with_pass = RedisConfig(password=password)
    config_with_pass_ssl = RedisConfig(ssl=True, password=password)

    assert config_with_no_pass.redis_url == "redis://localhost:6379/0"
    assert config_with_ssl.redis_url == "rediss://localhost:6379/0"
    assert config_with_pass.redis_url == f"redis://:{password}@localhost:6379/0"
    assert config_with_pass_ssl.redis_url == f"rediss://:{password}@localhost:6379/0"


def test_register_model_without_primary_key(redis_store):
    """Throws error when a model without the _primary_key_field class variable set is registered"""

    class ModelWithoutPrimaryKey(Model):
        title: str

    with pytest.raises(AttributeError, match=r"_primary_key_field"):
        redis_store.register_model(ModelWithoutPrimaryKey)

    ModelWithoutPrimaryKey._primary_key_field = None

    with pytest.raises(Exception, match=r"should have a _primary_key_field"):
        redis_store.register_model(ModelWithoutPrimaryKey)


def test_store_model(redis_store):
    """Tests the model method in store"""
    assert redis_store.model("Book") == Book

    with pytest.raises(KeyError):
        redis_store.model("Notabook")


parameters = [
    (pytest.lazy_fixture("redis_store"), books, Book),
    (pytest.lazy_fixture("redis_store"), extended_books, ExtendedBook),
    (pytest.lazy_fixture("redis_store"), test_models, ModelWithNone),
    (pytest.lazy_fixture("redis_store"), test_ip_models, ModelWithIP),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
async def test_bulk_insert(store, models, model_class):
    """Providing a list of Model instances to the insert method inserts the records in redis"""
    keys = [
        f"{type(model).__name__.lower()}_%&_{getattr(model, type(model)._primary_key_field)}"
        for model in models
    ]
    # keys = [f"book_%&_{book.title}" for book in models]
    await store.redis_store.delete(*keys)

    for key in keys:
        book_in_redis = await store.redis_store.hgetall(name=key)
        assert book_in_redis == {}

    await model_class.insert(models)

    async with store.redis_store.pipeline() as pipeline:
        for key in keys:
            pipeline.hgetall(name=key)
        models_in_redis = await pipeline.execute()
    models_deserialized = [
        model_class(**model_class.deserialize_partially(model))
        for model in models_in_redis
    ]
    assert models == models_deserialized


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
async def test_insert_single(store, models, model_class):
    """
    Providing a single Model instance
    """
    key = f"{type(models[0]).__name__.lower()}_%&_{getattr(models[0], type(models[0])._primary_key_field)}"
    model = await store.redis_store.hgetall(name=key)
    assert model == {}

    await model_class.insert(models[0])

    model = await store.redis_store.hgetall(name=key)
    model_deser = model_class(**model_class.deserialize_partially(model))
    assert models[0] == model_deser


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
async def test_select_default(store, models, model_class):
    """Selecting without arguments returns all the book models"""
    await model_class.insert(models)
    response = await model_class.select()
    for model in response:
        assert model in models


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
@pytest.mark.parametrize("execution_count", range(5))
async def test_select_pagination(store, models, model_class, execution_count):
    """Selecting with pagination"""
    limit = 2
    skip = randint(0, len(models) - limit)
    await model_class.insert(models)
    response = await model_class.select(skip=skip, limit=limit)
    assert len(response) == limit
    for model in response:
        assert model in models


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
async def test_select_no_contents(store, models, model_class):
    """Test that we get None when there are no models"""
    await store.redis_store.flushall()
    response = await model_class.select()

    assert response is None


@pytest.mark.asyncio
async def test_select_single_content(redis_store):
    """Check returns for a single instance"""
    # await redis_store.redis_store.flushall()
    await Book.insert([books[1]])
    response = await Book.select()
    assert len(response) == 1
    assert response[0] == books[1]

    books_dict = {book.title: book for book in books}
    response = await Book.select(columns=["title", "author", "in_stock"])

    assert response[0]["title"] == books[1].title
    assert response[0]["author"] == books[1].author
    assert response[0]["in_stock"] == books[1].in_stock
    with pytest.raises(KeyError):
        response[0]["published_on"]


@pytest.mark.asyncio
async def test_select_some_columns(redis_store):
    """
    Selecting some columns returns a list of dictionaries of all books models with only those columns
    """
    await Book.insert(books)
    books_dict = {book.title: book for book in books}
    columns = ["title", "author", "in_stock"]
    response = await Book.select(columns=["title", "author", "in_stock"])
    response_dict = {book["title"]: book for book in response}

    for title, book in books_dict.items():
        book_in_response = response_dict[title]
        assert isinstance(book_in_response, dict)
        assert sorted(book_in_response.keys()) == sorted(columns)
        for column in columns:
            assert f"{book_in_response[column]}" == f"{getattr(book, column)}"


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
@pytest.mark.parametrize("execution_count", range(5))
async def test_select_some_ids(store, models, model_class, execution_count):
    """
    Selecting some ids returns only those elements with the given ids
    """
    await model_class.insert(models)
    limit = 2
    skip = randint(0, len(models) - limit)

    to_select = models[skip : limit + skip]
    select_ids = [getattr(model, model_class._primary_key_field) for model in to_select]
    response = await model_class.select(ids=select_ids)
    assert len(response) > 0
    assert len(response) == len(to_select)
    for model in response:
        assert model in to_select


@pytest.mark.asyncio
async def test_select_bad_id(redis_store):
    """
    Selecting some ids returns only those elements with the given ids
    """
    await Book.insert(books)
    response = await Book.select(ids=["Not in there"])
    assert response is None


@pytest.mark.asyncio
async def test_update(redis_store):
    """
    Updating an item of a given primary key updates it in redis
    """
    await Book.insert(books)
    title = books[0].title
    new_author = "John Doe"
    key = f"book_%&_{title}"
    old_book_data = await redis_store.redis_store.hgetall(name=key)
    old_book = Book(**Book.deserialize_partially(old_book_data))
    assert old_book == books[0]
    assert old_book.author != new_author

    await Book.update(_id=title, data={"author": "John Doe"})

    book_data = await redis_store.redis_store.hgetall(name=key)
    book = Book(**Book.deserialize_partially(book_data))
    assert book.author == new_author
    assert book.title == old_book.title
    assert book.in_stock == old_book.in_stock
    assert book.published_on == old_book.published_on


@pytest.mark.asyncio
async def test_delete_single(redis_store):
    """Test deleting a single record"""
    await Book.insert(books)
    book_to_delete = books[1]
    await Book.delete(ids=book_to_delete.title)
    check_for_book = await redis_store.redis_store.hgetall(name=book_to_delete.title)
    assert check_for_book == {}


@pytest.mark.asyncio
async def test_delete_multiple(redis_store):
    """
    Providing a list of ids to the delete function will remove the items from redis
    """
    await Book.insert(books)
    books_to_delete = books[:2]
    books_left_in_db = books[2:]

    ids_to_delete = [book.title for book in books_to_delete]
    ids_to_leave_intact = [book.title for book in books_left_in_db]

    keys_to_delete = [f"book_%&_{_id}" for _id in ids_to_delete]
    keys_to_leave_intact = [f"book_%&_{_id}" for _id in ids_to_leave_intact]

    await Book.delete(ids=ids_to_delete)

    for key in keys_to_delete:
        deleted_book_in_redis = await redis_store.redis_store.hgetall(name=key)
        assert deleted_book_in_redis == {}

    async with redis_store.redis_store.pipeline() as pipeline:
        for key in keys_to_leave_intact:
            pipeline.hgetall(name=key)
        books_in_redis = await pipeline.execute()
    books_in_redis_as_models = [
        Book(**Book.deserialize_partially(book)) for book in books_in_redis
    ]
    assert books_left_in_db == books_in_redis_as_models


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
async def test_delete_all(store, models, model_class):
    """
    Delete all of a model from the redis
    """
    await model_class.insert(models)
    result = await model_class.select()
    assert len(result) == len(models)
    await model_class.delete()
    post_del_result = await model_class.select()
    assert post_del_result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("store, models, model_class", parameters)
async def test_delete_none(store, models, model_class):
    """
    Try to delete when the redis is empty for that model
    """
    assert await model_class.delete() is None


@pytest.mark.asyncio
async def test_unserializable_object(redis_store):
    class MyClass(object):
        ...

    class TestModel(Model):
        _primary_key_field = "name"
        name: str
        object: MyClass

    redis_store.register_model(TestModel)
    this_model = TestModel(name="test", object=MyClass())
    with pytest.raises(TypeError):
        await TestModel.insert(this_model)
