from datetime import date
from typing import Optional
from uuid import UUID

from app.db import get_connection

def create_cycle_phase_record(athlete_id: UUID,
                              dataset_id: UUID,
                              observed_on: date,
                              cycle_phase_type: int,
                              cycle_day: Optional[int]) -> dict:
    query = """
            INSERT INTO research.cycle_phase_records (
                athlete_id,
                dataset_id,
                observed_on,
                cycle_phase_type,
                cycle_day
                )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING cycle_phase_record_id, athlete_id, dataset_id, observed_on,
                        cycle_phase_type, cycle_day, created_at, updated_at;
            """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id), str(dataset_id), observed_on, cycle_phase_type, cycle_day))
            row = cur.fetchone()
            return dict(row)

def create_cycle_phase_record_batch(rows: list[dict]) -> list[dict]:
    query = """
            INSERT INTO research.cycle_phase_records (
                athlete_id,
                dataset_id,
                observed_on,
                cycle_phase_type,
                cycle_day
                )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING cycle_phase_record_id, athlete_id, dataset_id, observed_on,
                        cycle_phase_type, cycle_day, created_at, updated_at;
            """
    
    parameters = []
    for row in rows:
        parameter = (str(row.get("athlete_id")),
                     str(row.get("dataset_id")),
                     row.get("observed_on"),
                     row.get("cycle_phase_type"),
                     row.get("cycle_day"))
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

def get_cycle_phase_record_by_id(cycle_phase_record_id: UUID) -> Optional[dict]:
    query = """
            SELECT cycle_phase_record_id, athlete_id, dataset_id, observed_on,
                    cycle_phase_type, cycle_day, created_at, updated_at
            FROM research.cycle_phase_records
            WHERE cycle_phase_record_id = %s
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(cycle_phase_record_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def get_cycle_phase_record_for_athlete(athlete_id: UUID) -> Optional[dict]:
    query = """
            SELECT cycle_phase_record_id, athlete_id, dataset_id, observed_on,
                    cycle_phase_type, cycle_day, created_at, updated_at
            FROM research.cycle_phase_records
            WHERE athlete_id = %s
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

def get_cycle_phase_type_by_name(name: str) -> Optional[dict]:
    query = """
            SELECT cycle_phase_type_id, name
            FROM research.cycle_phase_types
            WHERE name = %s;
            """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
            return dict(row) if row else None