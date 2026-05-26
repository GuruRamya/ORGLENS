from typing import Optional
from loguru import logger

class TrustGapCalculator:
    def __init__(self):
        self.logger = logger

    def calculate_trust_gap(
        self,
        org_claims: dict,  
        actual_data: dict, 
    ) -> dict:
        claims_analysis = []
        total_gap = 0

        if "transparency" in org_claims or "transparent" in str(org_claims).lower():
            gap = self._analyze_transparency_claim(actual_data)
            claims_analysis.append(gap)
            total_gap += gap["gap"]

        if "merit" in str(org_claims).lower() or "hiring" in actual_data:
            gap = self._analyze_meritocracy_claim(actual_data)
            claims_analysis.append(gap)
            total_gap += gap["gap"]

        if "balance" in str(org_claims).lower() or "meeting" in actual_data:
            gap = self._analyze_balance_claim(actual_data)
            claims_analysis.append(gap)
            total_gap += gap["gap"]

        if "innovation" in str(org_claims).lower() or "risky" in actual_data:
            gap = self._analyze_innovation_claim(actual_data)
            claims_analysis.append(gap)
            total_gap += gap["gap"]

        if claims_analysis:
            overall_gap = total_gap / len(claims_analysis)
        else:
            overall_gap = 5.0

        return {
            "trust_gap_score": min(overall_gap, 10.0),
            "severity": self._gap_to_severity(overall_gap),
            "claims_analyzed": len(claims_analysis),
            "top_gaps": sorted(claims_analysis, key=lambda x: x["gap"], reverse=True)[:3],
            "all_gaps": claims_analysis,
            "alignment_score": 10.0 - min(overall_gap, 10.0), 
        }

    def analyze_claim(
        self,
        claim: str,
        supporting_evidence: dict,
        contradicting_evidence: dict,
    ) -> dict:
        support_strength = sum(v for v in supporting_evidence.values() if isinstance(v, (int, float)))
        contradict_strength = sum(v for v in contradicting_evidence.values() if isinstance(v, (int, float)))

        total = support_strength + contradict_strength
        if total > 0:
            support_ratio = support_strength / total
        else:
            support_ratio = 0.5

        gap = (1 - support_ratio) * 10

        is_contradiction = support_ratio < 0.3 and contradict_strength > 0

        return {
            "claim": claim,
            "gap": gap,
            "support_ratio": support_ratio,
            "is_contradiction": is_contradiction,
            "supporting_evidence_count": len(supporting_evidence),
            "contradicting_evidence_count": len(contradicting_evidence),
            "severity": self._gap_to_severity(gap),
        }

    def calculate_trend(
        self,
        current_gap: float,
        previous_gaps: list[float],
    ) -> str:
        if len(previous_gaps) < 2:
            return "unknown"

        recent = previous_gaps[-3:] if len(previous_gaps) >= 3 else previous_gaps

        import numpy as np
        trend_direction = np.polyfit(range(len(recent)), recent, 1)[0]

        if trend_direction > 0.3:
            return "widening"
        elif trend_direction < -0.3:
            return "narrowing"
        else:
            return "stable"


    def _analyze_transparency_claim(self, actual_data: dict) -> dict:
        gap = 5.0  

        approval_chain = actual_data.get("approval_chain_length", 0)
        if approval_chain > 10:
            gap = 8.5 
        elif approval_chain > 5:
            gap = 6.0
        elif approval_chain <= 2:
            gap = 2.0  

        decision_timing = actual_data.get("decisions_made_before_meetings_percent", 0)
        if decision_timing > 0.5:
            gap += 2.0 

        return {
            "claim": "Transparent decision-making",
            "gap": min(gap, 10.0),
            "evidence": {
                "approval_chain_length": approval_chain,
                "decisions_predetermined": decision_timing,
            },
            "summary": f"Approval chain: {approval_chain} people. {decision_timing*100:.0f}% of decisions made before meetings.",
        }

    def _analyze_meritocracy_claim(self, actual_data: dict) -> dict:
        gap = 5.0

        referral_hire_percent = actual_data.get("referral_hire_percent", 0.5)
        if referral_hire_percent > 0.7:
            gap = 8.0  
        elif referral_hire_percent > 0.5:
            gap = 6.0
        elif referral_hire_percent < 0.3:
            gap = 2.0

        internal_promo_percent = actual_data.get("internal_promotion_percent", 0.5)
        if internal_promo_percent < 0.2:
            gap += 2.0  

        return {
            "claim": "Merit-based hiring and promotion",
            "gap": min(gap, 10.0),
            "evidence": {
                "referral_hire_percent": referral_hire_percent,
                "internal_promotion_percent": internal_promo_percent,
            },
            "summary": f"{referral_hire_percent*100:.0f}% of hires are referrals. {internal_promo_percent*100:.0f}% of promotions are internal.",
        }

    def _analyze_balance_claim(self, actual_data: dict) -> dict:
        gap = 5.0

        avg_meetings = actual_data.get("avg_meetings_per_week", 10)
        if avg_meetings > 30:
            gap = 8.5
        elif avg_meetings > 15:
            gap = 6.0
        elif avg_meetings < 5:
            gap = 2.0

        after_hours_comm = actual_data.get("after_hours_communication_percent", 0)
        if after_hours_comm > 0.4:
            gap += 1.5

        return {
            "claim": "Work-life balance",
            "gap": min(gap, 10.0),
            "evidence": {
                "avg_meetings_per_week": avg_meetings,
                "after_hours_communication_percent": after_hours_comm,
            },
            "summary": f"Avg {avg_meetings} meetings/week. {after_hours_comm*100:.0f}% of communication happens after hours.",
        }

    def _analyze_innovation_claim(self, actual_data: dict) -> dict:
        gap = 5.0

        risky_approved = actual_data.get("risky_projects_approved_percent", 0.5)
        if risky_approved < 0.2:
            gap = 8.0 
        elif risky_approved < 0.4:
            gap = 6.0
        elif risky_approved > 0.7:
            gap = 2.0  

        decision_velocity = actual_data.get("avg_decision_days", 20)
        if decision_velocity > 30:
            gap += 2.0 

        return {
            "claim": "Innovation-first, move fast",
            "gap": min(gap, 10.0),
            "evidence": {
                "risky_projects_approved_percent": risky_approved,
                "avg_decision_days": decision_velocity,
            },
            "summary": f"{risky_approved*100:.0f}% of risky projects approved. Avg decision time: {decision_velocity} days.",
        }

    def _gap_to_severity(self, gap: float) -> str:
        """Convert gap score to severity level"""
        if gap >= 8:
            return "critical"
        elif gap >= 6:
            return "high"
        elif gap >= 4:
            return "medium"
        else:
            return "low"
