"""
Confidence & data quality framework.
Every finding tagged with confidence level.
Nothing reported without data sufficiency check.
"""
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from loguru import logger

class ConfidenceLevel(str, Enum):
    CRITICAL = "critical"     
    LOW = "low"                
    MEDIUM = "medium"          
    HIGH = "high"              
    VERY_HIGH = "very_high"    

class SignalStrength(str, Enum):
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class ConfidenceMetrics:
    """Measure data quality for the analysis."""
    total_messages: int
    total_employees: int
    messages_per_person: float
    date_range_days: int
    coverage_by_function: Dict[str, float]  
    coverage_by_level: Dict[str, float]
    confidence_breakdown: Dict[str, float]
    strengths_detected: List[str]
    limitations_detected: List[str]
    recommended_data_improvements: List[str]
    
    def calculate_base_confidence(self) -> float:
        """
        Confidence formula based on:
        - Message volume (more = better signal)
        - Coverage balance (balanced > skewed)
        - Time range (longer = more patterns)
        - Employee-to-message ratio
        """
        volume_score = min(self.messages_per_person / 10, 1.0)
        
        func_scores = list(self.coverage_by_function.values())
        if func_scores:
            well_covered = sum(1 for s in func_scores if s >= 0.3)
            coverage_balance = well_covered / len(func_scores)
        else:
            coverage_balance = 0
        
        time_score = min(self.date_range_days / 30, 1.0)
        if self.total_messages < 20:
            volume_score *= 0.5
        confidence = (volume_score * 0.4 + coverage_balance * 0.35 + time_score * 0.25)
        return max(0, min(confidence, 1.0))
    
    def get_confidence_breakdown(self) -> Dict[str, float]:
        """
        Explain how confidence was calculated.
        """

        volume_score = min(self.messages_per_person / 10, 1.0)
        func_scores = list(self.coverage_by_function.values())

        if func_scores:
            well_covered = sum(1 for s in func_scores if s >= 0.3)
            coverage_balance = well_covered / len(func_scores)
        else:
            coverage_balance = 0

        time_score = min(self.date_range_days / 30, 1.0)

        return {
            "message_volume": round(volume_score * 100, 1),
            "department_coverage": round(coverage_balance * 100, 1),
            "time_range_quality": round(time_score * 100, 1),
        }
    
    def get_strengths(self) -> List[str]:
        """
        Explain what makes this dataset reliable.
        """

        strengths = []
        if self.total_messages >= 50:
            strengths.append(
                f"Message volume is reasonably strong ({self.total_messages} messages)"
            )
        if self.messages_per_person >= 5:
            strengths.append(
                f"Healthy communication density ({self.messages_per_person:.1f} msgs/person)"
            )
        if self.date_range_days >= 30:
            strengths.append(
                f"Time coverage spans {self.date_range_days} days"
            )
        if len(self.coverage_by_function) >= 3:
            strengths.append(
                "Multiple departments represented in analysis"
            )
        return strengths
    
    def get_limitations(self) -> List[str]:
        """
        Explain what weakens confidence.
        """
        limitations = []
        if self.total_messages < 50:
            limitations.append(
                "Limited message volume reduces statistical reliability"
            )
        if self.messages_per_person < 3:
            limitations.append(
                "Low communication density may hide patterns"
            )
        if self.date_range_days < 15:
            limitations.append(
                "Short observation window limits trend detection"
            )
        low_coverage = [
            func
            for func, pct in self.coverage_by_function.items()
            if pct < 0.15
        ]
        if low_coverage:
            limitations.append(
                f"Underrepresented departments: {', '.join(low_coverage)}"
            )
        return limitations
    def get_improvement_recommendations(self) -> List[str]:
        """
        Tell user how to improve future confidence.
        """
        recs = []
        if self.total_messages < 100:
            recs.append(
                "Collect more communication samples across teams"
            )
        if self.date_range_days < 30:
            recs.append(
                "Analyze at least 30 days of organizational activity"
            )
        if self.messages_per_person < 5:
            recs.append(
                "Increase participation coverage across employees"
            )
        sparse_functions = [
            func
            for func, pct in self.coverage_by_function.items()
            if pct < 0.3
        ]
        if sparse_functions:
            recs.append(
                f"Increase representation from: {', '.join(sparse_functions)}"
            )
        return recs

    @property
    def overall_confidence(self) -> str:
        """Return confidence level as enum string."""
        return self.get_confidence_level().value

    @property
    def overall_confidence_pct(self) -> int:
        """Return confidence as percentage."""
        return int(self.calculate_base_confidence() * 100)

    @property
    def warnings(self) -> List[str]:
        """Return data quality warnings."""
        return self.get_warnings()
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Map confidence score to level."""
        conf = self.calculate_base_confidence()
        if conf < 0.3:
            return ConfidenceLevel.CRITICAL
        elif conf < 0.5:
            return ConfidenceLevel.LOW
        elif conf < 0.7:
            return ConfidenceLevel.MEDIUM
        elif conf < 0.85:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.VERY_HIGH
    
    def get_warnings(self) -> List[str]:
        """Generate warnings about data quality."""
        warnings = []
        
        if self.total_messages < 50:
            warnings.append(f"⚠️ Limited message volume ({self.total_messages} messages). Findings may be skewed by small sample.")
        
        if self.messages_per_person < 3:
            warnings.append(f"⚠️ Low message density ({self.messages_per_person:.1f} msgs/person). Communication patterns may be incomplete.")
        
        if self.date_range_days < 15:
            warnings.append(f"⚠️ Short time range ({self.date_range_days} days). Patterns need 30+ days to be reliable.")
        
        for func, coverage in self.coverage_by_function.items():
            if coverage < 0.15:
                warnings.append(f"⚠️ {func}: Only {coverage*100:.0f}% coverage. Conclusions unreliable.")
        
        return warnings

@dataclass
class SignalFinding:
    """
    A single finding with confidence baked in.
    Never report without confidence level.
    """
    signal_name: str              
    signal_strength: SignalStrength
    observed_value: float
    confidence_level: ConfidenceLevel
    confidence_pct: float         
    evidence_count: int          
    min_evidence_for_action: int  
    description: str
    recommendation: str
    
    def is_actionable(self) -> bool:
        """Only act if confidence > 65%."""
        return self.confidence_pct >= 65
    
    def to_dict(self) -> dict:
        """Format for API response."""
        return {
            "signal": self.signal_name,
            "strength": self.signal_strength.value,
            "observed": round(self.observed_value, 2),
            "confidence": self.confidence_level.value,
            "confidence_pct": int(self.confidence_pct),
            "evidence_count": self.evidence_count,
            "min_evidence_needed": self.min_evidence_for_action,
            "needs_more_evidence": max(0, self.min_evidence_for_action - self.evidence_count),
            "actionable": self.is_actionable(),
            "description": self.description,
            "recommendation": self.recommendation,
        }

class ConfidenceCalculator:
    """Compute confidence metrics from org data."""
    
    @staticmethod
    def from_ml_signals(ml_signals: dict) -> ConfidenceMetrics:
        """
        Build ConfidenceMetrics from the ML signals output.
        
        ml_signals contains:
        - message_count
        - employee_count
        - person_signals (by person)
        - all the signal categories
        """
        if not ml_signals:
            logger.warning("⚠️ ml_signals is None or empty. Using safe defaults.")

            ml_signals = {
                "message_count": 0,
                "employee_count": 0,
                "date_range": {},
                "person_signals": {}
            }
        
        total_messages = ml_signals.get("message_count", 0)
        total_employees = ml_signals.get("employee_count", 0)
        messages_per_person = total_messages / max(total_employees, 1)
        date_range = ml_signals.get("date_range") or {}
        start_str = date_range.get("start")
        end_str = date_range.get("end")
        date_range_days = 30 
        
        if start_str and end_str:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                date_range_days = (end - start).days
            except:
                pass
        
        person_signals = (ml_signals or {}).get("person_signals") or {}
        dept_coverage = {}
        if person_signals:
            total = len(person_signals)
            by_dept = {}
            for name, signals in person_signals.items():
                dept = signals.get("department", "Unknown")
                if dept not in by_dept:
                    by_dept[dept] = 0
                by_dept[dept] += 1
            
            for dept, count in by_dept.items():
                dept_coverage[dept] = count / total if total > 0 else 0
        level_coverage = {}
        if person_signals:
            total = len(person_signals)
            by_level = {}
            for name, signals in person_signals.items():
                level = signals.get("level", "Unknown")
                if level not in by_level:
                    by_level[level] = 0
                by_level[level] += 1
            
            for level, count in by_level.items():
                level_coverage[level] = count / total if total > 0 else 0
        
        metrics = ConfidenceMetrics(
        total_messages=total_messages,
        total_employees=total_employees,
        messages_per_person=messages_per_person,
        date_range_days=date_range_days,
        coverage_by_function=dept_coverage,
        coverage_by_level=level_coverage,
        confidence_breakdown={},
        strengths_detected=[],
        limitations_detected=[],
        recommended_data_improvements=[],
    )

        metrics.confidence_breakdown = metrics.get_confidence_breakdown()
        metrics.strengths_detected = metrics.get_strengths()
        metrics.limitations_detected = metrics.get_limitations()
        metrics.recommended_data_improvements = metrics.get_improvement_recommendations()

        return metrics
