import asyncio
from datetime import date
from typing import Dict
from typing import List
from typing import Optional

from pydantic_aioredis import Model
from pydantic_aioredis import RedisConfig
from pydantic_aioredis import Store


# Create models as you would create pydantic models i.e. using typings
class Book(Model):
    _primary_key_field: str = "title"
    title: str
    author: str
    published_on: date
    in_stock: bool = True
    locations: Optional[List[str]]


# Do note that there is no concept of relationships here
class Library(Model):
    # the _primary_key_field is mandatory
    _primary_key_field: str = "name"
    name: str
    address: str
    details: Optional[Dict[str, str]]


# Redisconfig. Change this configuration to match your redis server
redis_config = RedisConfig(db=5, host="localhost", password="password", ssl=False, port=6379)


# Create the store and register your models
store = Store(name="some_name", redis_config=redis_config, life_span_in_seconds=3600)
store.register_model(Book)
store.register_model(Library)

# Sample books. You can create as many as you wish anywhere in the code
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
        locations=["one", "two", "three"],
    ),
]
# Some library objects
libraries = [
    Library(name="The Grand Library", address="Kinogozi, Hoima, Uganda"),
    Library(
        name="Christian Library",
        address="Buhimba, Hoima, Uganda",
        details={"catalog": "huge", "fun_factor": "over 9000"},
    ),
]


async def work_with_orm():
    # Insert them into redis
    await Book.insert(books)
    await Library.insert(libraries)

    # Select all books to view them. A list of Model instances will be returned
    all_books = await Book.select()
    print(all_books)  # Will print [Book(title="Oliver Twist", author="Charles Dickens",
    # published_on=date(year=1215, month=4, day=4), in_stock=False), Book(...]

    # Or select some of the books
    some_books = await Book.select(ids=["Oliver Twist", "Jane Eyre"])
    print(some_books)  # Will return only those two books

    # Or select some of the columns. THIS RETURNS DICTIONARIES not MODEL Instances
    # The Dictionaries have values in string form so you might need to do some extra work
    books_with_few_fields = await Book.select(columns=["author", "in_stock"])
    print(books_with_few_fields)  # Will print [{"author": "'Charles Dickens", "in_stock": "True"},...]

    # When _auto_sync = True (default), updating any attribute will update that field in Redis too
    this_book = Book(
        title="Moby Dick",
        author="Herman Melvill",
        published_on=date(year=1851, month=10, day=18),
    )
    await Book.insert(this_book)
    # oops, there was a typo. Fix it
    this_book.author = "Herman Melville"
    this_book_from_redis = await Book.select(ids=["Moby Dick"])
    assert this_book_from_redis[0].author == "Herman Melville"

    # If you have _auto_save set to false on a model, you have to await .save() to update a model in tedis
    await this_book.save()

    all_libraries = await Library.select()
    print(all_libraries)
    # Delete any number of items
    await Library.delete(ids=["The Grand Library"])
    after_delete = await Library.select()
    print(after_delete)


if __name__ == "__main__":
    asyncio.run(work_with_orm())
