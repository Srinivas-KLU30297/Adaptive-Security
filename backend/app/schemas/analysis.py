from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class EmailAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=10)

class URLAnalysisRequest(BaseModel):
    url: HttpUrl

class AnalysisResponse(BaseModel):
    case_id: UUID
    task_id: Optional[str] = None
    status: str
    message: str
