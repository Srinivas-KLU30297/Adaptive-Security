from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.schemas.auth import UserOut

class ModalityResultOut(BaseModel):
    id: UUID
    modality: str
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    xai_data: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CaseOut(BaseModel):
    id: UUID
    user_id: UUID
    case_type: str
    input_summary: Optional[str] = None
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    status: str
    report_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    modality_results: List[ModalityResultOut] = []

    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    items: List[CaseOut]
    total: int
    page: int
    size: int
