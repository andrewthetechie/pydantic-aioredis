Serialization
=============

Data in Redis
#############
pydantic-aioredis uses Redis Hashes to store data. The ```_primary_key_field``` of each Model is used as the key of the hash.

Because Redis only supports string values as the fields of a hash, data types have to be serialized.

Simple data types
#################
Simple python datatypes that can be represented as a string and natively converted by pydantic are converted to strings and stored. Examples
are ints, floats, strs, bools, and Nonetypes.

Unintentional Type Casting with Union Types
*******************************************

When using Union types, pydantic will cast the value to the first type in the Union. This can cause unintended type casting. For example, if you have a field
of type Union[float, int], and you set the value to 1, pydantic will cast the value to a float 1.0. In the other direction (i.e. `x: Union[int, float]`) will result in
the value being casted as an int and rounded. If you used a value of x = 1.99, it would get cast as an int and rounded to 1.

This is an issue with Pydantic. More info can be found in
`this issue <https://github.com/andrewthetechie/pydantic-aioredis/issues/379>`_ reported by `david-wahlstedt <https://github.com/david-wahlstedt>`_ and `this issue in Pydantic <https://github.com/pydantic/pydantic/issues/4519>`_.

There are some `test cases <https://github.com/andrewthetechie/pydantic-aioredis/blob/main/test/test_union_typing.py>`_ in pydantic_aioredis that illustrate this problem.

Complex data types
##################
Complex data types are dumped to json with json.dumps().

Custom serialization is possible using `json_default <https://docs.python.org/3/library/json.html#:~:text=not%20None.-,If%20specified%2C%20default%20should%20be%20a%20function%20that%20gets%20called%20for%20objects%20that%20can%E2%80%99t%20otherwise%20be%20serialized.%20It%20should%20return%20a%20JSON%20encodable%20version%20of%20the%20object%20or%20raise%20a%20TypeError.%20If%20not%20specified%2C%20TypeError%20is%20raised.,-If%20sort_keys%20is>`_ and `json_object_hook <https://docs.python.org/3/library/json.html#:~:text=object_hook%20is%20an%20optional%20function%20that%20will%20be%20called%20with%20the%20result%20of%20any%20object%20literal%20decoded%20(a%20dict).%20The%20return%20value%20of%20object_hook%20will%20be%20used%20instead%20of%20the%20dict.%20This%20feature%20can%20be%20used%20to%20implement%20custom%20decoders%20(e.g.%20JSON%2DRPC%20class%20hinting).>`_.

These methods are part of the `abstract model <https://github.com/andrewthetechie/pydantic-aioredis/blob/main/pydantic_aioredis/abstract.py#L77>`_ and can be overridden in your
model to dump custom objects to json and then back to objects. An example is available in `examples <https://github.com/andrewthetechie/pydantic-aioredis/tree/main/examples/serializer>`_
