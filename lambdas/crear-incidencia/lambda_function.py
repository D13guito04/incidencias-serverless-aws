import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "incidencias")
NOTIFICATION_QUEUE_URL = os.environ.get("NOTIFICATION_QUEUE_URL")
PRIORIDADES = {"baja", "media", "alta"}

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(TABLE_NAME)
sqs = boto3.client("sqs")


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

    creada = datetime.now(timezone.utc).isoformat()
    incidencia = {
        "userId": user_id,
        "incidentId": str(uuid.uuid4()),
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "estado": "abierta",
        "creada": creada,
    }

    try:
        tabla.put_item(Item=incidencia)
    except ClientError:
        logger.exception("No se pudo guardar la incidencia")
        return respuesta(500, {"error": "No se pudo guardar la incidencia"})

    event_id = str(uuid.uuid4())
    mensaje = {
        "eventId": event_id,
        "eventType": "INCIDENT_CREATED",
        "userId": user_id,
        "incidentId": incidencia["incidentId"],
        "createdAt": creada,
    }

    try:
        if not NOTIFICATION_QUEUE_URL:
            raise RuntimeError("Falta la variable NOTIFICATION_QUEUE_URL")
        sqs.send_message(
            QueueUrl=NOTIFICATION_QUEUE_URL,
            MessageBody=json.dumps(mensaje, ensure_ascii=False),
        )
    except (BotoCoreError, ClientError, RuntimeError):
        logger.exception(
            "La incidencia se guardó, pero no se pudo encolar su auditoría",
            extra={"incidentId": incidencia["incidentId"], "eventId": event_id},
        )
        return respuesta(
            503,
            {
                "error": "La incidencia se guardó, pero la auditoría no se pudo encolar",
                "saved": True,
                "incidentId": incidencia["incidentId"],
            },
        )

    logger.info(
        "Incidencia creada y evento de auditoría encolado",
        extra={"incidentId": incidencia["incidentId"], "eventId": event_id},
    )
    return respuesta(201, incidencia)
