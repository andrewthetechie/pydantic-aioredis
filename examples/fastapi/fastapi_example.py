from datetime import date
from typing import List

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
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


# Do note that there is no concept of relationships here
class Library(Model):
    # the _primary_key_field is mandatory
    _primary_key_field: str = "name"
    name: str
    address: str


app = FastAPI()


@app.on_event("startup")
async def redis_setup():
    # Redisconfig. Change this configuration to match your redis server
    redis_config = RedisConfig(
        db=5, host="localhost", password="password", ssl=False, port=6379
    )

    # Create the store and register your models
    store = Store(
        name="some_name", redis_config=redis_config, life_span_in_seconds=3600
    )
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
        ),
    ]
    # Some library objects
    libraries = [
        Library(name="The Grand Library", address="Kinogozi, Hoima, Uganda"),
        Library(name="Christian Library", address="Buhimba, Hoima, Uganda"),
    ]

    await Book.insert(books)
    await Library.insert(libraries)


@app.get("/book/{title}", response_model=List[Book])
async def get_book(title: str) -> Book:
    response = await Book.select(ids=[title])
    if response is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return response


@app.get("/books", response_model=List[Book])
async def get_books():
    return await Book.select()


@app.get("/libraries", response_model=List[Library])
async def get_libraries():
    return await Library.select()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
