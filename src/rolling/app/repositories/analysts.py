from typing import Optional
from uuid import UUID

from rolling.app.db import get_connection

def create_analyst(username: str, email: str, password_hash: str,
                   password_salt: str) -> dict:
    """
    Create an analyst.

    Args:
        username (str): The username for the new analyst.
        email (EmailStr): The email address for the new analyst.
        password_hash (str): The hashed password for the new analyst.
        password_salt (str): The salt used for hashing the password.

    Returns:
        dict: A dictionary of the created analyst.
            - "analyst_id" (UUID): The ID of the created analyst.
            - "username" (str): The username for the created analyst.
            - "email" (str): The email address for the created analyst.
            - "created_at" (str): The date and time the created analyst was created.
            - "updated_at" (str): The date and time the created analyst was updated.
    """
    query = """
            INSERT INTO research.analysts (
                username,
                email,
                pswd_hash,
                pswd_salt
                )
            VALUES (%s, %s, %s, %s)
            RETURNING analyst_id, username, email, created_at, updated_at;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username, email, password_hash, password_salt))
            row = cur.fetchone()
            return dict(row)
        
def get_analyst_by_id(analyst_id: UUID) -> Optional[dict]:
    """
    Get an analyst by its ID.

    Args:
        analyst_id (UUID): The ID of the analyst to get.

    Returns:
        dict: A dictionary of the analyst, if it exists. None otherwise.
            - "analyst_id" (UUID): The ID of the analyst to get.
            - "username" (str): The username for the analyst.
            - "email" (str): The email address for the analyst.
            - "created_at" (str): The date and time the analyst was created.
            - "updated_at" (str): The date and time the analyst was updated.
    """
    query = """
            SELECT analyst_id, username, email, created_at, updated_at
            FROM research.analysts
            WHERE analyst_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analyst_id),))
            row = cur.fetchone()
            return dict(row) if row else None
        
def get_analyst_by_username(username: str) -> Optional[dict]:
    """
    Get an analyst by its username.

    Args:
        username (str): The username for the analyst to get.

    Returns:
        dict: A dictionary of the analyst, if it exists. None otherwise.
            - "analyst_id" (UUID): The ID of the analyst to get.
            - "username" (str): The username for the analyst.
            - "email" (str): The email address for the analyst.
            - "created_at" (str): The date and time the analyst was created.
            - "updated_at" (str): The date and time the analyst was updated.
    """
    query = """
            SELECT analyst_id, username, email, created_at, updated_at
            FROM research.analysts
            WHERE username = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            row = cur.fetchone()
            return dict(row) if row else None
