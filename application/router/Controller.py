import sqlite3
import json


class Controller:
    def __init__(self, path):
        self.path = path

    def _formulate_response(self, data, code=200):
        return {
            "isBase64Encoded": False,
            "statusCode": code,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "multiValueHeaders": {},
            "body": json.dumps(data),
        }

    def _query_database(self, query, params=None):
        print("IN QUERY DATABASE")
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            column_headers = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
        return {"headers": column_headers, "rows": rows}

    def _set_seasons(self, start_season_id, end_season_id):
        # Seasons ids range from 1 to 15 (2008-09 to 2022-23)
        if start_season_id is None and end_season_id is None:
            start_season_id = 1
            end_season_id = 15
        if start_season_id is None:
            start_season_id = 1
        if end_season_id is None:
            end_season_id = 15
        return start_season_id, end_season_id

    def error(self, message):
        return self._formulate_response({"message": message}, 400)

    def get_leagues(self):
        query = """
            SELECT *
            FROM League 
        """
        data = self._query_database(query)
        return self._formulate_response(data)

    def get_league_by_name(self, league_id):
        query = """
            SELECT *
            FROM League 
            WHERE League.name LIKE ?
        """
        like_pattern = f"%{league_id}%"
        params = (like_pattern,)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def get_teams(self):
        query = """
            SELECT *
            FROM Team 
        """
        data = self._query_database(query)
        return self._formulate_response(data)

    def get_team_by_name(self, team_name):
        query = """
            SELECT *
            FROM Team 
            WHERE Team.name LIKE ?
        """
        like_pattern = f"%{team_name}%"
        params = (like_pattern,)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def get_seasons(self):
        query = """
            SELECT *
            FROM Season 
        """
        data = self._query_database(query)
        return self._formulate_response(data)

    def betting_upsets(self, league_id, start_season_id=None, end_season_id=None):
        start_season_id, end_season_id = self._set_seasons(start_season_id, end_season_id)
        query = """
        SELECT 
            s.name as "Season",
            m.date as "MatchDate",
            htm.name as "HomeTeam",
            atm.name as "AwayTeam",
            CASE
                WHEN m.ft_result = 'A' THEN atm.name
                WHEN m.ft_result = 'H' THEN htm.name
            END as "Winner",
            ROUND(avg_odds.avg_home_odds, 2) as "AvgHomeOdds",
            ROUND(avg_odds.avg_draw_odds, 2) as "AvgDrawOdds",
            ROUND(avg_odds.avg_away_odds, 2) as "AvgAwayOdds",
            ROUND(CASE
                WHEN m.ft_result = 'A' THEN avg_odds.avg_away_odds
                WHEN m.ft_result = 'H' THEN avg_odds.avg_home_odds
                ELSE NULL
            END, 2) as "WinningOdds"
        FROM Match m
        JOIN Team htm on htm.id = m.home_team_id
        JOIN Team atm on atm.id = m.away_team_id
        JOIN League l on l.id = m.league_id
        JOIN Season s on s.id = m.season_id
        JOIN (
            SELECT 
                match_id,
                AVG(home_odds) as avg_home_odds,
                AVG(draw_odds) as avg_draw_odds,
                AVG(away_odds) as avg_away_odds
            FROM Odds
            GROUP BY match_id
        ) as avg_odds on avg_odds.match_id = m.id
        WHERE l.id = ?
        AND s.id >= ? AND s.id<= ?
        AND (
            (m.ft_result = 'A' AND avg_odds.avg_away_odds > avg_odds.avg_home_odds) OR 
            (m.ft_result = 'H' AND avg_odds.avg_home_odds > avg_odds.avg_away_odds)
        )
        ORDER BY "WinningOdds" DESC
        LIMIT 20;
        """
        params = (league_id, start_season_id, end_season_id)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def scoreline_occurrances(self, league_id, start_season_id=None, end_season_id=None):
        start_season_id, end_season_id = self._set_seasons(start_season_id, end_season_id)

        query = """
        SELECT 
            m.h_ft_goals AS "HomeGoals",
            m.a_ft_goals AS "AwayGoals",
            COUNT(*) AS "Occurrences", 
            ROUND((COUNT(*) * 100.0) / (
                SELECT COUNT(*) 
                FROM Match 
                JOIN Season ON Match.season_id = Season.id
                WHERE league_id = m.league_id
                AND season.name >= ? AND season.name <= ?
            ), 3) AS "Percentage"
        FROM Match m
        JOIN League l ON l.id = m.league_id
        JOIN Season s ON s.id = m.season_id
        WHERE l.id = ?
        AND s.id >= ? AND s.id<= ?
        GROUP BY m.h_ft_goals, m.a_ft_goals
        ORDER BY "Occurrences" DESC;
        """
        params = (start_season_id, end_season_id, league_id, start_season_id, end_season_id)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def team_history(self, team_id, start_season_id=None, end_season_id=None):
        start_season_id, end_season_id = self._set_seasons(start_season_id, end_season_id)
        query = """
        SELECT 
            s.name AS "Season",
            l.name AS "League",
            COUNT(m.id) AS "TotalMatches",
            SUM(CASE WHEN (m.home_team_id = t.id AND m.ft_result = 'H') OR (m.away_team_id = t.id AND m.ft_result = 'A') THEN 1 ELSE 0 END) AS "Wins",
            SUM(CASE WHEN m.ft_result = 'D' THEN 1 ELSE 0 END) AS "Draws",
            SUM(CASE WHEN (m.home_team_id = t.id AND m.ft_result = 'A') OR (m.away_team_id = t.id AND m.ft_result = 'H') THEN 1 ELSE 0 END) AS "Losses",
            SUM(CASE WHEN (m.home_team_id = t.id AND m.ft_result = 'H') OR (m.away_team_id = t.id AND m.ft_result = 'A') THEN 3 WHEN m.ft_result = 'D' THEN 1 ELSE 0 END) AS "Points",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_ft_goals ELSE m.a_ft_goals END) AS "GoalsFor",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.a_ft_goals ELSE m.h_ft_goals END) AS "GoalsAgainst",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_shots ELSE m.a_shots END) AS "Shots",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_shots_on_target ELSE m.a_shots_on_target END) AS "ShotsOnTarget",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_corners ELSE m.a_corners END) AS "Corners",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_fouls ELSE m.a_fouls END) AS "Fouls",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_yellow_cards ELSE m.a_yellow_cards END) AS "YellowCards",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_red_cards ELSE m.a_red_cards END) AS "RedCards"
        FROM Match m
        JOIN Season s ON s.id = m.season_id
        JOIN League l ON l.id = m.league_id
        JOIN Team t ON t.id = m.home_team_id OR t.id = m.away_team_id
        WHERE t.id = ?
        AND s.id >= ? AND s.id<= ?
        GROUP BY s.id
        ORDER BY s.id DESC;
        """
        params = (team_id, start_season_id, end_season_id)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def historical_table(self, league_id, start_season_id=None, end_season_id=None):
        start_season_id, end_season_id = self._set_seasons(start_season_id, end_season_id)
        query = """
        SELECT 
            t.name AS "Team",
            COUNT(m.id) AS "TotalMatches",
            SUM(CASE WHEN (m.home_team_id = t.id AND m.ft_result = 'H') OR (m.away_team_id = t.id AND m.ft_result = 'A') THEN 1 ELSE 0 END) AS "Wins",
            SUM(CASE WHEN m.ft_result = 'D' THEN 1 ELSE 0 END) AS "Draws",
            SUM(CASE WHEN (m.home_team_id = t.id AND m.ft_result = 'A') OR (m.away_team_id = t.id AND m.ft_result = 'H') THEN 1 ELSE 0 END) AS "Losses",
            SUM(CASE WHEN (m.home_team_id = t.id AND m.ft_result = 'H') OR (m.away_team_id = t.id AND m.ft_result = 'A') THEN 3 WHEN m.ft_result = 'D' THEN 1 ELSE 0 END) AS "Points",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_ft_goals ELSE m.a_ft_goals END) AS "GoalsFor",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.a_ft_goals ELSE m.h_ft_goals END) AS "GoalsAgainst",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_shots ELSE m.a_shots END) AS "Shots",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_shots_on_target ELSE m.a_shots_on_target END) AS "ShotsOnTarget",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_corners ELSE m.a_corners END) AS "Corners",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_fouls ELSE m.a_fouls END) AS "Fouls",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_yellow_cards ELSE m.a_yellow_cards END) AS "YellowCards",
            SUM(CASE WHEN m.home_team_id = t.id THEN m.h_red_cards ELSE m.a_red_cards END) AS "RedCards"
        FROM Match m
        JOIN Season s ON s.id = m.season_id
        JOIN Team t ON t.id = m.home_team_id OR t.id = m.away_team_id
        JOIN League l ON l.id = m.league_id
        WHERE l.id = ?
        AND s.id >= ? AND s.id<= ?
        GROUP BY t.id
        ORDER BY "Points" DESC, t.name;
        """
        params = (league_id, start_season_id, end_season_id)
        data = self._query_database(query, params)
        return self._formulate_response(data)

    def compare_leagues(self, start_season_id=None, end_season_id=None):
        start_season_id, end_season_id = self._set_seasons(start_season_id, end_season_id)
        query = """
        SELECT 
            l.name AS "League",
            COUNT(m.id) AS "TotalMatches",
            SUM(CASE WHEN m.ft_result = 'H' THEN 1 ELSE 0 END) AS "HomeWins",
            SUM(CASE WHEN m.ft_result = 'D' THEN 1 ELSE 0 END) AS "Draws",
            SUM(CASE WHEN m.ft_result = 'A' THEN 1 ELSE 0 END) AS "AwayWins",
            ROUND((AVG(m.a_ft_goals) + AVG(m.h_ft_goals)), 2) AS "GoalsPerMatch",
            ROUND((AVG(m.a_shots) + AVG(m.h_shots)), 2) AS "ShotsPerMatch",
            ROUND((AVG(m.a_shots_on_target) + AVG(m.h_shots_on_target)), 2) AS "ShotsOnTargetPerMatch",
            ROUND((AVG(m.a_corners) + AVG(m.h_corners)), 2) AS "CornersPerMatch",
            ROUND((AVG(m.a_fouls) + AVG(m.h_fouls)), 2) AS "FoulsPerMatch",
            ROUND((AVG(m.h_yellow_cards) + AVG(m.a_yellow_cards)), 2) AS "YellowCardsPerMatch",
            ROUND((AVG(m.a_red_cards) + AVG(m.h_red_cards)), 2) AS "RedCardsPerMatch"
        FROM Match m
        JOIN League l ON l.id = m.league_id
        JOIN Season s ON s.id = m.season_id
        WHERE s.id >= ? AND s.id <= ?
        GROUP BY l.id
        ORDER BY l.id;
        """
        params = (start_season_id, end_season_id)
        data = self._query_database(query, params)
        return self._formulate_response(data)
