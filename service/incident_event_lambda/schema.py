from pydantic import BaseSettings

class IncidentEventHandlerEnv(BaseSettings):
    INCIDENTS_TABLE: str
    NOTIFICATIONS_QUEUE_URL: str
