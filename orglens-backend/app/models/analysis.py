import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, JSON, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    progress: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    org_health_score: Mapped[float | None] = mapped_column(Float)   
    health_breakdown: Mapped[dict | None] = mapped_column(JSON)
    trust_gap_score: Mapped[float | None] = mapped_column(Float)    
    trust_gap_details: Mapped[dict | None] = mapped_column(JSON)
    power_structure: Mapped[dict | None] = mapped_column(JSON)
    top_influencers: Mapped[list | None] = mapped_column(JSON)
    gatekeepers: Mapped[list | None] = mapped_column(JSON)
    resilience_score: Mapped[float | None] = mapped_column(Float)   
    resilience_details: Mapped[dict | None] = mapped_column(JSON)
    decision_velocity: Mapped[dict | None] = mapped_column(JSON)
    system_diagnosis: Mapped[dict | None] = mapped_column(JSON)
    predictions: Mapped[dict | None] = mapped_column(JSON)
    contradictions: Mapped[list | None] = mapped_column(JSON, default=list)
    positive_signals: Mapped[list | None] = mapped_column(JSON, default=list)
    archetype: Mapped[dict | None] = mapped_column(JSON, default=dict)
    confidence_metrics: Mapped[dict | None] = mapped_column(JSON, default=dict)
    recommendations: Mapped[list | None] = mapped_column(JSON)
    messages_analyzed: Mapped[int | None] = mapped_column()
    decisions_extracted: Mapped[int | None] = mapped_column()
    date_range_start: Mapped[datetime | None] = mapped_column(DateTime)
    date_range_end: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="analyses")
