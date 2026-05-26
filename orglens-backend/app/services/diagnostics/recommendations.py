from typing import Optional
from loguru import logger

class RecommendationEngine:

    def __init__(self):
        self.logger = logger

    def generate_recommendations(
        self,
        diagnostics: dict,
    ) -> list[dict]:
        recommendations = []

        if diagnostics.get("trust_gap", {}).get("trust_gap_score", 0) > 6:
            recommendations.extend(self._trust_gap_recommendations(diagnostics["trust_gap"]))

        if diagnostics.get("resilience", {}).get("single_points_of_failure"):
            recommendations.extend(self._resilience_recommendations(diagnostics["resilience"]))

        if diagnostics.get("decision_velocity", {}).get("avg_days", 0) > 20:
            recommendations.extend(self._velocity_recommendations(diagnostics["decision_velocity"]))

        if diagnostics.get("power_structure"):
            recommendations.extend(self._power_structure_recommendations(diagnostics["power_structure"]))

        for rec in recommendations:
            rec["priority_rank"] = self._calculate_priority(rec)

        recommendations = sorted(recommendations, key=lambda x: x["priority_rank"])

        for idx, rec in enumerate(recommendations, 1):
            rec["rank"] = idx

        return recommendations

    def _trust_gap_recommendations(self, trust_gap_data: dict) -> list[dict]:
        """Generate recommendations for closing trust gaps"""
        recs = []

        gap_score = trust_gap_data.get("trust_gap_score", 5)

        recs.append({
            "id": "trust_gap_1",
            "title": "Formalize decision-making process",
            "description":
                "Create clear decision authority matrix. Document who decides what, "
                "by what criteria, in what timeline. Make this explicit to organization.",
            "domain": "governance",
            "impact": "high" if gap_score > 7 else "medium",
            "effort": "low",
            "timeline_weeks": 4,
            "cost_estimate": "$3K-5K",
            "expected_outcome": "40-60% improvement in decision clarity",
            "confidence": 0.85,
            "cost_if_ignored": "$500K+ annually in wasted meetings",
            "success_metrics": [
                "Decision authority matrix documented",
                "100% of org aware of decision rules",
                "Approval times reduced by 30%",
            ],
        })

        recs.append({
            "id": "trust_gap_2",
            "title": "Realign organizational systems to stated values",
            "description":
                "Audit hiring, promotion, compensation systems against stated values. "
                "Either change systems to match values, or update values to match reality.",
            "domain": "culture_systems",
            "impact": "high",
            "effort": "high",
            "timeline_weeks": 12,
            "cost_estimate": "$15K-25K",
            "expected_outcome": "Values-behavior alignment from 40% to 80%+",
            "confidence": 0.70,
            "cost_if_ignored": "$300K+ annual attrition from misalignment",
            "success_metrics": [
                "Compensation structure audited",
                "Promotion criteria documented and published",
                "Hiring process changed to match claimed criteria",
            ],
        })

        return recs

    def _resilience_recommendations(self, resilience_data: dict) -> list[dict]:
        """Generate recommendations for improving resilience"""
        recs = []

        spofs = resilience_data.get("single_points_of_failure", [])

        if spofs:
            top_spof = spofs[0]

            recs.append({
                "id": "resilience_1",
                "title": f"Succession plan for {top_spof.get('name')}",
                "description":
                    f"Identify and train 1-2 successors for {top_spof.get('name')}. "
                    f"Document their key decisions and domains. Cross-train backup.",
                "domain": "talent",
                "impact": "high",
                "effort": "medium",
                "timeline_weeks": 24,
                "cost_estimate": "$0 (internal time)",
                "expected_outcome": f"50% reduction in {top_spof.get('name')} bottleneck",
                "confidence": 0.80,
                "cost_if_ignored": f"${int(top_spof.get('impact_if_leaves', 5) * 400)}K if this person leaves",
                "success_metrics": [
                    "2 successors identified and trained",
                    "Key decisions documented",
                    "Backup can make 80%+ of decisions",
                ],
            })

        silos = resilience_data.get("knowledge_silos", [])
        if silos:
            critical_silos = [s for s in silos if s.get("is_at_risk")]

            for silo in critical_silos[:1]: 
                recs.append({
                    "id": "resilience_2",
                    "title": f"Eliminate knowledge silo: {silo.get('domain')}",
                    "description":
                        f"Currently, only {silo.get('owner')} understands {silo.get('domain')}. "
                        f"Document the knowledge. Train at least one backup.",
                    "domain": "knowledge_management",
                    "impact": "high",
                    "effort": "medium",
                    "timeline_weeks": 12,
                    "cost_estimate": "$2K-5K",
                    "expected_outcome": "Knowledge distributed to 2+ people",
                    "confidence": 0.75,
                    "cost_if_ignored": f"Loss of critical capability if {silo.get('owner')} unavailable",
                    "success_metrics": [
                        f"{silo.get('domain')} documented",
                        "Backup person trained",
                        "Backup can perform 90%+ of tasks independently",
                    ],
                })

        return recs

    def _velocity_recommendations(self, velocity_data: dict) -> list[dict]:
        """Generate recommendations for improving decision velocity"""
        recs = []

        avg_days = velocity_data.get("avg_days", 20)

        if avg_days > 25:
            recs.append({
                "id": "velocity_1",
                "title": "Streamline approval chains",
                "description":
                    "Map current approval process. Eliminate unnecessary approvers. "
                    "Define clear decision thresholds (under $X = manager decides, over = needs leadership).",
                "domain": "governance",
                "impact": "high",
                "effort": "low",
                "timeline_weeks": 3,
                "cost_estimate": "$1K-2K",
                "expected_outcome": "Decision time reduced from 20+ to 5-10 days",
                "confidence": 0.80,
                "cost_if_ignored": f"$50K+ weekly in lost productivity from slow decisions",
                "success_metrics": [
                    "Approval matrix simplified",
                    "Decision time reduced by 50%",
                    "Fewer meetings needed for decisions",
                ],
            })

        bottlenecks = velocity_data.get("bottleneck_persons", [])
        if bottlenecks:
            rec = bottlenecks[0]

            recs.append({
                "id": "velocity_2",
                "title": f"Reduce {rec.get('name')} decision bottleneck",
                "description":
                    f"{rec.get('name')} is slowing decisions by {rec.get('avg_delay_days')} days. "
                    f"Either delegate their decisions or add async approval process.",
                "domain": "talent",
                "impact": "high",
                "effort": "medium",
                "timeline_weeks": 4,
                "cost_estimate": "$0",
                "expected_outcome": f"Decision time reduced by {rec.get('avg_delay_days')} days",
                "confidence": 0.70,
                "cost_if_ignored": f"$20K+ weekly in lost velocity",
                "success_metrics": [
                    "Decisions delegated or async approval implemented",
                    "Decision time reduced",
                    f"{rec.get('name')} has more capacity",
                ],
            })

        return recs

    def _power_structure_recommendations(self, power_structure: dict) -> list[dict]:
        """Generate recommendations for power structure issues"""
        recs = []

        nodes = power_structure.get("nodes", [])

        hidden_powers = [n for n in nodes if n.get("type") == "hidden_power"]
        ignored_authorities = [n for n in nodes if n.get("type") == "ignored_authority"]

        if hidden_powers:
            hp = hidden_powers[0]

            recs.append({
                "id": "power_1",
                "title": f"Formalize {hp.get('name')}'s authority",
                "description":
                    f"{hp.get('name')} ({hp.get('title')}) has actual influence of {hp.get('actual_influence', 0):.1f}/10 "
                    f"but formal authority of only {hp.get('formal_authority', 0):.1f}/10. "
                    f"Recognize them formally or redistribute decision power.",
                "domain": "organizational_design",
                "impact": "high",
                "effort": "low",
                "timeline_weeks": 2,
                "cost_estimate": "$0",
                "expected_outcome": "Clarity on who actually has authority",
                "confidence": 0.85,
                "cost_if_ignored": "Continued org chart mismatch causes confusion and resentment",
                "success_metrics": [
                    f"{hp.get('name')}'s formal authority updated",
                    f"Org chart reflects actual power structure",
                    "Reduced confusion about decision authority",
                ],
            })

        if ignored_authorities:
            ia = ignored_authorities[0]

            recs.append({
                "id": "power_2",
                "title": f"Address {ia.get('name')}'s ignored authority",
                "description":
                    f"{ia.get('name')} ({ia.get('title')}) has formal authority of {ia.get('formal_authority', 0):.1f}/10 "
                    f"but actual influence of only {ia.get('actual_influence', 0):.1f}/10. "
                    f"Either redistribute their authority, or support them to increase influence.",
                "domain": "leadership_development",
                "impact": "medium",
                "effort": "medium",
                "timeline_weeks": 12,
                "cost_estimate": "$5K-10K",
                "expected_outcome": f"{ia.get('name')}'s influence increases by 3+ points",
                "confidence": 0.65,
                "cost_if_ignored": f"Continued frustration and possible departure of {ia.get('name')}",
                "success_metrics": [
                    f"{ia.get('name')}'s leadership coaching completed",
                    f"Their input sought in decisions",
                    "Influence score increases by 30%+",
                ],
            })

        return recs


    def _calculate_priority(self, recommendation: dict) -> float:
        score = 0.0

        impact_map = {"critical": 3, "high": 2, "medium": 1, "low": 0}
        score += impact_map.get(recommendation.get("impact", "low"), 1)

        effort_map = {"low": 2, "medium": 1, "high": 0}
        score += effort_map.get(recommendation.get("effort", "medium"), 1)

        timeline = recommendation.get("timeline_weeks", 10)
        if timeline <= 4:
            score += 1.0
        elif timeline <= 8:
            score += 0.5

        confidence = recommendation.get("confidence", 0.7)
        score *= confidence

        return score
