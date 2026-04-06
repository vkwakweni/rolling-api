from datetime import date
from typing import Optional
from uuid import UUID

from app.db import get_connection

def create_athlete(external_code: str,
                   dataset_id: UUID,
                   birth_date: Optional[date] = None,
                   birth_year: Optional[int] = None,
                   age_at_observation: Optional[int] = None,
                   age_logged_at: Optional[date] = None,
                   notes: Optional[str] = None) -> dict:
    query = """
            INSERT INTO research.athletes (
                external_code,
                dataset_id,
                birth_date,
                birth_year,
                age_at_observation,
                age_logged_at,
                notes
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING athlete_id, external_code, dataset_id, birth_date, birth_year, age_at_observation,
                        age_logged_at, notes, created_at, updated_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (external_code, dataset_id, birth_date, birth_year, age_at_observation,
                                age_logged_at, notes))
            row = cur.fetchone()
            return dict(row)
        
def create_athlete_batch(rows: list[dict]) -> list[dict]:
    """
    TODO rename the parameter better
    TODO is there a way to better name the expected fields?
    """
    query = """
            INSERT INTO research.athletes (
                external_code,
                dataset_id,
                birth_date,
                birth_year,
                age_at_observation,
                age_logged_at,
                notes
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING athlete_id, external_code, dataset_id, birth_date, birth_year, age_at_observation,
                        age_logged_at, notes, created_at, updated_at;
            """
    
    parameters = []
    for row in rows:
        parameter = (row.get("external_code"),
                     row.get("dataset_id"),
                     row.get("birth_date"),
                     row.get("birth_year"),
                     row.get("age_at_observation"),
                     row.get("age_logged_at"),
                     row.get("notes"))
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

def get_athlete_by_id(athlete_id: UUID) -> Optional[dict]:
    query = """
            SELECT athlete_id, external_code, dataset_id, birth_date, birth_year,
                    age_at_observation, age_logged_at, notes,
                    created_at, updated_at
            FROM research.athletes
            WHERE athlete_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(athlete_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def get_athlete_by_external_code(external_code: str) -> Optional[dict]:
    query = """
            SELECT athlete_id, external_code, dataset_id, birth_date, birth_year,
                    age_at_observation, age_logged_at, notes,
                    created_at, updated_at
            FROM research.athletes
            WHERE external_code = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (external_code,))
            row = cur.fetchone()
            return dict(row) if row else None
