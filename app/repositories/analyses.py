from typing import Optional, Any
from uuid import UUID

from psycopg2.extras import Json

from app.db import get_connection

# ANALYSIS RUN
def create_analysis_run(project_id: UUID,
                        created_by_analyst_id: UUID,
                        analysis_kind: str,
                        execution_mode: str,
                        status: str,
                        parameters: dict[str, Any]) -> dict:
    query = """
            INSERT INTO research.analysis_runs (
                project_id,
                created_by_analyst_id,
                analysis_kind,
                execution_mode,
                status,
                parameters
                )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING analysis_run_id, project_id, created_by_analyst_id,
                        analysis_kind, execution_mode, status,
                        started_at, finished_at, parameters;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id), str(created_by_analyst_id),
                                analysis_kind, execution_mode, status, Json(parameters)))
            row = cur.fetchone()
            return dict(row)
    

def get_analysis_run_by_id(analysis_run_id: UUID,
                           analyst_id: UUID) -> Optional[dict]:
    if not analyst_can_access_analysis_run(analyst_id, analysis_run_id):
        return None
    
    query = """
            SELECT analysis_run_id, project_id, created_by_analyst_id,
                    analysis_kind, execution_mode, status,
                    started_at, finished_at, parameters
            FROM research.analysis_runs
            WHERE analysis_run_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def get_analysis_runs_for_project(project_id: UUID, analyst_id: UUID) -> Optional[list[dict]]:
    access_query = """
                   SELECT 1
                   FROM projects.projects p
                   WHERE project_id = %s
                     AND (
                            p.owner_analyst_id = %s
                            OR EXISTS (
                                SELECT 1
                                FROM projects.project_analysts pa
                                WHERE pa.project_id = p.project_id
                                  AND pa.analyst_id = %s
                                  )
                            );
                   """
    
    query = """
            SELECT analysis_run_id, project_id, created_by_analyst_id,
                    analysis_kind, execution_mode, status,
                    started_at, finished_at, parameters
            FROM research.analysis_runs
            WHERE project_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(access_query, (str(project_id), str(analyst_id), str(analyst_id)))
            access_row = cur.fetchone()
            if not access_row:
                return None
            cur.execute(query, (str(project_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def link_dataset_to_analysis_run(analysis_run_id: UUID, dataset_id: UUID) -> dict:
    query = """
            INSERT INTO research.analysis_run_datasets (
                analysis_run_id,
                dataset_id
                )
            VALUES (%s, %s)
            RETURNING analysis_run_id, dataset_id, created_at;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id), str(dataset_id)))
            row = cur.fetchone()
            return dict(row)
        
def list_analysis_run_dataset_links(analysis_run_id: UUID) -> list[dict]:
    query = """
            SELECT analysis_run_id, dataset_id, created_at
            FROM research.analysis_run_datasets
            WHERE analysis_run_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def list_datasets_for_analysis_run(analysis_run_id: UUID) -> list[dict]:
    query = """
            SELECT d.dataset_id, d.uploaded_by_id, d.original_file_name,
                   d.stored_relative_path, d.content_hash, d.uploaded_at,
                   d.import_status, d.notes
            FROM research.analysis_run_datasets ard
            JOIN research.datasets d ON ard.dataset_id = d.dataset_id
            WHERE ard.analysis_run_id = %s
            ORDER BY d.uploaded_at DESC;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def list_analysis_runs_by_analyst(analyst_id: UUID) -> list[dict]:
    query = """
            SELECT analysis_run_id, project_id, created_by_analyst_id,
                    analysis_kind, execution_mode, status,
                    started_at, finished_at, parameters
            FROM research.analysis_runs
            WHERE created_by_analyst_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analyst_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

def list_analysis_runs_by_execution_mode(execution_mode: str) -> list[dict]:
    query = """
            SELECT analysis_run_id, project_id, created_by_analyst_id,
                    analysis_kind, execution_mode, status,
                    started_at, finished_at, parameters
            FROM research.analysis_runs
            WHERE execution_mode = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(execution_mode),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def analyst_can_access_analysis_run(analyst_id: UUID,
                                    analysis_run_id: UUID,
                                    ) -> bool:
    project_id_query = """
                       SELECT project_id
                       FROM research.analysis_runs
                       WHERE analysis_run_id = %s;
                       """
    
    access_query = """
                   SELECT 1
                   FROM projects.projects p
                   WHERE project_id = %s
                     AND (
                            p.owner_analyst_id = %s
                            OR EXISTS (
                                SELECT 1
                                FROM projects.project_analysts pa
                                WHERE pa.project_id = p.project_id
                                  AND pa.analyst_id = %s
                                  )
                            );
                   """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(project_id_query, (str(analysis_run_id),))
            project_row = cur.fetchone()
            if project_row is None:
                return False # Analysis run not found, treat as no access
            project_row = dict(project_row)["project_id"]
            cur.execute(access_query, (str(project_row), str(analyst_id), str(analyst_id)))
            row = cur.fetchone()
            return row is not None

# ANALYSIS RESULTS
def create_analysis_result(analysis_run_id: UUID,
                           result_type: str,
                           result_payload: dict[str, Any]) -> dict:
    query = """
            INSERT INTO research.analysis_results (
                analysis_run_id,
                result_type,
                result_payload
                )
            VALUES (%s, %s, %s)
            RETURNING analysis_result_id, analysis_run_id, result_type,
                        result_payload, created_at;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id), result_type, Json(result_payload)))
            row = cur.fetchone()
            return dict(row)

def get_analysis_result_by_id(analysis_result_id: UUID) -> Optional[dict]:
    query = """
            SELECT analysis_result_id, analysis_run_id, result_type,
                        result_payload, created_at
            FROM research.analysis_results
            WHERE analysis_result_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_result_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def list_analysis_results_by_analysis_run(analysis_run_id: UUID) -> list[dict]:
    query = """
            SELECT analysis_result_id, analysis_run_id, result_type,
                        result_payload, created_at
            FROM research.analysis_results
            WHERE analysis_run_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def analyst_can_access_analysis_result(
    analyst_id: UUID,
    analysis_result_id: UUID,
) -> bool:
    query = """
            SELECT analysis_run_id
            FROM research.analysis_results
            WHERE analysis_result_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_result_id),))
            row = cur.fetchone()
            if row is None:
                return False
            analysis_run_id = dict(row)["analysis_run_id"]
            return analyst_can_access_analysis_run(analyst_id, analysis_run_id)


# ANALYSIS REPORTS
def create_analysis_report(
    analysis_run_id: UUID,
    report_text: str,
    summary_text: Optional[str] = None,
) -> dict:
    query = """
            INSERT INTO research.analysis_reports (
                analysis_run_id,
                report_text,
                summary_text
                )
            VALUES (%s, %s, %s)
            RETURNING analysis_report_id, analysis_run_id, report_text,
                        summary_text, created_at;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id), report_text, summary_text))
            row = cur.fetchone()
            return dict(row)


def get_analysis_report_by_id(analysis_report_id: UUID) -> Optional[dict]:
    query = """
            SELECT analysis_report_id, analysis_run_id, report_text,
                    summary_text, created_at
            FROM research.analysis_reports
            WHERE analysis_report_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_report_id),))
            row = cur.fetchone()
            return dict(row) if row else None


def get_analysis_report_by_analysis_run(analysis_run_id: UUID) -> Optional[dict]:
    query = """
            SELECT analysis_report_id, analysis_run_id, report_text,
                    summary_text, created_at
            FROM research.analysis_reports
            WHERE analysis_run_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            row = cur.fetchone()
            return dict(row) if row else None


def analyst_can_access_analysis_report(
    analyst_id: UUID,
    analysis_report_id: UUID,
) -> bool:
    query = """
            SELECT analysis_run_id
            FROM research.analysis_reports
            WHERE analysis_report_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_report_id),))
            row = cur.fetchone()
            if row is None:
                return False
            analysis_run_id = dict(row)["analysis_run_id"]
            return analyst_can_access_analysis_run(analyst_id, analysis_run_id)
