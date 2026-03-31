from typing import Optional
from uuid import UUID

from app.db import get_connection

def create_analyst(username: str, email: str, password_hash: str,
                   password_salt: str) -> dict:
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
