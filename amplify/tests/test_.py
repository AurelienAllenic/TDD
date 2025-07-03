import json
import boto3
import pytest
from moto import mock_dynamodb
import os
import sys

# Charger tes lambdas comme avant
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'function', 'postUser', 'src')))
from index import lambda_handler as post_user_lambda

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'function', 'getUser', 'src')))
from index import lambda_handler as get_user_lambda

TABLE_NAME = "Users"

@pytest.fixture(scope="module")
def dynamodb_mock():
    with mock_dynamodb():
        # Crée la table mockée une seule fois par module de test
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[{
                "IndexName": "email-index",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        ).wait_until_exists()

        # Set l'ENV pour la lambda
        os.environ["TABLE_NAME"] = TABLE_NAME

        yield dynamodb  # on peut passer dynamodb si besoin

@pytest.fixture(scope="module")
def user_data(dynamodb_mock):
    # Crée un utilisateur via la lambda POST, dans la table mockée
    event = {
        "body": json.dumps({"email": "test@example.com"})
    }
    response = post_user_lambda(event, None)
    body = json.loads(response["body"])
    return {
        "response": response,
        "user_id": body["user_id"],
        "email": body["email"]
    }

def test_create_user_success(user_data):
    response = user_data["response"]
    body = json.loads(response["body"])

    assert response["statusCode"] == 201
    assert "user_id" in body
    assert body["email"] == "test@example.com"

def test_get_user_success(user_data):
    get_event = {
        "queryStringParameters": {
            "email": user_data["email"]
        }
    }
    response = get_user_lambda(get_event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["email"] == user_data["email"]


