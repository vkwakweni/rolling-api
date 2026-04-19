from datetime import datetime
from typing import Optional
from uuid import UUID

from rolling.app.db import get_connection

def create_dataset(uploaded_by_id: UUID,
                   original_file_name: str,
                   stored_relative_path: str,
                   content_hash: Optional[str] = None,
                   notes: Optional[str] = None) -> dict:
    """
    Create a dataset record.

    This records a successful dataset upload.

    Args:
        uploaded_by_id (UUID): The ID of the created dataset.
        original_file_name (str): The original file name of the created dataset.
        stored_relative_path (str): The stored file path of the created dataset.
        content_hash (str): The content hash of the created dataset. This is used to check for duplicate file uploads.
        notes (str): Any additional notes about the created dataset.

    Returns:
        dict: A dictionary of the created dataset.
            - "dataset_id" (UUID): The ID of the created dataset.
            - "uploaded_by_id" (UUID): The ID of the analyst who created the dataset.
            - "original_file_name" (str): The original file name of the created dataset.
            - "stored_relative_path" (str): The stored file path of the created dataset.
            - "content_hash" (str): The content hash of the created dataset.
            - "uploaded_at" (datetime): The date when the created dataset was uploaded.
            - "import_status" (str): The status of the created dataset (e.g. "successful")
            - "notes" (str): Any additional notes about the created dataset.
    """
    query = """
            INSERT INTO research.datasets (
                uploaded_by_id,
                original_file_name,
                stored_relative_path,
                content_hash,
                notes
                )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING dataset_id, uploaded_by_id, original_file_name,
                      stored_relative_path, content_hash, uploaded_at,
                      import_status, notes;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(uploaded_by_id), original_file_name, stored_relative_path,
                                content_hash, notes))
            row = cur.fetchone()
            return dict(row)

def get_dataset_by_id(dataset_id: UUID) -> Optional[dict]:
    """
    Get a dataset record by its ID.

    Args:
        dataset_id (UUID): The ID of the dataset.

    Returns:
        dict: A dictionary of the dataset record, if it exists. None otherwise.
            - "dataset_id" (UUID): The ID of the created dataset.
            - "uploaded_by_id" (UUID): The ID of the analyst who created the dataset.
            - "original_file_name" (str): The original file name of the created dataset.
            - "stored_relative_path" (str): The stored file path of the created dataset.
            - "content_hash" (str): The content hash of the created dataset.
            - "uploaded_at" (datetime): The date when the created dataset was uploaded.
            - "import_status" (str): The status of the created dataset (e.g. "successful")
            - "notes" (str): Any additional notes about the created dataset.
    """
    query = """
            SELECT dataset_id, uploaded_by_id, original_file_name,
                   stored_relative_path, content_hash, uploaded_at,
                   import_status, notes
            FROM research.datasets
            WHERE dataset_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(dataset_id),))
            row = cur.fetchone()
            return dict(row) if row else None

def list_datasets_for_analyst(uploaded_by_id: UUID) -> list[dict]:
    """
    List all datasets associated with a given analyst.

    Args:
        uploaded_by_id (UUID): The ID of the analyst who created the dataset.

    Returns:
        list[dict]: A list of dictionaries of dataset records. If there are no records, an empty list is returned.
    """
    query = """
            SELECT dataset_id, uploaded_by_id, original_file_name,
                   stored_relative_path, content_hash, uploaded_at,
                   import_status, notes
            FROM research.datasets
            WHERE uploaded_by_id = %s
            ORDER BY uploaded_at DESC;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(uploaded_by_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def list_datasets_for_project(project_id: UUID) -> list[dict]:
    raise NotImplementedError
