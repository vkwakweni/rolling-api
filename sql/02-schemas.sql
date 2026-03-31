-- Run inside the rolling database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- create application schemas
CREATE SCHEMA IF NOT EXISTS app_private AUTHORIZATION rolling_owner;
CREATE SCHEMA IF NOT EXISTS research AUTHORIZATION rolling_owner;
CREATE SCHEMA IF NOT EXISTS projects AUTHORIZATION rolling_owner;
