from datetime import date
from typing import Optional
from uuid import UUID

from app.db import get_connection

def create_symptom_record(athlete_id: UUID,
                          dataset_id: UUID,
                          symptom_id: int,
                          observed_on: date,
                          symptom_severity: Optional[str] = None,
                          notes: Optional[str] = None,
                          relative_day_to_cycle: Optional[int] = None) -> dict:
    query = """
            INSERT INTO research.symptom_records (
                athlete_id,
                dataset_id,
                symptom_id,
                observed_on,
                symptom_severity,
                notes,
                relative_day_to_cycle
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING symptom_record_id, athlete_id, dataset_id, symptom_id,
                        observed_on, symptom_severity, notes,
                        created_at, updated_at, relative_day_to_cycle;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id), str(dataset_id), symptom_id, observed_on,
                                symptom_severity, notes, relative_day_to_cycle))
            row = cur.fetchone()
            return dict(row)
        
def create_symptom_record_batch(rows: list[dict]) -> list[dict]:
    query = """
            INSERT INTO research.symptom_records (
                athlete_id,
                dataset_id,
                symptom_id,
                observed_on,
                symptom_severity,
                notes,
                relative_day_to_cycle
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING symptom_record_id, athlete_id, dataset_id, symptom_id,
                        observed_on, symptom_severity, notes,
                        created_at, updated_at, relative_day_to_cycle;
            """
    
    parameters = []
    for row in rows: # TODO rename this pattern
        parameter = (str(row.get("athlete_id")),
                     str(row.get("dataset_id")),
                     str(row.get("symptom_id")),
                     row.get("observed_on"),
                     row.get("symptom_severity"),
                     row.get("notes"),
                     row.get("relative_day_to_cycle"))
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

def get_symptom_record_by_id(symptom_record_id: UUID) -> Optional[dict]:
    query = """
            SELECT symptom_record_id, athlete_id, dataset_id, symptom_id,
                    observed_on, symptom_severity, notes,
                    created_at, updated_at, relative_day_to_cycle
            FROM research.symptom_records
            WHERE symptom_record_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(symptom_record_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def get_symptom_records_for_athlete(athlete_id: UUID) -> list[dict]:
    query = """
            SELECT symptom_record_id, athlete_id, dataset_id, symptom_id,
                    observed_on, symptom_severity, notes,
                    created_at, updated_at, relative_day_to_cycle
            FROM research.symptom_records
            WHERE athlete_id = %s
            ORDER BY observed_on DESC, created_at DESC;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

def get_symptom_by_name(name: str) -> Optional[dict]:
    query = """
            SELECT menstrual_symptom_id
            FROM research.menstrual_symptoms
            WHERE name = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
            return dict(row) if row else None
    