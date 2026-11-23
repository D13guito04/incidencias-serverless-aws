import json
import os

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "incidencias")
ESTADOS = {"abierta", "en curso", "cerrada"}

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

    incident_id = (event.get("pathParameters") or {}).get("incidentId")
    if not incident_id:
        return respuesta(400, {"error": "Falta el identificador de la incidencia"})

    try:
        datos = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return respuesta(400, {"error": "El cuerpo no es JSON válido"})

    if not isinstance(datos, dict):
        return respuesta(400, {"error": "El cuerpo debe ser un objeto JSON"})

    nuevo_estado = str(datos.get("estado") or "").strip().lower()
    if nuevo_estado not in ESTADOS:
        return respuesta(400, {"error": "estado debe ser abierta, en curso o cerrada"})

    try:
        resultado = tabla.update_item(
            Key={"userId": user_id, "incidentId": incident_id},
            UpdateExpression="SET #e = :estado",
            ConditionExpression="attribute_exists(incidentId)",
            ExpressionAttributeNames={"#e": "estado"},
            ExpressionAttributeValues={":estado": nuevo_estado},
            ReturnValues="ALL_NEW",
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return respuesta(404, {"error": "Incidencia no encontrada"})
        print("Error al actualizar la incidencia:", error)
        return respuesta(500, {"error": "No se pudo actualizar la incidencia"})

    return respuesta(200, resultado["Attributes"])
