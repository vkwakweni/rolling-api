# API request/response models for running and retrieving analyses
from datetime import datetime, date
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

from rolling.app.models.ai import GenerateAIAnalysisReportRequest, GenerateAIAnalysisReportResponse

# ANALYSIS RUNS
class AnalysisRunCreate(BaseModel):
    """
    Represents the data required to create a new analysis run.
    
    Attributes
        project_id (UUID): Unique identifier for a project.
        analysis_kind (str): The kind of analysis to be performed (e.g. "descriptive_hormone_analysis").
        execution_mode (str): The mode of execution for the analysis run (e.g. "traditional").
        parameters (Optional[dict[str, Any]]): A dictionary of additional parameters for the analysis.
    """
    project_id: UUID
    analysis_kind: str
    execution_mode: str
    status: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class AnalysisRunResponse(BaseModel):
    """
    Represents the data returned for an analysis run, including metadata about the run and its parameters.
    
    Attributes
        analysis_run_id (UUID): Unique identifier for the analysis run.
        project_id (UUID): Unique identifier for a project.
        created_by_analyst_id (UUID): Unique identifier for the analyst who created the run.
        analysis_kind (str): The kind of analysis that was executed (e.g. "descriptive_hormone_analysis").
        execution_mode (str): The mode of execution for the analysis run (e.g. "traditional").
        status (str): The current status of the analysis run (e.g. "running", "completed", "failed").
        started_at (datetime): A timestamp of when the analysis run was started.
        finished_at (Optional[datetime]): A timestamp of when the analysis run was finished, if applicable.
        parameters (dict[str, Any]): A dictionary of additional parameters for the analysis.
    """
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
    """
    Represents the data returned for an analysis result, including metadata about the result and its payload.
    
    Attributes
        analysis_result_id (UUID): Unique identifier for the analysis result.
        analysis_run_id (UUID): Unique identifier for the analysis run.
        result_type (str): The type of the analysis result (e.g. "descriptive_hormone_analysis").
        result_payload (dict[str, Any]): A dictionary containing the actual analysis results.
        created_at (datetime): A timestamp of when the analysis result was created.
    """
    analysis_result_id: UUID
    analysis_run_id: UUID
    result_type: str
    result_payload: dict[str, Any]
    created_at: datetime


# ANALYSIS REPORTS
class AnalysisReportResponse(BaseModel):
    """
    Represents the data returned for an analysis report, including metadata about the report and its content.
    
    Attributes
        analysis_report_id (UUID): Unique identifier for the analysis report.
        analysis_run_id (UUID): Unique identifier for the analysis run.
        report_text (str): The text of the analysis report.
        summary_text (Optional[str]): A summary of the analysis report, by default None.
        created_at (datetime): A timestamp of when the analysis report was created.
    """
    analysis_report_id: UUID
    analysis_run_id: UUID
    report_text: str
    summary_text: Optional[str] = None
    created_at: datetime


# REAL ANALYSIS
class RunDescriptiveHormoneAnalysisRequest(BaseModel):
    """
    Represents the data required to run a descriptive hormone analysis, including filters for hormone names, performance types, symptom names, and date range.
    
    Attributes
         project_id (UUID): Unique identifier for a project.
         include_hormone_names (Optional[list[str]]): An optional collection of hormone names to inclusively filter for in the analysis. By default, all hormone names will be included.
         include_performance_types (Optional[list[str]]): An optional collection of performance types to inclusively filter for in the analysis. By default, all performance types will be included.
         include_symptom_names (Optional[list[str]]): An optional collection of symptom names to inclusively filter for in the analysis. By default, all symptom names will be included.
         date_from (Optional[date]): The start date for the analysis period. By default, there is no start date filter and all data will be included.
         date_to (Optional[date]): The end date for the analysis period. By default, there is no end date filter and all data will be included.
         ai_assisted_report (bool): A flag indicating whether to generate an AI-assisted report for this analysis run. By default, this is set to False, meaning that no AI-assisted report will be generated unless explicitly requested.
         ai_analysis_report_request (Optional[GenerateAIAnalysisReportRequest]): An optional request object containing. By default, this is set to None and should only be included if `ai_assisted_report` is set to True.
    """
    project_id: UUID
    include_hormone_names: Optional[list[str]] = None
    include_performance_types: Optional[list[str]] = None
    include_symptom_names: Optional[list[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    ai_assisted_report: bool = False
    ai_analysis_report_request: Optional[GenerateAIAnalysisReportRequest] = None


class RunDescriptiveAnalysisResponse(BaseModel):
    """
    Represents the data returned after running a descriptive hormone analysis, including the analysis run metadata, results, and reports.
    
    Attributes
         analysis_run (AnalysisRunResponse): The metadata of the analysis run that was executed.
         analysis_result (Optional[AnalysisResultResponse]): The result of the analysis run, if available. By default, this is set to None and will only be included if the analysis run produced a result.
         analysis_report (Optional[AnalysisReportResponse]): The traditional analysis report generated from the analysis run, if available. By default, this is set to None and will only be included if a traditional report was generated.
         ai_analysis_report (Optional[GenerateAIAnalysisReportResponse]): The AI-assisted analysis report generated from the analysis run, if requested and available. By default, this is set to None and will only be included if `ai_assisted_report` was set to True in the request and an AI report was successfully generated.
         engine_result (dict[str, Any]): A dictionary containing the raw results produced by the analysis engine, which may include statistics, tables, and other data generated during the analysis process.
    """
    analysis_run: AnalysisRunResponse
    analysis_result: Optional[AnalysisResultResponse]
    analysis_report: Optional[AnalysisReportResponse]
    ai_analysis_report: Optional[GenerateAIAnalysisReportResponse] = None
    engine_result: dict[str, Any]
