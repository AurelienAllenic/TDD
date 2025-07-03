import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        # Initialise le client DynamoDB à l'intérieur de la fonction
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        table_name = os.environ.get("TABLE_NAME", "Users")
        table = dynamodb.Table(table_name)

        body = json.loads(event["body"])
        email = body["email"]
        user_id = str(uuid.uuid4())

        table.put_item(
            Item={
                "user_id": user_id,
                "email": email,
                "created_at": body.get("created_at", "2025-07-03")
            },
            ConditionExpression="attribute_not_exists(user_id)"
        )

        return {
            "statusCode": 201,
            "body": json.dumps({"user_id": user_id, "email": email})
        }

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "statusCode": 409,
                "body": json.dumps({"message": "User with this email already exists"})
            }
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e)
            })
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid input",
                "error": str(e)
            })
        }
