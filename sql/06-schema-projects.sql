CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TABLE CREATION
CREATE TABLE projects.projects (
    -- lists projects
    project_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_analyst_id    UUID NOT NULL REFERENCES research.analysts(analyst_id) ON DELETE RESTRICT,
    name                VARCHAR(50) NOT NULL,
    description         VARCHAR(300),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT project_owner_name_unique
        UNIQUE (owner_analyst_id, "name")
);

CREATE TABLE projects.project_analysts (
    -- links projects with analyses
    project_id  UUID NOT NULL REFERENCES projects.projects(project_id) ON DELETE CASCADE,
    analyst_id  UUID NOT NULL REFERENCES research.analysts(analyst_id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at	TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project_id, analyst_id)      
);

CREATE TABLE projects.project_athletes (
    -- links projects with athletes
    project_id  UUID NOT NULL REFERENCES projects.projects(project_id) ON DELETE CASCADE,
    athlete_id  UUID NOT NULL REFERENCES research.athletes(athlete_id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at	TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project_id, athlete_id)
);

CREATE TABLE projects.project_datasets (
    -- links projects with datasets
    project_id  UUID NOT NULL REFERENCES projects.projects(project_id) ON DELETE CASCADE,
    dataset_id  UUID NOT NULL REFERENCES research.datasets(dataset_id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at 	TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project_id, dataset_id)
);

-- FUNCTIONS AND TRIGGERS
-- insert project creator as project analyst
CREATE OR REPLACE FUNCTION projects.add_owner_to_project_analysts()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO projects.project_analysts (
        project_id,
        analyst_id,
        created_at
    )
    VALUES (
        NEW.project_id,
        NEW.owner_analyst_id,
        NOW()
    )
    ON CONFLICT (project_id, analyst_id) DO NOTHING;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_add_owner_to_project_analysts
AFTER INSERT ON projects.projects
FOR EACH ROW
EXECUTE FUNCTION projects.add_owner_to_project_analysts();

-- triggers for updating updated_at
DROP TRIGGER IF EXISTS trg_projects_set_row_timestamps ON projects.projects;
DROP TRIGGER IF EXISTS trg_project_analysts_set_row_timestamps ON projects.project_analysts;
DROP TRIGGER IF EXISTS trg_project_athletes_set_row_timestamps ON projects.project_athletes;

CREATE TRIGGER trg_projects_set_row_timestamps
BEFORE INSERT OR UPDATE ON projects.projects
FOR EACH ROW
EXECUTE FUNCTION app_private.set_row_timestamps();

CREATE TRIGGER trg_project_analysts_set_row_timestamps
BEFORE INSERT OR UPDATE ON projects.project_analysts
FOR EACH ROW
EXECUTE FUNCTION app_private.set_row_timestamps();

CREATE TRIGGER trg_project_athletes_set_row_timestamps
BEFORE INSERT OR UPDATE ON projects.project_athletes
FOR EACH ROW
EXECUTE FUNCTION app_private.set_row_timestamps();
