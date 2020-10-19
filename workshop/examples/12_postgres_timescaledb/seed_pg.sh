#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE products;
    \c products;
    CREATE TABLE transactions (
     user_id INT NOT NULL,
     product_id VARCHAR(30) NOT NULL,
     quantity INT NOT NULL,
     created_at TIMESTAMPTZ NOT NULL
    );
    INSERT INTO transactions VALUES (20,20,98,'2020-02-10 20:02:02.000000 +00:00');
EOSQL

