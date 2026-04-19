from typing import Optional, Any
from uuid import UUID

from psycopg2.extras import Json

from rolling.app.db import get_connection

# ANALYSIS RUN
def create_analysis_run(project_id: UUID,
                        created_by_analyst_id: UUID,
                        analysis_kind: str,
                        execution_mode: str,
                        status: str,
                        parameters: dict[str, Any]) -> dict:
    """
    Creates a new analysis run associated with a project and an analyst.

    Args:
        project_id (UUID): The ID of the project to associate with this analysis run.
        created_by_analyst_id (UUID): The ID of the analyst who created this analysis run.
        analysis_kind (str): The kind of analysis run to create (e.g. "descriptive_hormone_analysis").
        execution_mode (str): The mode to in which execute the analysis (e.g. "traditional").
        status (str): The status of the analysis run (e.g. "completed").
        parameters (dict[str, Any]): Additional parameters of the analysis run.

    Returns:
        dict: The dictionary of the created analysis run.
            - "analysis_run_id" (UUID): The ID of the analysis run created.
            - "project_id" (UUID): The ID of the project associated with this analysis run.
            - "created_by_analyst_id" (UUID): The ID of the analyst who created this analysis run.
            - "analysis_kind" (str): The kind of analysis run to create (e.g. "descriptive_hormone_analysis").
            - "execution_mode" (str): The execution mode of the analysis run (e.g. "traditional").
            - "status" (str): The status of the analysis run (e.g. "completed").
            - "started_at" (datetime): A timestamp of when the analysis run was started.
            - "finished_at" (datetime): A timestamp of when the analysis run was finished, if applicable.
            - "parameters" (dict[str, Any]): A dictionary of additional parameters of the analysis run.
    """
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
    """
    Gets the analysis run record associated with a particular analysis run ID.

    It first checks whether the given analyst can access the given analysis run.

    Args:
        analysis_run_id (UUID): The ID of the analysis run to retrieve.
        analyst_id (UUID): The analyst accessing the analysis run record.

    Returns:
        Optional[dict]: A dictionary of the analysis run record, if it exists and is accessible to the given analyst. Otherwise, None.
            - "analysis_run_id" (UUID): The ID of the analysis run retrieved.
            - "project_id" (UUID): The ID of the project associated with this analysis run.
            - "created_by_analyst_id" (UUID): The ID of the analyst who created this analysis run.
            - "analysis_kind" (str): The kind of analysis run to create (e.g. "descriptive_hormone_analysis").
            - "execution_mode" (str): The execution mode of the analysis run (e.g. "traditional").
            - "status" (str): The status of the analysis run (e.g. "completed").
            - "started_at" (datetime): A timestamp of when the analysis run was started.
            - "finished_at" (datetime): A timestamp of when the analysis run was finished, if applicable.
            - "parameters" (dict[str, Any]): A dictionary of additional parameters of the analysis run.
    """
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

def get_analysis_runs_for_project(project_id: UUID, analyst_id: UUID) -> Optional[list[dict]]: # TODO rename to list_ and change return type
    """
    List the analysis runs associated with a particular project.

    It first checks whether the given analyst can access the given project.

    Args:
        project_id (UUID): The ID of the project to list the analysis runs for.
        analyst_id (UUID): The ID of the analyst accessing the record.

    Returns:
        Optional[list[dict]]: A list of dictionaries containing analysis run records. If the project is not found or the analyst is not allowed to access the project, None is returned.
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
                return None # TODO change to empty list
            cur.execute(query, (str(project_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def link_dataset_to_analysis_run(analysis_run_id: UUID, dataset_id: UUID) -> dict:
    """
    Links an analysis run to a dataset.

    This is to note that an analysis run made use of particular datasets.

    Args:
        analysis_run_id (UUID): The ID of the analysis run to link to the dataset.
        dataset_id (UUID): The ID of the dataset to link to the analysis run.

    Returns:
        dict: A dictionary of created record linking an analysis run to a dataset.
            - "analysis_run_id" (UUID): The ID of the analysis run.
            - "dataset_id" (UUID): The ID of the dataset to link to the analysis run.
            - "created_at" (datetime): A timestamp of when the analysis run was created.
    """
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
    """
    TODO: not completed
    List the linked analysis runs and datasets.

    Args:
        analysis_run_id (UUID): The ID of the analysis run to list the linked datasets.

    Returns:
        list[dict]: A list of dictionaries containing linked analysis runs and datasets records.
    """
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
    """
    Lists the datasets associated with the given analysis run.

    Args:
        analysis_run_id (UUID): The ID of the analysis run to list the datasets associated with the given analysis.

    Returns:
        list[dict]: A list of dictionaries containing datasets associated with the given analysis.

        Each dictionary in the list has the following data:
            - "dataset_id" (UUID): The ID of the dataset to list the datasets associated with the given analysis.
            - "uploaded_by_id" (UUID): The ID of the analyst who created the dataset associated with the given analysis.
            - "original_file_name" (str): The original file name of the uploaded dataset.
            - "stored_relative_path" (str): The stored relative path of the uploaded dataset.
            - "content_hash" (str): The content hash of the uploaded dataset.
            - "uploaded_at" (datetime): A timestamp of when the uploaded dataset was created.
            - "import status" (str): The status of the uploaded dataset.
            - "notes" (str): Notes on the uploaded dataset.
    """
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
    """
    List the analysis runs associated with the given analyst.

    Args:
        analyst_id (UUID): The ID of the analyst to list the associated analysis runs.

    Returns:
        list[dict]: A list of dictionaries containing analysis run records associated with the given analyst. If there are no analysis runs, an empty list is returned.
    """
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
    """
    List the analysis runs associated with the given execution mode.

    Args:
        execution_mode (str): The execution mode to list the associated analysis runs.

    Returns:
        list[dict]: A list of dictionaries containing analysis run records associated with the given execution mode.
    """
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
    """
    Validates whether the given analyst can access the given analysis run.

    Args:
        analyst_id (UUID): The ID of the analyst to check.
        analysis_run_id (UUID): The ID of the analysis run to check.

    Returns:
        bool: True if the analysis run exists and is accessible, False otherwise.
    """
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
def create_analysis_result(analysis_run_id: UUID, # TODO check access before creating
                           result_type: str,
                           result_payload: dict[str, Any]) -> dict:
    """
    Creates a new analysis result.

    Args:
        analysis_run_id (UUID): The ID of the analysis run to associate with the new analysis result.
        result_type (str): The type of the analysis result (e.g. "descriptive_hormone_analysis").
        result_payload (dict): The payload of the analysis result.

    Returns:
        dict: A dictionary containing the created analysis result record.
            - "analysis_run_id" (UUID): The ID of the analysis run.
            - "result_type" (str): The type of the analysis result.
            - "result_payload" (dict): The payload of the analysis result.
    """
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
    """
    Get an analysis result by its ID.

    Args:
        analysis_result_id (UUID): The ID of the analysis result to get.

    Returns:
        dict: A dictionary containing the analysis result record.
            - "analysis_result_id" (UUID): The ID of the created analysis result.
            - "analysis_run_id" (UUID): The ID of the associated analysis run.
            - "result_type" (str): The type of the analysis result.
            - "result_payload" (dict): The payload of the analysis result.
            - "created_at" (datetime): The timestamp of when the analysis result was created.
    """
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
    """
    Lists the analysis result records associated with the given analysis run.

    Args:
        analysis_run_id (UUID): The ID of the analysis run.

    Returns:
        list[dict]: A list of analysis result records associated with the given analysis run.
    """
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


def analyst_can_access_analysis_result( # TODO fix indentation
    analyst_id: UUID,
    analysis_result_id: UUID,
) -> bool:
    """
    Validates whether the given analysis result is accessible to the given analyst.

    Args:
        analyst_id (UUID): The ID of the analyst to check.
        analysis_result_id (UUID): The ID of the analysis result to check.

    Returns:
        bool: True if the analysis result exists and is accessible to the given analyst. False otherwise.
    """
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
    """
    Creates an analysis report.

    Args:
        analysis_run_id (UUID): The ID of the analysis run to associate with the report.
        report_text (str): The text of the analysis report.
        summary_text (Optional[str]): The text of the analysis report summary text.

    Returns:
        dict: A dictionary containing the analysis report record.
            - "analysis_report_id" (UUID): The ID of the created analysis report.
            - "analysis_run_id" (UUID): The ID of the associated analysis run.
            - "report_text" (str): The text of the analysis report.
            - "summary_text" (str): The text of the analysis report summary text.
            - "created_at" (datetime): The timestamp of when the analysis report was created.
    """
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
    """
    Get an analysis report by its ID.

    Args:
        analysis_report_id (UUID): The ID of the analysis report to get.

    Returns:
        dict: A dictionary containing the analysis report record.
            - "analysis_report_id" (UUID): The ID of the analysis report.
            - "analysis_run_id" (UUID): The ID of the associated analysis run.
            - "report_text" (str): The text of the analysis report.
            - "summary_text" (str): The text of the analysis report summary text.
            - "created_at" (datetime): The timestamp of when the analysis report was created.
    """
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
    """
    Get the analysis report by its analysis run.

    Args:
        analysis_run_id (UUID): The ID of the analysis run associated with the analysis report.

    Returns:
        Optional[dict]: A dictionary containing the analysis report record, if it exists.
            - "analysis_report_id" (UUID): The ID of the analysis report.
            - "analysis_run_id" (UUID): The ID of the associated analysis run.
            - "report_text" (str): The text of the analysis report.
            - "summary_text" (str): The text of the analysis report summary text.
            - "created_at" (datetime): The timestamp of when the analysis report was created.
    """
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
    """
    Validates if the given analyst can access the given analysis report.

    Args:
        analyst_id (UUID): The ID of the analyst to check.
        analysis_report_id (UUID): The ID of the analysis run to check.

    Returns:
        bool: True if the analysis report exists and is accessible to the given analyst. False otherwise.
    """
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
