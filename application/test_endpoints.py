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
        response = requests.get(f"{API_URL}/leagues", headers=headers)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["headers"]), 4)
        self.assertEqual(len(data["rows"]), 12)

    def test_get_league(self):
        response = requests.get(f"{API_URL}/leagues/1", headers=headers)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["headers"]), 4)
        self.assertEqual(len(data["rows"]), 1)


if __name__ == "__main__":
    unittest.main()
