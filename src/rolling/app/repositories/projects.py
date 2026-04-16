from typing import Optional
from uuid import UUID

from rolling.app.db import get_connection

def create_project(owner_analyst_id: UUID, name: str,
                   description: Optional[str] = None) -> dict:
    query = """
            INSERT INTO projects.projects (
                owner_analyst_id,
                name,
                description
                )
            VALUES (%s, %s, %s)
            RETURNING project_id, owner_analyst_id, name, description, created_at, updated_at;"""
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(owner_analyst_id), name, description))
            row = cur.fetchone()
            return dict(row)
        
def get_project_by_id(project_id: UUID) -> Optional[dict]:
    query = """
            SELECT project_id, owner_analyst_id, name, description, created_at, updated_at
            FROM projects.projects
            WHERE project_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id),))
            row = cur.fetchone()
            return dict(row) if row else None
        
def get_project_by_name(name: str, owner_analyst_id: UUID) -> Optional[dict]:
    query = """
            SELECT project_id, owner_analyst_id, name, description, created_at, updated_at
            FROM projects.projects
            WHERE name = %s
              AND owner_analyst_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name, str(owner_analyst_id)))
            row = cur.fetchone()
            return dict(row) if row else None

def list_projects_for_analyst(analyst_id: UUID) -> list[dict]:
    query = """
            SELECT pa.project_id, p.owner_analyst_id, p.name, p.description, p.created_at, p.updated_at
            FROM projects.project_analysts pa
            INNER JOIN projects.projects p ON pa.project_id = p.project_id
            WHERE pa.analyst_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(analyst_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    
def analyst_can_access_project(analyst_id: UUID, project_id: UUID) -> bool:
    query = """
            SELECT 1
            FROM projects.projects p
            WHERE project_id = %s
              AND (
                  p.owner_analyst_id = %s
                  OR EXISTS (
                      SELECT 1
                      FROM projects.project_analysts pa
                      WHERE pa.project_id = p.project_id
                        AND pa.analyst_id = %s
                        )
                    );
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id), str(analyst_id), str(analyst_id)))
            row = cur.fetchone()
            return row is not None
        
def analyst_can_share_project(analyst_id: UUID, project_id: UUID) -> bool:
    query = """
            SELECT 1
            FROM projects.projects
            WHERE project_id = %s
              AND owner_analyst_id = %s;
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id), str(analyst_id),))
            row = cur.fetchone()
            return row is not None
        
def share_project_with_analyst(project_id: UUID, analyst_id: UUID) -> Optional[dict]:
    query = """
            INSERT INTO projects.project_analysts(project_id, analyst_id)
            VALUES (%s, %s)
            ON CONFLICT (project_id, analyst_id) DO NOTHING
            RETURNING analyst_id,
                      (SELECT username FROM research.analysts ra WHERE ra.analyst_id = %s) AS username,
                      (SELECT email FROM research.analysts ra WHERE ra.analyst_id = %s) AS email,
                      created_at;
            """ # if already in there, it won't insert and won't return anything
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id), str(analyst_id), str(analyst_id), str(analyst_id)))
            row = cur.fetchone() # returns nothing if already in there
            return dict(row) if row else None
        
def list_project_members(project_id: UUID) -> list[dict]:
    query = """
            SELECT pa.analyst_id, ra.username, ra.email, pa.created_at
            FROM projects.project_analysts pa
            LEFT JOIN research.analysts ra ON pa.analyst_id = ra.analyst_id
            WHERE project_id = %s;
            """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id),))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def link_dataset_to_project(project_id: UUID, dataset_id: UUID) -> dict:
    query = """
        INSERT INTO projects.project_datasets (project_id, dataset_id)
        VALUES (%s, %s)
        RETURNING project_id, dataset_id, created_at;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(project_id), str(dataset_id)))
            row = cur.fetchone()
            return dict(row)
