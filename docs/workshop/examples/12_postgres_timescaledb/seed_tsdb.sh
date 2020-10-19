#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE measurements;
    \c measurements;
    CREATE TABLE events (
     user_id INT8 NOT NULL,
     product_id VARCHAR NOT NULL,
     quantity INT8 NOT NULL,
     created_at TIMESTAMPTZ NOT NULL
    );
EOSQL
