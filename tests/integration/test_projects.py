# project access/share behaviour tests
from fastapi.testclient import TestClient
from tests.integration.base import BaseIntegrationTestCase

class TestProjects(BaseIntegrationTestCase):

    def test_create_project(self) -> None:
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]

        response = self.client.post("/projects",
                                    json={"name": "Project A",
                                          "description": "Testing create project",},
                                    headers=self.get_auth_headers(analyst_id))

        self.assertEqual(response.status_code, 201)
        body = response.json()

        self.assertEqual(body.get("name"), "Project A",
                         "Project names do not match")
        self.assertEqual(body.get("description"), "Testing create project",
                         "Projection descriptions do not match")
        self.assertEqual(body.get("owner_analyst_id"), analyst_id,
                         "Owner analyst '{}' does not match payload analyst '{}'".format(body.get("owner_analyst_id"), analyst_id))
        self.assertIn("project_id", body,
                      "Project ID not returned")
        self.assertIn("created_at", body,
                      "Project creation time not updated")
        self.assertIn("updated_at", body,
                      "Project update not returned")

    def test_list_projects_for_current_analyst(self) -> None:
        analyst = self.create_analyst()
        analyst_id = analyst.get("analyst_id")

        created_project = self.create_project(analyst_id)

        response = self.client.get("/projects",
                                   headers=self.get_auth_headers(analyst_id))

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertIsInstance(body, list,
                              "Did not return a list of JSONs of projects")
        self.assertGreaterEqual(len(body), 1,
                                "Returned list length is not greater than one")
        self.assertTrue(any(project.get("project_id") == created_project.get("project_id") for project in body),
                        "Project in response body and the original payload do not match")

    def test_get_project_by_id(self) -> None:
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]

        created_project = self.create_project(analyst_id)
        project_id = created_project["project_id"]

        response = self.client.get(f"/projects/{project_id}",
                                   headers=self.get_auth_headers(analyst_id))

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(body["project_id"], project_id,
                         "Project IDs do not match")
        self.assertEqual(body.get("owner_analyst_id"), analyst_id,
                         "Owner analyst ID of response and session analyst do not match")
        self.assertEqual(body["name"], created_project["name"],
                         "Response project name and original payload project name do not match")

    def test_cannot_get_another_analysts_project(self) -> None:
        analyst_a = self.create_analyst()
        analyst_b_payload = self.make_unique_analyst_payload()

        analyst_a_id = analyst_a["analyst_id"]

        project = self.create_project(analyst_a_id)
        project_id = project["project_id"]

        analyst_b_response = self.client.post("/analysts",
                                              json=analyst_b_payload)
        self.assertEqual(analyst_b_response.status_code, 201)
        analyst_b = analyst_b_response.json()
        analyst_b_id = analyst_b["analyst_id"]

        response = self.client.get(f"/projects/{project_id}",
                                   headers=self.get_auth_headers(analyst_b_id))

        self.assertEqual(response.status_code, 403)

    def test_other_analyst_gets_empty_project_list(self) -> None:
        analyst_a = self.create_analyst()
        analyst_b_payload = self.make_unique_analyst_payload()

        analyst_a_id = analyst_a["analyst_id"]

        self.create_project(analyst_a_id)

        analyst_b_response = self.client.post("/analysts",
                                              json=analyst_b_payload)
        self.assertEqual(analyst_b_response.status_code, 201)
        analyst_b = analyst_b_response.json()
        analyst_b_id = analyst_b["analyst_id"]

        response = self.client.get("/projects",
                                   headers=self.get_auth_headers(analyst_b_id))

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertIsInstance(body, list)
        self.assertEqual(body, [])