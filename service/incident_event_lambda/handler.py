import json
import logging

import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from incident_event_lambda.schema import IncidentEventHandlerEnv
from responses import get_response
from schemas.incident import Incident

logger = logging.getLogger()
logger.setLevel(logging.INFO)

env = IncidentEventHandlerEnv()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(env.INCIDENTS_TABLE)

sqs = boto3.client('sqs')


def lambda_handler(event, context):
    try:
        logger.info(f'{event=}')
        body = json.loads(event.get('body'))
        incident = Incident(**body)
        
        response = table.put_item(
            Item={
                'incident_id': incident.IncidentId,
                'cvss': str(incident.Cvss),
                'description': incident.Description
        })

        logger.info(f'put_item result: {response}')

        response = sqs.send_message(
            QueueUrl=env.NOTIFICATIONS_QUEUE_URL,
            MessageBody=incident.json()
        )
        logger.info(f'sqs send_message result: {response}')

        return get_response(code=200, message='Incident handled')

    except ClientError as ex:
        return get_response(code=500, message=f'Internal error: {str(ex)}')
    except ValidationError as ex:
        logger.error(str(ex))
        return get_response(code=400, message=f'Invalid input: {str(ex)}')
    except Exception as ex:
        logger.error(str(ex))
        return get_response(code=400, message=f'Unknown error: {str(ex)}')

