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


class AgentTraceMetadata(BaseModel):
    status: Optional[str] = None
    operation: Optional[str] = None
    notes: Optional[str] = None


class AgentTraceCreate(BaseModel):
    analysis_run_id: UUID
    step_name: str
    tool_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTraceResponse(BaseModel):
    agent_trace_id: UUID
    analysis_run_id: UUID
    step_name: str
    tool_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AIAnalysisReportCreate(BaseModel):
    analysis_run_id: UUID
    agent_trace_id: UUID
    model_name: str
    report_text: str
    summary_text: Optional[str] = None
    comparison_notes: Optional[str] = None


class AIAnalysisReportResponse(BaseModel):
    ai_analysis_report_id: UUID
    analysis_run_id: UUID
    agent_trace_id: UUID
    model_name: str
    report_text: str
    summary_text: Optional[str] = None
    comparison_notes: Optional[str] = None
    created_at: datetime


class GenerateAIReportResponse(BaseModel):
    agent_trace: AgentTraceResponse
    ai_report: AIAnalysisReportResponse

class AIPrompt(BaseModel):
    ...

class AIModelOutput(BaseModel):
    ...
