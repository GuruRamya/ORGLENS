import os
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.database import get_db
from app.models import AnalysisReport, AnalysisStatus, Organization
from app.services.confidence.confidence_framework import ConfidenceCalculator

router = APIRouter()

def _get_demo_ids() -> tuple[str | None, str | None]:
    return (
        os.getenv("DEMO_ORG_ID"),
        os.getenv("DEMO_ANALYSIS_ID"),
    )


def _parse_json_field(field):
    if field is None:
        return None
    if isinstance(field, str):
        try:
            return json.loads(field)
        except Exception:
            return None
    return field


@router.get("/status")
async def demo_status():
    org_id, analysis_id = _get_demo_ids()
    return {
        "configured": bool(org_id and analysis_id),
        "demo_org_id": org_id,
        "demo_analysis_id": analysis_id,
    }


@router.get("/report")
async def get_demo_report(db: AsyncSession = Depends(get_db)):
    org_id, analysis_id = _get_demo_ids()
    if not org_id or not analysis_id:
        raise HTTPException(
            status_code=503,
            detail="Demo organization not configured. Run seed_demo.py first.",
        )

    try:
        result = await db.execute(
            select(AnalysisReport).where(AnalysisReport.id == UUID(analysis_id))
        )
        analysis = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load demo report")

    if not analysis:
        raise HTTPException(status_code=404, detail="Demo analysis not found. Re-run seed_demo.py.")

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=202,
            detail=f"Demo analysis is still {analysis.status.value}. Check back in a few minutes.",
        )

    org_result = await db.execute(
        select(Organization).where(Organization.id == UUID(org_id))
    )
    org = org_result.scalar_one_or_none()

    ps = _parse_json_field(analysis.power_structure) or {}
    trust_details = _parse_json_field(analysis.trust_gap_details) or {}
    resilience_details = _parse_json_field(analysis.resilience_details) or {}
    decision_velocity = _parse_json_field(analysis.decision_velocity) or {}
    system_diagnosis = _parse_json_field(analysis.system_diagnosis) or {}
    predictions = _parse_json_field(analysis.predictions) or {}
    archetype = _parse_json_field(analysis.archetype) or {}
    confidence_metrics_raw = _parse_json_field(analysis.confidence_metrics) or {}
    contradictions = _parse_json_field(analysis.contradictions) or []
    positive_signals = _parse_json_field(analysis.positive_signals) or []

    ml_signals = {
        "message_count": analysis.messages_analyzed or 0,
        "employee_count": len(ps.get("nodes", [])),
        "date_range": {
            "start": analysis.date_range_start.isoformat() if analysis.date_range_start else None,
            "end": analysis.date_range_end.isoformat() if analysis.date_range_end else None,
        },
    }
    metrics = ConfidenceCalculator.from_ml_signals(ml_signals)
    confidence_metrics = {
        "overall_confidence": metrics.overall_confidence,
        "overall_confidence_pct": metrics.overall_confidence_pct,
        "total_messages": metrics.total_messages,
        "total_employees": metrics.total_employees,
        "messages_per_person": round(metrics.messages_per_person, 2),
        "date_range_days": metrics.date_range_days,
        "coverage_by_function": {k: int(v * 100) for k, v in metrics.coverage_by_function.items()},
        "coverage_by_level": {k: int(v * 100) for k, v in metrics.coverage_by_level.items()},
        "confidence_breakdown": metrics.get_confidence_breakdown(),
        "strengths_detected": metrics.get_strengths(),
        "limitations_detected": metrics.get_limitations(),
        "recommended_data_improvements": metrics.get_improvement_recommendations(),
        "warnings": metrics.get_warnings(),
    }

    def _score_to_grade(score: float) -> str:
        if score >= 8.5: return "A"
        if score >= 7.0: return "B"
        if score >= 5.5: return "C"
        if score >= 4.0: return "D"
        return "F"

    def _severity_level(score: float) -> str:
        if score >= 8: return "critical"
        if score >= 6: return "high"
        if score >= 4: return "medium"
        return "low"

    def _resilience_to_risk(score: float) -> str:
        if score <= 3: return "critical"
        if score <= 5: return "high"
        if score <= 7: return "medium"
        return "low"

    def _velocity_benchmark(days: float) -> str:
        if days <= 5: return "fast"
        if days <= 15: return "normal"
        if days <= 30: return "slow"
        return "critical"

    def _extract_quick_wins(recommendations):
        if not recommendations: return []
        return [r for r in recommendations if r.get("impact") == "high" and r.get("effort") == "low"][:3]

    def _calculate_total_savings(recommendations):
        if not recommendations: return None
        total = 0
        for rec in recommendations:
            cost_str = rec.get("cost_if_ignored", "$0")
            try:
                cost_val = int("".join(filter(str.isdigit, cost_str.split()[0])))
                total += cost_val
            except Exception:
                pass
        if total >= 1_000_000:
            return f"${total / 1_000_000:.1f}M"
        if total >= 1_000:
            return f"${total / 1_000:.1f}K"
        return f"${total}" if total > 0 else None

    def _health_summary(score: float, breakdown: dict) -> str:
        grade = _score_to_grade(score)
        summaries = {
            "A": "Organization health is strong. Continue monitoring.",
            "B": "Organization is healthy with some areas for improvement.",
            "C": "Organization shows moderate dysfunction. Address key issues soon.",
            "D": "Organization has significant challenges that need urgent attention.",
        }
        return summaries.get(grade, "Organization is in critical condition. Immediate intervention required.")

    recs = analysis.recommendations or []
    health_score = analysis.org_health_score or 0
    trust_score = analysis.trust_gap_score or 0
    resil_score = analysis.resilience_score or 0
    avg_days = decision_velocity.get("avg_days", 0)

    return {
        "analysis_id": str(analysis.id),
        "org_id": str(analysis.org_id),
        "org_name": org.name if org else "Demo Organization",
        "analyzed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        "messages_analyzed": analysis.messages_analyzed,
        "decisions_extracted": analysis.decisions_extracted,
        "date_range": {
            "start": analysis.date_range_start.isoformat() if analysis.date_range_start else None,
            "end": analysis.date_range_end.isoformat() if analysis.date_range_end else None,
        },
        "is_demo": True,
        "org_health": {
            "org_health_score": health_score,
            "health_breakdown": analysis.health_breakdown or {},
            "grade": _score_to_grade(health_score),
            "summary": _health_summary(health_score, analysis.health_breakdown or {}),
        },

        "trust_gap": {
            "trust_gap_score": trust_score,
            "severity": _severity_level(trust_score),
            "claims_analyzed": len(trust_details.get("claims", [])),
            "top_gaps": sorted(
                trust_details.get("claims", []),
                key=lambda x: x.get("gap", 0),
                reverse=True
            )[:3],
            "trend": trust_details.get("trend", "stable"),
            "ml_evidence": trust_details.get("ml_evidence", {}),
        },

        "power_structure": {
            "nodes": ps.get("nodes", []),
            "edges": ps.get("edges", []),
            "clusters": ps.get("clusters", []),
            "hidden_powers": sum(1 for n in ps.get("nodes", []) if n.get("type") == "hidden_power"),
            "ignored_authorities": sum(1 for n in ps.get("nodes", []) if n.get("type") == "ignored_authority"),
        },

        "top_influencers": {
            "influencers": analysis.top_influencers or [],
            "total_analyzed": len(analysis.top_influencers) if analysis.top_influencers else 0,
        },

        "gatekeepers": {
            "gatekeepers": analysis.gatekeepers or [],
            "decision_gatekeepers": sum(
                1 for gk in (analysis.gatekeepers or [])
                if gk.get("gatekeeper_type") in ["decision", "both"]
            ),
            "information_gatekeepers": sum(
                1 for gk in (analysis.gatekeepers or [])
                if gk.get("gatekeeper_type") in ["information", "both"]
            ),
        },

        "resilience": {
            "resilience_score": resil_score,
            "risk_level": _resilience_to_risk(resil_score),
            "single_points_of_failure": resilience_details.get("single_points_of_failure", []),
            "knowledge_silos": resilience_details.get("knowledge_silos", []),
            "ml_signals": resilience_details.get("ml_signals", {}),
        },

        "decision_velocity": {
            "avg_days": avg_days,
            "benchmark": _velocity_benchmark(avg_days),
            "trend": decision_velocity.get("trend", "stable"),
            "trend_data": decision_velocity.get("trend_data", []),
            "bottlenecks": decision_velocity.get("bottleneck_persons", []),
            "ml_signals": decision_velocity.get("ml_signals", {}),
        },

        "system_diagnosis": {
            "root_causes": system_diagnosis.get("root_causes", []),
            "who_profits": system_diagnosis.get("who_profits_from_gaps", []),
            "predicted_if_unchanged": system_diagnosis.get("predicted_if_unchanged", ""),
            "dysfunction_cost_annual": system_diagnosis.get("dysfunction_cost_annual"),
            "ceo_briefing": system_diagnosis.get("ceo_briefing"),
            "political_map": system_diagnosis.get("political_map"),
            "culture_toxins": system_diagnosis.get("culture_toxins", []),
            "between_the_lines": system_diagnosis.get("between_the_lines", []),
            "alert_signals": system_diagnosis.get("alert_signals", []),
        },

        "predictions": {
            "attrition_risks": predictions.get("attrition_risk", []),
            "decision_reversal_risks": predictions.get("decision_reversals", []),
            "velocity_forecast": predictions.get("velocity_trend", "stable"),
            "health_forecast_6mo": float(predictions.get("org_health_6mo", 5.0)),
            "key_risks": predictions.get("key_risks", []),
        },

        "recommendations": {
            "recommendations": recs,
            "quick_wins": _extract_quick_wins(recs),
            "total_potential_savings": _calculate_total_savings(recs),
        },

        "contradictions": contradictions,
        "positive_signals": positive_signals,
        "archetype": archetype,
        "confidence_metrics": confidence_metrics,
    }
