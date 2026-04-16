from pathlib import Path
from pprint import pprint
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from main import app
from app.services.analysis_runner import run_descriptive_hormone_analysis


FIXTURES_DIR = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "ingest_import_analyse"
    / "good_complete_bundle"
)
UPLOAD_FILE_NAMES = [
    "athletes.csv",
    "performances.csv",
    "hormones.csv",
    "symptoms.csv",
    "cycle_phases.csv",
]


def build_auth_headers(analyst_id: str) -> dict[str, str]:
    return {"X-Analyst-Id": analyst_id}


def create_analyst(client: TestClient) -> dict:
    suffix = uuid4().hex[:8]
    payload = {
        "username": f"verify_{suffix}",
        "email": f"verify_{suffix}@example.com",
        "password_hash": "local-dev-hash",
        "password_salt": "local-dev-salt",
    }
    response = client.post("/analysts", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def create_project(client: TestClient, analyst_id: str) -> dict:
    payload = {
        "name": f"verify-project-{uuid4().hex[:8]}",
        "description": "Verification project for ingest -> import -> analysis flow",
    }
    response = client.post(
        "/projects",
        json=payload,
        headers=build_auth_headers(analyst_id),
    )
    assert response.status_code == 201, response.text
    return response.json()


def upload_fixture_bundle(client: TestClient, analyst_id: str, project_id: str) -> dict:
    files = []
    for file_name in UPLOAD_FILE_NAMES:
        file_path = FIXTURES_DIR / file_name
        files.append(("files", (file_name, file_path.read_bytes(), "text/csv")))

    response = client.post(
        f"/datasets/upload?project_id={project_id}",
        files=files,
        headers=build_auth_headers(analyst_id),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["is_valid"] is True, body
    assert body["validation"]["is_valid"] is True, body
    assert len(body["datasets"]) == len(UPLOAD_FILE_NAMES), body
    return body


def run_analysis(project_id: str, analyst_id: str) -> dict:
    result = run_descriptive_hormone_analysis(
        project_id=UUID(project_id),
        analyst_id=UUID(analyst_id),
    )
    assert result["analysis_run"]["analysis_kind"] == "descriptive_hormone_analysis", result
    assert result["analysis_result"]["result_type"] == "descriptive_hormone_analysis", result
    # assert result["engine_result"]["summary"]["group_count"] > 0, result
    assert len(result["engine_result"]["tables"]) >= 1, result
    return result


def main() -> None:
    assert FIXTURES_DIR.exists(), f"Fixture directory not found: {FIXTURES_DIR}"

    with TestClient(app) as client:
        # create a fresh analyst
        analyst = create_analyst(client)
        analyst_id = analyst["analyst_id"]

        # create a fresh project
        project = create_project(client, analyst_id)
        project_id = project["project_id"]

        upload_result = upload_fixture_bundle(client, analyst_id, project_id)
        analysis_result = run_analysis(project_id, analyst_id)

    print("Verification succeeded.")
    print()
    print("Analyst:")
    pprint(analyst)
    print()
    print("Project:")
    pprint(project)
    print()
    print("Upload summary:")
    pprint(
        {
            "project_id": upload_result["project_id"],
            "dataset_count": len(upload_result["datasets"]),
            "uploaded_file_names": [row["original_file_name"] for row in upload_result["datasets"]],
        }
    )
    print()
    print("Analysis summary:")
    pprint(
        {
            "analysis_run_id": analysis_result["analysis_run"]["analysis_run_id"],
            "analysis_result_id": analysis_result["analysis_result"]["analysis_result_id"],
            "summary": analysis_result["engine_result"]["summary"],
            "table_names": [table["name"] for table in analysis_result["engine_result"]["tables"]],
        }
    )


if __name__ == "__main__":
    main()
