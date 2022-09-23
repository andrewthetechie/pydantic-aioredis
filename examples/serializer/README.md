# asyncio_example

This is a working example using python-aioredis with asyncio and a custom serializer for a python object BookCover.

Book.json_default is used to serialize the BookCover object to a dictionary that json.dumps can dump to a string and store in redis.
Book.json_object_hook can convert a dict from redis back to a BookCover object.

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
python custom_serializer.py
[Book(title='Great Expectations', author='Charles Dickens', published_on=datetime.date(1220, 4, 4), cover=<__main__.BookCover object at 0x10410c4c0>), Book(title='Jane Eyre', author='Charlotte Bronte', published_on=datetime.date(1225, 6, 4), cover=<__main__.BookCover object at 0x10410d4e0>), Book(title='Moby Dick', author='Herman Melville', published_on=datetime.date(1851, 10, 18), cover=<__main__.BookCover object at 0x10410d060>), Book(title='Oliver Twist', author='Charles Dickens', published_on=datetime.date(1215, 4, 4), cover=<__main__.BookCover object at 0x10410c760>), Book(title='Wuthering Heights', author='Emily Bronte', published_on=datetime.date(1600, 4, 4), cover=<__main__.BookCover object at 0x10410d690>)]
[Book(title='Jane Eyre', author='Charlotte Bronte', published_on=datetime.date(1225, 6, 4), cover=<__main__.BookCover object at 0x10410cdc0>), Book(title='Oliver Twist', author='Charles Dickens', published_on=datetime.date(1215, 4, 4), cover=<__main__.BookCover object at 0x10410d7e0>)]
[{'author': 'Charles Dickens', 'cover': <__main__.BookCover object at 0x10410d7b0>}, {'author': 'Charlotte Bronte', 'cover': <__main__.BookCover object at 0x10410d8d0>}, {'author': 'Herman Melville', 'cover': <__main__.BookCover object at 0x10410d840>}, {'author': 'Charles Dickens', 'cover': <__main__.BookCover object at 0x10410d960>}, {'author': 'Emily Bronte', 'cover': <__main__.BookCover object at 0x10410d900>}]
```
