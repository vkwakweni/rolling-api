from typing import Optional, Any
from uuid import UUID

from psycopg2.extras import Json

from app.db import get_connection
from app.repositories.analyses import get_analysis_run_by_id


# AI AGENT TRACES
def create_agent_trace(analyst_id: UUID,
                       analysis_run_id: UUID,
                       step_name: str,
                       tool_name: str,
                       metadata: dict[str, Any]
                       ) -> Optional[dict]:
    if get_analysis_run_by_id(analyst_id=analyst_id, analysis_run_id=analysis_run_id) is None:
        return None
    
    query = """
            INSERT INTO app_private.agent_traces (
                analysis_run_id,
                step_name,
                tool_name,
                metadata
                )
            VALUES (%s, %s, %s, %s)
            RETURNING agent_trace_id, analysis_run_id, step_name, tool_name,
                        metadata, created_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analysis_run_id), step_name, tool_name, Json(metadata)))
            row = cur.fetchone()
            return dict(row)

def get_agent_trace_by_id(analyst_id: UUID,
                          agent_trace_id: UUID
                          ) -> Optional[dict]:
    query = """
            SELECT agent_trace_id, analysis_run_id, step_name, tool_name,
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


# AI ANALYSIS REPORTS
def create_ai_analysis_report(analyst_id: UUID,
                              analysis_run_id: UUID,
                              agent_trace_id: UUID,
                              model_name: str,
                              report_text: str,
                              summary_text: Optional[str] = None,
                              comparison_notes: Optional[str] = None
                              ) -> Optional[dict]:
    
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
    query = """
            SELECT ai_analysis_report_id, analysis_run_id, agent_trace_id, model_name,
                    report_text, summary_text, comparison_notes, created_at
            FROM research.ai_analysis_reports
            WHERE ai_analysis_report_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
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
