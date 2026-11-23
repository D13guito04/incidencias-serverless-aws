import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "incidencias")
PRIORIDADES = {"baja", "media", "alta"}

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
    # Aquí solo leemos quién es el usuario.
    try:
        user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    except KeyError:
        return respuesta(401, {"error": "No autenticado"})

    try:
        datos = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return respuesta(400, {"error": "El cuerpo no es JSON válido"})

    if not isinstance(datos, dict):
        return respuesta(400, {"error": "El cuerpo debe ser un objeto JSON"})

    titulo = str(datos.get("titulo") or "").strip()
    descripcion = str(datos.get("descripcion") or "").strip()
    prioridad = str(datos.get("prioridad") or "").strip().lower()

    if not titulo or prioridad not in PRIORIDADES:
        return respuesta(400, {"error": "Faltan datos: titulo y prioridad (baja, media o alta)"})

    incidencia = {
        "userId": user_id,
        "incidentId": str(uuid.uuid4()),
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "estado": "abierta",
        "creada": datetime.now(timezone.utc).isoformat(),
    }

    try:
        tabla.put_item(Item=incidencia)
    except ClientError as error:
        print("Error al guardar la incidencia:", error)
        return respuesta(500, {"error": "No se pudo guardar la incidencia"})

    return respuesta(201, incidencia)