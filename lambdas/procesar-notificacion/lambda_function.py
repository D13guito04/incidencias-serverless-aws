import json
import logging
import os
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

AUDIT_TABLE_NAME = os.environ["AUDIT_TABLE_NAME"]
FORCE_EXCEPTION = os.environ.get("FORCE_EXCEPTION", "false").lower() == "true"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
audit_table = dynamodb.Table(AUDIT_TABLE_NAME)


def process_record(record, context):
    message = json.loads(record.get("body") or "{}")
    required = ("eventId", "eventType", "userId", "incidentId", "createdAt")
    if any(not message.get(field) for field in required):
        raise ValueError("El mensaje no contiene todos los campos requeridos")
    if message["eventType"] != "INCIDENT_CREATED":
        raise ValueError("Tipo de evento no admitido")

    # Interruptor temporal para comprobar los reintentos y la DLQ.
    # Debe permanecer en false fuera de las pruebas de fallo.
    if FORCE_EXCEPTION:
        raise RuntimeError("Excepción de prueba activada")

    audit_record = {
        "eventId": message["eventId"],
        "eventType": message["eventType"],
        "userId": message["userId"],
        "incidentId": message["incidentId"],
        "createdAt": message["createdAt"],
        "processedAt": datetime.now(timezone.utc).isoformat(),
    }

    try:
        audit_table.put_item(
            Item=audit_record,
            ConditionExpression=Attr("eventId").not_exists(),
        )
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            logger.info(
                json.dumps(
                    {
                        "event": "AUDIT_DUPLICATE_IGNORED",
                        "eventId": message["eventId"],
                        "incidentId": message["incidentId"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return
        raise

    logger.info(
        json.dumps(
            {
                "event": "INCIDENT_CREATED_AUDIT",
                "eventId": message["eventId"],
                "incidentId": message["incidentId"],
                "processedAt": audit_record["processedAt"],
                "requestId": context.aws_request_id,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def lambda_handler(event, context):
    records = event.get("Records", [])
    for record in records:
        process_record(record, context)
    return {"processed": len(records)}
