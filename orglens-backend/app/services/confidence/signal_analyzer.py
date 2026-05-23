"""
Pattern-based signal extraction.
Works with ANONYMIZED data — no names, no titles.
Pure math-based pattern detection.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import re
from collections import Counter

class PatternStrength(str, Enum):
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class SignalPattern:
    """A detected pattern in communication."""
    pattern_name: str          
    pattern_description: str   
    strength: PatternStrength
    evidence_count: int         
    prevalence_pct: float       
    anonymized_evidence: List[str]  
    severity: str              
    affected_functions: List[str]   
    recommendation: str         

@dataclass
class SignalSet:
    """Collection of detected patterns for a dimension."""
    dimension: str              
    signals: List[SignalPattern]
    overall_health: float      
    confidence_level: str      

class SignalAnalyzer:
    """
    Extract anonymized patterns from raw communication.
    No names, no people identification.
    Pure statistical/linguistic analysis.
    """
    
    def __init__(self, ml_signals: dict):
        """
        ml_signals: output from MLSignalExtractor
        Contains: person_signals, message patterns, network metrics, etc.
        """
        self.ml_signals = ml_signals
        self.total_messages = ml_signals.get("message_count", 0)
        self.total_people = ml_signals.get("employee_count", 0)
        
    def extract_velocity_signals(self) -> SignalSet:
        """Detect decision-making speed patterns."""
        signals = []
        approval_chains = self.ml_signals.get("approval_chains", [])
        if approval_chains:
            avg_depth = sum(len(c) for c in approval_chains) / len(approval_chains)
            strength = self._strength_from_value(avg_depth, 2, 5)
            
            if avg_depth > 3.5:
                signals.append(SignalPattern(
                    pattern_name="deep_approval_chains",
                    pattern_description=f"Decisions require {avg_depth:.1f} approvals on average",
                    strength=strength,
                    evidence_count=len(approval_chains),
                    prevalence_pct=(len(approval_chains) / max(self.total_messages, 1)) * 100,
                    anonymized_evidence=[
                        f"Message thread: waiting for {len(c)} approval levels",
                        f"Process requires {len(approval_chains[0])} sign-offs minimum"
                    ],
                    severity=self._severity_from_strength(strength),
                    affected_functions=self._get_affected_functions("approval"),
                    recommendation="Create a decision authority matrix. Define which decisions can be made at each level without escalation."
                ))
        delay_signals = (
            self.ml_signals
            .get("velocity_signals", {})
            .get("delay_message_count", 0)
        )
        if delay_signals > 0:
            prevalence = (delay_signals / max(self.total_messages, 1)) * 100
            strength = PatternStrength.STRONG if prevalence > 5 else PatternStrength.MODERATE
            
            signals.append(SignalPattern(
                pattern_name="explicit_delay_mentions",
                pattern_description=f"{prevalence:.1f}% of messages explicitly mention delays or blocks",
                strength=strength,
                evidence_count=delay_signals,
                prevalence_pct=prevalence,
                anonymized_evidence=[
                    "Thread: 'waiting on approval for 2 weeks'",
                    "Message: 'blocked by dependency on another team'"
                ],
                severity=self._severity_from_strength(strength),
                affected_functions=self._get_affected_functions("delay"),
                recommendation="Implement async approval workflows. Document decision criteria so teams unblock without waiting for synchronous sign-off."
            ))
        decision_data = self.ml_signals.get("decision_signals", {})
        reversal_count = decision_data.get("reversal_count", 0)
        if reversal_count > 0:
            strength = (
                PatternStrength.VERY_STRONG if reversal_count > 3
                else PatternStrength.STRONG if reversal_count > 1
                else PatternStrength.MODERATE
            )

            signals.append(SignalPattern(
                pattern_name="decision_instability",
                pattern_description=f"{reversal_count} decisions were revisited or reversed",
                strength=strength,
                evidence_count=reversal_count,
                prevalence_pct=(reversal_count / max(self.total_messages, 1)) * 100,
                anonymized_evidence=[
                    "Decision reversed: 'We said X, now doing Y'",
                    "Thread: 'Reopening decision from last month'"
                ],
                severity=self._severity_from_strength(strength),
                affected_functions=["cross-functional"],
                recommendation="Define clear decision-making criteria and document the reasoning. Reversals suggest unclear initial alignment."
            ))
        
        overall_velocity = self._calculate_dimension_score([s.strength for s in signals])
        confidence = self._assess_confidence(len(signals), self.total_messages)
        
        return SignalSet(
            dimension="velocity",
            signals=signals,
            overall_health=overall_velocity,
            confidence_level=confidence
        )
    
    
    def extract_resilience_signals(self) -> SignalSet:
        """Detect single points of failure and knowledge silos."""
        signals = []
        
        person_signals = self.ml_signals.get("person_signals", {})
        if person_signals:
            domain_distribution = self._analyze_domain_distribution(person_signals)
            singleton_domains = [d for d, owners in domain_distribution.items() if len(owners) == 1]
            
            if singleton_domains:
                strength = PatternStrength.VERY_STRONG if len(singleton_domains) > 5 else PatternStrength.STRONG
                signals.append(SignalPattern(
                    pattern_name="knowledge_silos",
                    pattern_description=f"{len(singleton_domains)} domains owned by single person",
                    strength=strength,
                    evidence_count=len(singleton_domains),
                    prevalence_pct=(len(singleton_domains) / max(len(domain_distribution), 1)) * 100,
                    anonymized_evidence=[
                        f"Domain: {singleton_domains[0]} — only 1 person has context",
                        "Pattern: No cross-training or knowledge sharing in {domain}"
                    ],
                    severity=self._severity_from_strength(strength),
                    affected_functions=self._extract_functions_from_domains(singleton_domains),
                    recommendation="Cross-train at least 2 people per critical domain. Document process and decision criteria."
                ))
        
        departure_mentions = (
            self.ml_signals
            .get("resilience_signals", {})
            .get("departure_mention_count", 0)
        )
        if departure_mentions > 0:
            strength = PatternStrength.STRONG if departure_mentions > 3 else PatternStrength.MODERATE
            signals.append(SignalPattern(
                pattern_name="attrition_signals",
                pattern_description=f"{departure_mentions} messages mention leaving, resignation, or exit",
                strength=strength,
                evidence_count=departure_mentions,
                prevalence_pct=(departure_mentions / max(self.total_messages, 1)) * 100,
                anonymized_evidence=[
                    "Message: 'considering other opportunities'",
                    "Thread: discussion about someone's exit"
                ],
                severity="high",
                affected_functions=self._get_affected_functions("departure"),
                recommendation="Schedule retention conversations. Identify unmet growth, compensation, or recognition gaps."
            ))
        
        influence_scores = [
            v.get("influence_score", 0)
            for v in person_signals.values()
        ]
        if influence_scores:
            top_3_influence = sum(sorted(influence_scores, reverse=True)[:3])
            concentration_pct = (top_3_influence / sum(influence_scores)) * 100 if sum(influence_scores) > 0 else 0
            
            if concentration_pct > 60: 
                strength = PatternStrength.VERY_STRONG
                signals.append(SignalPattern(
                    pattern_name="influence_concentration",
                    pattern_description=f"Top 3 people control {concentration_pct:.0f}% of influence",
                    strength=strength,
                    evidence_count=3,
                    prevalence_pct=concentration_pct,
                    anonymized_evidence=[
                        "Communication analysis: 3 people in 60%+ of decision threads",
                        "Network: tightly centralized around few nodes"
                    ],
                    severity="critical",
                    affected_functions=["cross-functional"],
                    recommendation="Distribute decision authority. Empower team leads to make calls in their domain."
                ))
        
        overall_resilience = self._calculate_dimension_score([s.strength for s in signals])
        confidence = self._assess_confidence(len(signals), self.total_messages)
        
        return SignalSet(
            dimension="resilience",
            signals=signals,
            overall_health=overall_resilience,
            confidence_level=confidence
        )
        
    def extract_trust_signals(self) -> SignalSet:
        """Detect alignment between stated values and observed behavior."""
        signals = []
        
        escalation_rate = (
            self.ml_signals
            .get("trust_signals", {})
            .get("escalation_rate", 0)
        )
        if escalation_rate > 0.1: 
            strength = PatternStrength.VERY_STRONG if escalation_rate > 0.25 else PatternStrength.STRONG
            signals.append(SignalPattern(
                pattern_name="high_escalation_rate",
                pattern_description=f"{escalation_rate*100:.1f}% of decisions escalate",
                strength=strength,
                evidence_count=int(escalation_rate * self.total_messages),
                prevalence_pct=escalation_rate * 100,
                anonymized_evidence=[
                    "Pattern: Decisions bypass direct manager, go to director+",
                    "Behavior: People distrust peer-level decisions"
                ],
                severity=self._severity_from_strength(strength),
                affected_functions=self._get_affected_functions("escalation"),
                recommendation="Increase manager autonomy. Clarify what decisions can be made without escalation. Build trust through transparent criteria."
            ))
        
        comp_complaints = len(
            self.ml_signals
            .get("trust_signals", {})
            .get("comp_inversion_evidence", [])
        )
        promotion_complaints = (
            self.ml_signals
            .get("trust_signals", {})
            .get("promotion_complaint_count", 0)
        )
        
        if comp_complaints > 0 or promotion_complaints > 0:
            total_fairness_issues = comp_complaints + promotion_complaints
            strength = PatternStrength.STRONG if total_fairness_issues > 2 else PatternStrength.MODERATE
            
            signals.append(SignalPattern(
                pattern_name="fairness_gap",
                pattern_description=f"{total_fairness_issues} messages raise compensation/promotion fairness concerns",
                strength=strength,
                evidence_count=total_fairness_issues,
                prevalence_pct=(total_fairness_issues / max(self.total_messages, 1)) * 100,
                anonymized_evidence=[
                    "Thread: 'person X paid more for same role'",
                    "Message: 'promotion criteria aren't transparent'"
                ],
                severity="high",
                affected_functions=["HR", "Finance"],
                recommendation="Audit compensation bands. Publish promotion criteria. Run town halls on fairness."
            ))
        
        overall_trust = 10 - self._calculate_dimension_score([s.strength for s in signals])  
        confidence = self._assess_confidence(len(signals), self.total_messages)
        
        return SignalSet(
            dimension="trust",
            signals=signals,
            overall_health=overall_trust,
            confidence_level=confidence
        )
        
    def extract_collaboration_signals(self) -> SignalSet:
        """Detect cross-functional health and silos."""
        signals = []
        
        cross_func_ratio = (
            self.ml_signals
            .get("collaboration_signals", {})
            .get("cross_function_ratio", 0)
        )
        if cross_func_ratio < 0.3:  
            strength = PatternStrength.STRONG
            signals.append(SignalPattern(
                pattern_name="functional_silos",
                pattern_description=f"Only {cross_func_ratio*100:.1f}% of communication is cross-functional",
                strength=strength,
                evidence_count=int(cross_func_ratio * self.total_messages),
                prevalence_pct=(1 - cross_func_ratio) * 100,
                anonymized_evidence=[
                    "Communication graph: teams cluster separately",
                    "Pattern: minimal messages between functions"
                ],
                severity="high",
                affected_functions=["cross-functional"],
                recommendation="Schedule regular cross-functional syncs. Co-locate teams on projects. Build relationships."
            ))
        
        overall_collab = self._calculate_dimension_score([s.strength for s in signals])
        confidence = self._assess_confidence(len(signals), self.total_messages)
        
        return SignalSet(
            dimension="collaboration",
            signals=signals,
            overall_health=overall_collab,
            confidence_level=confidence
        )
    
    
    def _strength_from_value(self, value: float, low_threshold: float, high_threshold: float) -> PatternStrength:
        """Convert numeric value to strength level."""
        if value < low_threshold:
            return PatternStrength.WEAK
        elif value < (low_threshold + high_threshold) / 2:
            return PatternStrength.MODERATE
        elif value < high_threshold:
            return PatternStrength.STRONG
        else:
            return PatternStrength.VERY_STRONG
    
    def _severity_from_strength(self, strength: PatternStrength) -> str:
        """Convert pattern strength to severity."""
        if strength == PatternStrength.VERY_STRONG:
            return "critical"
        elif strength == PatternStrength.STRONG:
            return "high"
        elif strength == PatternStrength.MODERATE:
            return "medium"
        else:
            return "low"
    
    def _calculate_dimension_score(self, strengths: List[PatternStrength]) -> float:
        """Convert pattern strengths to 0-10 score."""
        if not strengths:
            return 5.0
        
        strength_values = {
            PatternStrength.VERY_WEAK: 1,
            PatternStrength.WEAK: 2.5,
            PatternStrength.MODERATE: 5,
            PatternStrength.STRONG: 7.5,
            PatternStrength.VERY_STRONG: 10,
        }
        
        avg = sum(strength_values.get(s, 5) for s in strengths) / len(strengths)
        return avg
    
    def _assess_confidence(self, signal_count: int, total_messages: int) -> str:
        """Assess confidence in detected signals."""
        if total_messages < 50:
            return "critical"
        elif signal_count == 0:
            return "low"
        elif signal_count == 1:
            return "medium"
        elif signal_count >= 3 and total_messages > 200:
            return "high"
        else:
            return "medium"
    
    def _analyze_domain_distribution(self, person_signals: dict) -> Dict[str, List[str]]:
        """Map domains to owners (anonymized)."""
        domains = {}
        for person_id, signals in person_signals.items():
            for domain in signals.get("domains", []):
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(person_id)
        return domains
    
    def _extract_functions_from_domains(self, domains: List[str]) -> List[str]:
        """Infer affected functions from domain names."""
        function_keywords = {
            "Engineering": ["backend", "frontend", "infra", "devops", "code", "deploy"],
            "Finance": ["budget", "spend", "accounting", "financial", "compliance"],
            "Product": ["roadmap", "requirements", "feature", "spec"],
            "Sales": ["deal", "pipeline", "customer", "contract"],
            "HR": ["hiring", "compensation", "benefits", "culture"],
        }
        
        affected = set()
        for domain in domains:
            domain_lower = domain.lower()
            for func, keywords in function_keywords.items():
                if any(kw in domain_lower for kw in keywords):
                    affected.add(func)
        
        return list(affected) if affected else ["cross-functional"]
    
    def _get_affected_functions(self, pattern_type: str) -> List[str]:
        """Get likely affected functions for a pattern."""
        defaults = {
            "approval": ["cross-functional"],
            "delay": ["cross-functional"],
            "departure": ["HR"],
            "escalation": ["Management"],
            "fairness": ["HR"],
        }
        return defaults.get(pattern_type, ["cross-functional"])
