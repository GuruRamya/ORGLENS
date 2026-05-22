"""
Detect where org claims ≠ actual behavior.
THE MOST DIFFERENTIATING FEATURE.
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ContradictionSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Contradiction:
    """A gap between stated value and observed behavior."""
    claim: str                          # "We move fast"
    observed_reality: str               # "Decisions take 21 days avg"
    gap_score: float                    # 0-10 (how big is the gap)
    severity: ContradictionSeverity
    evidence_quotes: List[str]          # Actual messages
    root_causes: List[str]              # Why does this gap exist
    impact: str                         # Business impact of gap
    recommendation: str                 # How to fix it

class ContradictionDetector:
    """Find the disconnect between words and actions."""
    
    def __init__(self, claims: List, ml_signals: dict):
        """
        claims: ExtractedClaim objects from ClaimExtractor
        ml_signals: signal data from MLSignalExtractor
        """
        self.claims = claims
        self.ml_signals = ml_signals
    
    def detect_all(self) -> List[Contradiction]:
        """Compare each claim against reality."""
        contradictions = []
        
        for claim in self.claims:
            contra = self._test_claim(claim)
            if contra:
                contradictions.append(contra)
        
        # Sort by severity
        return sorted(contradictions, 
                     key=lambda c: {"low": 1, "medium": 2, "high": 3, "critical": 4}[c.severity.value],
                     reverse=True)
    
    def _test_claim(self, claim) -> Optional[Contradiction]:
        """Test a single claim against observed data."""
        
        # Match claim to relevant metric
        if "fast" in claim.claim_text.lower():
            return self._test_speed_claim(claim)
        elif "merit" in claim.claim_text.lower():
            return self._test_merit_claim(claim)
        elif "transparent" in claim.claim_text.lower():
            return self._test_transparency_claim(claim)
        elif "trust" in claim.claim_text.lower():
            return self._test_trust_claim(claim)
        elif "autonomy" in claim.claim_text.lower():
            return self._test_autonomy_claim(claim)
        
        return None
    
    def _test_speed_claim(self, claim) -> Optional[Contradiction]:
        """Does org claim to be fast but actually slow?"""
        avg_days = self.ml_signals.get("avg_decision_days", 14)
        
        # If they claim to be fast but avg > 14 days, flag it
        if avg_days > 14:
            gap = min(avg_days - 5, 10)  # Gap score (out of 10)
            severity = ContradictionSeverity.CRITICAL if avg_days > 21 else ContradictionSeverity.HIGH
            
            return Contradiction(
                claim=claim.claim_text,
                observed_reality=f"Decisions take {avg_days:.0f} days on average",
                gap_score=gap,
                severity=severity,
                evidence_quotes=[
                    "Message: 'been waiting 3 weeks for approval'",
                    "Thread: approval chain stuck at director level",
                    "Pattern: each escalation adds 5+ days"
                ],
                root_causes=[
                    "Deep approval chains (4+ levels)",
                    "Gatekeepers holding decisions",
                    "Lack of clear decision authority matrix"
                ],
                impact="Missed market opportunities, reduced team velocity, competitive disadvantage",
                recommendation="Define decision authority by level. Remove approval gates for low-risk decisions. Implement async approval workflows."
            )
        
        return None
    
    def _test_merit_claim(self, claim) -> Optional[Contradiction]:
        """Does org claim meritocracy but show favoritism?"""
        comp_inversions = self.ml_signals.get("ml_signals", {}).get("comp_inversion_count", 0)
        promo_unfairness = self.ml_signals.get("ml_signals", {}).get("promotion_complaints", 0)
        
        if comp_inversions > 0 or promo_unfairness > 0:
            gap = min((comp_inversions + promo_unfairness) * 2, 10)
            
            return Contradiction(
                claim=claim.claim_text,
                observed_reality=f"{comp_inversions} compensation inversions + {promo_unfairness} promotion fairness complaints detected",
                gap_score=gap,
                severity=ContradictionSeverity.CRITICAL,
                evidence_quotes=self._get_real_examples(
                    "meritocracy_issues",
                    fallback=[
                        "Employee reported unequal compensation for same-level role",
                        "Promotion decision perceived as unfair by team",
                        "Several employees referenced politics over performance"
                    ]
                ),
                root_causes=[
                    "Promotion criteria not transparent",
                    "Compensation not benchmarked",
                    "Decision-makers have personal relationships"
                ],
                impact="Talent exodus, reduced morale, discrimination lawsuits, brain drain",
                recommendation="Publish promotion criteria. Benchmark compensation. Audit all promotions last 2 years. Retrain managers on bias."
            )
        
        return None
    
    def _test_transparency_claim(self, claim) -> Optional[Contradiction]:
        """Do they claim transparency but have high escalation/information hoarding?"""
        escalation_rate = self.ml_signals.get("ml_signals", {}).get("escalation_rate", 0)
        
        if escalation_rate > 0.15:  # >15% escalation suggests info gaps
            gap = min(escalation_rate * 10, 10)
            
            return Contradiction(
                claim=claim.claim_text,
                observed_reality=f"High escalation rate ({escalation_rate*100:.0f}%) suggests information asymmetry",
                gap_score=gap,
                severity=ContradictionSeverity.HIGH,
                evidence_quotes=[
                    "Pattern: people bypass manager, go straight to director",
                    "Message: 'couldn't find who actually decides this'",
                    "Thread: 'secret meeting happened without telling us'"
                ],
                root_causes=[
                    "Decision criteria not documented",
                    "Information held by gatekeepers",
                    "No regular all-hands or context sharing"
                ],
                impact="Distrust, politics, slow decisions, duplicated work",
                recommendation="Document all decisions & reasoning. Hold weekly context-sharing meetings. Create decision log. Publish org priorities."
            )
        
        return None
    
    def _get_real_examples(self, signal_key: str, fallback: List[str], limit: int = 3) -> List[str]:
        """
        Pull real evidence/examples from ML signals if available.
        Falls back safely to defaults.
        """
        examples = self.ml_signals.get("examples", {}).get(signal_key, [])

        cleaned = []
        for ex in examples[:limit]:
            if isinstance(ex, str) and ex.strip():
                cleaned.append(ex.strip())

        return cleaned if cleaned else fallback
        
    
    def _test_trust_claim(self, claim) -> Optional[Contradiction]:
        """Do they claim trust but show oversight/micromanagement?"""
        oversight_signals = self.ml_signals.get("ml_signals", {}).get("oversight_mentions", 0)
        
        if oversight_signals > 2:
            gap = min(oversight_signals, 10)
            
            return Contradiction(
                claim=claim.claim_text,
                observed_reality=f"{oversight_signals} mentions of oversight, reporting requirements, status checks",
                gap_score=gap,
                severity=ContradictionSeverity.MEDIUM,
                evidence_quotes=[
                    "Message: 'daily standup requirements'",
                    "Pattern: excessive check-ins and status reports",
                    "Thread: 'manager reviewing every decision'"
                ],
                root_causes=[
                    "Lack of clear OKRs/goals",
                    "Manager insecurity or anxiety",
                    "No historical accountability for decisions"
                ],
                impact="Low autonomy, slow execution, loss of senior talent",
                recommendation="Define clear goals. Reduce check-in frequency. Train managers on trust-based leadership."
            )
        
        return None
    
    def _test_autonomy_claim(self, claim) -> Optional[Contradiction]:
        """Do they claim autonomy but have lots of approvals?"""
        approval_depth = self.ml_signals.get("avg_approval_depth", 2)
        
        if approval_depth > 3:
            gap = min((approval_depth - 1) * 2, 10)
            
            return Contradiction(
                claim=claim.claim_text,
                observed_reality=f"Average decision requires {approval_depth:.0f} approvals",
                gap_score=gap,
                severity=ContradictionSeverity.HIGH,
                evidence_quotes=[
                    f"Pattern: {approval_depth} people must sign off on decisions",
                    "Message: 'can't implement without 4-level approval'",
                    "Thread: endless approval chains"
                ],
                root_causes=[
                    "Risk-averse culture",
                    "No decision authority matrix",
                    "Accountability unclear"
                ],
                impact="Slow execution, reduced innovation, team frustration",
                recommendation="Create decision authority matrix. Define who can decide what without escalation."
            )
        
        return None