-- verifying the end-to-end flow of analysis runs and results on the backend

SELECT analysis_run_id, project_id, created_by_analyst_id,
       analysis_kind, execution_mode, status, parameters
FROM research.analysis_runs
ORDER BY started_at DESC
LIMIT 5;

SELECT analysis_result_id, analysis_run_id, result_type, result_payload
FROM research.analysis_results
ORDER BY created_at DESC
LIMIT 5;
