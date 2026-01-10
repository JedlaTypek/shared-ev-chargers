#!/bin/bash
set -e

SOURCE_DIR="/mnt/prod_data"
DATA_DIR="/var/lib/postgresql/data"

echo "==============================================="
echo "BETA DB INIT: CLONING PRODUCTION DATA"
echo "==============================================="

# 1. Check Source
if [ ! -d "$SOURCE_DIR" ] || [ -z "$(ls -A $SOURCE_DIR)" ]; then
    echo "WARNING: Source directory $SOURCE_DIR is empty or missing."
    echo "Skipping clone. Starting with empty/existing beta DB."
else
    echo "Source found. Cloning from $SOURCE_DIR..."
    
    # 2. Clean Destination (CAUTION: Wipes beta DB on every start!)
    # We only clear if PGDATA is really the data dir
    if [ "$PGDATA" = "$DATA_DIR" ]; then
        echo "Cleaning $DATA_DIR..."
        rm -rf "$DATA_DIR"/*
    fi

    # 3. Copy Data
    echo "Copying data (cp -a)..."
    cp -a "$SOURCE_DIR"/. "$DATA_DIR"/
    
    # 4. Ensure Permissions (just in case, though -a should handle it)
    # Since we are running as root or the user defined in Dockerfile
    # Postgres image usually runs entrypoint as root then steps down.
    chown -R postgres:postgres "$DATA_DIR"
    chmod 700 "$DATA_DIR"
    
    echo "Clone complete."
fi

# 5. Handover to original entrypoint
echo "Starting PostgreSQL..."
exec docker-entrypoint.sh postgres
