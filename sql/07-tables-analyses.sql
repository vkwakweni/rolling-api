-- ANALYSES
DROP TABLE IF EXISTS research.analysis_runs CASCADE;
DROP TABLE IF EXISTS research.analysis_results CASCADE;
DROP TABLE IF EXISTS research.analysis_reports CASCADE;

CREATE TABLE research.analysis_runs (
    -- for logging analyses
    analysis_run_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id              UUID NOT NULL REFERENCES projects.projects(project_id) ON DELETE CASCADE,
    created_by_analyst_id   UUID NOT NULL REFERENCES research.analysts(analyst_id) ON DELETE RESTRICT,
    analysis_kind           TEXT NOT NULL,
    execution_mode          TEXT NOT NULL, -- traditional | ai_assisted
    status                  TEXT NOT NULL DEFAULT 'completed',
    started_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at             TIMESTAMPTZ,
    parameters              JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE research.analysis_run_datasets (
    analysis_run_id   UUID NOT NULL REFERENCES research.analysis_runs(analysis_run_id) ON DELETE CASCADE,
    dataset_id        UUID NOT NULL REFERENCES research.datasets(dataset_id) ON DELETE CASCADE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (analysis_run_id, dataset_id)
);


CREATE TABLE research.analysis_results (
    -- for statistical summaries and conclusions (structured outpits)
    analysis_result_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id     UUID NOT NULL REFERENCES research.analysis_runs(analysis_run_id) ON DELETE CASCADE,
    result_type         TEXT NOT NULL,
    result_payload      JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE research.analysis_reports (
    -- for metadata for reports
    analysis_report_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id     UUID NOT NULL UNIQUE REFERENCES research.analysis_runs(analysis_run_id) ON DELETE CASCADE,
    report_text         TEXT NOT NULL, -- could be very large (I think in Markdown format)
    summary_text        TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

