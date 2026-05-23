import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Float, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class MessageSource(str, enum.Enum):
    SLACK = "slack"
    GMAIL = "gmail"
    UPLOAD = "upload"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    source: Mapped[MessageSource] = mapped_column(SAEnum(MessageSource), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))  
    sender_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"))
    sender_raw: Mapped[str | None] = mapped_column(String(255))  
    channel_or_thread: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    contains_decision: Mapped[bool | None] = mapped_column(default=False)
    contains_objection: Mapped[bool | None] = mapped_column(default=False)
    sentiment_score: Mapped[float | None] = mapped_column(Float)   
    urgency_score: Mapped[float | None] = mapped_column(Float)    
    decision_keywords: Mapped[list | None] = mapped_column(JSON)   
    topics: Mapped[list | None] = mapped_column(JSON)              
    influence_signal: Mapped[float | None] = mapped_column(Float)  
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="messages")
    sender: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[sender_id])

class DecisionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVERSED = "reversed"
    STALLED = "stalled"


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)   
    domain: Mapped[str | None] = mapped_column(String(100))           
    status: Mapped[DecisionStatus] = mapped_column(SAEnum(DecisionStatus), nullable=False)
    proposed_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolution_days: Mapped[float | None] = mapped_column(Float)      
    proposer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"))
    supporters: Mapped[list | None] = mapped_column(JSON)    
    objectors: Mapped[list | None] = mapped_column(JSON)    
    deciders: Mapped[list | None] = mapped_column(JSON)      
    followed_objector: Mapped[bool | None] = mapped_column()  
    power_play_score: Mapped[float | None] = mapped_column(Float)  
    source_message_ids: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="decisions")
    proposer: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[proposer_id])
