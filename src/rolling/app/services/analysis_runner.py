from uuid import UUID
from typing import Optional
from datetime import date
from decimal import Decimal

from rolling.app.repositories.projects import analyst_can_access_project
from rolling.app.repositories.analysis_inputs import list_hormone_dysmenorrhea_performance_analysis_rows
from rolling.app.repositories.analyses import create_analysis_run, create_analysis_result, create_analysis_report
from rolling.analysis_engine.contracts import HormoneObservation, HormoneAnalysisInput
from rolling.analysis_engine.methods.descriptive_hormone_analysis import DescriptiveHormoneAnalysis
from rolling.analysis_engine.reports.traditional_reports import build_descriptive_hormone_report

def run_descriptive_hormone_analysis(project_id: UUID,
                                     analyst_id: UUID,
                                     include_hormone_names: Optional[list[str]]=None,
                                     include_performance_types: Optional[list[str]]=None,
                                     include_symptom_names: Optional[list[str]]=None,
                                     date_from: Optional[date]=None,
                                     date_to: Optional[date]=None,
                                     ) -> dict: # TODO change to Optional
    """
    Execute descriptive hormone analysis using the analysis engine. It is main function used in API routing to run an analysis.

    The main steps of execution are:
    1. Verifying that the given analyst can access the project.
    2. Fetching the input for the analysis from the database, filtering based on the given parameters.
    3. Converting the fetched analysis inputs into structured objects, namely a HormoneObservation
    4. Building input for the analysis engine.
    5. Instantiating the analysis engine.
    6. Run the analysis
    7. Persist the analysis run with the parameters.
    8. Persist the analysis result.
    9. Create and persist the traditional analysis report.

    Args:
        project_id (UUID): The ID of the project from which to get data.
        analyst_id (UUID): The ID of the analysis running the analysis.
        include_hormone_names (Optional[list[str]]): List of hormone names to include in the analysis run. By default, all hormones are considered.
        include_performance_types (Optional[list[str]]): List of performance types to include in the run. By default, all performance types are considered.
        include_symptom_names (Optional[list[str]])): List of menstrual symptoms to include in the run. By default, all menstrual symptoms are considers.
        date_from (Optional[date]): Used to filter for observations from this date inclusively. By default, all dates are considered.
        date_to (Optional[date]): Used to filter for observations until this date inclusively. By default, all dates are considered.

    Returns:
        Optional[dict]: The persisted records for the analysis run.
            - "analysis_run" (dict): The persisted analysis run record.
            - "analysis_result" (dict): The persisted analysis result record.
            - "analysis_report" (dict): The persisted analysis report record.
            - "engine_result" (dict): The analysis result payload.
    """
    # verify project access
    if not analyst_can_access_project(analyst_id, project_id):
        return None
    
    # fetch analysis input rows
    analysis_input_rows = list_hormone_dysmenorrhea_performance_analysis_rows(
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        include_hormone_names=include_hormone_names,
        include_performance_types=include_performance_types,
        include_symptom_names=include_symptom_names,
    ) 
    
    # call the engine
    #   convert raw rows into HormoneObservation (in contract)
    observations = build_hormone_observations(analysis_input_rows)

    #   build HormoneAnalysisInput (engine input payload)
    analysis_input = build_hormone_analysis_input(project_id=project_id,
                                                  hormone_observations=observations,
                                                  include_hormone_names=include_hormone_names,
                                                  include_performance_types=include_performance_types,
                                                  include_symptom_names=include_symptom_names,
                                                  date_from=date_from,
                                                  date_to=date_to)
   
    #   instantiate the analysis engine
    analysis = DescriptiveHormoneAnalysis()

    # persist the run
    result = analysis.run(payload=analysis_input)

    parameters = build_analysis_parameters(include_hormone_names=include_hormone_names,
                                           include_performance_types=include_performance_types,
                                           include_symptom_names=include_symptom_names,
                                           date_from=date_from,
                                           date_to=date_to,
                                           )
    analysis_run_record = create_analysis_run(project_id=project_id,
                                                created_by_analyst_id=analyst_id,
                                                analysis_kind=result.analysis_kind,
                                                execution_mode="traditional",
                                                status="completed",
                                                parameters=parameters)
    # TODO link dataset
    
    
    # persist the result
    result_type = result.analysis_kind
    result_payload = make_json_safe({"analysis_kind": result.analysis_kind,
                                     "engine_version": result.engine_version,
                                     "generated_at": result.generated_at.isoformat(),
                                     "summary": result.summary,
                                     "tables": result.tables,
                                     "metadata": result.metadata,
                                     "conclusions": result.conclusions})
    
    analysis_result_record = create_analysis_result(analysis_run_id=analysis_run_record["analysis_run_id"],
                                                    result_type=result_type,
                                                    result_payload=result_payload)

    # creates report
    report_payload = build_descriptive_hormone_report(result)
    analysis_report_record = create_analysis_report(analysis_run_id=analysis_run_record["analysis_run_id"],
                                                    report_text=report_payload["report_text"],
                                                    summary_text=report_payload["summary_text"])
    
    # return a combined structured dict
    return {"analysis_run": analysis_run_record,
            "analysis_result": analysis_result_record,
            "analysis_report": analysis_report_record,
            "engine_result": result_payload}

def build_hormone_observations(rows: list[dict]) -> list[HormoneObservation]:
    """
    Converts a list of data obtained from the database to structured objects.

    Args:
        rows (list[dict]): A list of dictionaries containing hormone observation data.

    Returns:
        list[HormoneObservation]: A list of structured objects containing hormone observation data. If rows is empty, an empty list is returned.
    """
    observations = []
    for row in rows:
        obs = HormoneObservation(athlete_id=row.get("athlete_id"),
                                 observed_on=row.get("observed_on"),
                                 hormone_name=row.get("hormone_name"),
                                 measured_value=row.get("measured_value"),
                                 measurement_unit=row.get("measurement_unit"),
                                 symptom_name=row.get("symptom_name"),
                                 symptom_severity=row.get("symptom_severity"),
                                 relative_day_to_cycle=row.get("relative_day_to_cycle"),
                                 performance_type=row.get("performance_type"),
                                 metric_name=row.get("metric_name"),
                                 metric_value=row.get("metric_value"),
                                 metric_unit=row.get("metric_unit"),
        )
        observations.append(obs)
    return observations

def build_hormone_analysis_input(project_id: UUID,
                                 hormone_observations: list[HormoneObservation],
                                 include_hormone_names, # TODO add types
                                 include_performance_types,
                                 include_symptom_names,
                                 date_from,
                                 date_to) -> HormoneAnalysisInput:
    """
    Constructs input for the hormone analysis.

    Args:
        project_id (UUID): The ID of the project from which to get data.
        hormone_observations (list[HormoneObservation]): A list of HormoneObservation objects.
        include_hormone_names (Optional[list[str]]): An optional collection of hormone names to inclusively filter for in `observations`.
        include_performance_types (Optional[list[str]]): An optional collection of hormone names to inclusively filter for in `observations`.
        include_symptom_names (Optional[list[str]]): An optional collection of symptom names to inclusively filter for in `observations`.
        date_from (Optional[date]): Used to filter for observations from this date inclusively.
        date_to (Optional[date]): Used to filter for observations until this date inclusively.

    Returns:
        HormoneAnalysisInput: The input for the hormone analysis.
    """
    analysis_input = HormoneAnalysisInput(project_id=project_id,
                                          observations=hormone_observations,
                                          include_hormone_names=include_hormone_names,
                                          include_performance_types=include_performance_types,
                                          include_symptom_names=include_symptom_names,
                                          date_from=date_from,
                                          date_to=date_to
    )
    return analysis_input

def build_analysis_parameters(include_hormone_names: Optional[list[str]]=None,
                              include_performance_types: Optional[list[str]]=None,
                              include_symptom_names: Optional[list[str]]=None,
                              date_from: Optional[date]=None,
                              date_to: Optional[date]=None) -> dict:
    """Puts the analysis parameters in the form of a dictionary."""
    return {"include_hormone_names": include_hormone_names,
            "include_performance_types": include_performance_types,
            "include_symptom_names": include_symptom_names,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None}

def make_json_safe(value): # TODO add return type
    """
    If applicable, converts value to safe types.

    For example:
        - If value is type Decimal, it converts it to a float.
        - If value is a collection type, it ensures that all values are safe types.
    """
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {key: make_json_safe(val) for key, val in value.items()}

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    return value
