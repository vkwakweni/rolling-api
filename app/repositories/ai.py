from typing import Optional, Any
from uuid import UUID

from app.db import get_connection


# AI AGENT TRACES
def create_agent_trace(analyst_id: UUID,
                       analysis_run_id: UUID,
                       step_name: str,
                       tool_name: str,
                       metadata: dict[str, Any] = None
                       ) -> dict:
    ...

def get_agent_trace_by_id(analyst_id: UUID,
                          agent_trace_id: UUID
                          ) -> Optional[dict]:
    ...


# AI ANALYSIS REPORTS
def create_ai_analysis_report(analyst_id: UUID,
                              analysis_run_id: UUID,
                              agent_trace_id: UUID,
                              model_name: str,
                              report_text: str,
                              summary_text: Optional[str] = None,
                              comparison_notes: Optional[str] = None
                              ) -> dict:
    ...

def get_ai_analysis_report_by_id(analyst_id: UUID,
                                 ai_analysis_report_id: UUID
                                 ) -> Optional[dict]:
    ...

def list_ai_analysis_reports_for_analysis_run(analyst_id: UUID,
                                              analysis_run_id: UUID
                                              ) -> list[dict]:
    ...
