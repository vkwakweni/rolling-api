from datetime import date
from typing import Optional
from uuid import UUID

from rolling.app.db import get_connection

def list_hormone_dysmenorrhea_performance_analysis_rows(project_id: UUID,
                                                     date_from: Optional[date]=None,
                                                     date_to: Optional[date]=None,
                                                     include_hormone_names: Optional[list[str]]=None,
                                                     include_symptom_names: Optional[list[str]]=None,
                                                     include_performance_types: Optional[list[str]]=None,
                                                     include_cycle_phases: Optional[list[str]]=None
                                                     ) -> list[dict]:
    """
    Lists the observations used for analyses of hormone, dysmenorrhea, and performance.

    The parameters are used to filter the datasets for observations that satisfy them.

    Args:
        - project_id (UUID): The project ID from which to get the associated observations.
        - date_from (Optional[date]): Filter for observations from this data inclusively.
        - date_to (Optional[date]): Filter for observations to this data inclusively.
        - inlucde_hormone_names (Optional[list[str]]): An optional collection of hormone names to inclusively filter for. By default, all hormones are included.
        - include_symptom_names (Optional[list[str]]): An optional collection of menstrual symptom names to inclusively filter for. By default, all menstrual symptoms are included.
        - include_performance_types (Optional[list[str]]): An optional collection of performance types to inclusively filter for. By default, all performance types are included.

    Returns:
        list[dict]: A list of dictionaries which represent the observations used in the analysis.

        Each dictionary contains the following data:
            - "athlete_id" (UUID): The ID of the athlete.
            - "observed_on" (date): The day the observation was made.
            - "hormone_name" (str): The name of the hormone.
            - "measured_value" (float | int): The measured value of the hormone.
            - "measurement_unit" (str): The measurement unit of the hormone.
            - "symptom_name" (str): The name of the menstrual symptom.
            - "symptom_severity" (str): The severity of the menstrual symptom.
            - cycle_phase: (Optional[str]): The cycle phase the athlete was in.
            - performance_type (Optional[str]): The type of performance performed on the observed day, which represents the intensity of the performance.
            - metric_name (Optional[str]): A name of a performance metric (e.g. 'BPM' for heart rate)
            - metric_value (Optional[str]): The value of the performance metric.
            - metric_unit (Optional[str]): The unit of measurement for the performance metric.
    """
    query = """
            SELECT DISTINCT ON (
                                    hm.athlete_id,
                                    hm.observed_on,
                                    h.name,
                                    ms.name,
                                    pt.name,
                                    cpt.name
                                )
                hm.athlete_id AS athlete_id,
                hm.observed_on AS observed_on,
                h.name AS hormone_name,
                hm.measured_value AS measured_value,
                hm.unit AS measurement_unit,
                ms.name AS symptom_name,
                sr.symptom_severity AS symptom_severity,
                cpt.name as cycle_phase,
                sr.relative_day_to_cycle AS relative_day_to_cycle,
                pt.name AS performance_type,
                mt.name AS metric_name,
                pr.metric_value AS metric_value,
                pr.metric_unit as metric_unit
            FROM research.hormone_measurements hm
            LEFT JOIN research.hormones h
                ON hm.hormone_id = h.hormone_id
            LEFT JOIN research.symptom_records sr
                ON hm.athlete_id = sr.athlete_id
            AND hm.observed_on = sr.observed_on
            LEFT JOIN research.menstrual_symptoms ms
                ON sr.symptom_id = ms.menstrual_symptom_id
            LEFT JOIN research.performance_records pr
                ON hm.athlete_id = pr.athlete_id
            AND hm.observed_on = pr.observed_on
            LEFT JOIN research.cycle_phase_records cp
                ON hm.athlete_id = cp.athlete_id
            AND hm.observed_on = cp.observed_on
            LEFT JOIN research.performance_types pt
                ON pr.performance_type = pt.performance_type_id
            LEFT JOIN research.performance_metric_types mt
                ON pr.metric_type = mt.metric_type_id
            LEFT JOIN research.cycle_phase_types cpt
                ON cp.cycle_phase_type = cpt.cycle_phase_type_id
            JOIN projects.project_datasets pd
                ON hm.dataset_id = pd.dataset_id
            WHERE pd.project_id = %s
            """
    
    params = [str(project_id)]

    if date_from is not None:
        query += " AND hm.observed_on >= %s"
        params.append(date_from)

    if date_to is not None:
        query += " AND hm.observed_on <= %s"
        params.append(date_to)

    if include_hormone_names:
        query += " AND h.name = ANY(%s)"
        params.append(include_hormone_names)

    if include_symptom_names:
        query += " AND ms.name = ANY(%s)"
        params.append(include_symptom_names)

    if include_performance_types:
        query += " AND pt.name = ANY(%s)"
        params.append(include_performance_types)

    if include_cycle_phases:
        query += " AND cpt.name = ANY(%s)"
        params.append(include_cycle_phases)

    query += """
             ORDER BY hm.athlete_id, hm.observed_on, h.name, ms.name, pt.name, cpt.name;
             """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

def list_pain_performance_analysis_rows(project_id: UUID,
                                        date_from: Optional[date]=None,
                                        date_to: Optional[date]=None,
                                        metric_names: Optional[list[str]]=None,
                                        symptom_names: Optional[list[str]]=None,
                                        ) -> list[dict]:
    """TODO delete"""
    query = """
            SELECT sr.athlete_id,
                   sr.observed_on,
                   ms.name AS symptom_name,
                   sr.symptom_severity,
                   sr.relative_day_to_cycle,
                   pt.name AS performance_type,
                   mt.name AS metric_name,
                   pr.metric_unit,
                   pr.metric_value
            FROM research.symptom_records sr
            JOIN research.performance_records pr
                ON sr.athlete_id = pr.athlete_id
                AND sr.observed_on = pr.observed_on
            JOIN projects.project_datasets pd_symptom
                ON sr.dataset_id = pd_symptom.dataset_id
            JOIN projects.project_datasets pd_performance
                ON pr.dataset_id = pd_performance.dataset_id
            LEFT JOIN research.menstrual_symptoms ms
                ON sr.symptom_id = ms.menstrual_symptom_id
            LEFT JOIN research.performance_types pt
                ON pr.performance_type = pt.performance_type_id
            LEFT JOIN research.performance_metric_types mt
                ON pr.metric_type = mt.metric_type_id
            WHERE pd_symptom.project_id = %s
              AND pd_performance.project_id = %s
              """
    
    params = [str(project_id), str(project_id)]

    if date_from is not None:
        query += "  AND sr.observed_on >= %s"
        params.append(date_from)

    if date_to is not None:
        query += "  AND sr.observed_on <= %s"
        params.append(date_to)

    if metric_names:
        query += "  AND mt.name = ANY(%s)"
        params.append(metric_names)

    if symptom_names:
        query += "  AND ms.name = ANY(%s)"
        params.append(symptom_names)

    query += """
            ORDER BY sr.athlete_id, sr.observed_on, mt.name;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
