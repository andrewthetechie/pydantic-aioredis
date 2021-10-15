Extras
======
pydantic-aioredis works well with other python modules in the pydantic ecosystem. There are some extras offered to make
those integrations tighter

FastAPI
-------
The `FastAPI <https://fastapi.tiangolo.com/>`_ extra adds a new base model called FastAPIModel. It has a single additional classmethod, select_or_404.

Usage
^^^^^
.. code-block:: python

   from pydantic_aioredis.config import RedisConfig
   from pydantic_aioredis.store import Store
   from pydantic_aioredis.ext.FastAPI import FastAPIModel

   class Model(FastAPIModel):
        _primary_key_field = "name"
        name: str
    
    store = Store(
        name="sample",
        redis_config=RedisConfig()
    )
    store.register_model(Model)
    app = FastAPI()

    @app.get("/", response_model=List[Model])
    async def get_endpoint():
        return await Model.select_or_404()

Module
^^^^^^
.. automodule:: pydantic_aioredis.ext.FastAPI.model
    ::member::

FastAPI Crudrouter
------------------
`FastAPI Crud Router <https://fastapi-crudrouter.awtkns.com/>`_ extra adds a CRUD generator for use with FastAPI Crud Router.
You can use your pydantic-aioredis models with fastapi-crudrouter to automatically generate crud routes.

Usage
^^^^^

.. code-block:: python


    from pydantic_aioredis.config import RedisConfig
    from pydantic_aioredis.store import Store
    from pydantic_aioredis.ext.FastAPI import PydanticAioredisCRUDRouter
    from pydantic_aioredis import Model

    class Model(FastAPIModel):
        _primary_key_field = "name"
        name: str

    store = Store(
        name="sample",
        redis_config=RedisConfig()
    )
    store.register_model(Model)
    app = FastAPI()

    router = PydanticAioredisCRUDRouter(schema=Model, store=store)
    app.include_router(router)

Module
^^^^^^
.. automodule:: pydantic_aioredis.ext.FastAPI.crudrouter
    ::member::
