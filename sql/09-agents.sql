-- AGENTS
CREATE TABLE app_private.agent_traces (
    -- Tracking what agents do
    agent_trace_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id UUID NOT NULL REFERENCES research.analysis_runs(analysis_run_id) ON DELETE CASCADE,
    step_name TEXT NOT NULL,
    tool_name TEXT,
    trace_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
