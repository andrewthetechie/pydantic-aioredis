Quick Start
===========

Examples
^^^^^^^^

Examples are in the `examples/ <https://github.com/andrewthetechie/pydantic-aioredis/tree/main/examples>`_ directory of this repo.

Installation
^^^^^^^^^^^^

Install the package

.. code-block::

   pip install pydantic-aioredis


Quick Usage
^^^^^^^^^^^

Import the ``Store``\ , the ``RedisConfig`` and the ``Model`` classes.

Store and RedisConfig let you configure and customize the connection to your redis instance. Model is the base class for your ORM models.

.. code-block::

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
    store = Store(name='some_name', redis_config=RedisConfig(db=5, host='localhost', port=6379), life_span_in_seconds=3600)
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


        this_book = Book(title="Moby Dick", author='Herman Melvill', published_on=date(year=1851, month=10, day=17))
        await Book.insert(this_book)
        # oops, there was a typo. Fix it
        # Update is an async context manager and will update redis with all changes in one operations
        async with this_book.update():
            this_book.author = "Herman Melville"
            this_book.published_on=date(year=1851, month=10, day=18)
        this_book_from_redis = await Book.select(ids=["Moby Dick"])
        assert this_book_from_redis[0].author == "Herman Melville"
        assert this_book_from_redis[0].author == date(year=1851, month=10, day=18)

        # Delete any number of items
        await Library.delete(ids=["The Grand Library"])

    # Now run these updates
    loop = asyncio.get_event_loop()
    loop.run_until_complete(work_with_orm())
