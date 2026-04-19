from typing import Optional, Any
from uuid import UUID

from psycopg2.extras import Json

from rolling.app.db import get_connection
from rolling.app.repositories.analyses import get_analysis_run_by_id
from rolling.app.repositories.analyses import analyst_can_access_analysis_run


# AI AGENT TRACES
def create_agent_trace(analyst_id: UUID,
                       analysis_run_id: UUID,
                       step_name: str,
                       model_name: str,
                       metadata: dict[str, Any]
                       ) -> Optional[dict]:
    """
    Creates a new agent trace for a specific analysis run.
    
    It first checks if the analysis run exists and is accessible by the analyst. If not, it returns None.
    If the analysis run is valid, it inserts a new record into the agent_traces table and returns the created agent trace as a dictionary.
    
    Args:
        analyst_id (UUID): The ID of the analyst creating the agent trace.
        analysis_run_id (UUID): The ID of the analysis run to which the agent trace belongs.
        step_name (str): The name of the step in the agent's process.
        model_name (str): The name of the AI model used in this step.
        metadata (dict[str, Any]): Additional metadata related to this agent trace.

    Returns:
        Optional[dict]: A dictionary representing the created agent trace, or None if the analysis run is not found or not accessible by the analyst.
            - "agent_trace_id" (UUID): The ID of the agent trace created.
            - "analysis_run_id" (UUID): The ID of the analysis run to which the agent trace belongs.
            - "step_name" (str): The name of the step in the agent's process.
            - "model_name" (str): The name of the AI model used in this step.
            - "metadata" (dict[str, Any]): Additional metadata related to this agent trace.
            - "created_at" (datetime): The time the agent trace was created.
    """
    if get_analysis_run_by_id(analyst_id=analyst_id, analysis_run_id=analysis_run_id) is None:
        return None
    
    query = """
            INSERT INTO app_private.agent_traces (
                analysis_run_id,
                step_name,
                model_name,
                metadata
                )
            VALUES (%s, %s, %s, %s)
            RETURNING agent_trace_id, analysis_run_id, step_name, model_name,
                        metadata, created_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id), step_name, model_name, Json(metadata)))
            row = cur.fetchone()
            return dict(row)

def get_agent_trace_by_id(analyst_id: UUID,
                          agent_trace_id: UUID
                          ) -> Optional[dict]:
    """
    Gets the agent trace record associated with a particular agent trace ID.

    Args:
        analyst_id (UUID): The ID of the analyst creating the agent trace.
        agent_trace_id (UUID): The ID of the agent trace to retrieve.

    Returns:
        Optional[dict]: A dictionary of agent trace record, if it exists and is accessible to the given analyst. Otherwise, None.
            - "agent_trace_id" (UUID): The ID of the agent trace retrieved.
            - "analysis_run_id" (UUID): The ID of the analysis associated with the agent trace.
            - "step_name" (str): The name of the step in the agent's process.
            - "model_name" (str): The name of the AI model used in this step.
            - "metadata" (dict[str, Any]): Additional metadata related to this agent trace.
            - "created_at" (datetime): The time the agent trace was created.
    """
    query = """
            SELECT agent_trace_id, analysis_run_id, step_name, model_name,
                    metadata, created_at
            FROM app_private.agent_traces
            WHERE agent_trace_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(agent_trace_id),))
            row = cur.fetchone()
            if not row:
                return None
            analysis_run_id = dict(row).get("analysis_run_id")
            if get_analysis_run_by_id(analysis_run_id, analyst_id) is not None:
                return dict(row)
            return None
        
def list_agent_traces_by_analysis_run(analyst_id: UUID,
                                      analysis_run_id: UUID
                                      ) -> list[dict]:
    """
    Lists the agent traces associated with a particular analysis run.

    Args:
        analyst_id (UUID): The ID of the analyst accessing the record.
        analysis_run_id (UUID): The ID of the analysis run to list the agent traces for.

    Returns:
        list[dict]: A list of dictionaries containing agent trace records. If the analysis run is not found or the analyst is not allowed to access the analysis run, an empty list is returned.
    """
    if get_analysis_run_by_id(analysis_run_id=analysis_run_id, analyst_id=analyst_id) is None:
        return []
    
    query = """
            SELECT agent_trace_id, analysis_run_id, step_name, model_name,
                    metadata, created_at
            FROM app_private.agent_traces
            WHERE analysis_run_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]


# AI ANALYSIS REPORTS
def create_ai_analysis_report(analyst_id: UUID,
                              analysis_run_id: UUID,
                              agent_trace_id: UUID,
                              model_name: str,
                              report_text: str,
                              summary_text: Optional[str] = None,
                              comparison_notes: Optional[str] = None
                              ) -> Optional[dict]:
    """
    Creates a new AI analysis report.

    Args
        analyst_id (UUID): The ID of the analyst created the report.
        analysis_run_id (UUID): The ID of the analysis run for which the report generated.
        model_name (str): The name of the AI model used to generate the report.
        report_text (str): The text of the report.
        summary_text (str): A summary of the report.
        comparison (Optional[str]): A comparison between the traditional report and the AI-generated report.

    Returns:
        Optional[dict]: A dictionary of the created AI analysis report record, if the analysis run exists and the analyst can access the analysis run. Otherwise, None.
            - "analysis_run_id" (UUID): The ID of the analysis associated with the agent trace.
            - "agent_trace_id" (UUID): The ID of the agent trace created.
            - "model_name" (str): The name of the AI model used in this step.
            - "report_text" (str): The text of the report.
            - "summary_text" (str): The summary of the report.
            - "comparison_notes" (Optional[str]): A comparison between the traditional report and the AI-generated report.
    """
    if get_analysis_run_by_id(analysis_run_id=analysis_run_id, analyst_id=analyst_id) is None:
        return None
    
    query = """
            INSERT INTO research.ai_analysis_reports (
                analysis_run_id,
                agent_trace_id,
                model_name,
                report_text,
                summary_text,
                comparison_notes
                )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING ai_analysis_report_id, analysis_run_id, agent_trace_id, model_name,
                        report_text, summary_text, comparison_notes, created_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id), str(agent_trace_id), model_name,
                                report_text, summary_text, comparison_notes))
            row = cur.fetchone()
            return dict(row)


def get_ai_analysis_report_by_id(analyst_id: UUID,
                                 ai_analysis_report_id: UUID
                                 ) -> Optional[dict]:
    """
    Gets the AI analysis report associated with a particular AI analysis run.

    Args:
        analyst_id (UUID): The ID of the analyst creating the agent trace.
        ai_analysis_report_id (UUID): The ID of the AI analysis report to retrieve.

    Returns:
        Optional[dict]: A dictionary of the AI analysis report record, if it exists and is accessible to the given analyst. Otherwise, None.
            - "ai_analysis_report_id" (UUID): The ID of the AI analysis report retrieved.
            - "analysis_run_id" (UUID): The ID of the analysis associated with the AI analysis report record.
            - "agent_trace_id" (UUID): The ID of the agent trace.
            - "model_name" (str): The name of the AI model used to generate the report.
            - "report_text" (str): The text of the report.
            - "summary_text" (str): The summary of the report.
            - "comparison_notes" (Optional[str]): A comparison between the traditional report and the AI-generated report.
            - "created_at": created_at
        """
    run_query = """
                SELECT analysis_run_id
                FROM research.ai_analysis_reports aar
                WHERE ai_analysis_report_id = %s;
                """
    
    query = """
            SELECT ai_analysis_report_id, analysis_run_id, agent_trace_id, model_name,
                    report_text, summary_text, comparison_notes, created_at
            FROM research.ai_analysis_reports
            WHERE ai_analysis_report_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(run_query, (str(ai_analysis_report_id),))
            row = cur.fetchone()
            if row is not None:
                if not analyst_can_access_analysis_run(analyst_id=analyst_id,
                                                       analysis_run_id=row.get("analysis_run_id")):
                    return None

            cur.execute(query, (str(ai_analysis_report_id),))
            row = cur.fetchone()
            if not row:
                return None
            if get_analysis_run_by_id(analysis_run_id=dict(row).get("analysis_run_id"),
                                      analyst_id=analyst_id) is not None:
                return dict(row)
            return None

def list_ai_analysis_reports_for_analysis_run(analyst_id: UUID,
                                              analysis_run_id: UUID
                                              ) -> list[dict]:
    """
        Lists the AI analysis reports associated with a particular analysis run.

        Args:
            analyst_id (UUID): The ID of the analyst accessing the record.
            analysis_run_id (UUID): The ID of the analysis run to list the AI analysis reports for.

        Returns:
            list[dict]: A list of dictionaries containing AI analysis report records. If the analysis run is not found or the analyst is not allowed to access the analysis run, an empty list is returned.
        """
    if get_analysis_run_by_id(analysis_run_id=analysis_run_id, analyst_id=analyst_id) is None:
        return []
    
    query = """
            SELECT ai_analysis_report_id, analysis_run_id, agent_trace_id, model_name,
                    report_text, summary_text, comparison_notes, created_at
            FROM research.ai_analysis_reports
            WHERE analysis_run_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
