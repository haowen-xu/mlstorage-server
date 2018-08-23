#!/usr/bin/env bash

exec /usr/local/bin/mlserver \
    --host "${MLSTORAGE_SERVER_HOST}" \
    --port "${MLSTORAGE_SERVER_PORT}" \
    --workers "${MLSTORAGE_SERVER_WORKERS}" \
    --storage-root "${MLSTORAGE_EXPERIMENT_ROOT}" \
    --mongo "${MLSTORAGE_MONGO_CONN}" \
    --db "${MLSTORAGE_MONGO_DB}" \
    --collection "${MLSTORAGE_MONGO_COLL}"
