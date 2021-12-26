.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


run-benchmark: start-docker
	python benchmark.py -i 100

start-redis: ## Runs a copy of redis in docker
	docker run -it -d --rm --name pydantic-aioredis-example -p 6379:6379 -e REDIS_PASSWORD=password bitnami/redis || echo "$(REDIS_CONTAINER_NAME) is either running or failed"

stop-redis: ## Stops the redis in docker
	docker stop pydantic-aioredis-example
