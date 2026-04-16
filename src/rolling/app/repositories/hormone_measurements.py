from typing import Optional
from uuid import UUID
from datetime import date

from rolling.app.db import get_connection

def create_hormone_measurement(athlete_id: UUID,
                               hormone_id: int,
                               dataset_id: UUID,
                               measured_value: float,
                               unit: Optional[str],
                               observed_on: date) -> dict:
    query = """
            INSERT INTO research.hormone_measurements (
                athlete_id,
                hormone_id,
                dataset_id,
                measured_value,
                unit,
                observed_on
                )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING hormone_measurement_id, athlete_id, hormone_id, dataset_id, measured_value,
                        unit, observed_on, created_at, updated_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id), str(hormone_id), str(dataset_id),
                                measured_value, unit, observed_on))
            row = cur.fetchone()
            return dict(row)

def create_hormone_measurement_batch(rows: list[dict]) -> list[dict]:
    query = """
            INSERT INTO research.hormone_measurements (
                athlete_id,
                hormone_id,
                dataset_id,
                measured_value,
                unit,
                observed_on
                )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING hormone_measurement_id, athlete_id, hormone_id, dataset_id, measured_value,
                        unit, observed_on, created_at, updated_at;
            """
    
    parameters = []
    for row in rows:
        parameter = (str(row.get("athlete_id")),
                     row.get("hormone_id"),
                     str(row.get("dataset_id")),
                     row.get("measured_value"),
                     row.get("unit"),
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

def get_hormone_measurement_by_id(hormone_measurement_id: UUID) -> Optional[dict]:
    query = """
            SELECT hormone_measurement_id, athlete_id, hormone_id, dataset_id,
                    measured_value, unit, observed_on, created_at, updated_at
            FROM research.hormone_measurements
            WHERE hormone_measurement_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(hormone_measurement_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def get_hormone_measurements_for_athlete(athlete_id: UUID) -> Optional[list[dict]]:
    query = """
            SELECT hormone_measurement_id, athlete_id, hormone_id, dataset_id,
                    measured_value, unit, observed_on, created_at, updated_at
            FROM research.hormone_measurements
            WHERE athlete_id = %s;
            """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def get_hormone_by_name(name: str) -> Optional[dict]:
    query = """
            SELECT hormone_id
            FROM research.hormones
            WHERE name = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
            return dict(row) if row else None
