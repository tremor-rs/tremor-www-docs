#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE measurements;
    \c measurements;
    CREATE TABLE events (
     user_id INT NOT NULL,
     product_id VARCHAR(30) NOT NULL,
     quantity INT NOT NULL,
     created_at TIMESTAMP NOT NULL
    );
EOSQL
