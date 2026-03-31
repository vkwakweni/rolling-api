-- Setting up the database
-- Run as postgres in database postgres

-- Create privileged roles
CREATE ROLE rolling_owner NOLOGIN;

CREATE ROLE rolling_migrator
    LOGIN PASSWORD 'change_migrator';

CREATE ROLE appuser
    LOGIN PASSWORD 'change_appuser';

CREATE DATABASE rolling
    OWNER rolling_owner
    ENCODING 'UTF-8';

GRANT CONNECT, TEMP ON DATABASE rolling TO appuser;
GRANT rolling_owner TO rolling_migrator;