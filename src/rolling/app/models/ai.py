from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AIAnalysisReportInput(BaseModel):
    """
    Represents input for an AI Analysis Report.
    
    This is created by the input builder for the AI service. It contains only whilelisted values for the AI model.
    
    Attributes
        summary (dict[str, Any]): A dictionary of containing the group labels, observation count, and statistics for grouped and compared observations.
        tables (list[dict[str, Any]): A list of tables, represented as a dictionary with a key-value pair for the name of the statistic group and another pair for the labels and statistical values.
        report_text (Optional[str]): An analysis report that was constructed traditionally, by default None.
        summary_test (Optional[str]): A summary of the traditionally generated analysis report, by default None.
        metadata (dict[str, Any]): A dictionary of metadata for the analysis run.
        
    """
    summary: dict[str, Any] = Field(default_factory=dict)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    report_text: Optional[str] = None
    summary_text: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTraceMetadata(BaseModel): # TODO rename
    """
    DEPRECATED: Represents metadata for an AI generated analysis report.
    
    Attributes
        status (Optional[str]): Describes whether the AI analysis report generation was completed.
        operation (Optional[str]): Describes what task was performed. Version 1 only supports `'ai_report_generation'`, by defa.
        notes (Optional[str]): Any notes following the AI analysis report generation, by default None.
    """
    status: str
    operation: str
    notes: Optional[str] = None


class AgentTraceCreate(BaseModel):
    """
    Represents input for creating an agent trace in the database.
    
    Attributes
        analysis_run_id (UUID): Unique identifier for the analysis run on which the trace if basing its operations.
        step_name (str): Describes what task is being performed. Version 1 only supports `'ai_report_generation'`.
        model_name (str): The AI model used perform the service.
        metadata (dict[str, Any]): A dictionary of metadata for the agent trace, including the status of task and what operation is being performed.
    """
    analysis_run_id: UUID
    step_name: str
    model_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTraceResponse(BaseModel):
    """
    Represents the database object of an agent trace.
    
    Attributes
        agent_trace_id (UUID): Unique identifier for the agent trace.
        analysis_run_id (UUID): Unique identifier for the analysis run on which the trace if basing its operations.
        step_name (str): Describes what task is being performed. Version 1 only supports `'ai_report_generation'`.
        model_name (str): The AI model used perform the service.
        metadata (dict[str, Any]): A dictionary of metadata for the agent trace, including the status of task and what operation is being performed.
        created_at (datetime): A timestamp of when the task was completed.
    """
    agent_trace_id: UUID
    analysis_run_id: UUID
    step_name: str
    model_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AIAnalysisReportCreate(BaseModel):
    """
    Represents input for creating an AI analysis report database object.
    
    Attributes
        analysis_run_id (UUID): Unique identifier for the analysis run on which the trace if basing its operations.
        agent_trace_id (UUID): Unique identifier for the agent trace.
        model_name (str): The AI model used perform the service.
        report_text (Optional[str]): An analysis report that was constructed traditionally, by default None.
        summary_test (Optional[str]): A summary of the traditionally generated analysis report, by default None.
        comparison_notes (Optional[str]): Notes on the differences between the traditional and AI-generated analysis reports, by default None. In Version 1, this is not implemented.
    """
    analysis_run_id: UUID
    agent_trace_id: UUID
    model_name: str
    report_text: str
    summary_text: Optional[str] = None
    comparison_notes: Optional[str] = None


class AIAnalysisReportResponse(BaseModel):
    """
    Represents the database object for an AI analysis report.
    
    Attributes
        ai_analysis_report_id (UUID): Unique identifier for the AI analysis report.
        agent_trace_id (UUID): Unique identifier for the agent trace.
        model_name (str): The AI model used perform the service.
        report_text (Optional[str]): An analysis report that was constructed traditionally, by default None.
        summary_test (Optional[str]): A summary of the traditionally generated analysis report, by default None.
        comparison_notes (Optional[str]): Notes on the differences between the traditional and AI-generated analysis reports, by default None. In Version 1, this is not implemented.

    """
    ai_analysis_report_id: UUID
    analysis_run_id: UUID
    agent_trace_id: UUID
    model_name: str
    report_text: str
    summary_text: Optional[str] = None
    comparison_notes: Optional[str] = None
    created_at: datetime


class GenerateAIAnalysisReportRequest(BaseModel):
    """
    Represents a request to generate an AI analysis report using a specific model.

    Attributes
        model_name (str): The name of the AI model that will provide the service.
    """
    model_name: str
    

class GenerateAIAnalysisReportResponse(BaseModel):
    """
    Represents the response after generating an AI analysis report, including the agent trace of the operation and the generated AI analysis report.
    
    Attributes
        agent_trace (AgentTraceResponse): The agent trace of the operation.
        ai_report (AIAnalysisReportResponse): The generated AI analysis report.
    """
    agent_trace: AgentTraceResponse
    ai_report: AIAnalysisReportResponse


class AIAnalysisReportRequest(BaseModel):
    """
    Represents a request to generate an AI analysis report for a specific analysis run.
    
    Attributes
        analysis_run_id (UUID): Unique identifier for the analysis run on which the AI report will be based.
    """
    ai_analysis_report_id: UUID


class AIPrompt(BaseModel):
    """
    Represents the prompt that will be sent to the AI model, including the system prompt, user prompt, and any tools that the model can use to complete the task.
    
    Attributes
        system_prompt (str): The system prompt for the AI model. This includes high-level standing instructions for the model.
        user_prompt (str): The user prompt for the AI model. This includes task-specific instructions and content for the model.
        tools (list[dict[str, Any]]): A list of tools that the AI model can use.
    """
    system_prompt: str
    user_prompt: str
    tools: list[dict[str, Any]] = Field(default_factory=list)


class AIModelOutput(BaseModel):
    """
    Represents the output from the AI model after generating an analysis report, including the model name, the generated report text, and a summary of the report.
    
    Attributes
        model_name (str): The name of the AI model that generated the output.
        report_text (str): The generated analysis report text.
        summary_text (Optional[str]): A summary of the generated analysis report, by default None.
    """
    model_name: str
    report_text: str
    summary_text: Optional[str] = None
