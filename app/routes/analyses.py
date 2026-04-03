from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai_client import create_ollama_client
from app.dependencies.auth import get_current_analyst_id
from app.models.analyses import (AnalysisRunCreate,
                                 AnalysisRunResponse,
                                 AnalysisResultResponse,
                                 AnalysisReportResponse,
                                 RunDescriptiveHormoneAnalysisRequest,
                                 RunDescriptiveAnalysisResponse)
from app.models.ai import GenerateAIReportRequest, GenerateAIReportResponse
from app.repositories.analyses import (create_analysis_run,
                                       analyst_can_access_analysis_run,
                                       analyst_can_access_analysis_result,
                                       get_analysis_run_by_id,
                                       get_analysis_runs_for_project,
                                       get_analysis_result_by_id,
                                       list_analysis_results_by_analysis_run,
                                       get_analysis_report_by_analysis_run)
from app.repositories.projects import analyst_can_access_project
from app.services.analysis_runner import run_descriptive_hormone_analysis
from app.services.ai.orchestrator import AIReportOrchestrator
from app.services.ai.provider import OllamaProvider

router = APIRouter(prefix="/analyses", tags=["analyses"])

@router.post("/descriptive-hormone/run", response_model=RunDescriptiveAnalysisResponse)
def execute_descriptive_hormone_analysis(payload: RunDescriptiveHormoneAnalysisRequest,
                                        current_analyst_id: UUID = Depends(get_current_analyst_id),
                                        ) -> RunDescriptiveAnalysisResponse:
    """
    TODO decide if runner should verify or if route should verify and handle exceptions from runner --- IGNORE ---
    For now, runner will return None if no access to project, and route will handle that
    """
    if not analyst_can_access_project(current_analyst_id, payload.project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this project")
    
    analysis = run_descriptive_hormone_analysis(project_id=payload.project_id,
                                                analyst_id=current_analyst_id,
                                                include_hormone_names=payload.include_hormone_names,
                                                include_performance_types=payload.include_performance_types,
                                                include_symptom_names=payload.include_symptom_names,
                                                date_from=payload.date_from,
                                                date_to=payload.date_to
                                                )
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No observations found for the specified filters, cannot run analysis")
    return RunDescriptiveAnalysisResponse(**analysis)


# ANALYSIS RUNS
@router.post("/run", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def create_analysis_run_route(payload: AnalysisRunCreate,
                              current_analyst_id: UUID = Depends(get_current_analyst_id)
                              ) -> AnalysisRunResponse:
    row = create_analysis_run(project_id=payload.project_id,
                              created_by_analyst_id=current_analyst_id,
                              analysis_kind=payload.analysis_kind,
                              execution_mode=payload.execution_mode,
                              status=payload.status,
                              parameters=payload.parameters
                              )
    return AnalysisRunResponse(**row)

@router.get("/run/{analysis_run_id}", response_model=AnalysisRunResponse)
def get_analysis_run_route(analysis_run_id: UUID,
                           current_analyst_id: UUID = Depends(get_current_analyst_id),
                           ) -> AnalysisRunResponse:
    if not analyst_can_access_analysis_run(analyst_id=current_analyst_id,
                                           analysis_run_id=analysis_run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to analysis runs in this project")
    
    row = get_analysis_run_by_id(analysis_run_id=analysis_run_id,
                                 analyst_id=current_analyst_id)

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Analysis run not found",)
    
    return AnalysisRunResponse(**row)

@router.get("/projects/{project_id}/runs", response_model=list[AnalysisRunResponse])
def list_analysis_runs_for_project_route(project_id: UUID,
                                         current_analyst_id: UUID = Depends(get_current_analyst_id),) -> list[AnalysisRunResponse]:
    rows = get_analysis_runs_for_project(project_id, current_analyst_id)
    if rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to analysis runs in this project")
    return [AnalysisRunResponse(**row) for row in rows]

# ANALYSIS RESULTS
@router.get("/results/{analysis_result_id}", response_model=AnalysisResultResponse)
def get_analysis_result_route(analysis_result_id: UUID,
                              current_analyst_id: UUID = Depends(get_current_analyst_id),
                              ) -> AnalysisResultResponse:
    
    if not analyst_can_access_analysis_result(analyst_id=current_analyst_id,
                                              analysis_result_id=analysis_result_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis result")
    
    row = get_analysis_result_by_id(analysis_result_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Analysis result not found")
    
    return AnalysisResultResponse(**row)

@router.get("/runs/{analysis_run_id}/results", response_model=list[AnalysisResultResponse])
def list_analysis_results_for_run_route(analysis_run_id: UUID,
                                        current_analyst_id: UUID = Depends(get_current_analyst_id),
                                        ) -> list[AnalysisResultResponse]:
    if not analyst_can_access_analysis_run(analyst_id=current_analyst_id,
                                           analysis_run_id=analysis_run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")

    rows = list_analysis_results_by_analysis_run(analysis_run_id=analysis_run_id)
    return [AnalysisResultResponse(**row) for row in rows]

@router.get("/runs/{analysis_run_id}/report", response_model=AnalysisReportResponse)
def get_analysis_report_for_run_route(analysis_run_id: UUID,
                                      current_analyst_id: UUID = Depends(get_current_analyst_id),
                                      ) -> AnalysisReportResponse:
    if not analyst_can_access_analysis_run(analyst_id=current_analyst_id,
                                           analysis_run_id=analysis_run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")
    
    row = get_analysis_report_by_analysis_run(analysis_run_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Analysis report not found")
    
    return AnalysisReportResponse(**row)

@router.post("/runs/{analysis_run_id}/ai-report", response_model=GenerateAIReportResponse)
def create_ai_analysis_report_route(analysis_run_id: UUID,
                                    payload: GenerateAIReportRequest,
                                    current_analyst_id: UUID = Depends(get_current_analyst_id),
                                    ) -> GenerateAIReportResponse:

    ollama_client = create_ollama_client()
    provider = OllamaProvider(ollama_client)

    orchestrator = AIReportOrchestrator(model_name=payload.model_name,
                                        provider=provider)

    try:
        response = orchestrator.generate_ai_report_for_analysis_run(analyst_id=current_analyst_id,
                                                                    analysis_run_id=analysis_run_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="AI report could not be generated")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")

    return response
