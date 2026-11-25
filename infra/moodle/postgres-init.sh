#!/bin/sh
set -eu
# Password comes from a private mounted file; never log it.
pw=$(cat /tmp/moodle-password)
psql -v ON_ERROR_STOP=1 --username postgres --dbname moodle <<SQL >/dev/null
CREATE ROLE moodle LOGIN PASSWORD '$pw' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
ALTER DATABASE moodle OWNER TO moodle;
GRANT ALL ON SCHEMA public TO moodle;
SQL
rm -f /tmp/moodle-password
