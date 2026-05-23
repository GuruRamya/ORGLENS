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
    status: str  

class DataQualityCardSchema(BaseModel):
    overall_confidence: str 
    overall_confidence_pct: int
    total_messages: int
    total_employees: int
    messages_per_person: float
    date_range_days: int
    reasoning: list[str] = []
    weak_areas: list[dict] = []
    
    
    coverage_by_function: Dict[str, int]  
    coverage_by_level: Dict[str, int]     
    
    warnings: List[str]
    
    signals_pending_data: List[SignalFindingSchema]
    
    data_sufficiency_summary: str
    recommendation: str

    class Config:
        from_attributes = True
