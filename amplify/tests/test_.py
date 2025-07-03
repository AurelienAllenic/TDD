import sys
from pathlib import Path
import json
import boto3
import pytest
from moto import mock_dynamodb

# Ajout dynamique du chemin vers le dossier contenant index.py
sys.path.append(str(Path(__file__).resolve().parents[3] / "backend/function/postUser/src"))

from index import handler  # import maintenant possible

TABLE_NAME = "Users"
GSI_NAME = "email-index"

@mock_dynamodb
def test_post_user():
    # 1. Création table DynamoDB mockée
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")

    dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": GSI_NAME,
                "KeySchema": [
                    {"AttributeName": "email", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )

    # 2. Simulation de l'event Lambda POST
    event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "username": "martin",
            "email": "martin@example.com"
        })
    }

    # 3. Appel de la Lambda handler
    response = handler(event, None)

    # 4. Assertions sur la réponse
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["message"] == "Utilisateur créé"
    assert body["user"]["username"] == "martin"
    assert body["user"]["email"] == "martin@example.com"
