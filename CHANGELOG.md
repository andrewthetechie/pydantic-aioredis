# Changelog

## [1.2.1](https://github.com/andrewthetechie/pydantic-aioredis/compare/v1.2.0...v1.2.1) (2023-01-21)


### Bug Fixes

* fix json types ([38a2608](https://github.com/andrewthetechie/pydantic-aioredis/commit/38a26084c65c9f01319318fecc3bfcf43d03474d))
* poetry update ([#431](https://github.com/andrewthetechie/pydantic-aioredis/issues/431)) ([968282e](https://github.com/andrewthetechie/pydantic-aioredis/commit/968282e4c87ac324e2380853508a189d0fcfe39d))

## [1.2.0](https://github.com/andrewthetechie/pydantic-aioredis/compare/v1.1.1...v1.2.0) (2022-12-21)


### Features

* auto_sync and auto_save ([#401](https://github.com/andrewthetechie/pydantic-aioredis/issues/401)) ([0e11e9d](https://github.com/andrewthetechie/pydantic-aioredis/commit/0e11e9dedef38c8d7b6226a143e7a3ae7ad2a340))

## [1.1.1](https://github.com/andrewthetechie/pydantic-aioredis/compare/v1.1.0...v1.1.1) (2022-12-19)


### Bug Fixes

* cleanup serializer ([#399](https://github.com/andrewthetechie/pydantic-aioredis/issues/399)) ([ec1421c](https://github.com/andrewthetechie/pydantic-aioredis/commit/ec1421c55608d87400eeb3e49332c61dddc0c5f6))


### Documentation

* add david-wahlstedt as a contributor for doc, and review ([#394](https://github.com/andrewthetechie/pydantic-aioredis/issues/394)) ([c9beb1a](https://github.com/andrewthetechie/pydantic-aioredis/commit/c9beb1aa85a7c394aceb0ab5cde10f6dfb32bf1a))
* add docs about Union types and casting ([#383](https://github.com/andrewthetechie/pydantic-aioredis/issues/383)) ([2af6167](https://github.com/andrewthetechie/pydantic-aioredis/commit/2af61672e3fb02db60f5faea0a6bf1fd528dcb6a))
* update contributors shield ([84cc727](https://github.com/andrewthetechie/pydantic-aioredis/commit/84cc727763f7757ead8ecaf870885e4dd71636b0))

## [1.1.0](https://github.com/andrewthetechie/pydantic-aioredis/compare/v1.0.0...v1.1.0) (2022-12-17)


### Features

* py3.11 support ([#391](https://github.com/andrewthetechie/pydantic-aioredis/issues/391)) ([2a82181](https://github.com/andrewthetechie/pydantic-aioredis/commit/2a82181ffb29ed7e26c314a0b9d9f0f2f29a6abb))


### Bug Fixes

* add toml ([ea583b1](https://github.com/andrewthetechie/pydantic-aioredis/commit/ea583b152c2aecf31495cc95303ba79ec821e799))
* update all requirements, safety ignore ([ebc1e86](https://github.com/andrewthetechie/pydantic-aioredis/commit/ebc1e863e251c9d8a7976d75335f84b29d1d2b4b))


### Documentation

* add all contributors ([#384](https://github.com/andrewthetechie/pydantic-aioredis/issues/384)) ([01dae8f](https://github.com/andrewthetechie/pydantic-aioredis/commit/01dae8fbfe706bba60e6be429ad040c4d641ecef))
* add andrewthetechie as a contributor for code, and doc ([#386](https://github.com/andrewthetechie/pydantic-aioredis/issues/386)) ([90739f9](https://github.com/andrewthetechie/pydantic-aioredis/commit/90739f9bae9667662175811404b7ecc3d7ca76ec))
* add david-wahlstedt as a contributor for test ([#388](https://github.com/andrewthetechie/pydantic-aioredis/issues/388)) ([ad155f7](https://github.com/andrewthetechie/pydantic-aioredis/commit/ad155f79e303d72a9717021ae89668e51d8f50d6))
* add gtmanfred as a contributor for test ([#390](https://github.com/andrewthetechie/pydantic-aioredis/issues/390)) ([2428db4](https://github.com/andrewthetechie/pydantic-aioredis/commit/2428db486b9fcd2ce654c711f5a7fe5b25f456de))
* add martin ([23f0e56](https://github.com/andrewthetechie/pydantic-aioredis/commit/23f0e560a65bad108b82f6e4f40384ff69156e26))
* update development docs ([97640e8](https://github.com/andrewthetechie/pydantic-aioredis/commit/97640e843f2f201f88e6c3ed580fd5947464e00a))

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
