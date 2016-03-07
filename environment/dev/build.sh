#! /bin/bash

###############################################################################
echo "[*] Getting statics..."
cd ../
bower --config.analytics=false install
cd -

###############################################################################
echo "[*] Generating translations..."
./manage.py compilemessages

###############################################################################
echo "[*] Waiting for Postgres to start..."
CURLE_COULDNT_CONNECT="7"

curl -s  -o /dev/null http://$DB_PORT_5432_TCP_ADDR:$DB_PORT_5432_TCP_PORT/
while [ "$?" == "$CURLE_COULDNT_CONNECT" ]
do
  sleep 1
  curl -s  -o /dev/null http://$DB_PORT_5432_TCP_ADDR:$DB_PORT_5432_TCP_PORT/
done

###############################################################################
echo "[*] Applying migrations..."
./manage.py migrate

###############################################################################
echo "[!] FINISHED!"
echo "[!] You can login with admin/admin"
