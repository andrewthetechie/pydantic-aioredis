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
        <img src="https://github.com/andrewthetechie/pydantic-aioredis/actions/workflows/run_tests_with_tox.yaml/badge.svg?branch=main">
        <img src="https://img.shields.io/codecov/c/github/andrewthetechie/pydantic-aioredis">
    <br />
    <a href="https://pypi.org/project/pydantic-aioredis" target="_blank">
        <img src="https://img.shields.io/pypi/v/pydantic-aioredis" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/pydantic-aioredis">
    <img src="https://img.shields.io/badge/license-MIT-green">
</p>

## Main Dependencies


-   [Python +3.6](https://www.python.org)
-   [aioredis 2.0](https://aioredis.readthedocs.io/en/latest/)
-   [pydantic](https://github.com/samuelcolvin/pydantic/)

## Getting Started

### Examples
Examples are in the [examples/](./examples) directory of this repo.

### Installation
Install the package

    
    pip install pydantic-aioredis

### Quick Usage
Import the `Store`, the `RedisConfig` and the `Model` classes and use accordingly

    
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
    

## Development

The [Makefile](./makefile) has useful targets to help setup your
development encironment. We suggest using pyenv to have access to
multiple python versions easily.

### Environment Setup

-   Clone the repo and enter its root folder

    ``` {.sourceCode .bash}
    git clone https://github.com/andrewthetechie/pydantic-aioredis.git && cd pydantic-aioredis
    ```

-   Create a python 3.9 virtual environment and activate it. We suggest
    using [pyenv](https://github.com/pyenv/pyenv) to easily setup
    multiple python environments on multiple versions.

    ``` {.sourceCode .bash}
    # We use the extra python version (3.6, 3.7, 3.8) for tox testing
    pyenv install 3.9.7 3.6.15 3.7.12 3.8.12
    pyenv virtualenv 3.9.7 python-aioredis
    pyenv local python-aioredis 3.6.15 3.7.12 3.8.12
    ```

-   Install the dependencies

    ``` {.sourceCode .bash}
    make setup
    ```

### How to Run Tests

-   Run the test command to run tests on only python 3.9

    ``` {.sourceCode .bash}
    make test
    ```

    or

    ``` {.sourceCode .bash}
    pytest
    ```

-   Run the tox command to run all python version tests

    ``` {.sourceCode .bash}
    make tox
    ```

    or

    ``` {.sourceCode .base}
    tox
    ```

### Test Requirements

Prs should always have tests to cover the change being made. Code
coverage goals for this project are 100% coverage.

### Code Linting

All code should pass Flake8 and be blackened. If you install and setup
pre-commit (done automatically by environment setup), pre-commit will
lint your code for you.

You can run the linting manually with make

``` {.sourceCode .bash}
make lint
```

## CI

CI is run via Github Actions on all PRs and pushes to the main branch. 

Releases are automatically released by Github Actions to Pypi.

License
-------

Licensed under the [MIT License](./LICENSE)
