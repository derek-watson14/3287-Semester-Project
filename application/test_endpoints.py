import dotenv
import os
import requests
import unittest

dotenv.load_dotenv()

API_URL = os.environ["API_URL"]
API_KEY = os.environ["API_KEY"]

headers = {"X-API-Key": API_KEY}


class APITestCase(unittest.TestCase):
    def test_get_leagues(self):
        response = requests.get(f"{API_URL}/league", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_league_by_name(self):
        response = requests.get(f"{API_URL}/league?name=Premier League", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_teams(self):
        response = requests.get(f"{API_URL}/team", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_team_by_name(self):
        response = requests.get(f"{API_URL}/team?name=Dortmund", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_seasons(self):
        response = requests.get(f"{API_URL}/season", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_betting_upsets(self):
        response = requests.get(f"{API_URL}/reports/betting-upsets?leagueId=1", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_scoreline_occurrances(self):
        response = requests.get(
            f"{API_URL}/reports/scoreline-occurrences?leagueId=1", headers=headers
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_team_history(self):
        response = requests.get(f"{API_URL}/reports/team-history?teamId=222", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_historical_table(self):
        response = requests.get(f"{API_URL}/reports/historical-table?leagueId=1", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)

    def test_get_compare_leagues(self):
        response = requests.get(f"{API_URL}/reports/league-compare", headers=headers)
        data = response.json()
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
