# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional


class Summary(BaseModel):
    symptoms: str
    duration: str
    severity_reason: str
    recommendation: str


class TriageResponse(BaseModel):
    category: str
    severity: str
    response: str
    summary: Optional[Summary] = None