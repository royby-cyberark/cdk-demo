from typing import Optional
from pydantic import BaseModel, confloat


class Incident(BaseModel):
    IncidentId: str
    Description: Optional[str]
    Cvss: confloat(ge=1.0, le=10.0)
