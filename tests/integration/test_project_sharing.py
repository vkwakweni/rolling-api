from tests.integration.base import BaseIntegrationTestCase

class TestProjectSharing(BaseIntegrationTestCase):
    def test_owner_can_share_project_with_another_analyst(self):
        owner = self.create_analyst()
        owner_id = owner["analyst_id"]

        shared_analyst = self.create_analyst()
        shared_analyst_id = shared_analyst["analyst_id"]

        project = self.create_project(owner_id)
        project_id = project["project_id"]

        response = self.client.post(
            f"/projects/{project_id}/share",
            json=[{"analyst_id": shared_analyst_id}],
            headers=self.get_auth_headers(owner_id),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["analyst_id"], shared_analyst_id)

    def test_list_project_members_returns_owner_and_shared_analyst(self):
        owner = self.create_analyst()
        owner_id = owner["analyst_id"]

        shared_analyst = self.create_analyst()
        shared_analyst_id = shared_analyst["analyst_id"]

        project = self.create_project(owner_id)
        project_id = project["project_id"]

        share_response = self.client.post(
            f"/projects/{project_id}/share",
            json=[{"analyst_id": shared_analyst_id}],
            headers=self.get_auth_headers(owner_id),
        )
        self.assertEqual(share_response.status_code, 200)

        response = self.client.get(
            f"/projects/{project_id}/members",
            headers=self.get_auth_headers(owner_id),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertIsInstance(body, list)
        member_ids = {member["analyst_id"] for member in body}

        self.assertIn(owner_id, member_ids)
        self.assertIn(shared_analyst_id, member_ids)

    def test_shared_analyst_can_list_and_access_project(self):
        owner = self.create_analyst()
        owner_id = owner["analyst_id"]

        shared_analyst = self.create_analyst()
        shared_analyst_id = shared_analyst["analyst_id"]

        project = self.create_project(owner_id)
        project_id = project["project_id"]

        share_response = self.client.post(
            f"/projects/{project_id}/share",
            json=[{"analyst_id": shared_analyst_id}],
            headers=self.get_auth_headers(owner_id),
        )
        self.assertEqual(share_response.status_code, 200)

        list_response = self.client.get(
            "/projects",
            headers=self.get_auth_headers(shared_analyst_id),
        )
        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()

        self.assertTrue(
            any(project_row["project_id"] == project_id for project_row in list_body)
        )

        get_response = self.client.get(
            f"/projects/{project_id}",
            headers=self.get_auth_headers(shared_analyst_id),
        )
        self.assertEqual(get_response.status_code, 200)
        get_body = get_response.json()

        self.assertEqual(get_body["project_id"], project_id)

    def test_non_owner_cannot_share_project(self):
        owner = self.create_analyst()
        owner_id = owner["analyst_id"]

        shared_analyst = self.create_analyst()
        shared_analyst_id = shared_analyst["analyst_id"]

        third_analyst = self.create_analyst()
        third_analyst_id = third_analyst["analyst_id"]

        project = self.create_project(owner_id)
        project_id = project["project_id"]

        first_share_response = self.client.post(
            f"/projects/{project_id}/share",
            json=[{"analyst_id": shared_analyst_id}],
            headers=self.get_auth_headers(owner_id),
        )
        self.assertEqual(first_share_response.status_code, 200)

        second_share_response = self.client.post(
            f"/projects/{project_id}/share",
            json=[{"analyst_id": third_analyst_id}],
            headers=self.get_auth_headers(shared_analyst_id),
        )

        self.assertEqual(second_share_response.status_code, 403)

    def test_unrelated_analyst_cannot_access_members_route(self):
        owner = self.create_analyst()
        owner_id = owner["analyst_id"]

        unrelated_analyst = self.create_analyst()
        unrelated_analyst_id = unrelated_analyst["analyst_id"]

        project = self.create_project(owner_id)
        project_id = project["project_id"]

        response = self.client.get(
            f"/projects/{project_id}/members",
            headers=self.get_auth_headers(unrelated_analyst_id),
        )

        self.assertEqual(response.status_code, 403)