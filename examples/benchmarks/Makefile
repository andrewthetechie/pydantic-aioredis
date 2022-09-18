.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


run-benchmark: ## Run the benchmarking suite
	pytest test_benchmarks.py -n 0

setup: ## Setup extra benchmarking requirements
	pip install -r requirements.txt
