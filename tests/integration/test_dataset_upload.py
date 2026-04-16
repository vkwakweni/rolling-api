# tests/integration/test_dataset_upload.py
# TODO fix formating
from pathlib import Path

from tests.integration.base import BaseIntegrationTestCase


class TestDatasetUpload(BaseIntegrationTestCase):
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    def test_upload_valid_csv_files(self):
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]
        project = self.create_project(analyst_id)
        project_id = project["project_id"]

        GOOD_BUNDLE_DIR = self.FIXTURES_DIR / "ingest_import_analyse" / "good_complete_bundle"

        files = [
            ("files", ("athletes.csv", (GOOD_BUNDLE_DIR / "athletes.csv").read_bytes(), "text/csv")),
            ("files", ("performances.csv", (GOOD_BUNDLE_DIR / "performances.csv").read_bytes(), "text/csv")),
            ("files", ("hormones.csv", (GOOD_BUNDLE_DIR / "hormones.csv").read_bytes(), "text/csv")),
            ("files", ("symptoms.csv", (GOOD_BUNDLE_DIR / "symptoms.csv").read_bytes(), "text/csv")),
            ("files", ("cycle_phases.csv", (GOOD_BUNDLE_DIR / "cycle_phases.csv").read_bytes(), "text/csv")),
        ]

        response = self.client.post(
            f"/datasets/upload?project_id={project_id}",
            files=files,
            headers=self.get_auth_headers(analyst_id),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(body["project_id"], project_id)
        self.assertTrue(body["is_valid"])
        self.assertTrue(body["validation"]["is_valid"])
        self.assertEqual(len(body["validation"]["files"]), 5)
        self.assertEqual(len(body["datasets"]), 5)

    def test_upload_invalid_csv_file_returns_validation_errors(self):
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]
        project = self.create_project(analyst_id)
        project_id = project["project_id"]
        GOOD_BUNDLE_DIR = self.FIXTURES_DIR / "ingest_import_analyse" / "good_complete_bundle"

        files = [
            ("files", ("athletes.csv", (GOOD_BUNDLE_DIR / "athletes.csv").read_bytes(), "text/csv")),
            ("files", ("hormones.csv", (self.FIXTURES_DIR / "ingest_import_analyse" / "bad_invalid_hormone_measurement" / "hormones.csv").read_bytes(), "text/csv")),
        ]

        response = self.client.post(
            f"/datasets/upload?project_id={project_id}",
            files=files,
            headers=self.get_auth_headers(analyst_id),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertFalse(body["is_valid"])
        self.assertFalse(body["validation"]["is_valid"])
        self.assertEqual(body["datasets"], [])

        invalid_files = [f for f in body["validation"]["files"] if not f["is_valid"]]
        self.assertGreaterEqual(len(invalid_files), 1)
        self.assertGreaterEqual(len(invalid_files[0]["errors"]), 1)

    def test_upload_valid_csv_files_persists_to_db(self):
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]
        project = self.create_project(analyst_id)
        project_id = project["project_id"]
        GOOD_BUNDLE_DIR = self.FIXTURES_DIR / "ingest_import_analyse" / "good_complete_bundle"

        files = [("files", ("athletes.csv", (GOOD_BUNDLE_DIR /  "athletes.csv").read_bytes(), "text/csv")),
                 ("files", ("performances.csv", (GOOD_BUNDLE_DIR / "performances.csv").read_bytes(), "text/csv")),
                 ("files", ("hormones.csv", (GOOD_BUNDLE_DIR / "hormones.csv").read_bytes(), "text/csv")),
                 ]

        response = self.client.post(f"/datasets/upload?project_id={project_id}",
                                    files=files,
                                    headers=self.get_auth_headers(analyst_id))
        
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["is_valid"])

        db_rows = self.fetch_datasets_for_analyst(analyst_id)

        uploaded_names = {row["original_file_name"] for row in db_rows}
        self.assertIn("athletes.csv", uploaded_names)
        self.assertIn("performances.csv", uploaded_names)
        self.assertIn("hormones.csv", uploaded_names)

        for row in db_rows:
            if row["original_file_name"] in {"athletes.csv", "performances.csv", "hormones.csv"}:
                self.assertEqual(row["uploaded_by_id"], analyst_id)
                self.assertTrue(row["stored_relative_path"])
                self.assertIsNotNone(row["content_hash"])
                
                saved_file_path = self.PROJECT_ROOT / row["stored_relative_path"]
                self.assertTrue(saved_file_path.exists())

    def test_upload_invalid_csv_file_does_not_persist(self):
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]
        project = self.create_project(analyst_id)
        project_id = project["project_id"]

        files = [("files", ("hormones.csv", (self.FIXTURES_DIR / "ingest_import_analyse" / "bad_invalid_hormone_measurement" / "hormones.csv").read_bytes(), "text/csv")),]

        response = self.client.post(f"/datasets/upload?project_id={project_id}",
                                    files=files,
                                    headers=self.get_auth_headers(analyst_id))
        body = response.json()
        self.assertFalse(body["is_valid"])

        db_rows = self.fetch_datasets_for_analyst(analyst_id)
        self.assertEqual(len(db_rows), 0) # this relies on a unique analyst per test

    def test_shared_analyst_can_upload_to_shared_project(self):
        owner = self.create_analyst()
        owner_id = owner["analyst_id"]

        shared_analyst = self.create_analyst()
        shared_analyst_id = shared_analyst["analyst_id"]

        project = self.create_project(owner_id)
        project_id = project["project_id"]
        GOOD_BUNDLE_DIR = self.FIXTURES_DIR / "ingest_import_analyse" / "good_complete_bundle"

        share_response = self.client.post(
            f"/projects/{project_id}/share",
            json=[{"analyst_id": shared_analyst_id}],
            headers=self.get_auth_headers(owner_id),
        )
        self.assertEqual(share_response.status_code, 200)

        files = [
            ("files", ("athletes.csv", (GOOD_BUNDLE_DIR / "athletes.csv").read_bytes(), "text/csv")),
            ("files", ("performances.csv", (GOOD_BUNDLE_DIR / "performances.csv").read_bytes(), "text/csv")),
            ("files", ("hormones.csv", (GOOD_BUNDLE_DIR / "hormones.csv").read_bytes(), "text/csv")),
            ("files", ("symptoms.csv", (GOOD_BUNDLE_DIR / "symptoms.csv").read_bytes(), "text/csv")),
            ("files", ("cycle_phases.csv", (GOOD_BUNDLE_DIR / "cycle_phases.csv").read_bytes(), "text/csv")),
        ]

        response = self.client.post(
            f"/datasets/upload?project_id={project_id}",
            files=files,
            headers=self.get_auth_headers(shared_analyst_id),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertTrue(body["is_valid"])
        self.assertTrue(body["validation"]["is_valid"])
        self.assertEqual(len(body["datasets"]), 5)

        db_rows = self.fetch_datasets_for_analyst(shared_analyst_id)
        uploaded_names = {row["original_file_name"] for row in db_rows}

        self.assertIn("athletes.csv", uploaded_names)
        self.assertIn("performances.csv", uploaded_names)
        self.assertIn("hormones.csv", uploaded_names)
        self.assertIn("symptoms.csv", uploaded_names)
        self.assertIn("cycle_phases.csv", uploaded_names)
