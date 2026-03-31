from datetime import date
from typing import Optional
from uuid import UUID

from app.db import get_connection

def create_performance(athlete_id: UUID,
                       dataset_id: UUID,
                       performance_type: UUID,
                       metric_type: int,
                       metric_value: float,
                       metric_unit: Optional[str],
                       observed_on: date) -> dict:
    query = """
            INSERT INTO research.performance_records (
                athlete_id,
                dataset_id,
                performance_type,
                metric_type,
                metric_value,
                metric_unit,
                observed_on
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING performance_record_id, athlete_id, dataset_id, performance_type,
                        metric_type, metric_value, metric_unit,
                        observed_on, created_at, updated_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id), str(dataset_id), str(performance_type), metric_type,
                                metric_value, metric_unit, observed_on))
            row = cur.fetchone()
            return dict(row)

def create_performance_batch(rows: list[dict]) -> list[dict]: # TODO rename to create_performance_record_batch
    query = """
            INSERT INTO research.performance_records (
                athlete_id,
                dataset_id,
                performance_type,
                metric_type,
                metric_value,
                metric_unit,
                observed_on
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING performance_record_id, athlete_id, dataset_id, performance_type,
                        metric_type, metric_value, metric_unit,
                        observed_on, created_at, updated_at;
            """
    
    parameters = []
    for row in rows:
        parameter = (str(row.get("athlete_id")),
                     str(row.get("dataset_id")),
                     str(row.get("performance_type")),
                     row.get("metric_type"),
                     row.get("metric_value"),
                     row.get("metric_unit"),
                     row.get("observed_on"))
        parameters.append(parameter)

    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                inserted_rows = []
                for parameter in parameters:
                    cur.execute(query, parameter)
                    inserted_row = cur.fetchone()
                    inserted_rows.append(inserted_row)
                conn.commit()
                return [dict(row) for row in inserted_rows]
        except Exception as e: # TODO get the specific error
            conn.rollback()
            raise e 


def get_performance_by_id(performance_record_id: UUID) -> Optional[dict]:
    query = """
            SELECT performance_record_id, athlete_id, dataset_id, performance_type,
                    metric_type, metric_value, metric_unit,
                    observed_on, created_at, updated_at
            FROM research.performance_records
            WHERE performance_record_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(performance_record_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def get_performances_for_athlete(athlete_id: UUID) -> Optional[list[dict]]:
    query = """
            SELECT performance_record_id, athlete_id, dataset_id, performance_type,
                    metric_type, metric_value, metric_unit,
                    observed_on, created_at, updated_at
            FROM research.performance_records
            WHERE athlete_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def get_performance_by_name(name: str) -> Optional[dict]:
    query = """
            SELECT performance_type_id
            FROM research.performance_types
            WHERE name = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
            return dict(row) if row else None

def get_metric_by_name(name: str) -> Optional[dict]:
    query = """
            SELECT metric_type_id
            FROM research.performance_metric_types
            WHERE name = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
            return dict(row) if row else None
     
