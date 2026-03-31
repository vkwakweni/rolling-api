from uuid import UUID
from typing import Optional
from datetime import date
from decimal import Decimal

from app.repositories.projects import analyst_can_access_project
from app.repositories.analysis_inputs import list_hormone_dysmenorrhea_performance_analysis_rows
from app.repositories.analyses import create_analysis_run, create_analysis_result, create_analysis_report
from analysis_engine.contracts import HormoneObservation, HormoneAnalysisInput
from analysis_engine.methods.descriptive_hormone_analysis import DescriptiveHormoneAnalysis
from analysis_engine.reports.traditional_reports import build_descriptive_hormone_report

def run_descriptive_hormone_analysis(project_id: UUID,
                                     analyst_id: UUID,
                                     include_hormone_names: Optional[list[str]]=None,
                                     include_performance_types: Optional[list[str]]=None,
                                     include_symptom_names: Optional[list[str]]=None,
                                     date_from: Optional[date]=None,
                                     date_to: Optional[date]=None,
                                     ) -> dict:
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
                                 include_hormone_names,
                                 include_performance_types,
                                 include_symptom_names,
                                 date_from,
                                 date_to) -> HormoneAnalysisInput:
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
    return {"include_hormone_names": include_hormone_names,
            "include_performance_types": include_performance_types,
            "include_symptom_names": include_symptom_names,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None}

def make_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {key: make_json_safe(val) for key, val in value.items()}

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    return value
