from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
import enum


class OrgCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    size_estimate: Optional[int] = None
    mission_statement: Optional[str] = None


class OrgResponse(BaseModel):
    id: UUID
    name: str
    industry: Optional[str]
    size_estimate: Optional[int]
    slack_connected: bool
    gmail_connected: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeCreate(BaseModel):
    name: str
    email: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    manager_name: Optional[str] = None  
    tenure_months: Optional[int] = None


class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    email: Optional[str]
    title: Optional[str]
    department: Optional[str]
    level: Optional[str]
    influence_score: Optional[float]
    formal_authority_score: Optional[float]
    resilience_impact_score: Optional[float]

    model_config = {"from_attributes": True}
