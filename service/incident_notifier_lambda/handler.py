import logging

import boto3
import json
from pydantic import ValidationError

from responses import get_response
from incident_notifier_lambda.consts import INCIDENT_NOTIFICATION_THRESHOLD
from incident_notifier_lambda.schema import NotifierHandlerEnv
from schemas.incident import Incident

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        env = NotifierHandlerEnv()
        logger.info(f'{event=}')

        # TODO - Validate SQS record
        incident_event = json.loads(event['Records'][0]['body'])
        incident = Incident(**incident_event)

        cvss = incident.Cvss
        if cvss > INCIDENT_NOTIFICATION_THRESHOLD:
            sns.publish(
                TopicArn=env.INCIDENT_NOTIFICATION_SNS_TOPIC, 
                Subject='Oy Vey Zmir!',
                Message=incident.json()
            )
            
    except ValidationError as ex:
        logger.error(ex)
        return get_response(code=400, message=f'Invalid input: {str(ex)}')
    except Exception as ex:
        logger.error(str(ex))
        return get_response(code=400, message=f'Unknown error: {str(ex)}')


    return get_response(code=200, body='Incident notification lambda finished')