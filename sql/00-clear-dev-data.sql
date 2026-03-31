-- Clears workflow and imported data while preserving seeded lookup/reference tables.

BEGIN;

TRUNCATE TABLE
    app_private.agent_traces,
    research.analysis_reports,
    research.analysis_results,
    research.analysis_run_datasets,
    research.analysis_runs,
    projects.project_datasets,
    projects.project_athletes,
    projects.project_analysts,
    research.performance_records,
    research.hormone_measurements,
    research.cycle_phase_records,
    research.symptom_records,
    research.athlete_body,
    research.athletes,
    research.datasets,
    projects.projects,
    research.analysts
RESTART IDENTITY CASCADE;

COMMIT;
