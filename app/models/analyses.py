# API request/response models for running and retrieving analyses
from datetime import datetime, date
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ai import GenerateAIAnalysisReportRequest, GenerateAIAnalysisReportResponse

# ANALYSIS RUNS
class AnalysisRunCreate(BaseModel):
    project_id: UUID
    analysis_kind: str
    execution_mode: str
    status: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class AnalysisRunResponse(BaseModel):
    analysis_run_id: UUID
    project_id: UUID
    created_by_analyst_id: UUID
    analysis_kind: str
    execution_mode: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    parameters: dict[str, Any] = Field(default_factory=dict)


# ANALYSIS RESULTS
class AnalysisResultResponse(BaseModel):
    analysis_result_id: UUID
    analysis_run_id: UUID
    result_type: str
    result_payload: dict[str, Any]
    created_at: datetime


# ANALYSIS REPORTS
class AnalysisReportResponse(BaseModel):
    analysis_report_id: UUID
    analysis_run_id: UUID
    report_text: str
    summary_text: Optional[str] = None
    created_at: datetime


# REAL ANALYSIS
class RunDescriptiveHormoneAnalysisRequest(BaseModel):
    project_id: UUID
    include_hormone_names: Optional[list[str]] = None
    include_performance_types: Optional[list[str]] = None
    include_symptom_names: Optional[list[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    ai_assisted_report: bool = False
    ai_analysis_report_request: Optional[GenerateAIAnalysisReportRequest] = None


class RunDescriptiveAnalysisResponse(BaseModel):
    analysis_run: AnalysisRunResponse
    analysis_result: Optional[AnalysisResultResponse]
    analysis_report: Optional[AnalysisReportResponse]
    ai_analysis_report: Optional[GenerateAIAnalysisReportResponse] = None
    engine_result: dict[str, Any]
