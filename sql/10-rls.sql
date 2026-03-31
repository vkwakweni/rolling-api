-- TODO: Description

-- 1. Analysts can only access projects they belong to

-- 2. All research data access flows through project membership

ALTER TABLE projects.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects.projects FORCE ROW LEVEL SECURITY;

-- Project membership
CREATE POLICY analyst_select_policy ON projects.projects
FOR SELECT
USING (
    app_private.is_service_role()
    OR owner_analyst_id = app_private.current_user_id()
    OR EXISTS (
        SELECT 1
        FROM projects.project_analysts pa
        WHERE pa.analyst_id = app_private.current_user_id()
          AND pa.project_id = projects.projects.project_id
    )
);

CREATE POLICY analyst_insert_policy ON projects.projects
FOR INSERT
WITH CHECK (
    app_private.is_service_role()
    OR owner_analyst_id = app_private.current_user_id()
);

CREATE POLICY analyst_update_policy ON projects.projects
FOR UPDATE
WITH CHECK (
    app_private.is_service_role()
    OR owner_analyst_id = app_private.current_user_id()
);

CREATE POLICY analyst_delete_policy ON projects.projects
FOR DELETE
USING (
    app_private.is_service_role()
    OR owner_analyst_id = app_private.current_user_id()
);

CREATE POLICY project_analyst_select_policy ON projects.project_analysts
FOR SELECT
USING (
    app_private.is_service_role()
    OR analyst_id = app_private.current_user_id()
);
