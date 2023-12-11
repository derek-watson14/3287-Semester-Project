import sqlite3
import json


class Controller:
    def __init__(self, path):
        self.path = path

    def _formulate_response(self, data):
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "multiValueHeaders": {},
            "body": json.dumps(data),
        }

    def _query_database(self, query, params=None):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            column_headers = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
        return {"headers": column_headers, "rows": rows}

    def get_leagues(self):
        query = """
            SELECT *
            FROM League 
        """
        data = self._query_database(query)
        return self._formulate_response(data)

    def get_league(self, league_id):
        query = """
            SELECT *
            FROM League 
            WHERE id = ?
        """
        params = (league_id,)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def get_teams(self):
        query = """
            SELECT *
            FROM Team 
        """
        data = self._query_database(query)
        return self._formulate_response(data)

    def get_team(self, team_id):
        query = """
            SELECT *
            FROM Team 
            WHERE id = ?
        """
        params = (team_id,)
        data = self._query_database(query, params)
        return self._formulate_response(data)
