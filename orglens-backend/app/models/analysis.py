import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, JSON, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisReport(Base):
    """
    One report per analysis run. Stores all computed metrics.
    The frontend reads from this model to populate the dashboard cards.
    """
    __tablename__ = "analysis_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    progress: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    # === CARD 1: Org Health Score ===
    org_health_score: Mapped[float | None] = mapped_column(Float)   # 0-10 composite
    health_breakdown: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "decision_quality": 7.2,
    #   "decision_velocity": 4.1,
    #   "alignment": 2.8,
    #   "trust": 5.5,
    #   "resilience": 3.0,
    #   "information_flow": 6.2
    # }

    # === CARD 2: Trust Gap ===
    trust_gap_score: Mapped[float | None] = mapped_column(Float)    # 0-10, higher = bigger gap
    trust_gap_details: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "claims": [{"claim": "flat hierarchy", "reality": "12-person approval chain", "gap": 8.5}],
    #   "alignment_score": 3.2,
    #   "trend": "widening"
    # }

    # === CARD 3: Power Structure ===
    power_structure: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "nodes": [{"id": "emp_id", "name": "Sarah", "title": "Sr Engineer",
    #              "formal_authority": 4, "actual_influence": 9.2, "type": "hidden_power"}],
    #   "edges": [{"from": "emp_id1", "to": "emp_id2", "weight": 0.8, "type": "decision_influence"}],
    #   "clusters": [{"name": "Real Decision Makers", "members": ["id1", "id2"]}]
    # }

    # === CARD 4: Top Influencers ===
    top_influencers: Mapped[list | None] = mapped_column(JSON)
    # [
    #   {
    #     "employee_id": "uuid",
    #     "name": "Sarah Chen",
    #     "title": "Sr Engineer",
    #     "influence_score": 9.2,
    #     "formal_authority": 4.0,
    #     "gap": "high",          # formal vs. actual gap
    #     "evidence": [
    #       {"decision": "Hiring freeze Q2", "outcome": "followed objection", "date": "2024-03"},
    #       {"decision": "Budget cut proposal", "outcome": "reversed after pushback", "date": "2024-04"}
    #     ],
    #     "type": "hidden_power"   # hidden_power | formal_leader | ignored_authority | neutral
    #   }
    # ]

    # === CARD 5: Gatekeepers ===
    gatekeepers: Mapped[list | None] = mapped_column(JSON)
    # [
    #   {
    #     "employee_id": "uuid",
    #     "name": "Raj Patel",
    #     "gatekeeper_type": "decision",    # decision | information | both
    #     "blocks_count": 8,
    #     "credibility_score": 0.62,        # how often their blocks improved outcomes
    #     "power_play_score": 0.38,         # how often it was a power move
    #     "domains": ["hiring", "budget"],
    #     "summary": "Blocks initiatives. 62% improve outcomes. 38% appear to be power plays."
    #   }
    # ]

    # === CARD 6: Resilience Score ===
    resilience_score: Mapped[float | None] = mapped_column(Float)   # 0-10 org-level
    resilience_details: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "overall": 3.2,
    #   "single_points_of_failure": [
    #     {
    #       "employee_id": "uuid",
    #       "name": "Sarah Chen",
    #       "impact_if_leaves": 8.5,
    #       "risk_level": "critical",
    #       "estimated_departure_probability": 0.4,
    #       "reason": "Makes 60% of critical decisions. No successor identified."
    #     }
    #   ],
    #   "knowledge_silos": [
    #     {"domain": "vendor relationships", "owned_by": "Elena M.", "backup": false}
    #   ]
    # }

    # === CARD 7: Decision Velocity ===
    decision_velocity: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "avg_days": 21.3,
    #   "claimed": "rapid",
    #   "trend": [{"period": "Q1 2024", "avg_days": 18}, {"period": "Q2 2024", "avg_days": 21}],
    #   "by_domain": [{"domain": "hiring", "avg_days": 34}, {"domain": "budget", "avg_days": 12}],
    #   "bottleneck_persons": [{"name": "Sarah", "avg_delay_days": 8}]
    # }

    # === CARD 8: System Diagnosis ===
    system_diagnosis: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "root_causes": [
    #     {"system": "decision governance", "issue": "...", "severity": "high", "fixable": true}
    #   ],
    #   "who_profits_from_gaps": [{"name": "...", "how": "..."}],
    #   "predicted_if_unchanged": "..."
    # }

    # === CARD 9: Predictions ===
    predictions: Mapped[dict | None] = mapped_column(JSON)
    # {
    #   "attrition_risk": [{"name": "Sarah", "probability": 0.4, "timeline": "12 months"}],
    #   "decision_reversals": [{"decision_id": "...", "reversal_probability": 0.73}],
    #   "velocity_trend": "worsening",
    #   "org_health_6mo": 5.8
    # }
    
    # === CARD 10: Contradictions ===
    contradictions: Mapped[list | None] = mapped_column(JSON, default=list)
    # [
    #   {
    #     "claim": "We have flat hierarchy",
    #     "observed_reality": "12-person approval chain for decisions",
    #     "gap_score": 8.7,
    #     "severity": "high",
    #     "evidence_quotes": [
    #       "Need VP approval before rollout",
    #       "Escalated to director for final sign-off"
    #     ],
    #     "root_causes": ["over-centralized decision rights", "risk-avoidance culture"],
    #     "impact": "slow decision velocity, frustration in teams",
    #     "recommendation": "delegate approval authority to domain leads"
    #   }
    # ]
    
    # === CARD 11: Positive Signals ===
    positive_signals: Mapped[list | None] = mapped_column(JSON, default=list)
    # [
    #   {
    #     "category": "communication",
    #     "description": "Improved cross-team transparency in Q2",
    #     "strength_score": 7.8,
    #     "evidence": [
    #       "weekly org-wide updates introduced",
    #       "faster resolution of inter-team blockers"
    #     ],
    #     "affected_people": ["engineering", "product teams"],
    #     "affected_functions": ["delivery", "planning"],
    #     "growth_potential": "high"
    #   }
    # ]
    
    # === CARD 12: Archetype ===
    archetype: Mapped[dict | None] = mapped_column(JSON, default=dict)
    # {
    #   "archetype": "Bottlenecked Innovator Org",
    #   "name": "Controlled Chaos System",
    #   "description": "High innovation potential but slowed by centralized decision control",
    #   "strengths": [
    #     "strong technical talent",
    #     "high initiative density"
    #   ],
    #   "vulnerabilities": [
    #     "decision bottlenecks",
    #     "hidden power structures"
    #   ],
    #   "recommended_focus": "decentralize decision-making + formalize influence mapping",
    #   "confidence": 0.84
    # }
    
    # === CARD 13: Confidence Metrics ===
    confidence_metrics: Mapped[dict | None] = mapped_column(JSON, default=dict)
    # {
    #   "overall_confidence": 0.82,
    #   "overall_confidence_pct": 82,
    #   "total_messages": 12450,
    #   "total_employees": 86,
    #   "messages_per_person": 144.7,
    #   "date_range_days": 90,
    #   "coverage_by_function": {
    #     "engineering": 0.91,
    #     "product": 0.76,
    #     "hr": 0.64
    #   },
    #   "coverage_by_level": {
    #     "junior": 0.88,
    #     "senior": 0.79,
    #     "lead": 0.66
    #   },
    #   "warnings": [
    #     "low HR signal density",
    #     "limited executive communication data"
    #   ],
    #   "data_sufficiency_summary": "Strong technical coverage, moderate leadership visibility",
    #   "recommendation": "increase leadership communication sampling"
    # }
    
    # === CARD 14: Recommendations ===
    recommendations: Mapped[list | None] = mapped_column(JSON)
    # [
    #   {
    #     "id": 1,
    #     "title": "Formalize Sarah's decision authority",
    #     "description": "...",
    #     "impact": "high",
    #     "effort": "low",
    #     "timeline_weeks": 4,
    #     "cost_estimate": "$5K",
    #     "expected_roi": "40% clarity improvement, 30% time savings",
    #     "confidence": 0.85,
    #     "cost_if_ignored": "$1.2M over 3 years",
    #     "priority_rank": 1
    #   }
    # ]

    # Metadata
    messages_analyzed: Mapped[int | None] = mapped_column()
    decisions_extracted: Mapped[int | None] = mapped_column()
    date_range_start: Mapped[datetime | None] = mapped_column(DateTime)
    date_range_end: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="analyses")