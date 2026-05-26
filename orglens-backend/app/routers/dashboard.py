from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from loguru import logger
from typing import Optional
import os
from app.services.auth import get_current_user
from app.models.auth import User
from app.services.confidence.confidence_framework import ConfidenceCalculator
from app.schemas.confidence import DataQualityCardSchema
from app.config import settings
from app.database import get_db
from app.models import AnalysisReport, AnalysisStatus, Organization
from app.schemas.analysis import (
    FullDashboardResponse,
    OrgHealthCard,
    TrustGapCard,
    PowerStructureCard,
    InfluencerCard,
    GatekeeperCard,
    ResilienceCard,
    DecisionVelocityCard,
    DiagnosisCard,
    PredictionsCard,
    RecommendationsCard,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

DEMO_ANALYSIS_ID = os.getenv("DEMO_ANALYSIS_ID")
DEMO_ORG_ID      = os.getenv("DEMO_ORG_ID")


def _is_demo(analysis_id: str) -> bool:
    return DEMO_ANALYSIS_ID and str(analysis_id) == str(DEMO_ANALYSIS_ID)

def _parse_json_field(field):
    """Handle both dict and string JSON fields"""
    if field is None:
        return {}
    if isinstance(field, str):
        import json
        try:
            return json.loads(field)
        except:
            return {}
    return field


@router.get("/report/{analysis_id}")
async def get_dashboard_report(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme), 
):
    if not _is_demo(analysis_id):
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            user = await get_current_user(token, db)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    ps = _parse_json_field(analysis.power_structure)
    trust_details = _parse_json_field(analysis.trust_gap_details)
    resilience_details = _parse_json_field(analysis.resilience_details)
    decision_velocity = _parse_json_field(analysis.decision_velocity)
    system_diagnosis = _parse_json_field(analysis.system_diagnosis)
    predictions = _parse_json_field(analysis.predictions)
    archetype = _parse_json_field(analysis.archetype)
    confidence_metrics = _parse_json_field(analysis.confidence_metrics)
    contradictions_raw = analysis.contradictions or []
    positive_signals_raw = analysis.positive_signals or []
    org_result = await db.execute(
        select(Organization).where(Organization.id == analysis.org_id)
    )
    org = org_result.scalar_one_or_none()
    ml_signals = {
        "message_count": analysis.messages_analyzed or 0,
        "employee_count": len(ps.get("nodes", [])) if ps else 0,
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
        "coverage_by_function": {k: int(v*100) for k, v in metrics.coverage_by_function.items()},
        "coverage_by_level": {k: int(v*100) for k, v in metrics.coverage_by_level.items()},
        "confidence_breakdown": metrics.get_confidence_breakdown(),
        "strengths_detected": metrics.get_strengths(),
        "limitations_detected": metrics.get_limitations(),
        "recommended_data_improvements": metrics.get_improvement_recommendations(),
        "warnings": metrics.get_warnings(),
    }
    if confidence_metrics:
        confidence_metrics["reasoning"] = [
            f"Analysis based on {analysis.messages_analyzed} messages",
            "Low confidence due to insufficient communication density"
            if analysis.messages_analyzed < 100
            else "Sufficient communication density"
        ]

        confidence_metrics["reliability"] = {
            "power_structure": 32,
            "trust_analysis": 48,
            "decision_velocity": 71,
        }
    
    if archetype:
        for field in ["classification_reasons", "supporting_metrics", "strengths",
                      "vulnerabilities", "recommended_focus", "confidence_pct",
                      "risk_level", "trajectory"]:
            if field not in archetype:
                if field == "supporting_metrics":
                    archetype[field] = {
                        "decision_velocity_days": decision_velocity.get("avg_days", 14) if decision_velocity else 14,
                        "trust_score": 10 - (analysis.trust_gap_score or 5),
                        "health_score": analysis.org_health_score or 5,
                        "resilience_score": analysis.resilience_score or 5,
                    }
                elif field in ["classification_reasons", "strengths", "vulnerabilities", "recommended_focus"]:
                    archetype[field] = []
                elif field == "confidence_pct":
                    archetype[field] = 85
                elif field == "risk_level":
                    archetype[field] = "medium"
                elif field == "trajectory":
                    archetype[field] = "stable"
                    
    contradictions = []
    for c in contradictions_raw:
        contradictions.append({
            "claim": c.get("claim", ""),
            "observed_reality": c.get("observed_reality", ""),
            "gap_score": c.get("gap_score", 0),
            "severity": c.get("severity", "medium"),
            "evidence_quotes": c.get("evidence_quotes", c.get("evidence", [])),
            "root_causes": c.get("root_causes", []),
            "impact": c.get("impact", "Organizational friction"),
            "recommendation": c.get("recommendation", "Address the root causes systematically"),
        })
        
    positive_signals = [
        {
            "category": p.get("category", "unknown"),
            "description": p.get("description", ""),
            "strength_score": p.get("strength_score", 5),
            "evidence": p.get("evidence", []),
            "affected_people": p.get("affected_people", 0),
            "affected_functions": p.get("affected_functions", []),
            "growth_potential": p.get("growth_potential", "medium"),
            "confidence_pct": p.get("confidence_pct", 70),
        }
        for p in positive_signals_raw
    ]
    try:
        dashboard = FullDashboardResponse(
            analysis_id=analysis.id,
            org_id=analysis.org_id,
            org_name=org.name if org else "Unknown",
            analyzed_at=analysis.completed_at,
            messages_analyzed=analysis.messages_analyzed,
            decisions_extracted=analysis.decisions_extracted,
            date_range={
                "start": analysis.date_range_start.isoformat() if analysis.date_range_start else None,
                "end": analysis.date_range_end.isoformat() if analysis.date_range_end else None,
            },
            org_health=OrgHealthCard(
                org_health_score=analysis.org_health_score or 0,
                health_breakdown=analysis.health_breakdown or {},
                grade=_score_to_grade(analysis.org_health_score or 0),
                summary=_generate_health_summary(analysis.org_health_score or 0, analysis.health_breakdown),
            ),
            trust_gap=TrustGapCard(
                trust_gap_score=analysis.trust_gap_score or 0,
                severity=_severity_level(analysis.trust_gap_score or 0),
                claims_analyzed=len(trust_details.get("claims", [])),
                top_gaps=_extract_top_gaps(trust_details),
                trend=trust_details.get("trend", "stable"),
            ),
            power_structure=PowerStructureCard(
                nodes=ps.get("nodes", []),
                edges=ps.get("edges", []),
                clusters=ps.get("clusters", []),
                hidden_powers=_count_hidden_powers(ps),
                ignored_authorities=_count_ignored_authorities(ps),
            ),
            top_influencers=InfluencerCard(
                influencers=analysis.top_influencers or [],
                total_analyzed=len(analysis.top_influencers) if analysis.top_influencers else 0,
            ),
            gatekeepers=GatekeeperCard(
                gatekeepers=analysis.gatekeepers or [],
                decision_gatekeepers=_count_gatekeeper_type(analysis.gatekeepers, "decision"),
                information_gatekeepers=_count_gatekeeper_type(analysis.gatekeepers, "information"),
            ),
            resilience=ResilienceCard(
                resilience_score=analysis.resilience_score or 0,
                risk_level=_resilience_to_risk(analysis.resilience_score or 0),
                single_points_of_failure=analysis.resilience_details.get("single_points_of_failure", []) if analysis.resilience_details else [],
                knowledge_silos=analysis.resilience_details.get("knowledge_silos", []) if analysis.resilience_details else [],
            ),
            decision_velocity=DecisionVelocityCard(
                avg_days=analysis.decision_velocity.get("avg_days", 0) if analysis.decision_velocity else 0,
                benchmark=_velocity_benchmark(analysis.decision_velocity.get("avg_days", 0) if analysis.decision_velocity else 0),
                trend=analysis.decision_velocity.get("trend", "stable") if analysis.decision_velocity else "stable",
                trend_data=analysis.decision_velocity.get("trend_data", []) if analysis.decision_velocity else [],
                bottlenecks=analysis.decision_velocity.get("bottleneck_persons", []) if analysis.decision_velocity else [],
            ),
            system_diagnosis=DiagnosisCard(
                root_causes=analysis.system_diagnosis.get("root_causes", []) if analysis.system_diagnosis else [],
                who_profits=analysis.system_diagnosis.get("who_profits_from_gaps", []) if analysis.system_diagnosis else [],
                predicted_if_unchanged=analysis.system_diagnosis.get("predicted_if_unchanged", "") if analysis.system_diagnosis else "",
                dysfunction_cost_annual=analysis.system_diagnosis.get("dysfunction_cost_annual") if analysis.system_diagnosis else None,
            ),
            predictions=PredictionsCard(
                attrition_risks=analysis.predictions.get("attrition_risk", []) if analysis.predictions else [],
                decision_reversal_risks=analysis.predictions.get("decision_reversals", []) if analysis.predictions else [],
                velocity_forecast=analysis.predictions.get("velocity_trend", "stable") if analysis.predictions else "stable",
                health_forecast_6mo=analysis.predictions.get("org_health_6mo", 5.0) if analysis.predictions else 5.0,
            ),
            contradictions=contradictions,
            positive_signals=positive_signals,
            archetype=archetype,
            confidence_metrics=confidence_metrics,
            recommendations=RecommendationsCard(
                recommendations=analysis.recommendations or [],
                quick_wins=_extract_quick_wins(analysis.recommendations),
                total_potential_savings=_calculate_total_savings(analysis.recommendations),
            ),
        )
        return dashboard.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")


@router.get("/card/{analysis_id}/{card_type}")
async def get_dashboard_card(
    analysis_id: str,
    card_type: str,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
):
    if not _is_demo(analysis_id) and not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    card_mapping = {
        "org_health": lambda: {
            "org_health_score": analysis.org_health_score or 0,
            "health_breakdown": analysis.health_breakdown,
            "grade": _score_to_grade(analysis.org_health_score),
            "summary": _generate_health_summary(analysis.org_health_score, analysis.health_breakdown),
        },
        "trust_gap": lambda: {
            "trust_gap_score": analysis.trust_gap_score,
            "severity": _severity_level(analysis.trust_gap_score or 0),
            "claims_analyzed": len(analysis.trust_gap_details.get("claims", []) if analysis.trust_gap_details else []),
            "top_gaps": _extract_top_gaps(analysis.trust_gap_details),
            "trend": analysis.trust_gap_details.get("trend", "stable") if analysis.trust_gap_details else "stable",
        },
        "power_structure": lambda: {
            "nodes": analysis.power_structure.get("nodes", []) if analysis.power_structure else [],
            "edges": analysis.power_structure.get("edges", []) if analysis.power_structure else [],
            "clusters": analysis.power_structure.get("clusters", []) if analysis.power_structure else [],
            "hidden_powers": _count_hidden_powers(analysis.power_structure),
            "ignored_authorities": _count_ignored_authorities(analysis.power_structure),
        },
        "influencers": lambda: {
            "influencers": analysis.top_influencers or [],
            "total_analyzed": len(analysis.top_influencers) if analysis.top_influencers else 0,
        },
        "gatekeepers": lambda: {
            "gatekeepers": analysis.gatekeepers or [],
            "decision_gatekeepers": _count_gatekeeper_type(analysis.gatekeepers, "decision"),
            "information_gatekeepers": _count_gatekeeper_type(analysis.gatekeepers, "information"),
        },
        "resilience": lambda: {
            "resilience_score": analysis.resilience_score,
            "risk_level": _resilience_to_risk(analysis.resilience_score or 0),
            "single_points_of_failure": analysis.resilience_details.get("single_points_of_failure", []) if analysis.resilience_details else [],
            "knowledge_silos": analysis.resilience_details.get("knowledge_silos", []) if analysis.resilience_details else [],
        },
        "decision_velocity": lambda: {
            "avg_days": analysis.decision_velocity.get("avg_days", 0) if analysis.decision_velocity else 0,
            "benchmark": _velocity_benchmark(analysis.decision_velocity.get("avg_days", 0) if analysis.decision_velocity else 0),
            "trend": analysis.decision_velocity.get("trend", "stable") if analysis.decision_velocity else "stable",
            "trend_data": analysis.decision_velocity.get("trend", []) if analysis.decision_velocity else [],
            "bottlenecks": analysis.decision_velocity.get("bottleneck_persons", []) if analysis.decision_velocity else [],
        },
        "diagnosis": lambda: {
            "root_causes": analysis.system_diagnosis.get("root_causes", []) if analysis.system_diagnosis else [],
            "who_profits": analysis.system_diagnosis.get("who_profits_from_gaps", []) if analysis.system_diagnosis else [],
            "predicted_if_unchanged": analysis.system_diagnosis.get("predicted_if_unchanged", "") if analysis.system_diagnosis else "",
            "dysfunction_cost_annual": analysis.system_diagnosis.get("dysfunction_cost_annual") if analysis.system_diagnosis else None,
        },
        "predictions": lambda: {
            "attrition_risks": analysis.predictions.get("attrition_risk", []) if analysis.predictions else [],
            "decision_reversal_risks": analysis.predictions.get("decision_reversals", []) if analysis.predictions else [],
            "velocity_forecast": analysis.predictions.get("velocity_trend", "stable") if analysis.predictions else "stable",
            "health_forecast_6mo": analysis.predictions.get("org_health_6mo", 5.0) if analysis.predictions else 5.0,
        },
        "recommendations": lambda: {
            "recommendations": analysis.recommendations or [],
            "quick_wins": _extract_quick_wins(analysis.recommendations),
            "total_potential_savings": _calculate_total_savings(analysis.recommendations),
        },
    }

    if card_type not in card_mapping:
        raise HTTPException(status_code=400, detail=f"Unknown card type: {card_type}")
    try:
        return card_mapping[card_type]()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/card/{analysis_id}/data-quality")
async def get_data_quality_card(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
):
    if not _is_demo(analysis_id) and not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from uuid import UUID
    
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.id == UUID(analysis_id))
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    ml_signals = {
        "message_count": analysis.messages_analyzed or 0,
        "employee_count": 0,  
        "person_signals": {},
        "date_range": {
            "start": analysis.date_range_start.isoformat() if analysis.date_range_start else None,
            "end": analysis.date_range_end.isoformat() if analysis.date_range_end else None,
        }
    }
    metrics = ConfidenceCalculator.from_ml_signals(ml_signals)
    confidence_metrics = ConfidenceCalculator.from_ml_signals(ml_signals)
    conf_level = confidence_metrics.get_confidence_level()
    conf_pct = int(confidence_metrics.calculate_base_confidence() * 100)
    warnings = confidence_metrics.get_warnings()

    coverage_func = {
        func: int(cov * 100)
        for func, cov in confidence_metrics.coverage_by_function.items()
    }
    coverage_level = {
        lvl: int(cov * 100)
        for lvl, cov in confidence_metrics.coverage_by_level.items()
    }
    
    if conf_pct < 30:
        recommendation = "⚠️ CRITICAL: Data too limited. Collect more communication data (target: 100+ messages, 30+ days, balanced coverage across teams)."
    elif conf_pct < 50:
        recommendation = "⚠️ LIMITED DATA: Findings below 65% confidence should not drive major decisions. Collect 2-4 more weeks of data."
    elif conf_pct < 70:
        recommendation = "📊 MEDIUM DATA: Some findings actionable (>65% confidence), others still forming. Continue monitoring."
    else:
        recommendation = "✅ GOOD DATA: Confidence is high enough for strategic decisions. Continue collecting to refine findings."
    
    return DataQualityCardSchema(
        overall_confidence=conf_level.value,
        overall_confidence_pct=conf_pct,
        total_messages=confidence_metrics.total_messages,
        total_employees=confidence_metrics.total_employees,
        messages_per_person=round(confidence_metrics.messages_per_person, 2),
        date_range_days=confidence_metrics.date_range_days,
        coverage_by_function=coverage_func,
        coverage_by_level=coverage_level,
        reasoning=[
            f"Only {confidence_metrics.total_messages} messages analyzed",
            f"Coverage spans {confidence_metrics.date_range_days} days",

            "Limited communication volume reduces confidence"
            if confidence_metrics.total_messages < 100
            else "Communication volume sufficient",

            "Insufficient organizational coverage"
            if confidence_metrics.total_employees < 10
            else "Good employee coverage",
        ],

        weak_areas=[
            {
                "signal": "Power Structure",
                "confidence": 30,
                "reason": "Too few interactions to map influence accurately"
            },
            {
                "signal": "Trust Analysis",
                "confidence": 45,
                "reason": "Limited contradiction evidence"
            }
        ] if conf_pct < 60 else [],
        warnings=warnings,
        signals_pending_data=[],  
        data_sufficiency_summary=f"Analysis based on {confidence_metrics.total_messages} messages across {confidence_metrics.total_employees} people over {confidence_metrics.date_range_days} days.",
        recommendation=recommendation,
    )


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


def _generate_health_summary(score: float, breakdown: dict) -> str:
    grade = _score_to_grade(score)
    if grade == "A":
        return "Organization health is strong. Continue monitoring."
    elif grade == "B":
        return "Organization is healthy with some areas for improvement."
    elif grade == "C":
        return "Organization shows moderate dysfunction. Address key issues soon."
    elif grade == "D":
        return "Organization has significant challenges that need urgent attention."
    else:
        return "Organization is in critical condition. Immediate intervention required."


def _extract_top_gaps(details: dict) -> list:
    if not details or "claims" not in details:
        return []
    claims = details.get("claims", [])
    return sorted(claims, key=lambda x: x.get("gap", 0), reverse=True)[:3]


def _count_hidden_powers(structure: dict) -> int:
    if not structure or "nodes" not in structure:
        return 0
    return sum(1 for node in structure["nodes"] if node.get("type") == "hidden_power")


def _count_ignored_authorities(structure: dict) -> int:
    if not structure or "nodes" not in structure:
        return 0
    return sum(1 for node in structure["nodes"] if node.get("type") == "ignored_authority")


def _count_gatekeeper_type(gatekeepers: list, gk_type: str) -> int:
    if not gatekeepers:
        return 0
    return sum(1 for gk in gatekeepers if gk.get("gatekeeper_type") in [gk_type, "both"])


def _extract_quick_wins(recommendations: list) -> list:
    if not recommendations:
        return []
    return [r for r in recommendations if r.get("impact") == "high" and r.get("effort") == "low"][:3]


def _calculate_total_savings(recommendations: list) -> str:
    if not recommendations:
        return None
    total = 0
    for rec in recommendations:
        cost_str = rec.get("cost_if_ignored", "$0")
        try:
            cost_val = int(''.join(filter(str.isdigit, cost_str.split()[0])))
            total += cost_val
        except:
            pass
    if total > 0:
        if total >= 1_000_000:
            return f"${total / 1_000_000:.1f}M"
        elif total >= 1_000:
            return f"${total / 1_000:.1f}K"
        return f"${total}"
    return None

@router.post("/classify-nodes")
async def classify_nodes(
    payload: dict,
    token: Optional[str] = Depends(oauth2_scheme),
):
    from groq import Groq
    import os, json
    
    nodes = payload.get("nodes", [])
    if not nodes:
        return {"nodes": []}
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    lines = "\n".join([
        f"{i+1}. {n.get('name')} | Title: {n.get('title','N/A')} | "
        f"Dept: {n.get('department','N/A')} | "
        f"Formal authority: {n.get('formal_authority','N/A')} | "
        f"Actual influence: {n.get('actual_influence','N/A')}"
        for i, n in enumerate(nodes)
    ])
    
    prompt = f"""You are an expert organizational analyst. Classify each person's org level and power type.

PEOPLE:
{lines}

CLASSIFICATION RULES:
Level (pick exactly one): C-Suite, VP, Director, Manager, Senior IC, IC
  - C-Suite: CEO, CFO, CTO, COO, CPO, CHRO, CMO, CRO, President, Co-founder
  - VP: Vice President, SVP, EVP, Head of dept at senior level
  - Director: Director, Sr Director, Principal
  - Manager: Manager, Team Lead, Eng Lead, Tech Lead
  - Senior IC: Senior anything, Staff, Principal IC, Architect
  - IC: Engineer, Analyst, Designer, PM, Coordinator, Associate (no seniority prefix)

Power type (pick exactly one): hidden_power, formal_leader, ignored_authority, gatekeeper, neutral
  - hidden_power: actual_influence exceeds formal_authority by 1.5+ points
  - formal_leader: formal_authority >= 7.5 AND actual_influence approximately equals formal (within 1.5)
  - ignored_authority: formal_authority exceeds actual_influence by 1.5+
  - gatekeeper: controls access to information or decisions regardless of scores
  - neutral: none of the above

Return ONLY a valid JSON array, no markdown, no explanation:
[{{"name":"...","level":"...","power_type":"..."}}]"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        classified = json.loads(raw)
        name_map = {c["name"].lower().strip(): c for c in classified}
        result = []
        for node in nodes:
            match = name_map.get((node.get("name") or "").lower().strip(), {})
            result.append({
                **node,
                "level": match.get("level") or node.get("level") or "IC",
                "power_type": match.get("power_type") or node.get("type") or "neutral",
            })
        return {"nodes": result}
    except Exception as e:
        logger.error(f"Node classification error: {e}")
        result = []
        for node in nodes:
            fa = node.get("formal_authority", 0)
            ai = node.get("actual_influence", 0)
            if ai - fa > 1.5:
                power_type = "hidden_power"
            elif fa >= 7.5 and abs(ai - fa) <= 1.5:
                power_type = "formal_leader"
            elif fa - ai > 1.5:
                power_type = "ignored_authority"
            else:
                power_type = "neutral"
            result.append({**node, "power_type": power_type})
        return {"nodes": result}


@router.post("/chat/{analysis_id}")
async def chat_with_analysis(
    analysis_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
):
    if not _is_demo(analysis_id) and not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from groq import Groq
    import os, json
    
    messages = payload.get("messages", [])
    context = payload.get("context", {})
    
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an expert organizational analyst embedded inside OrgLens.
You analyze ONLY organizational structure, operational bottlenecks, leadership effectiveness, 
workflow patterns, governance, collaboration dynamics, decision systems, organizational risks.
Use ONLY evidence available in the analysis data.
Keep responses concise (2-4 paragraphs max).

ANALYSIS DATA:
{json.dumps(context, indent=2)}"""
                },
                *[{"role": m["role"], "content": m["content"]} for m in messages[-6:]]
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")
