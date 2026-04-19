from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from rolling.app.exceptions import AIProviderModelError
from rolling.app.ai_client import create_ollama_client
from rolling.app.dependencies.auth import get_current_analyst_id
from rolling.app.models.analyses import (AnalysisRunCreate,
                                 AnalysisRunResponse,
                                 AnalysisResultResponse,
                                 AnalysisReportResponse,
                                 RunDescriptiveHormoneAnalysisRequest,
                                 RunDescriptiveAnalysisResponse)
from rolling.app.models.ai import (GenerateAIAnalysisReportRequest,
                           GenerateAIAnalysisReportResponse,
                           AIAnalysisReportResponse,
                           AIAnalysisReportRequest)
from rolling.app.repositories.analyses import (create_analysis_run,
                                       analyst_can_access_analysis_run,
                                       analyst_can_access_analysis_result,
                                       get_analysis_run_by_id,
                                       get_analysis_runs_for_project,
                                       get_analysis_result_by_id,
                                       list_analysis_results_by_analysis_run,
                                       get_analysis_report_by_analysis_run)
from rolling.app.repositories.projects import analyst_can_access_project
from rolling.app.repositories.ai import get_ai_analysis_report_by_id
from rolling.app.services.analysis_runner import run_descriptive_hormone_analysis
from rolling.app.services.ai.orchestrator import AIReportOrchestrator
from rolling.app.services.ai.provider import OllamaProvider

router = APIRouter(prefix="/analyses", tags=["analyses"])

@router.post("/descriptive-hormone/run", response_model=RunDescriptiveAnalysisResponse)
def execute_descriptive_hormone_analysis(payload: RunDescriptiveHormoneAnalysisRequest,
                                        current_analyst_id: UUID = Depends(get_current_analyst_id),
                                        ) -> RunDescriptiveAnalysisResponse:
    """
    Executes a descriptive hormone analysis and persists the results to the database.

    This endpoint receives a JSON payload for a descriptive hormone analysis request, validates if the current analyst
    can access the project. It returns an analysis response, which can optionally include an AI-generated analysis
    report. It persists the analysis run, results, report, and optionally, the AI analysis report.

    Args:
        payload (RunDescriptiveHormoneAnalysisRequest): The parameters for the descriptive hormone analysis.
        current_analyst_id (UUID): The current analyst ID running the analysis.

    Returns:
        RunDescriptiveAnalysisResponse: The result of the descriptive analysis, containing the project and analyst associated with the analysis run, as well as the parameters for the analysis. It is can optionally include an AI analysis report.

    Raises:
        HTTPException:
            - If the analyst cannot access the project (404 Not Found).
            - If the AI report could not be generated (404 Not Found).
            - If the analyst cannot access the analysis run (404 Not Found).
            - If the AI model in unavailable (502 Bad Gateway).
            - If the service cannot connect to the AI model (503 Service Unavailable).
            - If no observations remained after the filtering (404 Not Found).
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
                                                date_to=payload.date_to,
                                                )
    
    if payload.ai_assisted_report and payload.ai_analysis_report_request and analysis is not None:
        ollama_client = create_ollama_client()
        provider = OllamaProvider(ollama_client)
        try:
            orchestrator = AIReportOrchestrator(model_name=payload.ai_analysis_report_request.model_name,
                                                provider=provider)
            ai_analysis_report = orchestrator.generate_ai_report_for_analysis_run(analyst_id=current_analyst_id,
                                                                                  analysis_run_id=analysis["analysis_run"]["analysis_run_id"])
            analysis["ai_analysis_report"] = ai_analysis_report
        except ValueError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, # TODO change the exception type
                                detail="AI report could not be generated")
        except PermissionError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, # TODO Don't think this can happen here
                                detail="Not allowed access to this analysis run")
        except AIProviderModelError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail="Invalid or unavailable AI model for the configured provider")
        except ConnectionError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=str(e))

    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No observations found for the specified filters, cannot run analysis")
    return RunDescriptiveAnalysisResponse(**analysis)


# ANALYSIS RUNS
@router.post("/run", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def create_analysis_run_route(payload: AnalysisRunCreate,
                              current_analyst_id: UUID = Depends(get_current_analyst_id)
                              ) -> AnalysisRunResponse:
    """
    Creates a new analysis run and persists it to the database.

    This endpoint receives a JSON payload for creating an analysis run record, persists it to the database, and returns a
    structured analysis run response.

    Args:
        payload (AnalysisRunCreate): A Pydantic model with the data needed to create an analysis run record.
        current_analyst_id (UUID): The current analyst ID creating the analysis run.

    Returns:
        AnalysisRunResponse: The created analysis run record.
    """
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
    """
    Retrieve the details for an analysis run.

    This endpoint queries the database to find an analysis run by its ID. It first verifies if the current analyst can
    access the analysis run.

    Args:
        analysis_run_id (UUID): The analysis run ID to retrieve.
        current_analyst_id (UUID): The current analyst ID accessing the analysis run.

    Returns:
        AnalysisRunResponse: The analysis run record, if it exists.

    Raises:
        HTTPException:
            - If the analyst is not allowed to access the analysis run (404 Not Found).
            - If the analysis run does not exist (404 Not Found).
    """
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
                                         current_analyst_id: UUID = Depends(get_current_analyst_id),
                                         ) -> list[AnalysisRunResponse]:
    """
    Retrieves a list of analysis runs for a project.

    This endpoint queries the database to find the analysis runs for a project. It first verifies if the current analyst
    can access the project.

    Args:
        project_id (UUID): The project ID to list the analysis runs for.
        current_analyst_id (UUID): The current analyst ID accessing analysis runs for the project.

    Returns:
        list[AnalysisRunResponse]: The list of analysis runs for the project.

    Raises:
        HTTPException: If the analysis is not allowed to access the project (404 Not Found).
    """
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
    """
    Retrieve the details for an analysis result.

    This endpoint queries the database to find an analysis result by its ID. It first verifies if the current analyst can
    access the analysis result.

    Args:
        analysis_result_id (UUID): The analysis result ID to retrieve.
        current_analyst_id (UUID): The current analyst ID accessing the analysis run.

    Returns:
        AnalysisResultResponse: The analysis run record, if it exists.

    Raises:
        HTTPException:
            - If the analyst is not allowed to access the analysis result (404 Not Found).
            - If the analysis result does not exist (404 Not Found).
    """
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
    """
    Retrieves a list of analysis results for an analysis run.

    This endpoint queries the database to find the analysis results for an analysis run. It first verifies if the
    current analyst can access the analysis run.

    Args:
        analysis_run_id (UUID): The project ID to list the analysis runs for.
        current_analyst_id (UUID): The current analyst ID accessing analysis runs for the project.

    Returns:
        list[AnalysisResultResponse]: The list of analysis results for the analysis run.

    Raises:
        HTTPException: If the analysis is not allowed to access the project (404 Not Found).
    """
    if not analyst_can_access_analysis_run(analyst_id=current_analyst_id,
                                           analysis_run_id=analysis_run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")

    rows = list_analysis_results_by_analysis_run(analysis_run_id=analysis_run_id)
    return [AnalysisResultResponse(**row) for row in rows]

# ANALYSIS REPORTS
@router.get("/runs/{analysis_run_id}/report", response_model=AnalysisReportResponse)
def get_analysis_report_for_run_route(analysis_run_id: UUID,
                                      current_analyst_id: UUID = Depends(get_current_analyst_id),
                                      ) -> AnalysisReportResponse:
    """
    Retrieves an analysis report for an analysis run.

    This endpoint queries the database to find the analysis report associated with an analysis run. It first verifies if
    the current analyst can access the analysis run. It first verifies if the current analyst can access the analysis run.

    Args:
        analysis_run_id (UUID): The project ID to list the analysis runs for.
        current_analyst_id (UUID): The current analyst ID accessing analysis runs for the project.

    Returns:
        AnalysisReportResponse: The analysis report record, if it exists.

    Raises:
        HTTPException
            - If the analyst is not allowed to access the analysis run (404 Not Found).
            - If the analysis report record is not found (404 Not Found).
    """
    if not analyst_can_access_analysis_run(analyst_id=current_analyst_id,
                                           analysis_run_id=analysis_run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")
    
    row = get_analysis_report_by_analysis_run(analysis_run_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Analysis report not found")
    
    return AnalysisReportResponse(**row)

@router.post("/runs/{analysis_run_id}/ai-report", response_model=GenerateAIAnalysisReportResponse)
def create_ai_analysis_report_route(analysis_run_id: UUID,
                                    payload: GenerateAIAnalysisReportRequest,
                                    current_analyst_id: UUID = Depends(get_current_analyst_id),
                                    ) -> GenerateAIAnalysisReportResponse:
    """
    Creates an AI analysis report for an exists analysis run, and persists it to the database.

    This endpoint receives an existing analysis run, a JSON payload for an AI analysis report request, persists it to
    the database, and returns a structured analysis run response. It verifies that the current analyst can access
    the analysis run.

    Args:
        analysis_run_id (UUID): The ID of an existing analysis run record.
        payload (AnalysisRunCreate): A Pydantic model with the data needed to create an analysis run record.
        current_analyst_id (UUID): The current analyst ID creating the analysis run.

    Returns:
        GenerateAIAnalysisReportResponse: The created AI analysis report record.

    Raises:
        HTTPException:
            - If the AI report could not be generated (404 Not Found).
            - If the analyst cannot access the analysis run (404 Not Found).
            - If the AI model in unavailable (502 Bad Gateway).
            - If the service cannot connect to the AI model (503 Service Unavailable).
    """
    ollama_client = create_ollama_client()
    provider = OllamaProvider(ollama_client)

    try:
        orchestrator = AIReportOrchestrator(model_name=payload.model_name,
                                            provider=provider)
        response = orchestrator.generate_ai_report_for_analysis_run(analyst_id=current_analyst_id,
                                                                    analysis_run_id=analysis_run_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="AI report could not be generated")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")
    except AIProviderModelError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Invalid or unavailable AI model for the configured provider")
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=str(e))

    return response

@router.get("/runs/{analysis_run_id}/ai-report", response_model=AIAnalysisReportResponse)
def get_ai_analysis_report_route(analysis_run_id: UUID,
                                 payload: AIAnalysisReportRequest,
                                 current_analyst_id: UUID = Depends(get_current_analyst_id),
                                ) -> AIAnalysisReportResponse:
    """
    Retrieve the details for an AI analysis result.

    This endpoint queries the database to find an AI analysis result by its ID. It first verifies if the current analyst
    can access the analysis run.

    Args:
        analysis_run_id (UUID): The analysis run ID to retrieve.
        payload (AIAnalysisReportRequest): A Pydantic model with the data needed to retrieve an analysis run record.
        current_analyst_id (UUID): The current analyst ID accessing the analysis run.

    Returns:
        AIAnalysisReportResponse: The AI analysis report record, if it exists.

    Raises:
        HTTPException:
            - If the analyst is not allowed to access the analysis result (404 Not Found).
            - If the analysis result does not exist (404 Not Found).
    """
    if not analyst_can_access_analysis_run(analyst_id=current_analyst_id,
                                           analysis_run_id=analysis_run_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this analysis run")
    
    row = get_ai_analysis_report_by_id(analyst_id=current_analyst_id,
                                       ai_analysis_report_id=payload.ai_analysis_report_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not allowed access to this AI analysis report") # TODO change the error to non-existence

    return AIAnalysisReportResponse(**row)
