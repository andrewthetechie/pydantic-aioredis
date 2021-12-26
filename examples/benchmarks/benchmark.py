import argparse
import asyncio
import json
import time
from datetime import date
from random import randint
from random import random
from random import sample
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

import aioredis
from faker import Faker
from pydantic import BaseModel
from pydantic import Field
from pydantic_aioredis import Model
from pydantic_aioredis import RedisConfig
from pydantic_aioredis import Store
from tqdm import tqdm


# Create models as you would create pydantic models i.e. using typings
class BookBase(BaseModel):
    title: str
    author: str
    published_on: date
    in_stock: bool = True
    isbn: str
    extra_info: Optional[str] = None


class Book(BookBase, Model):
    _primary_key_field: str = "title"


class Library(Model):
    # the _primary_key_field is mandatory
    _primary_key_field: str = "name"
    _json_fields: List[str] = ["books_in_library"]
    name: str
    address: str
    books_in_library: List[BookBase]


class Librarian(Model):
    _primary_key_field = "name"
    _json_fields: List[str] = ["qualifications"]
    name: str
    age: int = Field(..., ge=21, le=100)
    qualifications: List[str]


# Redisconfig. Change this configuration to match your redis server
redis_config = RedisConfig(
    db=5, host="localhost", password="password", ssl=False, port=6379
)


# Create the store and register your models
store = Store(name="benchmark", redis_config=redis_config, life_span_in_seconds=600)

Faker.seed(random())
redis = aioredis.from_url("redis://:password@localhost:6379")


async def setup(
    count_of_books: int = 1000,
    count_of_libraries: int = 1000,
    books_in_library: int = 20,
    count_of_librarians: int = 1000,
):
    store.register_model(Book)
    store.register_model(Library)
    store.register_model(Librarian)
    await cleanup()
    fake = Faker()
    books = list()
    tqdm.write(f"Generating {count_of_books} books")
    for _ in tqdm(range(count_of_books)):
        books.append(
            Book(
                title=fake.sentence(),
                author=fake.name(),
                published_on=fake.date(),
                in_stock=fake.boolean(),
                isbn=fake.isbn13(),
            )
        )
    libraries = list()
    tqdm.write(f"Generating {count_of_libraries} libraries")
    for _ in tqdm(range(count_of_libraries)):
        libraries.append(
            Library(
                name=fake.name(),
                address=fake.address(),
                books_in_library=sample(books, books_in_library),
            )
        )

    librarians = list()
    librarian_quals = ["ALA-APA", "MLS", "CPLA", "LSSC"]

    tqdm.write(f"Generating {count_of_librarians} librarians")
    for _ in tqdm(range(count_of_librarians)):
        librarians.append(
            Librarian(
                name=fake.name(),
                age=randint(21, 99),
                qualifications=sample(
                    librarian_quals, randint(1, len(librarian_quals))
                ),
            )
        )
    return books, libraries, librarians


async def cleanup():
    await redis.flushall()


async def timer(awaitable) -> Tuple[float, Any]:
    start = time.perf_counter()
    result = await awaitable
    stop = time.perf_counter()
    return stop - start, result


async def benchmark(books: List[Book], libraries: List[Library], librarians):
    to_return = {}
    time, _ = await timer(Book.insert(books))
    to_return["Book Insert (no serializer)"] = time
    time, _ = await timer(Book.select())
    to_return["Book Select all (no serializer)"] = time
    time, _ = await timer(Book.select(columns=["isbn"]))
    to_return["Book Select all One Column (no serializer)"] = time

    time, _ = await timer(Library.insert(libraries))
    to_return["Library Insert (json serializer Pydantic)"] = time
    time, _ = await timer(Library.select())
    to_return["Library Select all (json serializer Pydantic)"] = time
    time, _ = await timer(Library.select(columns=["address"]))
    to_return["Library Select all One Column (json serializer Pydantic)"] = time
    time, _ = await timer(Library.select(columns=["books_in_library"]))
    to_return["Library Select all JSON Column (json serializer Pydantic)"] = time

    time, _ = await timer(Librarian.insert(librarians))
    to_return["Librarian Insert (json serializer Non-Pydantic)"] = time
    time, _ = await timer(Librarian.select())
    to_return["Librarian Select all (json serializer Non-Pydantic)"] = time
    time, _ = await timer(Librarian.select(columns=["name"]))
    to_return["Librarian Select all One Column (json serializer Non-Pydantic)"] = time
    return to_return


async def run_benchmark(
    number_of_iterations: int = 1000, number_of_objects: int = 1000
):
    tqdm.write(
        f"Starting benchmark run of {number_of_iterations} iterations. Will output data at the end of the run"
    )
    tqdm.write(
        "Total run time will differ from benchmark reports due to setup and cleanup tasks"
    )
    books, libraries, librarians = await setup(
        count_of_books=number_of_objects,
        count_of_libraries=number_of_objects,
        count_of_librarians=number_of_objects,
    )
    results = {}
    test_start = time.perf_counter()
    tqdm.write("Setup complete, starting benchmarks")
    try:
        for _ in tqdm(range(number_of_iterations)):
            for key, value in (await benchmark(books, libraries, librarians)).items():
                if key not in results:
                    results[key] = list()
                results[key].append(value)
            await cleanup()
        tqdm.write(json.dumps(results))
    except KeyboardInterrupt:
        tqdm.write("Cancelling loop")
    test_stop = time.perf_counter()

    for key, values in results.items():
        tqdm.write(
            f"{key}: {sum(values) / len(values)}s average over "
            + f"{len(values)} iterations ({len(values) / sum(values)} it/s) "
        )
    tqdm.write(f"Total test time: {test_stop - test_start}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a benchmark of python-aioredis")
    parser.add_argument(
        "-i",
        "--iterations",
        action="store",
        default=10,
        help="Number of iterations to run",
    )
    parser.add_argument(
        "-n",
        "--number-of-objects",
        action="store",
        default=1000,
        help="Number of objects to generate",
    )
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_benchmark(int(args.iterations), int(args.number_of_objects))
    )
