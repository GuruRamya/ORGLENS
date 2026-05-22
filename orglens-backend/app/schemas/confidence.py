from pydantic import BaseModel
from typing import Dict, List, Optional

class SignalFindingSchema(BaseModel):
    signal: str
    strength: str
    observed: float
    confidence: str
    confidence_pct: int
    evidence_count: int
    min_evidence_needed: int
    needs_more_evidence: int
    actionable: bool
    description: str
    recommendation: str

class CoverageSchema(BaseModel):
    function: str
    coverage_pct: int
    confidence: str
    status: str  # "good", "weak", "critical"

class DataQualityCardSchema(BaseModel):
    """Response for the Data Quality & Confidence card."""
    overall_confidence: str  # "low", "medium", "high", etc.
    overall_confidence_pct: int
    total_messages: int
    total_employees: int
    messages_per_person: float
    date_range_days: int
    reasoning: list[str] = []
    weak_areas: list[dict] = []
    
    # Coverage
    coverage_by_function: Dict[str, int]  # {"Engineering": 85, "Finance": 15}
    coverage_by_level: Dict[str, int]     # {"C-Suite": 95, "IC": 40}
    
    # Data quality warnings
    warnings: List[str]
    
    # Findings that need more data
    signals_pending_data: List[SignalFindingSchema]
    
    # Overall assessment
    data_sufficiency_summary: str
    recommendation: str

    class Config:
        from_attributes = True