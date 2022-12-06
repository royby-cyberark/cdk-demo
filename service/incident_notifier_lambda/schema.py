from pydantic import BaseSettings

class NotifierHandlerEnv(BaseSettings):
    INCIDENT_NOTIFICATION_SNS_TOPIC: str
