# asyncio_example

This is a working example using python-aioredis with asyncio.

# Requirements

This example requires a running redis server. You can change the RedisConfig on line 28 in the example to match connecting to your running redis.

For your ease of use, we've provided a Makefile in this directory that can start and stop a redis using docker.

`make start-redis`

`make stop-redis`

The example is configured to connect to this dockerized redis automatically

# Expected Output

This is a working example. If you try to run it and find it broken, first check your local env. If you are unable to get the
example running, please raise an Issue

```bash
python asyncio_example.py
[Book(title='Jane Eyre', author='Charles Dickens', published_on=datetime.date(1225, 6, 4), in_stock=False), Book(title='Great Expectations', author='Charles Dickens', published_on=datetime.date(1220, 4, 4), in_stock=True), Book(title='Wuthering Heights', author='Jane Austen', published_on=datetime.date(1600, 4, 4), in_stock=True), Book(title='Oliver Twist', author='Charles Dickens', published_on=datetime.date(1215, 4, 4), in_stock=False)]
[Book(title='Oliver Twist', author='Charles Dickens', published_on=datetime.date(1215, 4, 4), in_stock=False), Book(title='Jane Eyre', author='Charles Dickens', published_on=datetime.date(1225, 6, 4), in_stock=False)]
[{'author': 'Charles Dickens', 'in_stock': 'False'}, {'author': 'Charles Dickens', 'in_stock': 'True'}, {'author': 'Jane Austen', 'in_stock': 'True'}, {'author': 'Charles Dickens', 'in_stock': 'False'}]
```
