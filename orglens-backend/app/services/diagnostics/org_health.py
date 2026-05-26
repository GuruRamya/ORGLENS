from typing import Optional
from loguru import logger
import numpy as np

class OrgHealthCalculator:
    def __init__(self):
        self.logger = logger

    def calculate_org_health_score(
        self,
        trust_gap_score: float,
        resilience_score: float,
        decision_velocity_days: float,
        decision_quality_score: float,
        alignment_score: float,
        information_flow_score: float,
    ) -> dict:
        trust_normalized = 10.0 - trust_gap_score  
        resilience_normalized = resilience_score
        decision_quality_normalized = decision_quality_score
        alignment_normalized = alignment_score
        information_flow_normalized = information_flow_score

        if decision_velocity_days <= 5:
            velocity_score = 10.0
        elif decision_velocity_days <= 15:
            velocity_score = 8.0
        elif decision_velocity_days <= 30:
            velocity_score = 5.0
        else:
            velocity_score = 2.0

        weights = {
            "trust": 0.25,
            "resilience": 0.20,
            "decision_velocity": 0.20,
            "decision_quality": 0.15,
            "alignment": 0.15,
            "information_flow": 0.05,
        }

        weighted_score = (
            trust_normalized * weights["trust"] +
            resilience_normalized * weights["resilience"] +
            velocity_score * weights["decision_velocity"] +
            decision_quality_normalized * weights["decision_quality"] +
            alignment_normalized * weights["alignment"] +
            information_flow_normalized * weights["information_flow"]
        )

        final_score = max(0, min(weighted_score, 10.0))

        breakdown = {
            "trust": trust_normalized,
            "resilience": resilience_normalized,
            "decision_velocity": velocity_score,
            "decision_quality": decision_quality_normalized,
            "alignment": alignment_normalized,
            "information_flow": information_flow_normalized,
        }

        grade = self._score_to_grade(final_score)
        summary = self._score_to_summary(final_score)

        return {
            "org_health_score": final_score,
            "grade": grade,
            "health_breakdown": breakdown,
            "status": self._score_to_status(final_score),
            "summary": summary,
            "urgency": self._score_to_urgency(final_score),
        }

    def calculate_decision_quality_score(
        self,
        decisions_made: list[dict],
    ) -> float:
        if not decisions_made:
            return 5.0

        quality_scores = []

        for decision in decisions_made:
            score = 5.0  

            if decision.get("followed_objections_count", 0) > 0:
                score += 1.0

            if decision.get("reversed_count", 0) == 0:
                score += 2.0
            elif decision.get("reversed_count", 0) == 1:
                score += 0.5

            if decision.get("positive_outcomes"):
                score += 1.5

            quality_scores.append(min(score, 10.0))

        return np.mean(quality_scores)

    def calculate_alignment_score(
        self,
        stated_values: list[str],
        actual_behaviors: dict, 
    ) -> float:
        if not stated_values or not actual_behaviors:
            return 5.0

        alignment_scores = []

        for value in stated_values:
            actual = actual_behaviors.get(value, 0.5)

            if actual >= 0.7:
                alignment_scores.append(9.0)
            elif actual >= 0.4:
                alignment_scores.append(5.0)
            else:
                alignment_scores.append(2.0)

        return np.mean(alignment_scores)

    def calculate_information_flow_score(
        self,
        communication_network: dict,
        information_silos: list,
    ) -> float:
        score = 5.0

        nodes = communication_network.get("nodes", [])
        edges = communication_network.get("edges", [])

        if len(nodes) > 0:
            connection_density = len(edges) / (len(nodes) ** 2) if len(nodes) > 1 else 0

            if connection_density > 0.3:
                score += 3.0
            elif connection_density > 0.15:
                score += 1.5
            else:
                score -= 1.0

        sole_owner_silos = [s for s in information_silos if s.get("owner_count", 1) == 1]

        if sole_owner_silos:
            silo_penalty = min(len(sole_owner_silos) * 0.5, 3.0)
            score -= silo_penalty

        return max(0, min(score, 10.0))

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 8.5:
            return "A"
        elif score >= 7.0:
            return "B"
        elif score >= 5.5:
            return "C"
        elif score >= 4.0:
            return "D"
        else:
            return "F"

    def _score_to_status(self, score: float) -> str:
        """Convert score to health status"""
        if score >= 8.0:
            return "healthy"
        elif score >= 6.5:
            return "functional"
        elif score >= 4.5:
            return "at_risk"
        elif score >= 2.0:
            return "critical"
        else:
            return "dysfunctional"

    def _score_to_urgency(self, score: float) -> str:
        """Convert score to action urgency"""
        if score < 3.0:
            return "immediate_intervention_required"
        elif score < 4.5:
            return "urgent_attention_needed"
        elif score < 6.0:
            return "high_priority_improvement"
        elif score < 7.5:
            return "monitor_and_maintain"
        else:
            return "maintain_current_practices"

    def _score_to_summary(self, score: float) -> str:
        """Generate human-readable summary of org health"""
        if score >= 8.5:
            return "Organization is healthy with strong fundamentals. Continue current practices."
        elif score >= 7.0:
            return "Organization is functional with some areas for improvement."
        elif score >= 5.5:
            return "Organization shows moderate dysfunction. Key issues need attention."
        elif score >= 4.0:
            return "Organization has significant challenges requiring urgent action."
        else:
            return "Organization is in critical condition. Immediate comprehensive intervention required."

    def identify_lowest_scoring_components(self, breakdown: dict, top_n: int = 3) -> list[dict]:
        """Identify which components are dragging down score"""
        components = [
            {"name": k, "score": v, "normalized": v / 10.0}
            for k, v in breakdown.items()
        ]

        sorted_components = sorted(components, key=lambda x: x["score"])

        return sorted_components[:top_n]
