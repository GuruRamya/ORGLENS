from dataclasses import dataclass
from typing import List
from enum import Enum

class OrgArchetype(str, Enum):
    FAST_AND_POLITICAL = "fast_and_political"     
    SLOW_BUT_HEALTHY = "slow_but_healthy"         
    CHAOTIC_STARTUP = "chaotic_startup"            
    WAITING_FOR_EXODUS = "waiting_for_exodus"      
    HIGH_PERFORMANCE = "high_performance"          
    BUREAUCRATIC = "bureaucratic"                  
    FRAGMENTED = "fragmented"                      
    STABLE_MATURE = "stable_mature"               

@dataclass
class ArchetypeProfile:
    """Classification of org operating mode."""
    
    archetype: OrgArchetype
    name: str
    description: str

    strengths: List[str]
    vulnerabilities: List[str]
    recommended_focus: List[str]
    confidence_pct: int
    classification_reasons: List[str]
    supporting_metrics: dict
    risk_level: str
    trajectory: str   

    def to_dict(self) -> dict:
        return {
            "archetype": self.archetype.value,
            "name": self.name,
            "description": self.description,
            "strengths": self.strengths,
            "vulnerabilities": self.vulnerabilities,
            "recommended_focus": self.recommended_focus,
            "confidence_pct": self.confidence_pct,
            "classification_reasons": self.classification_reasons,
            "supporting_metrics": self.supporting_metrics,
            "risk_level": self.risk_level,
            "trajectory": self.trajectory,
        }

class ArchetypeClassifier:
    """Classify org into archetype based on signals."""
    
    def __init__(self, ml_signals: dict, contradictions: List = None):
        self.ml_signals = ml_signals
        self.contradictions = contradictions or []
        self.velocity_score = ml_signals.get("avg_decision_days", 14)
        self.trust_score = 10 - ml_signals.get("trust_gap_score", 5)
        self.health_score = ml_signals.get("org_health_score", 5)
        self.resilience_score = ml_signals.get("resilience_score", 5)
        self.attrition_risk = ml_signals.get("ml_signals", {}).get("attrition_risk_count", 0)
    
    def classify(self) -> ArchetypeProfile:
        """Determine org archetype."""
        fast = self.velocity_score < 10        
        healthy = self.health_score > 6.5      
        trusted = self.trust_score > 6         
        resilient = self.resilience_score > 6 
        attrition_risk = self.attrition_risk > 2
        
        if fast and healthy and trusted and resilient:
            return self._high_performance()
        
        elif fast and not healthy:
            return self._fast_and_political()
        
        elif not fast and healthy and trusted:
            return self._slow_but_healthy()
        
        elif attrition_risk and self.health_score < 4:
            return self._waiting_for_exodus()
        
        elif not fast and not healthy:
            return self._bureaucratic()
        
        elif self.trust_score < 3:
            return self._fragmented()
        
        elif not fast and healthy:
            return self._stable_mature()
        
        else:
            return self._chaotic_startup()
    
    def _high_performance(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.HIGH_PERFORMANCE,
            name="🏆 High-Performance Organization",
            description="Fast decisions, healthy culture, high trust. Rare. Maintain at all costs.",
            strengths=[
                "Rapid decision-making without politics",
                "Strong employee engagement and trust",
                "Clear authority and ownership",
                "Knowledge is shared, not hoarded",
                "Sustainable pace"
            ],
            vulnerabilities=[
                "Risk of complacency",
                "Potential scalability challenges",
                "Market pressure could break culture"
            ],
            recommended_focus=[
                "Document culture for new hires",
                "Scale without losing speed",
                "Build deeper bench strength",
                "Maintain psychological safety as you grow"
            ],
            confidence_pct=90,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="low",

            trajectory=self._determine_trajectory()
        )
    
    def _build_reasoning(self) -> tuple[list[str], dict]:
        reasons = []

        if self.velocity_score < 10:
            reasons.append(
                f"Decision velocity is fast ({self.velocity_score:.1f} avg days)"
            )
        else:
            reasons.append(
                f"Decision-making is slow ({self.velocity_score:.1f} avg days)"
            )

        if self.trust_score < 5:
            reasons.append(
                f"Trust indicators are weak ({self.trust_score:.1f}/10)"
            )
        else:
            reasons.append(
                f"Trust indicators are healthy ({self.trust_score:.1f}/10)"
            )

        if self.health_score < 5:
            reasons.append(
                f"Organizational health signals are concerning ({self.health_score:.1f}/10)"
            )
        else:
            reasons.append(
                f"Organizational health appears stable ({self.health_score:.1f}/10)"
            )

        if self.attrition_risk > 2:
            reasons.append(
                f"{self.attrition_risk} attrition-risk indicators detected"
            )

        if len(self.contradictions) > 0:
            reasons.append(
                f"{len(self.contradictions)} organizational contradictions detected"
            )

        metrics = {
            "decision_velocity_days": round(self.velocity_score, 1),
            "trust_score": round(self.trust_score, 1),
            "health_score": round(self.health_score, 1),
            "resilience_score": round(self.resilience_score, 1),
            "attrition_risk_signals": self.attrition_risk,
            "contradictions_detected": len(self.contradictions),
        }

        return reasons, metrics
    
    def _determine_trajectory(self) -> str:
        contradiction_count = len(self.contradictions)

        if self.health_score >= 7 and contradiction_count <= 1:
            return "improving"

        if self.health_score <= 4 or contradiction_count >= 3:
            return "declining"

        return "stable"
    
    def _fast_and_political(self) -> ArchetypeProfile:

        reasons, metrics = self._build_reasoning()

        return ArchetypeProfile(
            archetype=OrgArchetype.FAST_AND_POLITICAL,

            name="⚡ Fast but Political",

            description=(
                "The organization moves quickly, but informal influence "
                "appears stronger than transparent merit systems."
            ),

            strengths=[
                "Teams can execute rapidly when priorities are clear",
                "Decision cycles are faster than industry average",
                "High responsiveness during operational pressure",
                "People know how to navigate the system to get things done"
            ],

            vulnerabilities=[
                "Perceived favoritism weakens trust",
                "High performers may disengage if merit feels inconsistent",
                "Political alignment may matter more than contribution",
                "Decisions risk becoming personality-driven instead of principle-driven",
                "Retention risk increases for strong independent talent"
            ],

            recommended_focus=[
                "Standardize promotion and compensation frameworks",
                "Increase transparency around major decisions",
                "Reduce dependency on informal influence networks",
                "Create visible career progression criteria",
                "Protect and retain high-performing individual contributors"
            ],

            confidence_pct=85,

            classification_reasons=reasons,

            supporting_metrics=metrics,

            risk_level="high",

            trajectory=self._determine_trajectory()
        )
    
    def _slow_but_healthy(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.SLOW_BUT_HEALTHY,
            name="🌱 Slow but Healthy",
            description="Decisions take time, but people trust each other and feel safe.",
            strengths=[
                "High psychological safety",
                "Low politics",
                "Strong collaboration",
                "Low attrition",
                "People actually enjoy working here"
            ],
            vulnerabilities=[
                "Can't move fast when market demands it",
                "Risk of becoming irrelevant",
                "Slow growth",
                "May lose talent to faster competitors"
            ],
            recommended_focus=[
                "Streamline decision-making without adding politics",
                "Identify what can be decided faster",
                "Delegate more authority to frontline",
                "Implement async communication",
                "Still maintain culture as you speed up"
            ],
            confidence_pct=80,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="low",

            trajectory=self._determine_trajectory()
        )
    
    def _chaotic_startup(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.CHAOTIC_STARTUP,
            name="🚀 Chaotic Startup",
            description="Low structure, high energy, unclear roles. Works at small scale, breaks at scale.",
            strengths=[
                "Fast iteration",
                "High energy and hustle",
                "Few approval gates",
                "Innovation mindset"
            ],
            vulnerabilities=[
                "Burnout risk",
                "Unclear accountability",
                "No institutional knowledge",
                "Attrition as people get tired",
                "Can't scale past ~50 people"
            ],
            recommended_focus=[
                "Define roles and responsibilities",
                "Establish basic decision authority",
                "Document key decisions and reasoning",
                "Create some structure without killing speed",
                "Succession plan for key people"
            ],
            confidence_pct=75,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="medium",

            trajectory=self._determine_trajectory()
        )
    
    def _waiting_for_exodus(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.WAITING_FOR_EXODUS,
            name="🔴 Waiting for Exodus",
            description="Low health, multiple attrition risks. Crisis mode. Organizational health deteriorating.",
            strengths=[
                "Maybe crisis creates urgency for change",
                "Can't get worse"
            ],
            vulnerabilities=[
                "High attrition risk",
                "Key people leaving soon",
                "Remaining people demoralized",
                "Rapid spiral downward",
                "May not recover"
            ],
            recommended_focus=[
                "IMMEDIATE: Identify & retain critical people",
                "Emergency culture/trust intervention",
                "Leadership change may be necessary",
                "Root cause analysis of dysfunction",
                "Consider org restructure",
                "Transparent communication to all"
            ],
            confidence_pct=85,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="critical",

            trajectory=self._determine_trajectory()
        )
    
    def _bureaucratic(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.BUREAUCRATIC,
            name="📋 Bureaucratic",
            description="Slow and political. Worst of both worlds.",
            strengths=[
                "Maybe stable in the short term?",
                "Clear (if slow) processes"
            ],
            vulnerabilities=[
                "Can't move fast when needed",
                "Politics still alive (slowness doesn't eliminate it)",
                "Talent leaves for better opportunities",
                "Irrelevance in fast-moving markets"
            ],
            recommended_focus=[
                "Pick ONE dimension to fix first (speed or trust)",
                "Remove unnecessary approval gates",
                "Increase transparency to reduce politics",
                "Delegate authority",
                "Rebuild trust through consistent action"
            ],
            confidence_pct=80,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="high",

            trajectory=self._determine_trajectory()
        )
    
    def _fragmented(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.FRAGMENTED,
            name="💔 Fragmented",
            description="Low trust, silos, different subgroups have different agendas.",
            strengths=[
                "Possible pockets of good teams",
                "Clear where problems are"
            ],
            vulnerabilities=[
                "Low collaboration",
                "Politics across silos",
                "Information hoarding",
                "Suboptimal decisions (locally optimal)",
                "High conflict"
            ],
            recommended_focus=[
                "Cross-functional initiatives to build relationships",
                "Unified goals and metrics",
                "Transparency on company direction",
                "Conflict resolution training",
                "Maybe need new leadership to break silos"
            ],
            confidence_pct=75,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="high",

            trajectory=self._determine_trajectory()
        )
    
    def _stable_mature(self) -> ArchetypeProfile:
        return ArchetypeProfile(
            archetype=OrgArchetype.STABLE_MATURE,
            name="🏛️ Stable Mature",
            description="Slow but stable. Not growing fast, but not in crisis.",
            strengths=[
                "Predictable",
                "Low chaos",
                "People generally happy",
                "Profitable, sustainable"
            ],
            vulnerabilities=[
                "Risk of stagnation",
                "May miss market shifts",
                "Talent gets bored",
                "Slow to innovate"
            ],
            recommended_focus=[
                "Inject growth mindset without breaking culture",
                "Enable calculated risk-taking",
                "Career development to retain talent",
                "Innovation time/budget",
                "Stay relevant in market"
            ],
            confidence_pct=85,

            classification_reasons=self._build_reasoning()[0],

            supporting_metrics=self._build_reasoning()[1],

            risk_level="medium",

            trajectory=self._determine_trajectory()
        )
