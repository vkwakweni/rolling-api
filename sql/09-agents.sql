-- AGENTS
CREATE TABLE app_private.agent_traces (
    -- Tracking what agents do
    agent_trace_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id UUID NOT NULL REFERENCES research.analysis_runs(analysis_run_id) ON DELETE CASCADE,
    step_name       TEXT NOT NULL,
    model_name      TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE research.ai_analysis_reports (
    ai_analysis_report_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id         UUID NOT NULL REFERENCES research.analysis_runs(analysis_run_id) ON DELETE CASCADE,
    agent_trace_id          UUID REFERENCES app_private.agent_traces(agent_trace_id) ON DELETE SET NULL,
    model_name              TEXT NOT NULL,
    report_text             TEXT NOT NULL,
    summary_text            TEXT,
    comparison_notes        TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

