.PHONY: docker_build build dev rm stop shell up dbshell clean

PROJECT_NAME=wiggum

DOCKER_COMPOSE_OPTS= -p ${PROJECT_NAME} -f ../docker-compose.yml -f ./docker-compose.dev.yml
DOCKER_COMPOSE_CMD= docker-compose ${DOCKER_COMPOSE_OPTS}

default: build

# Build Stack
docker_build:
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD} build

# Build app
build: docker_build
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD} run --rm app /bin/bash -ic "../environment/dev/build.sh"; \
		${DOCKER_COMPOSE_CMD} stop; \
		${DOCKER_COMPOSE_CMD} rm -f

# Set the dev environment with the app up & running
dev: docker_build
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD} run --service-ports --rm app /bin/bash -ic "../environment/dev/build.sh; ./manage.py runserver 0.0.0.0:8009"; \
		${DOCKER_COMPOSE_CMD} stop; \
		${DOCKER_COMPOSE_CMD} rm -f

# Delete all the created containers
rm:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD} rm -f

# Stop all the created containers
stop:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD} stop

# Get a shell without ports mapping
shell:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD} run --rm app /bin/bash

# Get dev environment but with a shell instead of the running app
up: docker_build
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD} run --service-ports --rm app /bin/bash -ic "../environment/dev/build.sh; /bin/bash"; \
		${DOCKER_COMPOSE_CMD} stop; \
		${DOCKER_COMPOSE_CMD} rm -f

test:
	cd environment/dev && \
	${DOCKER_COMPOSE_CMD} run --service-ports --rm sut; \
	${DOCKER_COMPOSE_CMD} stop; \
	${DOCKER_COMPOSE_CMD} rm -f


dbshell:
	cd environment/dev && \
		${DOCKER_COMPOSE_CMD} run --rm app /bin/bash -ic "./manage.py dbshell"

# Clean orphan images
clean:
	docker rmi `docker images -q --filter "dangling=true"`
