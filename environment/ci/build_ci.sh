#!/usr/bin/env bash

CURRENT_PATH=$(dirname "${BASH_SOURCE[0]}")

# Set env vars needed by the docker client
source $HOME/docker_host

# unique ID for docker compose
UUID=wiggum_$HOSTNAME

# Notifications URL
export PROJECT_NAME="wiggum"


# Timeout for tests
TESTS_TIMEOUT="10m"

# Create first then run command
DOCKER_COMPOSE_OPTS="-p $UUID -f $CURRENT_PATH/../docker-compose.yml -f $CURRENT_PATH/docker-compose.ci.yml"
docker-compose ${DOCKER_COMPOSE_OPTS} build
docker-compose ${DOCKER_COMPOSE_OPTS} up -d
timeout $TESTS_TIMEOUT docker-compose  ${DOCKER_COMPOSE_OPTS} \
                                        run \
                                       -e CI_BUILD_REF_NAME=${CI_BUILD_REF_NAME} \
                                       -e CI_BUILD_REF=${CI_BUILD_REF} \
                                        app ./environment/ci/run.sh
# Capture exit code to return afterwards
EXIT_CODE=$?
echo $EXIT_CODE

# Destroy everything
docker-compose ${DOCKER_COMPOSE_OPTS} stop
docker-compose ${DOCKER_COMPOSE_OPTS} rm -fv
RUN_ID=$(echo $UUID | tr '[:upper:]' '[:lower:]' | sed "s/[^0-9a-z]//g")
docker rm -vf `docker ps -a | grep $RUN_ID| awk '{ print $1 }'`

if [ "$EXIT_CODE" == 124 ]; then
    echo "TEST TIMEOUT! (limit: $TESTS_TIMEOUT)"
fi

# The real exit code of tests
exit $EXIT_CODE
