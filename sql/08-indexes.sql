CREATE INDEX performance_records_athlete_time_idx
ON research.performance_records (athlete_id, observed_on);

CREATE INDEX cycle_phase_records_athlete_time_idx
ON research.cycle_phase_records (athlete_id, observed_on);

CREATE INDEX symptom_records_athlete_time_idx
ON research.symptom_recordS (athlete_id, observed_on);

CREATE INDEX hormone_measurements_athlete_time_idx
ON research.hormone_measurements (athlete_id, observed_on);

CREATE INDEX project_analysts_analyst_idx
ON projects.project_analysts (analyst_id);

CREATE INDEX project_athletes_athlete_idx
ON projects.project_athletes (athlete_id);

CREATE INDEX analysis_runs_project_idx
ON research.analysis_runs (project_id, started_at);

