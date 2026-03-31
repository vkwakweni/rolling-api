CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- HELPERS
CREATE OR REPLACE FUNCTION app_private.current_user_id()
-- Current user helper: gets current ID, NULL if abset
    RETURNS UUID
    LANGUAGE sql
    STABLE
    AS $$
        SELECT current_setting('app.current_user_id', true)::uuid
    $$;

CREATE OR REPLACE FUNCTION app_private.is_service_role()
-- Service role helper
    RETURNS boolean
    LANGUAGE sql
    STABLE
    AS $$
        SELECT current_user = 'appuser'
    $$;

CREATE OR REPLACE FUNCTION app_private.set_row_timestamps()
-- Timestamp trigger
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF TG_OP = 'INSERT' THEN
            IF NEW.created_at IS NULL THEN
                NEW.created_at := NOW();
            END IF;
            IF NEW.updated_at IS NULL THEN
                NEW.updated_at := NOW();
            END IF;
        ELSE
            NEW.updated_at := NOW();
        END IF;
        RETURN NEW;
    END;
    $$;

