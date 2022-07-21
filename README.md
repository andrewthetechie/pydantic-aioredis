# pydantic-aioredis

A simple declarative ORM for Redis, using aioredis. Use your Pydantic
models like an ORM, storing data in Redis!

Inspired by
[pydantic-redis](https://github.com/sopherapps/pydantic-redis) by
[Martin Ahindura](https://github.com/Tinitto)

<p align="center">
    <a href="https://github.com/andrewthetechie/pydantic-aioredis" target="_blank">
        <img src="https://img.shields.io/github/last-commit/andrewthetechie/pydantic-aioredis" alt="Latest Commit">
    </a>
    <img src="https://img.shields.io/badge/license-MIT-green">
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/andrewthetechie/pydantic-aioredis?label=Latest%20Release">
    <br />
    <a href="https://github.com/andrewthetechie/pydantic-aioredis/issues"><img src="https://img.shields.io/github/issues/andrewthetechie/pydantic-aioredis" /></a>
    <img alt="GitHub Workflow Status Test and Lint (branch)" src="https://img.shields.io/github/workflow/status/andrewthetechie/pydantic-aioredis/Tests/main?label=Tests">
    <br />
    <a href="https://pypi.org/project/pydantic-aioredis" target="_blank">
        <img src="https://img.shields.io/pypi/v/pydantic-aioredis" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/pydantic-aioredis">
</p>

## Main Dependencies

- [Python +3.7](https://www.python.org)
- [redis-py <4.3.0](https://github.com/redis/redis-py)
- [pydantic](https://github.com/samuelcolvin/pydantic/)

## Getting Started

### Examples

Examples are in the [examples/](./examples) directory of this repo.

### Installation

Install the package

    pip install pydantic-aioredis

### Quick Usage

Import the `Store`, the `RedisConfig` and the `Model` classes and use accordingly

```python
import asyncio
from datetime import date
from pydantic_aioredis import RedisConfig, Model, Store

# Create models as you would create pydantic models i.e. using typings
class Book(Model):
    _primary_key_field: str = 'title'
    title: str
    author: str
    published_on: date
    in_stock: bool = True

# Do note that there is no concept of relationships here
class Library(Model):
    # the _primary_key_field is mandatory
    _primary_key_field: str = 'name'
    name: str
    address: str

# Create the store and register your models
store = Store(name='some_name', redis_config=RedisConfig(db=5, host='localhost', port=6379),life_span_in_seconds=3600)
store.register_model(Book)
store.register_model(Library)

# Sample books. You can create as many as you wish anywhere in the code
books = [
    Book(title="Oliver Twist", author='Charles Dickens', published_on=date(year=1215, month=4, day=4),
        in_stock=False),
    Book(title="Great Expectations", author='Charles Dickens', published_on=date(year=1220, month=4, day=4)),
    Book(title="Jane Eyre", author='Charles Dickens', published_on=date(year=1225, month=6, day=4), in_stock=False),
    Book(title="Wuthering Heights", author='Jane Austen', published_on=date(year=1600, month=4, day=4)),
]
# Some library objects
libraries = [
    Library(name="The Grand Library", address="Kinogozi, Hoima, Uganda"),
    Library(name="Christian Library", address="Buhimba, Hoima, Uganda")
]

async def work_with_orm():
  # Insert them into redis
  await Book.insert(books)
  await Library.insert(libraries)

  # Select all books to view them. A list of Model instances will be returned
  all_books = await Book.select()
  print(all_books) # Will print [Book(title="Oliver Twist", author="Charles Dickens", published_on=date(year=1215, month=4, day=4), in_stock=False), Book(...]

  # Or select some of the books
  some_books = await Book.select(ids=["Oliver Twist", "Jane Eyre"])
  print(some_books) # Will return only those two books

  # Or select some of the columns. THIS RETURNS DICTIONARIES not MODEL Instances
  # The Dictionaries have values in string form so you might need to do some extra work
  books_with_few_fields = await Book.select(columns=["author", "in_stock"])
  print(books_with_few_fields) # Will print [{"author": "'Charles Dickens", "in_stock": "True"},...]

  # Update any book or library
  await Book.update(_id="Oliver Twist", data={"author": "John Doe"})

  # Delete any number of items
  await Library.delete(ids=["The Grand Library"])

# Now run these updates
loop = asyncio.get_event_loop()
loop.run_until_complete(work_with_orm())
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide](./CONTRIBUTING.rst)

## License

Licensed under the [MIT License](./LICENSE)
