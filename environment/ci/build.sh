
export PGPASSWORD=${DB_ENV_POSTGRES_PASSWORD}

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
