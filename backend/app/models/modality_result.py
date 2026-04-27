import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Uuid, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class ModalityResult(Base):
    __tablename__ = "modality_results"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    modality = Column(String(50), nullable=False) # email, url, image, video, audio
    verdict = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    xai_data = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="modality_results")
