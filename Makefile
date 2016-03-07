.PHONY: docker_build build dev rm stop shell up dbshell clean

PROJECT_NAME=wiggum

DOCKER_COMPOSE_CMD=docker-compose -p ${PROJECT_NAME} -f ../docker-compose.yml
DOCKER_COMPOSE_CMD_DEV=${DOCKER_COMPOSE_CMD} -f ./docker-compose.dev.yml
DOCKER_COMPOSE_CMD_CI=${DOCKER_COMPOSE_CMD} -f ./docker-compose.ci.yml

default: build

# Build Stack
docker_build:
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD_DEV} build

# Build app
build: docker_build
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD_DEV} run --rm app /bin/bash -ic "../environment/dev/build.sh"; \
		${DOCKER_COMPOSE_CMD_DEV} stop; \
		${DOCKER_COMPOSE_CMD_DEV} rm -f

# Set the dev environment with the app up & running
dev: docker_build
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD_DEV} run --service-ports --rm app /bin/bash -ic "../environment/dev/build.sh; ./manage.py runserver 0.0.0.0:8009"; \
		${DOCKER_COMPOSE_CMD_DEV} stop; \
		${DOCKER_COMPOSE_CMD_DEV} rm -f

# Delete all the created containers
rm:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD_DEV} rm -f

# Stop all the created containers
stop:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD_DEV} stop

# Get a shell without ports mapping
shell:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD_DEV} run --rm app /bin/bash

# Get dev environment but with a shell instead of the running app
up: docker_build
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD_DEV} run --service-ports --rm app /bin/bash -ic "../environment/dev/build.sh; /bin/bash"; \
		${DOCKER_COMPOSE_CMD_DEV} stop; \
		${DOCKER_COMPOSE_CMD_DEV} rm -f

# Test and CI stuff
test: test_ci test_ci_clean

test_ci:
	cd environment/ci && \
	${DOCKER_COMPOSE_CMD_CI} run --rm app

test_ci_clean:
	cd environment/ci && \
	${DOCKER_COMPOSE_CMD_CI} stop; \
	${DOCKER_COMPOSE_CMD_CI} rm -f

dbshell:
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD_DEV} run --rm app /bin/bash -ic "./manage.py dbshell"

# Clean orphan images
clean:
	docker rmi `docker images -q --filter "dangling=true"`
