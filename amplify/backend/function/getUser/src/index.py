import json
import boto3
import os

def lambda_handler(event, context):
    try:
        # Initialiser DynamoDB à l'intérieur de la fonction
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        table_name = os.environ.get("TABLE_NAME", "Users")
        table = dynamodb.Table(table_name)
        
        # Récupérer l'email selon la méthode HTTP / event
        email = None

        # Cas GET avec queryStringParameters
        # (optionnel) Cas POST avec body JSON
        if event.get("body"):
            try:
                body = json.loads(event["body"])
                email = body.get("email")
            except Exception:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in body"})
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Email parameter missing"})
            }

        # Chercher l'utilisateur dans DynamoDB via l'index email
        response = table.query(
            IndexName="email-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("email").eq(email)
        )
        items = response.get("Items", [])
        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }
        user = items[0]
        return {
            "statusCode": 200,
            "body": json.dumps(user)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }