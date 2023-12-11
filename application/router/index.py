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

    if pathParts[1] == "leagues":
        if len(pathParts) == 2:
            return cn.get_leagues()
        else:
            l_id = pathParts[2]
            return cn.get_league(l_id)
