# shared set up for integration test
# test client
# test analyst/project creation helpers
# optional test DB setup helpers
from unittest import TestCase
from fastapi.testclient import TestClient
from uuid import uuid4
from pathlib import Path

from app.main import app
from app.db import get_connection


class BaseIntegrationTestCase(TestCase):
    FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def make_unique_analyst_payload(self) -> dict:
        suffix = uuid4().hex[:8]
        return {"username": f"analyst_{suffix}",
                "email": f"analyst_{suffix}@example.com",
                "password_hash": f"dummy_hash_{suffix}",
                "password_salt": f"dummy_salt_{suffix}"}

    def create_analyst(self) -> dict:
        payload = self.make_unique_analyst_payload()
        response = self.client.post("/analysts", json=payload)
        self.assertEqual(response.status_code, 201)
        return response.json()
    
    def get_auth_headers(self, analyst_id: str) -> dict[str, str]:
        return {"X-Analyst-Id": analyst_id}
    
    def create_project(self, analyst_id: str) -> dict:
        response = self.client.post("/projects",
                                    json={"name": "Integration Test Project",
                                          "description": "Project for integration tests",},
                                    headers=self.get_auth_headers(analyst_id))
        self.assertEqual(response.status_code, 201)
        return response.json()
    
    def fetch_datasets_for_analyst(self, analyst_id: str) -> list[dict]:
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
                cur.execute(query, (analyst_id,))
                rows = cur.fetchall()
                return [dict(row) for row in rows]