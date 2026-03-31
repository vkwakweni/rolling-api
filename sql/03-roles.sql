-- Run inside the rolling data
GRANT CONNECT ON DATABASE rolling TO appuser;

-- Use all schemas
GRANT USAGE
    ON SCHEMA app_private, projects, research
    TO appuser;
-- Broad DML for projects and research
GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA projects, research
    TO appuser;
-- Read-only for app_private
GRANT SELECT
    ON ALL TABLES IN SCHEMA app_private
    TO appuser;
GRANT USAGE, SELECT
    ON ALL SEQUENCES IN SCHEMA app_private, projects, research
    TO appuser;

ALTER DEFAULT PRIVILEGES FOR ROLE rolling_owner
    IN SCHEMA projects, research
    GRANT SELECT, INSERT, UPDATE, DELETE
    ON TABLES TO appuser;

ALTER DEFAULT PRIVILEGES FOR ROLE rolling_owner
    IN SCHEMA app_private
    GRANT SELECT
    ON TABLES TO appuser;

ALTER DEFAULT PRIVILEGES FOR ROLE rolling_owner
    IN SCHEMA projects, research
    GRANT USAGE, SELECT
    ON SEQUENCES TO appuser;

ALTER DEFAULT PRIVILEGES FOR ROLE rolling_owner
    IN SCHEMA app_private
    GRANT USAGE, SELECT
    ON SEQUENCES TO appuser;

