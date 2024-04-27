.PHONY: test run

# use the new docker compose command if available or the legacy docker-compose command
DOCKER_COMPOSE := $(shell \
	docker compose version > /dev/null 2>&1; \
	if [ $$? -eq 0 ]; then \
		echo "docker compose"; \
	else \
		docker-compose version > /dev/null 2>&1; \
		if [ $$? -eq 0 ]; then \
			echo "docker-compose"; \
		fi; \
	fi; \
)

run:
	$(DOCKER_COMPOSE) up --build

test:
	$(DOCKER_COMPOSE) up -d redis
	pytest worker_test.py
	$(DOCKER_COMPOSE) down
