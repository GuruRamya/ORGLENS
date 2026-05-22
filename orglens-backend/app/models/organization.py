import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100))
    size_estimate: Mapped[int | None] = mapped_column(Integer)  # employee count

    # Narrative/Claims data
    mission_statement: Mapped[str | None] = mapped_column(Text)
    stated_values: Mapped[dict | None] = mapped_column(JSON)   # {"values": ["transparency", ...]}
    leadership_claims: Mapped[dict | None] = mapped_column(JSON)  # extracted from CEO emails etc.

    # Integration status
    slack_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    gmail_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    slack_access_token: Mapped[str | None] = mapped_column(Text)  # encrypted in prod
    gmail_access_token: Mapped[str | None] = mapped_column(Text)  # encrypted in prod

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deletable: Mapped[bool] = mapped_column(Boolean, default=True)
    # Relationships
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="organization", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="organization", cascade="all, delete-orphan")
    decisions: Mapped[list["Decision"]] = relationship("Decision", back_populates="organization", cascade="all, delete-orphan")
    analyses: Mapped[list["AnalysisReport"]] = relationship("AnalysisReport", back_populates="organization", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    slack_user_id: Mapped[str | None] = mapped_column(String(100))

    # Formal structure
    title: Mapped[str | None] = mapped_column(String(255))
    department: Mapped[str | None] = mapped_column(String(100))
    level: Mapped[str | None] = mapped_column(String(50))   # IC, Manager, Director, VP, C-Suite
    manager_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"))
    tenure_months: Mapped[int | None] = mapped_column(Integer)

    # Computed influence metrics (updated after each analysis)
    influence_score: Mapped[float | None] = mapped_column(Float)          # 0-10
    formal_authority_score: Mapped[float | None] = mapped_column(Float)   # 0-10
    information_control_score: Mapped[float | None] = mapped_column(Float) # 0-10
    resilience_impact_score: Mapped[float | None] = mapped_column(Float)   # if this person leaves, impact 0-10
    credibility_score: Mapped[float | None] = mapped_column(Float)         # how often their blocks improve outcomes

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="employees")
    reports: Mapped[list["Employee"]] = relationship("Employee", foreign_keys=[manager_id])