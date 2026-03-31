from datetime import datetime
from typing import Optional
from uuid import UUID

from app.db import get_connection

def create_dataset(uploaded_by_id: UUID,
                   original_file_name: str,
                   stored_relative_path: str,
                   content_hash: Optional[str] = None,
                   notes: Optional[str] = None) -> dict:
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
