import os
import boto3
import json
from Controller import Controller

s3_client = boto3.client("s3")

BUCKET_NAME = os.environ["DB_BUCKET_NAME"]
DB_KEY = "soccer.db"
LOCAL_PATH = "/tmp/socccer.db"

s3_client.download_file(BUCKET_NAME, DB_KEY, LOCAL_PATH)

cn = Controller(LOCAL_PATH)


def handler(event, context):
    pathParts = event["path"].split("/")
    qsp = event["queryStringParameters"]
    method = event["httpMethod"]

    if method != "GET":
        return cn.error("Invalid method")

    if pathParts[1] == "league":
        if qsp is not None and "name" in qsp:
            l_name = qsp["name"]
            return cn.get_league_by_name(l_name)
        else:
            return cn.get_leagues()

    elif pathParts[1] == "team":
        if qsp is not None and "name" in qsp:
            t_name = qsp["name"]
            return cn.get_team_by_name(t_name)
        else:
            return cn.get_teams()

    elif pathParts[1] == "season":
        return cn.get_seasons()

    elif pathParts[1] == "reports":
        if pathParts[2] == "betting-upsets":
            if qsp is None or "leagueId" not in qsp:
                return cn.error("Invalid path or query string parameters")
            else:
                league_id = qsp["leagueId"]
                start_season = qsp["startSeasonId"] if "startSeasonId" in qsp else None
                end_season = qsp["endSeasonId"] if "endSeasonId" in qsp else None
                return cn.betting_upsets(league_id, start_season, end_season)

        elif pathParts[2] == "scoreline-occurrences":
            if qsp is None or "leagueId" not in qsp:
                return cn.error("Invalid path or query string parameters")
            else:
                league_id = qsp["leagueId"]
                start_season = qsp["startSeasonId"] if "startSeasonId" in qsp else None
                end_season = qsp["endSeasonId"] if "endSeasonId" in qsp else None
                return cn.scoreline_occurrances(league_id, start_season, end_season)

        elif pathParts[2] == "team-history":
            if qsp is None or "teamId" not in qsp:
                return cn.error("Invalid path or query string parameters")
            else:
                team_id = qsp["teamId"]
                start_season = qsp["startSeasonId"] if "startSeasonId" in qsp else None
                end_season = qsp["endSeasonId"] if "endSeasonId" in qsp else None
                return cn.team_history(team_id, start_season, end_season)

        elif pathParts[2] == "historical-table":
            if qsp is None or "leagueId" not in qsp:
                return cn.error("Invalid path or query string parameters")
            else:
                league_id = qsp["leagueId"]
                start_season = qsp["startSeasonId"] if "startSeasonId" in qsp else None
                end_season = qsp["endSeasonId"] if "endSeasonId" in qsp else None
                return cn.historical_table(league_id, start_season, end_season)

        elif pathParts[2] == "league-compare":
            if qsp is None:
                return cn.compare_leagues()
            else:
                start_season = qsp["startSeasonId"] if "startSeasonId" in qsp else None
                end_season = qsp["endSeasonId"] if "endSeasonId" in qsp else None
                return cn.compare_leagues(start_season, end_season)

    else:
        return cn.error("Invalid path or query string parameters")
