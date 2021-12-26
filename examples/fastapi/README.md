# asyncio_example

This is a working example using python-aioredis with FastAPI.

# Requirements

## Fastapi and Uvicorn

This example requires Fastapi and Uvicorn to run. You can install them from the requirements.txt in this directory

```bash
pip install -r requirements.txt
```

## Redis Server

This example requires a running redis server. You can change the RedisConfig on line 28 in the example to match connecting to your running redis.

For your ease of use, we've provided a Makefile in this directory that can start and stop a redis using docker.

`make start-redis`

`make stop-redis`

The example is configured to connect to this dockerized redis automatically

# Expected Output

This is a working example. If you try to run it and find it broken, first check your local env. If you are unable to get the
example running, please raise an Issue

```bash
python fastapi_example.py
INFO:     Started server process [122453]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```

In another terminal

```bash
curl locahost:8080/books
[{"title":"Jane Eyre","author":"Charles Dickens","published_on":"1225-06-04","in_stock":false},{"title":"Great Expectations","author":"Charles Dickens","published_on":"1220-04-04","in_stock":true},{"title":"Wuthering Heights","author":"Jane Austen","published_on":"1600-04-04","in_stock":true},{"title":"Oliver Twist","author":"Charles Dickens","published_on":"1215-04-04","in_stock":false}]

curl localhost:8080/libraries
[{"name":"Christian Library","address":"Buhimba, Hoima, Uganda"},{"name":"The Grand Library","address":"Kinogozi, Hoima, Uganda"}]

curl localhost:8080/book/Jane%20Eyre
[{"title":"Jane Eyre","author":"Charles Dickens","published_on":"1225-06-04","in_stock":false}]

curl -v localhost:8080/book/Not%20a%20book
< HTTP/1.1 404 Not Found
< date: Sat, 07 Aug 2021 17:20:45 GMT
< server: uvicorn
< content-length: 27
< content-type: application/json
{"detail":"Book not found"}
```
