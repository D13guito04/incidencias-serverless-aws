import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "incidencias")

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(TABLE_NAME)


def respuesta(codigo, cuerpo):
    return {
        "statusCode": codigo,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(cuerpo, ensure_ascii=False),
    }


def lambda_handler(event, context):
    # El autorizador de Cognito ya ha comprobado el token.
    try:
        user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    except KeyError:
        return respuesta(401, {"error": "No autenticado"})

    try:
        resultado = tabla.query(
            KeyConditionExpression=Key("userId").eq(user_id)
        )
    except ClientError as error:
        print("Error al consultar la tabla:", error)
        return respuesta(500, {"error": "No se pudieron leer las incidencias"})

    return respuesta(200, {"incidencias": resultado.get("Items", [])})