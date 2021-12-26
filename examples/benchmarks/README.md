# benchmarks

This is an example using asyncio to benchmark pydantic-aioredis. It inserts and selects 3 different models, showing off some
ways to use pydanctic-aioredis. It will print out average times after a number of iterations are run (default 1000).

# Requirements

## Python packages

This example requires extra packages not required with the main pydantic-aioredis. Install them from examples/benchmark/requirements.txt

`pip install -r examples/benchmark/requirements.txt`

## Redis-server

This example requires a running redis server. You can change the RedisConfig on line 28 in the example to match connecting to your running redis.

For your ease of use, we've provided a Makefile in this directory that can start and stop a redis using docker.

`make start-redis`

`make stop-redis`

The example is configured to connect to this dockerized redis automatically

# Expected Output

## Default run

```bash
make run-benchmark

Book Insert (no serializer): 1.0461471774643287s average over 1000 iterations (0.9558884462354703 it/s)
Book Select all (no serializer): 0.4893654828397557s average over 1000 iterations (2.0434624734811 it/s)
Book Select all One Column (no serializer): 0.29570942815579476s average over 1000 iterations (3.381698061629436 it/s)
Library Insert (json serializer Pydantic): 4.305753696010448s average over 1000 iterations (0.23224737655722458 it/s)
Library Select all (json serializer Pydantic): 4.303571802544408s average over 1000 iterations (0.23236512503608478 it/s)
Library Select all One Column (json serializer Pydantic): 0.29694281294289976s average over 1000 iterations (3.3676518050372675 it/s)
Library Select all JSON Column (json serializer Pydantic): 0.30982984498888255s average over 1000 iterations (3.2275780276618686 it/s)
Librarian Insert (json serializer Non-Pydantic): 1.013630559870042s average over 1000 iterations (0.9865527338956814 it/s)
Librarian Select all (json serializer Non-Pydantic): 0.45883838821575046s average over 1000 iterations (2.179416600011658 it/s)
Librarian Select all One Column (json serializer Non-Pydantic): 0.289615185608156s average over 1000 iterations (3.4528576182914024 it/s)
Total test time: 54704.83693834022s
```

## Custom run

```bash
make start-redis
# run 10 iterations
python benchmark.py -i 10
make stop-redis
```
