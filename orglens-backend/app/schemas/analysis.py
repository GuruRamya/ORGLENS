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


class UploadType(str, enum.Enum):
    ZIP = "zip"
    CSV_EMPLOYEES = "csv_employees"
    GMAIL_EXPORT = "gmail_export"
    SLACK_EXPORT = "slack_export"
    NARRATIVE_TEXT = "narrative_text"


class UploadResponse(BaseModel):
    upload_id: str
    org_id: UUID
    files_received: list[str]
    records_parsed: int
    status: str
    message: str


class AnalysisTriggerResponse(BaseModel):
    analysis_id: UUID
    org_id: UUID
    status: str
    message: str
    estimated_minutes: int


class AnalysisStatusResponse(BaseModel):
    analysis_id: UUID
    status: str
    progress_percent: Optional[int]
    message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class OrgHealthCard(BaseModel):
    org_health_score: float
    health_breakdown: dict
    grade: str         
    summary: str


class TrustGapCard(BaseModel):
    trust_gap_score: float
    severity: str       
    claims_analyzed: int
    top_gaps: list[dict]
    trend: str


class PowerStructureCard(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    clusters: list[dict]
    hidden_powers: int  
    ignored_authorities: int


class InfluencerCard(BaseModel):
    influencers: list[dict]
    total_analyzed: int


class GatekeeperCard(BaseModel):
    gatekeepers: list[dict]
    decision_gatekeepers: int
    information_gatekeepers: int


class ResilienceCard(BaseModel):
    resilience_score: float
    risk_level: str
    single_points_of_failure: list[dict]
    knowledge_silos: list[dict]


class DecisionVelocityCard(BaseModel):
    avg_days: float
    benchmark: str      
    trend: str
    trend_data: list[dict]
    bottlenecks: list[dict]


class DiagnosisCard(BaseModel):
    root_causes: list[dict]
    who_profits: list[dict]
    predicted_if_unchanged: str
    dysfunction_cost_annual: Optional[str]


class PredictionsCard(BaseModel):
    attrition_risks: list[dict]
    decision_reversal_risks: list[dict]
    velocity_forecast: str
    health_forecast_6mo: float


class RecommendationsCard(BaseModel):
    recommendations: list[dict]
    quick_wins: list[dict]   
    total_potential_savings: Optional[str]


class FullDashboardResponse(BaseModel):
    analysis_id: UUID
    org_id: UUID
    org_name: str
    analyzed_at: datetime
    messages_analyzed: int
    decisions_extracted: int
    date_range: dict

  
    org_health: OrgHealthCard
    trust_gap: TrustGapCard
    power_structure: PowerStructureCard
    top_influencers: InfluencerCard
    gatekeepers: GatekeeperCard
    resilience: ResilienceCard
    decision_velocity: DecisionVelocityCard
    system_diagnosis: DiagnosisCard
    predictions: PredictionsCard
    recommendations: RecommendationsCard
    contradictions: list[dict] = []
    positive_signals: list[dict] = []
    archetype: dict = {}
    confidence_metrics: dict = {}
