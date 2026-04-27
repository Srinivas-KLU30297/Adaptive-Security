import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    case_type = Column(String(50), nullable=False) # email, url, image, video, audio, full_scan
    input_summary = Column(Text, nullable=True)
    verdict = Column(String(50), nullable=True) # phishing, legitimate, deepfake, real, suspicious
    confidence = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True) # low, medium, high, critical
    status = Column(String(50), default="pending", index=True) # pending, processing, completed, failed
    report_path = Column(String(255), nullable=True)
    celery_task_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="cases")
    modality_results = relationship("ModalityResult", back_populates="case", cascade="all, delete-orphan")
