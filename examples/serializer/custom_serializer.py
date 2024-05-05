import asyncio
from datetime import date
from typing import Any

from pydantic_aioredis import Model
from pydantic_aioredis import RedisConfig
from pydantic_aioredis import Store


class BookCover:
    def __init__(self, cover_url: int, cover_size_x: int, cover_size_y: int):
        self.cover_url = cover_url
        self.cover_size_x = cover_size_x
        self.cover_size_y = cover_size_y

    @property
    def area(self):
        return self.cover_size_x * self.cover_size_y


# Create models as you would create pydantic models i.e. using typings
class Book(Model):
    _primary_key_field: str = "title"
    title: str
    author: str
    published_on: date
    cover: BookCover

    @classmethod
    def json_default(cls, obj: Any) -> str:
        """Since BookCover can't be directly json serialized, we have to write our own
        json_default to serialize it methods to handle it."""
        if isinstance(obj, BookCover):
            return {
                "__BookCover__": True,
                "cover_url": obj.cover_url,
                "cover_size_x": obj.cover_size_x,
                "cover_size_y": obj.cover_size_y,
            }

        return super().json_default(obj)

    @classmethod
    def json_object_hook(cls, obj: dict):
        """Since we're serializing BookCovers above, we need to write an
        object hook to turn them back into an Object"""
        if obj.get("__BookCover__", False):
            return BookCover(
                cover_url=obj["cover_url"],
                cover_size_x=obj["cover_size_x"],
                cover_size_y=obj["cover_size_y"],
            )
        super().json_object_hook(obj)


# Redisconfig. Change this configuration to match your redis server
redis_config = RedisConfig(db=5, host="localhost", password="password", ssl=False, port=6379)


# Create the store and register your models
store = Store(name="some_name", redis_config=redis_config, life_span_in_seconds=3600)
store.register_model(Book)


# Sample books. You can create as many as you wish anywhere in the code
books = [
    Book(
        title="Oliver Twist",
        author="Charles Dickens",
        published_on=date(year=1215, month=4, day=4),
        cover=BookCover(
            "https://images-na.ssl-images-amazon.com/images/I/51SmEM7LUGL._SX342_SY445_QL70_FMwebp_.jpg",
            333,
            499,
        ),
    ),
    Book(
        title="Great Expectations",
        author="Charles Dickens",
        published_on=date(year=1220, month=4, day=4),
        cover=BookCover(
            "https://images-na.ssl-images-amazon.com/images/I/51i715XqsYL._SX311_BO1,204,203,200_.jpg",
            333,
            499,
        ),
    ),
    Book(
        title="Jane Eyre",
        author="Charlotte Bronte",
        published_on=date(year=1225, month=6, day=4),
        cover=BookCover(
            "https://images-na.ssl-images-amazon.com/images/I/41saarVx+GL._SX324_BO1,204,203,200_.jpg",
            333,
            499,
        ),
    ),
    Book(
        title="Wuthering Heights",
        author="Emily Bronte",
        published_on=date(year=1600, month=4, day=4),
        cover=BookCover(
            "https://images-na.ssl-images-amazon.com/images/I/51ZKox7zBKL._SX338_BO1,204,203,200_.jpg",
            333,
            499,
        ),
    ),
]


async def work_with_orm():
    # Insert them into redis
    await Book.insert(books)

    # Select all books to view them. A list of Model instances will be returned
    all_books = await Book.select()
    print(all_books)  # Will print [Book(title="Oliver Twist", author="Charles Dickens",
    # published_on=date(year=1215, month=4, day=4), in_stock=False), Book(...]

    # Or select some of the books
    some_books = await Book.select(ids=["Oliver Twist", "Jane Eyre"])
    print(some_books)  # Will return only those two books

    # Or select some of the columns. THIS RETURNS DICTIONARIES not MODEL Instances
    # The Dictionaries have values in string form so you might need to do some extra work
    books_with_few_fields = await Book.select(columns=["author", "cover"])
    print(books_with_few_fields)  # Will print [{"author": "'Charles Dickens", "covker": Cover},...]

    # When _auto_sync = True (default), updating any attribute will update that field in Redis too
    this_book = Book(
        title="Moby Dick",
        author="Herman Melvill",
        published_on=date(year=1851, month=10, day=18),
        cover=BookCover("https://m.media-amazon.com/images/I/411a8Moy1mL._SY346_.jpg", 333, 499),
    )
    await Book.insert(this_book)
    # oops, there was a typo. Fix it
    this_book.author = "Herman Melville"
    this_book_from_redis = await Book.select(ids=["Moby Dick"])
    assert this_book_from_redis[0].author == "Herman Melville"

    # If you have _auto_save set to false on a model, you have to await .save() to update a model in tedis
    await this_book.save()


if __name__ == "__main__":
    asyncio.run(work_with_orm())
