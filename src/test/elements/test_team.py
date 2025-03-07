import unittest

import requests_mock

from grafana_client import GrafanaApi


class TeamsTestCase(unittest.TestCase):
    def setUp(self):
        self.grafana = GrafanaApi(
            ("admin", "admin"), host="localhost", url_path_prefix="", protocol="http"
        )

    @requests_mock.Mocker()
    def test_search_teams_url_encodes_query(self, m):
        m.get(
            "http://localhost/api/teams/search?query=my%20team&page=1",
            json={
                "totalCount": 1,
                "teams": [
                    {
                        "id": 1,
                        "orgId": 1,
                        "name": "MyTestTeam",
                        "email": "",
                        "avatarUrl": "/avatar/3f49c15916554246daa714b9bd0ee398",
                        "memberCount": 1,
                    }
                ],
                "page": 1,
                "perPage": 1000,
            },
        )
        teams = self.grafana.teams.search_teams("my team")
        self.assertEqual(teams[0]["name"], "MyTestTeam")
        self.assertEqual(len(teams), 1)

    @requests_mock.Mocker()
    def test_search_teams_loads_all_pages(self, m):
        m.get(
            "http://localhost/api/teams/search?query=team&page=1&perpage=1",
            json={
                "totalCount": 2,
                "teams": [
                    {
                        "id": 1,
                        "orgId": 1,
                        "name": "MyTestTeam",
                        "email": "",
                        "avatarUrl": "/avatar/3f49c15916554246daa714b9bd0ee398",
                        "memberCount": 1,
                    }
                ],
                "page": 1,
                "perPage": 1,
            },
        )

        m.get(
            "http://localhost/api/teams/search?query=team&page=2&perpage=1",
            json={
                "totalCount": 2,
                "teams": [
                    {
                        "id": 2,
                        "orgId": 1,
                        "name": "SecondTeam",
                        "email": "",
                        "avatarUrl": "/avatar/3f49c15916554246daa714b9bd0ee398",
                        "memberCount": 23,
                    }
                ],
                "page": 2,
                "perPage": 1,
            },
        )
        teams = self.grafana.teams.search_teams("team", perpage=1)
        self.assertEqual(teams[0]["name"], "MyTestTeam")
        self.assertEqual(teams[1]["name"], "SecondTeam")
        self.assertEqual(len(teams), 2)

    @requests_mock.Mocker()
    def test_search_teams_only_loads_requested_page(self, m):
        m.get(
            "http://localhost/api/teams/search?query=my%20team&page=2",
            json={
                "totalCount": 10,
                "teams": [
                    {
                        "id": 2,
                        "orgId": 1,
                        "name": "MyTestTeam",
                        "email": "",
                        "avatarUrl": "/avatar/3f49c15916554246daa714b9bd0ee398",
                        "memberCount": 1,
                    }
                ],
                "page": 1,
                "perPage": 1,
            },
        )
        teams = self.grafana.teams.search_teams("my team", 2)
        self.assertEqual(teams[0]["name"], "MyTestTeam")
        self.assertEqual(len(teams), 1)

    @requests_mock.Mocker()
    def test_get_team_by_name(self, m):
        m.get(
            "http://localhost/api/teams/search?name=my%20team",
            json={
                "totalCount": 1,
                "teams": [
                    {
                        "id": 2,
                        "orgId": 1,
                        "name": "my team",
                        "email": "",
                        "avatarUrl": "/avatar/3f49c15916554246daa714b9bd0ee398",
                        "memberCount": 1,
                    }
                ],
                "page": 1,
                "perPage": 1000,
            },
        )
        teams = self.grafana.teams.get_team_by_name("my team")
        self.assertEqual(teams[0]["name"], "my team")
        self.assertEqual(len(teams), 1)

    @requests_mock.Mocker()
    def test_get_team(self, m):
        m.get(
            "http://localhost/api/teams/1",
            json={
                "id": 1,
                "orgId": 1,
                "name": "MyTestTeam",
                "email": "",
                "created": "2017-12-15T10:40:45+01:00",
                "updated": "2017-12-15T10:40:45+01:00",
            },
        )
        team = self.grafana.teams.get_team("1")
        self.assertEqual(team["name"], "MyTestTeam")

    @requests_mock.Mocker()
    def test_add_team(self, m):
        m.post(
            "http://localhost/api/teams", json={"message": "Team created", "teamId": 2}
        )
        team = {"name": "MySecondTestTeam", "email": "email@example.org"}
        new_team = self.grafana.teams.add_team(team)
        self.assertEqual(new_team["teamId"], 2)

    @requests_mock.Mocker()
    def test_update_team(self, m):
        m.put("http://localhost/api/teams/3", json={"message": "Team updated"})
        team = {"name": "MyThirdTestTeam", "email": "email@example.org"}
        response = self.grafana.teams.update_team(3, team)
        self.assertEqual(response["message"], "Team updated")

    @requests_mock.Mocker()
    def test_delete_team(self, m):
        m.delete("http://localhost/api/teams/3", json={"message": "Team deleted"})
        response = self.grafana.teams.delete_team(3)
        self.assertEqual(response, True)

    @requests_mock.Mocker()
    def test_get_team_members(self, m):
        m.get(
            "http://localhost/api/teams/1/members",
            json=[
                {
                    "orgId": 1,
                    "teamId": 1,
                    "userId": 3,
                    "email": "user1@email.com",
                    "login": "user1",
                    "avatarUrl": "/avatar/1b3c32f6386b0185c40d359cdc733a79",
                }
            ],
        )
        members = self.grafana.teams.get_team_members("1")
        self.assertEqual(members[0]["login"], "user1")

    @requests_mock.Mocker()
    def test_add_team_member(self, m):
        m.post(
            "http://localhost/api/teams/1/members",
            json={"message": "Member added to Team"},
        )
        history = m.request_history
        add_res = self.grafana.teams.add_team_member("1", "3")
        self.assertEqual(history[0].json()["userId"], "3")
        self.assertEqual(add_res["message"], "Member added to Team")

    @requests_mock.Mocker()
    def test_remove_team_member(self, m):
        m.delete(
            "http://localhost/api/teams/13/members/2",
            json={"message": "Team member removed"},
        )
        remove_res = self.grafana.teams.remove_team_member("13", "2")
        self.assertEqual(remove_res["message"], "Team member removed")

    @requests_mock.Mocker()
    def test_get_team_preferences(self, m):
        m.get(
            "http://localhost/api/teams/1/preferences",
            json={"theme": "", "homeDashboardId": 0, "timezone": ""},
        )
        prefs = self.grafana.teams.get_team_preferences("1")
        self.assertEqual(prefs["homeDashboardId"], 0)

    @requests_mock.Mocker()
    def test_update_team_preferences(self, m):
        m.put(
            "http://localhost/api/teams/1/preferences",
            json={"message": "Preferences updated"},
        )
        prefs = {"theme": "light", "homeDashboardId": 0, "timezone": ""}

        updates = self.grafana.teams.update_team_preferences("1", prefs)
        history = m.request_history
        json_payload = history[0].json()
        self.assertEqual(json_payload["theme"], "light")
        self.assertEqual(updates["message"], "Preferences updated")
