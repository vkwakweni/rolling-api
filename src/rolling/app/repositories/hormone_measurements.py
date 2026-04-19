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
    """
    Creates a hormone measurement record.

    The hormone measurement is taken from an uploaded dataset. A hormone measurement can be created if the hormone name
    is in the database.

    Args:
        athlete_id (UUID): The ID of the athlete.
        hormone_id (UUID): The ID of the hormone.
        dataset_id (UUID): The ID of the dataset from which the measurement was obtained.
        measured_value (float): The measured value of the hormone.
        unit (Optional[str]): The unit of measurement of the measured value.
        observed_on (date): The date when the measurement was observed.

    Returns:
        dict: A dictionary of the created hormone measurement record.
            - "hormone_measurement_id" (UUID): The ID of the created hormone measurement.
            - "athlete_id" (UUID): The ID of the athlete.
            - "hormone_id" (UUID): The ID of the hormone.
            - "dataset_id" (UUID): The ID of the dataset from which the measurement was obtained.
            - "measured_value" (float): The measured value of the hormone.
            - "unit" (Optional[str]): The unit of measurement of the measured value.
            - "observed_on" (date): The date when the measurement was observed.
            - "created_at" (datetime): The date when the measurement was created.
            - "updated_at" (datetime): The date when the measurement was last updated.
    """
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
    """
    Creates several hormone measurement records.

    Args:
        rows (list[dict]): A list of dictionaries containing data to create a new hormone measurement record.

    Return:
        list[dict]: A list of dictionaries of the created hormone measurement records.
    """
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
    """
    Gets the hormone measurement record by ID.

    Args:
        hormone_measurement_id (UUID): The hormone measurement ID.

    Returns:
        Optional[dict]: A dictionary of the hormone measurement record.
            - "hormone_measurement_id" (UUID): The ID of the created hormone measurement.
            - "athlete_id" (UUID): The ID of the athlete.
            - "hormone_id" (UUID): The ID of the hormone.
            - "dataset_id" (UUID): The ID of the dataset from which the measurement was obtained.
            - "measured_value" (float): The measured value of the hormone.
            - "unit" (Optional[str]): The unit of measurement of the measured value.
            - "observed_on" (date): The date when the measurement was observed.
            - "created_at" (datetime): The date when the measurement was created.
            - "updated_at" (datetime): The date when the measurement was last updated.
    """
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

def get_hormone_measurements_for_athlete(athlete_id: UUID) -> Optional[list[dict]]: # TODO change return type
    """
    Gets the hormone measurements for an athlete.

    Args:
        athlete_id (UUID): The athlete ID.

    Returns:
        list[dict]: A list of dictionaries of hormone measurement records. If hormone measurement records exist, an empty list is returned.
    """
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
    """
    Gets the hormone by name.

    This is used for mapping the hormone ID and name.

    Args:
        name (str): The hormone name.

    Returns:
        Optional[dict]: A dictionary of the hormone ID.
            - "hormone_id" (UUID): The hormone ID.
    """
    # TODO add name to returned dictionary
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
