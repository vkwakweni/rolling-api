from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AIReportInput(BaseModel):
    summary: dict[str, Any] = Field(default_factory=dict)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    report_text: Optional[str] = None
    summary_text: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AITracePayload(BaseModel):
    report_text: str
    summary_text: Optional[str] = None
    model_name: Optional[str] = None
    traditional_report_excerpt: Optional[str] = None
    comparison: dict[str, Any] = Field(default_factory=dict)


class AgentTraceResponse(BaseModel):
    agent_trace_id: UUID
    analysis_run_id: UUID
    step_name: str
    tool_name: Optional[str] = None
    trace_payload: AITracePayload
    created_at: datetime


class AIReportGenerationResponse(BaseModel):
    agent_trace: AgentTraceResponse
    report_text: str
    summary_text: Optional[str] = None
