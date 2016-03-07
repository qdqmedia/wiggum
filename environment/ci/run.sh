#!/bin/bash -ex
set -o pipefail
echo "buld running at `hostname -f`"
echo "-----ENVIRONMENT-----"
env
echo "---------------------"

export DJANGO_SETTINGS_MODULE=wiggum.settings.ci
export PGPASSWORD=${DB_ENV_POSTGRES_PASSWORD}

source $HOME/.virtualenvs/wiggum/bin/activate

# Wait for postgres to be ready
echo "Waiting for postgres to be ready"

set +e
count=0
while true; do
  psql -c '\q' -h ${DB_PORT_5432_TCP_ADDR} -p ${DB_PORT_5432_TCP_PORT} -U ${DB_ENV_POSTGRES_USER} postgres 2>/dev/null
  if [ $? -eq 0 ]; then
    break
  fi
  count=$(($count + 1))
  if [ ${count} -gt 20 ]; then
    echo "Postgres seems not to be working"
    exit 1
  fi
  echo -n "."
  sleep 1
done
set -e

# Run tests
cd ./wiggum
./manage.py test --noinput --verbosity 2  --failfast

# Download deploy keys
keys_path=`pwd`/keys
download_deploy_keys ${keys_path}

# Get deployment author
author=$(get_author_email_from_git)

# Auto deploy to staging/beta if build ok and master branch
#tsuru_deploy_git_master_on_success $? ${CI_BUILD_REF_NAME} ${BETA_DEPLOY_URL} ${author} ${keys_path}

# Upload release
upload_release "../" ${CI_BUILD_REF_NAME} ${CI_BUILD_REF} ${RELEASES_URL} ${author}
