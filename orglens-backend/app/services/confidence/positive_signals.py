"""
Detect positive signals — what's working well.
Balance the doom machine narrative.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class StrengthCategory(str, Enum):
    RESILIENT_TEAMS = "resilient_teams"
    HEALTHY_MANAGERS = "healthy_managers"
    TRUST_CLUSTERS = "trust_clusters"
    VELOCITY_HOTSPOTS = "velocity_hotspots"
    COLLABORATION_ZONES = "collaboration_zones"
    PSYCHOLOGICAL_SAFETY = "psychological_safety"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    INNOVATION_CULTURE = "innovation_culture"

@dataclass
class PositiveSignal:
    """A strength or positive dynamic detected."""
    category: StrengthCategory
    description: str
    strength_score: float  # 0-10
    evidence: List[str]
    affected_people: int  # Anonymized count
    affected_functions: List[str]
    growth_potential: str  # "high", "medium", "low"
    confidence_pct: float = 0
    
class PositiveSignalDetector:
    """Find what's working. Build on strengths."""
    
    def __init__(self, ml_signals: dict):
        self.ml_signals = ml_signals
        self.person_signals = ml_signals.get("person_signals", {})
    
    def detect_all(self) -> List[PositiveSignal]:
        """Detect all positive signals."""
        signals = []
        signals.extend(self._detect_resilient_teams())
        signals.extend(self._detect_healthy_managers())
        signals.extend(self._detect_trust_clusters())
        signals.extend(self._detect_velocity_hotspots())
        signals.extend(self._detect_collaboration_zones())
        if len(signals) == 0:
            signals.extend(self._generate_fallback_strengths())

        # If still weak, supplement with fallback positives
        elif len(signals) < 2:
            signals.extend(self._generate_fallback_strengths()[:1])

        # Remove duplicates by description
        unique = []
        seen = set()

        for s in signals:
            if s.description not in seen:
                unique.append(s)
                seen.add(s.description)

        return unique
    
    def _detect_resilient_teams(self) -> List[PositiveSignal]:
        """Teams that handle crises without escalating."""
        signals = []
        
        # Look for teams with high sentiment + low escalation
        team_health = {}
        for person_id, psig in self.person_signals.items():
            team = psig.get("team", "Unknown")
            sentiment = psig.get("sentiment_score", 5)
            escalation_count = psig.get("escalation_count", 0)
            
            if team not in team_health:
                team_health[team] = {"sentiment": [], "escalations": []}
            
            team_health[team]["sentiment"].append(sentiment)
            team_health[team]["escalations"].append(escalation_count)
        
        for team, data in team_health.items():
            avg_sentiment = sum(data["sentiment"]) / len(data["sentiment"])
            avg_escalations = sum(data["escalations"]) / len(data["escalations"])
            
            if avg_sentiment >= 6.5 and avg_escalations < 0.5:
                signals.append(PositiveSignal(
                    category=StrengthCategory.RESILIENT_TEAMS,
                    description=f"Team handles challenges without constant escalation",
                    strength_score=avg_sentiment,
                    confidence_pct=80,
                    evidence=[
                        "Low escalation rate despite complex decisions",
                        "Positive sentiment in communication",
                        "Teams resolve issues at their level"
                    ],
                    affected_people=len(data["sentiment"]),
                    affected_functions=[team],
                    growth_potential="high"
                ))
        
        return signals
    
    def _detect_healthy_managers(self) -> List[PositiveSignal]:
        """Managers who delegate and empower."""
        signals = []
        
        for person_id, psig in self.person_signals.items():
            if psig.get("level") in ["Manager", "Director", "VP"]:
                delegation_score = psig.get("delegation_score", 0)
                decision_distribution = psig.get("decision_distribution_breadth", 0)
                
                if delegation_score > 7 and decision_distribution > 0.6:
                    signals.append(PositiveSignal(
                        category=StrengthCategory.HEALTHY_MANAGERS,
                        description=f"Manager empowers team — decisions distributed, not hoarded",
                        strength_score=delegation_score,
                        confidence_pct=75,
                        evidence=[
                            "Delegates decisions to reports",
                            "Doesn't appear in every approval chain",
                            "Team makes calls independently"
                        ],
                        affected_people=int(decision_distribution * 10),
                        affected_functions=[psig.get("department", "cross-functional")],
                        growth_potential="medium"
                    ))
        
        return signals
    
    def _generate_fallback_strengths(self) -> List[PositiveSignal]:
        """
        Even struggling organizations have strengths.
        Generate realistic fallback positives from available behavior.
        """
        fallback = []

        total_people = len(self.person_signals)

        # People still communicating = positive
        if total_people > 0:
            fallback.append(
                PositiveSignal(
                    category=StrengthCategory.COLLABORATION_ZONES,
                    description="Employees are still actively communicating and engaging despite organizational friction",
                    strength_score=5.5,
                    confidence_pct=60,
                    evidence=[
                        "Teams continue collaborating despite detected issues",
                        "Employees openly raise concerns instead of disengaging",
                        "Communication network remains active"
                    ],
                    affected_people=total_people,
                    affected_functions=["cross-functional"],
                    growth_potential="medium"
                )
            )

        # Escalations mean people still care
        escalation_rate = self.ml_signals.get("ml_signals", {}).get("escalation_rate", 0)

        if escalation_rate > 0:
            fallback.append(
                PositiveSignal(
                    category=StrengthCategory.PSYCHOLOGICAL_SAFETY,
                    description="Employees are willing to surface issues instead of silently disengaging",
                    strength_score=6.0,
                    confidence_pct=65,
                    evidence=[
                        "Concerns raised openly in communication channels",
                        "Employees escalate blockers instead of hiding them",
                        "Organizational problems are visible rather than suppressed"
                    ],
                    affected_people=max(3, int(total_people * 0.4)),
                    affected_functions=["cross-functional"],
                    growth_potential="high"
                )
            )

        # Fast orgs usually have execution energy
        avg_decision_days = self.ml_signals.get("avg_decision_days", 14)

        if avg_decision_days < 10:
            fallback.append(
                PositiveSignal(
                    category=StrengthCategory.VELOCITY_HOTSPOTS,
                    description="Organization shows signs of execution speed and operational urgency",
                    strength_score=6.8,
                    confidence_pct=70,
                    evidence=[
                        "Decisions move faster than industry average",
                        "Teams appear action-oriented",
                        "Low operational paralysis detected"
                    ],
                    affected_people=total_people,
                    affected_functions=["cross-functional"],
                    growth_potential="high"
                )
            )

        return fallback
    
    
    def _detect_trust_clusters(self) -> List[PositiveSignal]:
        """Groups of people who naturally work well together."""
        signals = []
        
        # Look for communication clusters with high trust
        collaboration_pairs = self.ml_signals.get("high_trust_pairs", [])
        
        if collaboration_pairs:
            signals.append(PositiveSignal(
                category=StrengthCategory.TRUST_CLUSTERS,
                description=f"Natural collaboration clusters — people trust & coordinate well",
                strength_score=min(len(collaboration_pairs) / 5, 10),
                confidence_pct=75,
                evidence=[
                    f"{len(collaboration_pairs)} pairs with strong mutual support",
                    "Frequent positive interactions",
                    "Decisions aligned without forced alignment"
                ],
                affected_people=len(collaboration_pairs) * 2,
                affected_functions=["cross-functional"],
                growth_potential="high"
            ))
        
        return signals
    
    def _detect_velocity_hotspots(self) -> List[PositiveSignal]:
        """Areas where decisions actually move fast."""
        signals = []
        
        # Look for teams/functions with fast decision cycles
        domain_velocities = self.ml_signals.get("domain_velocities", {})
        
        for domain, velocity_score in domain_velocities.items():
            if velocity_score > 7.5:  # High velocity
                signals.append(PositiveSignal(
                    category=StrengthCategory.VELOCITY_HOTSPOTS,
                    description=f"{domain}: decisions move quickly here",
                    strength_score=velocity_score,
                    confidence_pct=80,
                    evidence=[
                        f"Average decision cycle: <5 days",
                        "Few approval gates",
                        "Clear ownership and authority"
                    ],
                    affected_people=self.ml_signals.get(f"{domain}_people_count", 5),
                    affected_functions=[domain],
                    growth_potential="medium"
                ))
        
        return signals
    
    def _detect_collaboration_zones(self) -> List[PositiveSignal]:
        """Departments that work well together."""
        signals = []
        
        cross_func_quality = self.ml_signals.get("cross_function_quality", {})
        
        for pair, score in cross_func_quality.items():
            if score > 7:
                signals.append(PositiveSignal(
                    category=StrengthCategory.COLLABORATION_ZONES,
                    description=f"Strong collaboration: {pair}",
                    strength_score=score,
                    confidence_pct=75,
                    evidence=[
                        "High communication frequency",
                        "Positive tone in interactions",
                        "Aligned goals and outcomes"
                    ],
                    affected_people=0,  # Cross-functional
                    affected_functions=pair.split(" ↔ "),
                    growth_potential="high"
                ))
        
        return signals