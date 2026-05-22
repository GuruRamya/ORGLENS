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

    # Message data
    source: Mapped[MessageSource] = mapped_column(SAEnum(MessageSource), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))  # Slack ts, Gmail message id
    sender_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"))
    sender_raw: Mapped[str | None] = mapped_column(String(255))   # raw name/email before resolution
    channel_or_thread: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # NLP extracted fields
    contains_decision: Mapped[bool | None] = mapped_column(default=False)
    contains_objection: Mapped[bool | None] = mapped_column(default=False)
    sentiment_score: Mapped[float | None] = mapped_column(Float)   # -1 to 1
    urgency_score: Mapped[float | None] = mapped_column(Float)     # 0-1
    decision_keywords: Mapped[list | None] = mapped_column(JSON)   # ["approved", "rejected", ...]
    topics: Mapped[list | None] = mapped_column(JSON)              # ["hiring", "budget", ...]
    influence_signal: Mapped[float | None] = mapped_column(Float)  # 0-1, how influential is this message?

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
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

    # Decision data
    title: Mapped[str] = mapped_column(String(500), nullable=False)   # NLP-extracted summary
    domain: Mapped[str | None] = mapped_column(String(100))           # hiring, budget, product, process
    status: Mapped[DecisionStatus] = mapped_column(SAEnum(DecisionStatus), nullable=False)
    proposed_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolution_days: Mapped[float | None] = mapped_column(Float)       # days to decision

    # Who was involved (stored as JSON lists of employee IDs)
    proposer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"))
    supporters: Mapped[list | None] = mapped_column(JSON)    # [employee_id, ...]
    objectors: Mapped[list | None] = mapped_column(JSON)     # [employee_id, ...]
    deciders: Mapped[list | None] = mapped_column(JSON)      # who actually made the call

    # Influence metrics
    followed_objector: Mapped[bool | None] = mapped_column()  # did the final decision follow objectors?
    power_play_score: Mapped[float | None] = mapped_column(Float)  # 0-1, was this a power play vs. genuine conviction?

    # Source messages that led to this decision
    source_message_ids: Mapped[list | None] = mapped_column(JSON)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="decisions")
    proposer: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[proposer_id])