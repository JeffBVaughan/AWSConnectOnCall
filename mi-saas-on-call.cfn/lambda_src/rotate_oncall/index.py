import os
import boto3
from boto3.dynamodb.types import TypeDeserializer

# Initialize AWS services
sns = boto3.client("sns")
dynamodb = boto3.client("dynamodb")

# Set SMS attributes
sms_params = os.environ["SMSSenderId"]

# Define DynamoDB table parameters
table_name = os.environ["DynamoDBTableName"]
table_params = {"TableName": table_name}


def update_on_call_users(result):
    update_params = {
        "Key": {"id": {"N": str(result["id"])}},
        "AttributeUpdates": {"rank": {"Value": {"S": str(result["rank"])}}},
        "TableName": table_name,
    }
    dynamodb.update_item(**update_params)

def rotate_on_call_db(result, index, array):
    updated_result = result
    updated_result["rank"] -= 1
    if updated_result["rank"] == 0:
        team_members = [
            item for item in array if item["team"] == updated_result["team"]
        ]
        updated_result["rank"] = len(team_members)
    return updated_result

def send_sms(updated_roster_item):
    message = f"You are now the primary OnCall engineer this week for {updated_roster_item['team']} team"
    mobile_number = (
        updated_roster_item["countrycode"] + updated_roster_item["mobile"][1:]
    )
    if updated_roster_item["rank"] == 1:
        sns.publish(
            Message=message, MessageStructure="string", PhoneNumber=mobile_number
        )

def handler():
    try:
        # Scan DynamoDB table
        scan_result = dynamodb.scan(**table_params)

        # Unpack and rotate on-call roster
        rotate_on_call_db(
            boto3.dynamodb.types.TypeDeserializer().deserialize(item),
            index,
            scan_result["Items"],
        )
        for index, item in enumerate(scan_result["Items"])

        # Update on-call users in DynamoDB
        for item in updated_roster:
            update_on_call_users(item)
        boto3.session.Session().resource("dynamodb").batch_write_item(
            RequestItems={table_name: update_promises}
        )

        # Send SMS notifications
        for item in updated_roster:
            send_sms(item)
    except Exception as e:
        return e

    return None
