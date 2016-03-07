#!/bin/bash -ex
set -o pipefail
echo "buld running at `hostname -f`"
echo "-----ENVIRONMENT-----"
env
echo "---------------------"

export DJANGO_SETTINGS_MODULE=wiggum.settings.ci

source $HOME/.virtualenvs/wiggum/bin/activate

# Run tests
cd ./wiggum
./manage.py test --noinput --verbosity 2  --failfast
