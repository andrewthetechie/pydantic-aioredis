start-redis: ## Runs a copy of redis in docker
	docker run -it -d --rm --name pydantic-aioredis-example -p 6379:6379 -e REDIS_PASSWORD=password bitnami/redis || echo "$(REDIS_CONTAINER_NAME) is either running or failed"

stop-redis: ## Stops the redis in docker
	docker stop pydantic-aioredis-example
