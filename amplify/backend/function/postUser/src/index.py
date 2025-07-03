import json

def handler(event, context):
    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Méthode non autorisée"})
        }

    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        email = body.get("email")

        if not username or not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Champs manquants"})
            }

        # Simulation de la création de l'utilisateur
        user = {
            "username": username,
            "email": email
        }

        return {
            "statusCode": 201,
            "headers": {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "body": json.dumps({"message": "Utilisateur créé", "user": user})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
