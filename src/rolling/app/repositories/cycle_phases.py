from datetime import date
from typing import Optional
from uuid import UUID

from rolling.app.db import get_connection

def create_cycle_phase_record(athlete_id: UUID,
                              dataset_id: UUID,
                              observed_on: date,
                              cycle_phase_type: int,
                              cycle_day: Optional[int]) -> dict:
    """
    Creates a cycle phase record.

    This represents an observation what menstrual cycle phase an athlete was in on an observed date.

    Args:
        athlete_id (UUID): The athlete ID.
        dataset_id (UUID): The dataset ID.
        observed_on (date): The observed date.
        cycle_phase_type (int): The menstrual cycle phase type, e.g. "LUTEAL", "FOLLICULAR".
        cycle_day (Optional[int]): The menstrual cycle day.

    Returns:
        dict: The created cycle phase record.
            - "cycle_phase_record_id" (UUID): The ID of the cycle phase record.
            - "athlete_id" (UUID): The athlete ID.
            - "dataset_id" (UUID): The dataset ID.
            - "observed_on" (date): The observed date.
            - "cycle_phase_type" (int): The menstrual cycle phase type.
            - "cycle_day" (int): The menstrual cycle day.
            - "created_at" (datetime): A timestamp of when the cycle phase record was created.
            - "updated_at" (datetime): A timestamp of when the cycle phase record was updated.
    """
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
    """
    Create several cycle phase records.

    It takes a list of dictionaries containing data to create a new cycle phase record. If any error occurs, the transaction
    is rolled back and none of the cycle phase records are created.

    Args:
        rows (list[dict]): A list of dictionaries containing data to create a new cycle phase record.

    Returns:
        list[dict]: A list of dictionaries containing the data of the created cycle phase record.
    """
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
    """
    Get a cycle phase record by its ID.

    Args:
        cycle_phase_record_id (UUID): The ID of the cycle phase record.

    Returns:
        dict: The cycle phase record if it exists. None otherwise.
            - "cycle_phase_record_id" (UUID): The ID of the cycle phase record.
            - "athlete_id" (UUID): The athlete ID.
            - "dataset_id" (UUID): The dataset ID.
            - "observed_on" (date): The observed date.
            - "cycle_phase_type" (int): The menstrual cycle phase type.
            - "cycle_day" (int): The menstrual cycle day.
            - "created_at" (datetime): A timestamp of when the cycle phase record was created.
            - "updated_at" (datetime): A timestamp of when the cycle phase record was updated.
    """
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

def get_cycle_phase_record_for_athlete(athlete_id: UUID) -> Optional[dict]: # TODO rename and change return type
    """
    Lists the cycle phases associated with an athlete.

    Args:
        athlete_id (UUID): The athlete ID.

    Returns:
        list[dict]: A list cycle phase records associated with an athlete. Returns an empty list if no records are found.
    """
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
    """
    Gets the cycle phase type by its name.

    This is used for mapping the cycle phase type ID and name.

    Args:
        name (str): The name of the cycle phase type.

    Returns:
        Optional[dict]: The cycle phase type record, if it exists. None otherwise.
    """
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