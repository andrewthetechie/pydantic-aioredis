Automatic Saving
================

By default, a pydantic-aioredis model is only saved to Redis when its .save() method is called or when it is inserted(). This is to prevent unnecessary writes to Redis.

pydantic-aioredis has two options you can tweak for automatic saving:
    * _auto_save: Used to determine if a model is saved to redis on instantiate
    * _auto_sync: Used to determine if a change to a model is saved on setattr

These options can be set on a model or on a per instance basis.

.. code-block::

    import asyncio
    from pydantic_aioredis import RedisConfig, Model, Store

    class Book(Model):
        _primary_key_field: str = 'title'
        title: str
        author: str

        _auto_save: bool = True
        _auto_sync: bool = True


    class Movie(Model):
        _primary_key_field: str = 'title'
        title: str
        director: str

        _auto_sync: bool = True



    # Create the store and register your models
    store = Store(name='some_name', redis_config=RedisConfig(db=5, host='localhost', port=6379), life_span_in_seconds=3600)
    store.register_model(Book)

    async def autol():
        my_book = Book(title='The Hobbit', author='J.R.R. Tolkien')
        # my_book is already in redis
        book_from_redis = await Book.select(ids['The Hobbit'])
        assert book_from_redis[0] == my_book

        # _auto_save means that changing a field will automatically save the model
        my_book.author = 'J.R.R. Tolkien II'
        book_from_redis = await Book.select(ids['The Hobbit'])
        assert book_from_redis[0] == my_book

        my_movie = Movie(title='The Lord of the Rings', director='Peter Jackson')
        # my_move is not in redis until its inserted
        await Movie.insert(my_movie)

        # _auto_sync means that changing a field will automatically save the model
        my_movie.director = 'Peter Jackson II'
        movie_from_redis = await Movie.select(ids['The Hobbit'])
        assert movie_from_redis[0] == my_movie

        # _auto_sync and _auto_save can be set on a per instance basis
        local_book = Book(title='The Silmarillion', author='J.R.R. Tolkien', _auto_save=False, _auto_sync=False)
        # local_book is not automatically saved in redis and won't try to sync, even though the class has _auto_save and _auto_sync set to True
        books_in_redis = await Book.select()
        assert len(books_in_redis) == 1


    loop = asyncio.get_event_loop()
    loop.run_until_complete(auto())


There is also `AutoModel`, which is a subclass of `Model` that has `_auto_save` and `_auto_sync` set to True by default.

.. code-block::

    import asyncio
    from pydantic_aioredis import RedisConfig, AutoModel, Store

    class Book(AutoModel):
        _primary_key_field: str = 'title'
        title: str

    async def auto_model():
        my_book = Book(title='The Hobbit')
        # my_book is already in redis
        book_from_redis = await Book.select(ids['The Hobbit'])
        assert book_from_redis[0] == my_book

        # _auto_save means that changing a field will automatically save the model
        my_book.author = 'J.R.R. Tolkien II'
        book_from_redis = await Book.select(ids['The Hobbit'])
        assert book_from_redis[0] == my_book

    loop = asyncio.get_event_loop()
    loop.run_until_complete(auto_model())
