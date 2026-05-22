from typing import Optional
from loguru import logger
import numpy as np


class ResilienceCalculator:
    """
    Calculate organizational resilience: how fragile is it?
    Identifies: single points of failure, knowledge silos, key person dependencies.
    """

    def __init__(self):
        self.logger = logger

    def calculate_resilience_score(
        self,
        single_points_of_failure: list[dict],
        knowledge_silos: list[dict],
        decision_distribution: dict,  # {person: decisions_made_percent}
        department_cross_training: dict,  # {department: cross_trained_percent}
    ) -> float:
        """
        Calculate overall resilience score (0-10).
        Higher = more resilient. Lower = more fragile.
        """
        score = 10.0

        # Factor 1: Single points of failure (each costs 2-3 points)
        for spof in single_points_of_failure:
            impact = spof.get("impact_if_leaves", 0) / 10.0  # Normalize to 0-1
            score -= (impact * 3)  # Can lose up to 3 points per person

        # Factor 2: Knowledge silos (each costs 1 point)
        for silo in knowledge_silos:
            if not silo.get("backup_available", False):
                score -= 1

        # Factor 3: Decision concentration
        max_decision_share = max(decision_distribution.values()) if decision_distribution else 0.5
        decision_concentration_penalty = (max_decision_share - 0.2) * 5  # 0-5 point penalty
        score -= decision_concentration_penalty

        # Factor 4: Cross-training (bonus if good)
        avg_cross_training = np.mean(list(department_cross_training.values())) if department_cross_training else 0
        if avg_cross_training > 0.5:
            score += 1.5

        return max(0, min(score, 10.0))

    def identify_single_points_of_failure(
        self,
        employees: dict,  # {emp_id: {influence, knowledge_domains, tenure, ...}}
        decision_data: dict,  # {emp_id: decisions_made_count}
        knowledge_owners: dict,  # {domain: [owners]}
    ) -> list[dict]:
        """
        Identify employees whose loss would severely impact organization.

        Returns list of: {employee_id, name, impact_score, risk_level, reasons}
        """
        spofs = []

        # Check high-influence people
        for emp_id, emp_data in employees.items():
            influence_score = emp_data.get("influence_score", 0)
            decisions_made = decision_data.get(emp_id, 0)
            domains_owned = []

            # Count how many domains they uniquely own
            for domain, owners in knowledge_owners.items():
                if len([o for o in owners if o == emp_id]) == 1 and len(owners) == 1:
                    domains_owned.append(domain)

            # Calculate impact
            influence_impact = influence_score / 10.0 * 5  # 0-5
            decision_impact = min(decisions_made / 100.0 * 3, 3)  # 0-3
            silo_impact = len(domains_owned) * 2  # 0-2+ per domain

            total_impact = influence_impact + decision_impact + silo_impact

            if total_impact > 3.0:
                # Calculate departure probability
                tenure = emp_data.get("tenure_months", 36)
                departure_prob = 0.15  # Base rate

                # Higher influence, higher flight risk
                if influence_score > 6:
                    departure_prob += 0.15

                # Isolated experts at higher risk
                if len(domains_owned) > 0 and influence_score > 5:
                    departure_prob += 0.10

                spofs.append({
                    "employee_id": emp_id,
                    "name": emp_data.get("name", "Unknown"),
                    "title": emp_data.get("title"),
                    "influence_score": influence_score,
                    "decisions_made": decisions_made,
                    "knowledge_domains": domains_owned,
                    "impact_if_leaves": total_impact,
                    "risk_level": self._impact_to_risk_level(total_impact),
                    "departure_probability_12mo": departure_prob,
                    "reasons": self._generate_spof_reasons(
                        influence_score, decisions_made, domains_owned
                    ),
                })

        return sorted(spofs, key=lambda x: x["impact_if_leaves"], reverse=True)

    def identify_knowledge_silos(
        self,
        knowledge_owners: dict,  # {domain: [owner_ids]}
        backup_assignments: Optional[dict] = None,
    ) -> list[dict]:
        """
        Identify critical knowledge owned by single people.

        knowledge_owners format:
        {
            "vendor_relationships": ["emp_id_1"],
            "budget_process": ["emp_id_2"],
            "customer_data_system": ["emp_id_1", "emp_id_2"],
        }

        Returns: {domain, owners, is_at_risk, backup_available}
        """
        silos = []
        backup_assignments = backup_assignments or {}

        for domain, owners in knowledge_owners.items():
            if len(owners) == 1:
                backup_available = domain in backup_assignments and len(backup_assignments[domain]) > 0

                silos.append({
                    "domain": domain,
                    "owner": owners[0],
                    "owner_count": 1,
                    "is_at_risk": True,
                    "backup_available": backup_available,
                    "backup_owners": backup_assignments.get(domain, []),
                    "risk_level": "critical" if not backup_available else "medium",
                    "mitigation": "Cross-train at least one backup" if not backup_available else "Backup in place",
                })

            elif len(owners) < 3:
                backup_available = len(owners) >= 2

                silos.append({
                    "domain": domain,
                    "owner": owners[0],
                    "owner_count": len(owners),
                    "is_at_risk": True,
                    "backup_available": backup_available,
                    "backup_owners": owners[1:],
                    "risk_level": "high" if len(owners) == 2 else "medium",
                    "mitigation": "Add more people to knowledge base",
                })

        return sorted(silos, key=lambda x: (x["is_at_risk"], x["owner_count"]))

    def calculate_succession_readiness(
        self,
        key_person: dict,
        successors: list[dict],
    ) -> dict:
        """
        Assess readiness of successors to replace a key person.

        key_person: {name, role, influence_score, domains}
        successors: [{name, experience_years, trained_domains}]

        Returns: {readiness_score, ready_successors, training_needed, timeline}
        """
        readiness_scores = []

        for successor in successors:
            trained_domains = successor.get("trained_domains", [])
            key_domains = key_person.get("domains", [])

            # How many key domains are they trained in?
            domain_coverage = len(
                [d for d in key_domains if d in trained_domains]
            ) / max(len(key_domains), 1)

            # Experience level
            experience_multiplier = min(successor.get("experience_years", 0) / 5, 1.0)

            readiness = (domain_coverage + experience_multiplier) / 2

            readiness_scores.append({
                "successor": successor.get("name"),
                "readiness_score": readiness,
                "domain_coverage": domain_coverage,
                "experience_years": successor.get("experience_years", 0),
                "missing_domains": [d for d in key_domains if d not in trained_domains],
            })

        ready_successors = [s for s in readiness_scores if s["readiness_score"] > 0.7]
        partially_ready = [s for s in readiness_scores if 0.4 < s["readiness_score"] <= 0.7]

        if ready_successors:
            overall_readiness = 0.9  # Ready to transition
            timeline = "Immediately"
        elif partially_ready:
            overall_readiness = 0.5
            timeline = "3-6 months with training"
        else:
            overall_readiness = 0.1
            timeline = "12+ months, needs full training"

        return {
            "key_person": key_person.get("name"),
            "overall_readiness": overall_readiness,
            "ready_successors": ready_successors,
            "partially_ready_successors": partially_ready,
            "estimated_transition_timeline": timeline,
            "training_plan": self._generate_training_plan(key_person, partially_ready),
        }

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _impact_to_risk_level(self, impact: float) -> str:
        """Convert impact score to risk level"""
        if impact >= 7:
            return "critical"
        elif impact >= 5:
            return "high"
        elif impact >= 3:
            return "medium"
        else:
            return "low"

    def _generate_spof_reasons(
        self,
        influence: float,
        decisions: int,
        knowledge_domains: list,
    ) -> list[str]:
        """Generate human-readable reasons for single point of failure"""
        reasons = []

        if influence > 7:
            reasons.append("High organizational influence (likely needed for major decisions)")

        if decisions > 50:
            reasons.append(f"Made {decisions}+ key decisions (irreplaceable decision-maker)")

        if knowledge_domains:
            reasons.append(f"Sole owner of {len(knowledge_domains)} critical domain(s): {', '.join(knowledge_domains)}")

        return reasons

    def _generate_training_plan(
        self,
        key_person: dict,
        successors: list,
    ) -> list[str]:
        """Generate training plan for succession"""
        plan = []

        domains = key_person.get("domains", [])

        for successor in successors:
            missing = successor.get("missing_domains", [])

            if missing:
                plan.append(
                    f"{successor.get('successor')}: Train on {', '.join(missing)} "
                    f"(est. 6-8 weeks per domain)"
                )
            else:
                plan.append(f"{successor.get('successor')}: Ready for shadowing immediately")

        return plan