#!/bin/sh
set -e

# retrying alembic migrations until success (useful when DB starts slowly)
MAX_RETRIES=${MAX_RETRIES:-10}
RETRY_DELAY=${RETRY_DELAY:-5}

i=0
echo "Waiting for DB and running migrations (max ${MAX_RETRIES} attempts)..."
until make db-upgrade; do
    i=$((i+1))
    echo "alembic attempt ${i} failed"
    if [ "$i" -ge "$MAX_RETRIES" ]; then
        echo "Migrations failed after ${i} attempts, aborting."
        exit 1
    fi
    sleep "${RETRY_DELAY}"
done

echo "Migrations applied."

exec make prod
