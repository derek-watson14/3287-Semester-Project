import os
import boto3
import zipfile
import sqlite3
import json

s3_client = boto3.client("s3")

# Do this outside the handler to take advantage of the container reuse
# https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
bucket_name = os.environ["DB_BUCKET_NAME"]
db_key = "soccer.db"
db_path = "/tmp/socccer.db"

s3_client.download_file(bucket_name, db_key, db_path)


def query_database(db_path, query, params=None):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        column_headers = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return {"headers": column_headers, "rows": rows}


def handler(event, context):
    league_id = None

    if (
        "queryStringParameters" in event
        and event["queryStringParameters"] is not None
        and "league_id" in event["queryStringParameters"]
    ):
        league_id = event["queryStringParameters"]["league_id"]

    if league_id:
        query = """
            SELECT *
            FROM League 
            WHERE id = ?
        """
        params = (league_id,)
    else:
        query = """
            SELECT *
            FROM League 
        """
        params = ()

    result = query_database(db_path, query, params)

    formatted_results = [dict(zip(result["headers"], row)) for row in result["rows"]]

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json",
        },
        "body": formatted_results,
    }
