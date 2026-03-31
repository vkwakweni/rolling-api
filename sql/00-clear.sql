-- Run this script while connected to the `postgres` maintenance database, not `rolling`.
-- disconnect from database rolling
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'rolling'
  AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS rolling;

DROP ROLE IF EXISTS appuser;
DROP ROLE IF EXISTS rolling_migrator;
DROP ROLE IF EXISTS rolling_owner;
