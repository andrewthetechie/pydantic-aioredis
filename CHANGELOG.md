# Changelog

## [1.0.0](https://github.com/andrewthetechie/pydantic-aioredis/compare/v0.7.0...v1.0.0) (2022-09-23)


### ⚠ BREAKING CHANGES

* This is a breaking change to how updates for model attributes are saved to Redis. It removes the update classmethod and replaces with with a save method on each model.
* This will result in "data loss" for existing models stored in redis due to the change in default separator. To maintain backwards compatbility with 0.7.0 and below, you will need to modify your existing models to set _redis_separator = "_%&_" as a field on them.

### Features

* json_object_hook and serializer example ([#294](https://github.com/andrewthetechie/pydantic-aioredis/issues/294)) ([80c725e](https://github.com/andrewthetechie/pydantic-aioredis/commit/80c725e087b1a09917df1770ebc676139808b2cb))
* redis-separator ([#278](https://github.com/andrewthetechie/pydantic-aioredis/issues/278)) ([f367d30](https://github.com/andrewthetechie/pydantic-aioredis/commit/f367d300751b3a7550b54c31f6a7da58e9296351))
* update on setattr ([#287](https://github.com/andrewthetechie/pydantic-aioredis/issues/287)) ([f1ce5c2](https://github.com/andrewthetechie/pydantic-aioredis/commit/f1ce5c2b1fe292cfe8dd509cac477f617e36c057))


### Bug Fixes

* fix pre-commit in example ([ab94167](https://github.com/andrewthetechie/pydantic-aioredis/commit/ab94167a8ff22b5290f05a4b2eb3ea11a2fb4ab0))


### Documentation

* change typing to <3.10 compatible ([2ccfa0a](https://github.com/andrewthetechie/pydantic-aioredis/commit/2ccfa0a38911e2fce0c6baaa79d3d39a896e2613))
* fix incorrect links in CONTRIBUTING.rst ([a8ba8e5](https://github.com/andrewthetechie/pydantic-aioredis/commit/a8ba8e5626baf18a710577db946d52a6ddaed6fa))
* fix invalid doc in abstract.py ([32d0d13](https://github.com/andrewthetechie/pydantic-aioredis/commit/32d0d137fe87024f45e1875fe349d819a957f3f0))

## [0.7.0](https://github.com/andrewthetechie/pydantic-aioredis/compare/v0.6.0...v0.7.0) (2022-07-21)


### Features

* move to redis-py ([#217](https://github.com/andrewthetechie/pydantic-aioredis/issues/217)) ([bd2831b](https://github.com/andrewthetechie/pydantic-aioredis/commit/bd2831b66b7a4949cbd5f116b508d6cb54361321))


### Documentation

* update shields in readme ([a5bea90](https://github.com/andrewthetechie/pydantic-aioredis/commit/a5bea90df6a68eca2a08d01747d32bc1fdf03648))
