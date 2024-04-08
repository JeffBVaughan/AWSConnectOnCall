import os
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb = boto3.client("dynamodb")
table_name = os.environ["DynamoDBTableName"]


def handler(event):
    try:
        scan_result = dynamodb.scan(TableName=table_name)
        deserializer = TypeDeserializer()
        find_oncall = [
            deserializer.deserialize(item)
            for item in scan_result["Items"]
            if item["rank"]["S"] == event["Details"]["Parameters"]["lookuprank"]
            and item["team"]["S"] == event["Details"]["Parameters"]["lookupteam"]
        ]
        response = {"mobile": find_oncall[0]["mobile"]["S"][1:]}
        return response
    except Exception as e:
        raise e
