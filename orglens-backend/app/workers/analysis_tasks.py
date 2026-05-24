from dotenv import load_dotenv
load_dotenv()
#from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from loguru import logger
import uuid
import asyncio
import json
from app.services.ingestion.deduplicator import deduplicate_power_nodes
from app.config import settings
from app.models import (
    AnalysisReport, AnalysisStatus, Organization, Message, Employee, Decision,
    MessageSource, DecisionStatus
)
from app.services.nlp import DecisionExtractor, InfluenceScorer, SentimentAnalyzer
from app.services.ml import NetworkAnalyzer, InfluenceModel, Predictor
from app.services.diagnostics import TrustGapCalculator, ResilienceCalculator, OrgHealthCalculator, RecommendationEngine
from app.services.confidence.claim_extractor import ClaimExtractor
from app.services.confidence.contradiction_detector import ContradictionDetector
from app.services.confidence.positive_signals import PositiveSignalDetector
from app.services.confidence.org_archetype import ArchetypeClassifier
from app.services.confidence.confidence_framework import ConfidenceCalculator

#@shared_task(bind=True, max_retries=3)
#def analyze_organization(self, org_id: str, analysis_id: str):
    #"""
    #Main task that orchestrates the entire analysis pipeline.
    #Runs async operations properly within the Celery task.
    #"""
    #logger.info(f"Starting analysis for org {org_id}, analysis {analysis_id}")

    #try:
        #result = asyncio.run(
            #_async_analysis_pipeline(org_id, analysis_id)
        #)
        #logger.info(f"Analysis completed for org {org_id}")
        #return result

    #except Exception as exc:
        #logger.error(f"Analysis failed: {str(exc)}")
        #raise self.retry(exc=exc, countdown=60)


async def _async_analysis_pipeline(org_id: str, analysis_id: str):
    """
    Full pipeline:
    Step 1: Load data
    Step 2: Old NLP (enrich messages in DB)
    Step 3: New ML signal extraction (objective signals)
    Step 4: Groq AI narration (uses ML signals as constraints)
    Step 5: Save everything
    """
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with SessionLocal() as session:

            async def update_progress(step: int, total_steps: int = 5):
                analysis = await session.get(AnalysisReport, uuid.UUID(analysis_id))
                if analysis:
                    analysis.progress = int((step / total_steps) * 100)
                    await session.commit()

            logger.info("Step 1: Loading data...")
            org, employees, messages = await _load_org_data(session, org_id)

            analysis = await session.get(AnalysisReport, uuid.UUID(analysis_id))
            analysis.status = AnalysisStatus.PROCESSING
            await session.commit()
            await update_progress(1)

            logger.info("Step 2: NLP enrichment...")
            decisions, _ = await _nlp_pipeline(session, org_id, messages)
            await update_progress(2)

            logger.info("Step 3: ML signal extraction...")
            from app.services.ai_analysis import MLSignalExtractor, GroqNarrator

            employee_list = []
            for emp_id, emp_obj in employees.items():
                title = emp_obj.title or ""
                level = emp_obj.level or emp_obj.title or "" 
                dept = emp_obj.department or ""
                employee_list.append({
                    "id": str(emp_obj.id),
                    "name": emp_obj.name or "",
                    "title": title,
                    "level": level,
                    "department": dept,
                    "influence_score": emp_obj.influence_score or 0,
                    "formal_authority_score": emp_obj.formal_authority_score or 5.0,
                    "flight_risk": _infer_flight_risk(emp_obj),
                    "collaboration": emp_obj.credibility_score or 0.5,
                    "performance_rating": 7,
                    "tenure_months": emp_obj.tenure_months or 0,
                })

            message_list = []
            for m in messages:
                if not m.content:
                    continue
                message_list.append({
                    "source": m.source.value if hasattr(m.source, "value") else str(m.source),
                    "sender_raw": m.sender_raw or "",
                    "channel_or_thread": m.channel_or_thread or "",
                    "content": m.content,
                    "timestamp": str(m.timestamp),
                    "contains_decision": m.contains_decision or False,
                    "contains_objection": m.contains_objection or False,
                    "sentiment_score": m.sentiment_score or 0,
                    "urgency_score": m.urgency_score or 0,
                    "influence_signal": m.influence_signal or 0,
                    "topics": m.topics or [],
                })

            org_context = {
                "name": org.name,
                "industry": org.industry or "",
                "size_estimate": org.size_estimate or 0,
                "mission_statement": org.mission_statement or "",
            }

            extractor = MLSignalExtractor()
            ml_signals = extractor.extract_all_signals(
                employee_list, message_list, org_context
            )

            classic_ml = await _compute_classic_ml_scores(
                session, org_id, messages, decisions, employees
            )
            ml_signals["classic_ml_scores"] = classic_ml
            enrichment = _run_enrichment_analysis(ml_signals, org.mission_statement or "")
            ml_signals["contradictions"] = enrichment["contradictions"]
            ml_signals["positive_signals"] = enrichment["positive_signals"]
            ml_signals["archetype"] = enrichment["archetype"]
            ml_signals["confidence_metrics"] = enrichment["confidence_metrics"]

            logger.info(
                f"ML signals extracted: "
                f"{len(ml_signals.get('person_signals', {}))} persons, "
                f"{ml_signals.get('message_count', 0)} messages"
            )
            await update_progress(3)

            logger.info("Step 4: Groq AI narration...")
            narrator = GroqNarrator()
            ai_result = narrator.generate_analysis(ml_signals)

            logger.info(
                f"Groq result: "
                f"influencers={len(ai_result.get('top_influencers') or [])}, "
                f"gatekeepers={len(ai_result.get('gatekeepers') or [])}, "
                f"recommendations={len(ai_result.get('recommendations') or [])}, "
                f"root_causes={len((ai_result.get('system_diagnosis') or {}).get('root_causes') or [])}"
            )
            await update_progress(4)

            logger.info("Step 5: Saving results...")
            await _save_ai_analysis_results(
                session, analysis_id, org_id, ai_result, ml_signals, messages
            )
            await update_progress(5)

            return {"status": "success", "analysis_id": analysis_id}

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        async with SessionLocal() as session:
            analysis = await session.get(AnalysisReport, uuid.UUID(analysis_id))
            if analysis:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = str(e)[:500]
                analysis.progress = 0
                await session.commit()
        raise
    finally:
        await engine.dispose()


 
def _run_enrichment_analysis(ml_signals: dict, org_context_text: str) -> dict:
    """
    Run ClaimExtractor → ContradictionDetector → PositiveSignalDetector
    → ArchetypeClassifier → ConfidenceCalculator.
    Returns serializable dicts ready for DB storage.
    """
    from app.services.confidence.claim_extractor import ClaimExtractor
    from app.services.confidence.contradiction_detector import ContradictionDetector
    from app.services.confidence.positive_signals import PositiveSignalDetector
    from app.services.confidence.org_archetype import ArchetypeClassifier
    from app.services.confidence.confidence_framework import ConfidenceCalculator
 
    claims = ClaimExtractor(org_context_text).extract_claims()
    logger.info(f"  Claims extracted: {len(claims)}")
 
    signals_for_detector = dict(ml_signals)
    trust_s = ml_signals.get("trust_signals", {})
    vel_s = ml_signals.get("velocity_signals", {})
    dec_s = ml_signals.get("decision_signals", {})
    signals_for_detector.setdefault("avg_decision_days", dec_s.get("estimated_avg_days", 14))
    signals_for_detector.setdefault("trust_gap_score", trust_s.get("trust_gap_score", 0))
    signals_for_detector.setdefault("avg_approval_depth",
        dec_s.get("approval_chain_count", 0) / max(dec_s.get("decision_count", 1), 1) + 1)
    signals_for_detector["ml_signals"] = {
        "comp_inversion_count": len(trust_s.get("comp_inversion_evidence", [])),
        "promotion_complaints": trust_s.get("promotion_complaint_count", 0),
        "escalation_rate": trust_s.get("escalation_rate", 0),
        "oversight_mentions": sum(
            1 for m in ml_signals.get("velocity_signals", {}).get("delay_snippets", [])
            if any(w in (m or "").lower() for w in ["status check", "daily standup", "review", "oversight"])
        ),
        "attrition_risk_count": ml_signals.get("resilience_signals", {}).get("high_flight_risk_count", 0),
    }
 
    contradictions = ContradictionDetector(claims, signals_for_detector).detect_all()
    logger.info(f"  Contradictions detected: {len(contradictions)}")
 
    positive_signals = PositiveSignalDetector(ml_signals).detect_all()
    logger.info(f"  Positive signals detected: {len(positive_signals)}")
 
    arch_signals = dict(ml_signals)
    arch_signals.setdefault("avg_decision_days", dec_s.get("estimated_avg_days", 14))
    arch_signals.setdefault("org_health_score",
        _rough_health_from_signals(ml_signals))
    arch_signals.setdefault("resilience_score", 5.0)
    arch_signals.setdefault("trust_gap_score", trust_s.get("trust_gap_score", 0))
 
    archetype_profile = ArchetypeClassifier(arch_signals, contradictions).classify()
 
    confidence_metrics = ConfidenceCalculator.from_ml_signals(ml_signals)
    conf_pct = int(confidence_metrics.calculate_base_confidence() * 100)
    conf_level = confidence_metrics.get_confidence_level().value
    warnings = confidence_metrics.get_warnings()
 
    def _serialize_contradiction(c):
        return {
            "claim": c.claim,
            "observed_reality": c.observed_reality,
            "gap_score": round(c.gap_score, 2),
            "severity": c.severity.value if hasattr(c.severity, "value") else str(c.severity),
            "evidence_quotes": c.evidence_quotes,
            "root_causes": c.root_causes,
            "impact": c.impact,
            "recommendation": c.recommendation,
        }
 
    def _serialize_positive(s):
        return {
            "category": s.category.value if hasattr(s.category, "value") else str(s.category),
            "description": s.description,
            "strength_score": round(s.strength_score, 2),
            "evidence": s.evidence,
            "affected_people": s.affected_people,
            "affected_functions": s.affected_functions,
            "growth_potential": s.growth_potential,
            "confidence_pct": getattr(s, "confidence_pct", 80), 
            "momentum": getattr(s, "momentum", "stable"),         
        }
 
    def _serialize_archetype(a):
        return {
            "archetype": a.archetype.value if hasattr(a.archetype, "value") else str(a.archetype),
            "name": a.name,
            "description": a.description,
            "strengths": a.strengths,
            "vulnerabilities": a.vulnerabilities,
            "recommended_focus": a.recommended_focus,
            "confidence_pct": a.confidence_pct,                    
            "classification_reasons": a.classification_reasons,    
            "supporting_metrics": a.supporting_metrics,            
            "risk_level": a.risk_level,                           
            "trajectory": a.trajectory,                            
        }
 
    return {
        "contradictions": [_serialize_contradiction(c) for c in contradictions],
        "positive_signals": [_serialize_positive(s) for s in positive_signals],
        "archetype": _serialize_archetype(archetype_profile),
        "confidence_metrics": {
            "overall_confidence": conf_level,
            "overall_confidence_pct": conf_pct,
            "total_messages": confidence_metrics.total_messages,
            "total_employees": confidence_metrics.total_employees,
            "messages_per_person": round(confidence_metrics.messages_per_person, 2),
            "date_range_days": confidence_metrics.date_range_days,
            "coverage_by_function": {
                k: int(v * 100) for k, v in confidence_metrics.coverage_by_function.items()
            },
            "coverage_by_level": {
                k: int(v * 100) for k, v in confidence_metrics.coverage_by_level.items()
            },
            "confidence_breakdown": confidence_metrics.confidence_breakdown,
            "strengths_detected": confidence_metrics.strengths_detected,
            "limitations_detected": confidence_metrics.limitations_detected,
            "recommended_data_improvements": confidence_metrics.recommended_data_improvements,
            "warnings": confidence_metrics.get_warnings(),
        }
    }
 
 
def _rough_health_from_signals(ml_signals: dict) -> float:
    """Quick org health estimate from raw ML signals for archetype classifier."""
    trust_score = ml_signals.get("trust_signals", {}).get("trust_gap_score", 0)
    negative_ratio = ml_signals.get("sentiment_signals", {}).get("negative_ratio", 0.3)
    conflict_ratio = ml_signals.get("conflict_signals", {}).get("conflict_ratio", 0.1)
    health = 10 - (trust_score * 0.4) - (negative_ratio * 10 * 0.3) - (conflict_ratio * 10 * 0.3)
    return max(1.0, min(10.0, round(health, 2)))
 
 
def _confidence_recommendation(conf_pct: int) -> str:
    if conf_pct < 30:
        return "⚠️ CRITICAL: Data too limited. Collect more communication data (target: 100+ messages, 30+ days, balanced coverage)."
    elif conf_pct < 50:
        return "⚠️ LIMITED DATA: Findings below 65% confidence should not drive major decisions. Collect 2–4 more weeks of data."
    elif conf_pct < 70:
        return "📊 MEDIUM DATA: Some findings actionable (>65% confidence), others still forming. Continue monitoring."
    else:
        return "✅ GOOD DATA: Confidence is high enough for strategic decisions. Continue collecting to refine findings."
    


async def _load_org_data(session: AsyncSession, org_id: str):
    """
    Load organization, employees, messages from database.
    CRITICAL: Use selectinload() to eagerly fetch relationships
    """
    from uuid import UUID
    org_result = await session.execute(
        select(Organization).where(Organization.id == UUID(org_id))
    )
    org = org_result.scalar_one_or_none()

    emp_result = await session.execute(
        select(Employee).where(Employee.org_id == UUID(org_id))
    )
    employees_list = emp_result.scalars().all()
    employees = {str(e.id): e for e in employees_list}

    msg_result = await session.execute(
        select(Message)
        .where(Message.org_id == UUID(org_id))
        .options(selectinload(Message.sender))  
    )
    messages = msg_result.scalars().all()

    logger.info(f"Loaded: {len(employees)} employees, {len(messages)} messages")

    return org, employees, messages


async def _nlp_pipeline(session: AsyncSession, org_id: str, messages: list) -> tuple:
    """
    Extract decisions and influence signals from messages.
    Messages are already loaded, so no lazy loading will occur.
    """
    decision_extractor = DecisionExtractor()
    influence_scorer = InfluenceScorer()
    sentiment_analyzer = SentimentAnalyzer()

    all_decisions = []
    message_updates = []

    for msg in messages:
        if not msg.content or len(msg.content) < 20:
            continue

        decisions = decision_extractor.extract_decisions(msg.content)
        objections = decision_extractor.extract_objections(msg.content)
        influence_signals = decision_extractor.extract_influence_signals(msg.content)

        sentiment = sentiment_analyzer.analyze_sentiment(msg.content)
        urgency = sentiment_analyzer.analyze_urgency(msg.content)
        tone = sentiment_analyzer.analyze_tone(msg.content)

        msg.contains_decision = len(decisions) > 0
        msg.contains_objection = len(objections) > 0
        msg.sentiment_score = sentiment.get("sentiment_score", 0)
        msg.urgency_score = urgency.get("urgency_score", 0)
        msg.decision_keywords = [d.get("type") for d in decisions]
        msg.topics = list(set([d.get("domain") for d in decisions if d.get("domain")]))
        msg.influence_signal = influence_signals.get("influence_signal", 0)

        message_updates.append(msg)

        for decision in decisions:
            all_decisions.append({
                "title": decision.get("text", ""),
                "domain": decision.get("domain"),
                "status": DecisionStatus.PROPOSED,
                "proposer_id": msg.sender_id,
                "source_message_ids": [str(msg.id)],
                "proposed_at": msg.timestamp,
            })

    for msg in message_updates:
        await session.merge(msg)
    await session.commit()

    logger.info(f"Extracted {len(all_decisions)} decision moments")
    return all_decisions, None


async def _network_pipeline(messages: list, employees: dict) -> dict:
    """
    Build communication network from message patterns.
    """
    network_analyzer = NetworkAnalyzer()

    message_data = []
    for msg in messages:
        if msg.sender_id:
            message_data.append({
                "sender_id": str(msg.sender_id),
                "recipient_ids": [str(emp_id) for emp_id in employees.keys()],
                "content": msg.content or "",
                "timestamp": msg.timestamp,
                "influence_score": msg.influence_signal or 0.5,
            })

    network = network_analyzer.build_communication_network(message_data, employees)

    gatekeepers = network_analyzer.identify_gatekeepers(network.get("graph"))
    isolated = network_analyzer.identify_isolated_experts(network.get("graph"))
    alliances = network_analyzer.detect_alliances(network.get("graph"))

    return {
        "network": network,
        "gatekeepers": gatekeepers,
        "isolated_experts": isolated,
        "alliances": alliances,
    }


async def _ml_pipeline(
    session: AsyncSession,
    org_id: str,
    messages: list,
    decisions: list,
    employees: dict,
    network_data: dict,
) -> dict:
    """
    Train ML models and calculate influence scores.
    """
    influence_model = InfluenceModel()
    predictor = Predictor(influence_model)

    influence_scores = {}

    for emp_id, emp_obj in employees.items():
        emp_messages = [m for m in messages if str(m.sender_id) == emp_id]
        messages_count = len(emp_messages)
        avg_influence = sum(m.influence_signal or 0.5 for m in emp_messages) / max(messages_count, 1)

        emp_obj.influence_score = min(avg_influence * 10, 10.0)
        emp_obj.formal_authority_score = 5.0

        influence_scores[emp_id] = {
            "messages_count": messages_count,
            "avg_influence": avg_influence,
            "influence_score": emp_obj.influence_score,
        }

    await session.commit()
    logger.info(f"Calculated influence scores for {len(influence_scores)} employees")
    return influence_scores


async def _diagnostics_pipeline(
    session: AsyncSession,
    org_id: str,
    org: Organization,
    employees: dict,
    decisions: list,
    network_data: dict,
    influence_scores: dict,
) -> dict:
    """
    Run all diagnostic calculators.
    """
    trust_gap_calc = TrustGapCalculator()
    resilience_calc = ResilienceCalculator()
    org_health_calc = OrgHealthCalculator()

    org_claims = {
        "transparency": org.stated_values.get("transparency", "") if org.stated_values else "",
        "meritocracy": org.stated_values.get("meritocracy", "") if org.stated_values else "",
    }

    actual_data = {
        "approval_chain_length": 5,
        "referral_hire_percent": 0.65,
        "avg_meetings_per_week": 15,
        "risky_projects_approved_percent": 0.3,
    }

    trust_gap_result = trust_gap_calc.calculate_trust_gap(org_claims, actual_data)
    resilience_result = resilience_calc.calculate_resilience_score(
        single_points_of_failure=[],
        knowledge_silos=[],
        decision_distribution={},
        department_cross_training={},
    )

    org_health_result = org_health_calc.calculate_org_health_score(
        trust_gap_score=trust_gap_result.get("trust_gap_score", 5),
        resilience_score=resilience_result,
        decision_velocity_days=21,
        decision_quality_score=6.5,
        alignment_score=5.0,
        information_flow_score=6.0,
    )

    return {
        "trust_gap": trust_gap_result,
        "resilience": {
            "resilience_score": resilience_result,
            "single_points_of_failure": [],
            "knowledge_silos": [],
        },
        "org_health": org_health_result,
        "power_structure": network_data.get("network", {}),
    }

def _infer_flight_risk(emp_obj) -> str:
    """
    Infer flight risk from available employee data.
    Uses tenure, influence gap, and credibility signals.
    """
    tenure = emp_obj.tenure_months or 0
    if tenure < 12:
        return "high"
    elif tenure < 24:
        return "medium"

    influence = emp_obj.influence_score or 0
    authority = emp_obj.formal_authority_score or 5.0
    if influence > authority + 3:
        return "high"
    elif influence > authority + 1.5:
        return "medium"

    return "low"


async def _compute_classic_ml_scores(
    session,
    org_id: str,
    messages: list,
    decisions: list,
    employees: dict,
) -> dict:
    """
    Run the classic ML pipeline (NetworkAnalyzer, InfluenceModel, etc.)
    and return structured scores that get injected into ml_signals.
    These complement the new MLSignalExtractor scores.
    """
    from app.services.ml import NetworkAnalyzer, InfluenceModel, Predictor

    network_analyzer = NetworkAnalyzer()
    influence_model = InfluenceModel()
    predictor = Predictor(influence_model)

    message_data = []
    for msg in messages:
        if msg.sender_id:
            message_data.append({
                "sender_id": str(msg.sender_id),
                "recipient_ids": [str(emp_id) for emp_id in employees.keys()],
                "content": msg.content or "",
                "timestamp": msg.timestamp,
                "influence_score": msg.influence_signal or 0.5,
            })

    network = network_analyzer.build_communication_network(message_data, employees)
    graph = network.get("graph")

    gatekeepers = []
    isolated = []
    alliances = []

    if graph and graph.number_of_nodes() > 0:
        gatekeepers = network_analyzer.identify_gatekeepers(graph)
        isolated = network_analyzer.identify_isolated_experts(graph)
        alliances = network_analyzer.detect_alliances(graph)

    per_employee_scores = {}
    for emp_id, emp_obj in employees.items():
        emp_messages = [m for m in messages if str(m.sender_id) == emp_id]
        msg_count = len(emp_messages)
        avg_influence = (
            sum(m.influence_signal or 0.5 for m in emp_messages) / max(msg_count, 1)
        )
        influence_score = min(avg_influence * 10, 10.0)

        emp_obj.influence_score = influence_score
        emp_obj.formal_authority_score = 5.0

        per_employee_scores[emp_id] = {
            "influence_score": round(influence_score, 2),
            "message_count": msg_count,
            "avg_signal": round(avg_influence, 3),
        }

    await session.commit()

    return {
        "network_nodes": network.get("nodes", []),
        "network_edges": network.get("edges", []),
        "network_clusters": network.get("clusters", []),
        "network_centrality": network.get("centrality_metrics", {}),
        "ml_gatekeepers": gatekeepers[:5],
        "ml_isolated_experts": isolated[:5],
        "ml_alliances": alliances[:3],
        "per_employee_influence": per_employee_scores,
        "total_edges": len(network.get("edges", [])),
    }
async def _recommendations_pipeline(diagnostics: dict) -> list:
    """
    Generate recommendations based on diagnostics.
    """
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(diagnostics)
    return recommendations


async def _save_ai_analysis_results(
    session: AsyncSession,
    analysis_id: str,
    org_id: str,
    ai_result: dict,
    ml_signals: dict,
    messages: list,
):
    """
    Save combined ML + Groq AI results.
    ML signals provide objective metadata.
    Groq provides narratives, names, and explanations.
    ⚠️ KEY: Every card now includes reasoning/explanation fields
    """
    from uuid import UUID

    analysis = await session.get(AnalysisReport, UUID(analysis_id))
    if not analysis:
        logger.warning(f"Analysis {analysis_id} not found")
        return

    analysis.status = AnalysisStatus.COMPLETED
    analysis.completed_at = datetime.utcnow()
    analysis.messages_analyzed = len(messages)
    if ai_result.get("power_structure", {}).get("nodes"):
        ai_result["power_structure"]["nodes"] = deduplicate_power_nodes(
            ai_result["power_structure"]["nodes"]
        )
    if ai_result.get("top_influencers"):
        seen = set()
        ai_result["top_influencers"] = [
            inf for inf in ai_result["top_influencers"]
            if not (inf.get("name", "").lower() in seen or seen.add(inf.get("name", "").lower()))
        ]
    computed = ml_signals.get("computed_scores") or {}

    org_health = ai_result.get("org_health") or {}
    analysis.org_health_score = float(
        org_health.get("org_health_score")
        or computed.get("health_score")
        or 5.0
    )
    analysis.health_breakdown = (
        org_health.get("health_breakdown")
        or computed.get("health_breakdown")
        or {}
    )

    trust_gap = ai_result.get("trust_gap") or {}
    analysis.trust_gap_score = float(
        trust_gap.get("trust_gap_score")
        or computed.get("trust_gap_score")
        or 5.0
    )
    analysis.trust_gap_details = {
        "trust_gap_score": analysis.trust_gap_score,
        "severity": trust_gap.get("severity") or "medium",
        "alignment_score": trust_gap.get("alignment_score"),
        "trend": trust_gap.get("trend") or "stable",
        "claims": trust_gap.get("claims") or [],
        "ml_evidence": {
            "comp_inversion_count": len(
                ml_signals.get("trust_signals", {}).get("comp_inversion_evidence") or []
            ),
            "promotion_complaints": ml_signals.get("trust_signals", {}).get(
                "promotion_complaint_count", 0
            ),
            "escalation_rate": ml_signals.get("trust_signals", {}).get("escalation_rate", 0),
        },
    }

    person_signals = ml_signals.get("person_signals") or {}
    groq_power = ai_result.get("power_structure") or {}

    groq_node_map = {}
    for n in (groq_power.get("nodes") or []):
        name = (n.get("name") or "").lower().strip()
        if name:
            groq_node_map[name] = n

    level_authority = {
        "c-suite": 9.5, "vp": 8.0, "director": 7.0, "manager": 5.5,
        "senior ic": 4.5, "sr ic": 4.5, "ic": 3.0,
    }

    def _infer_power_type(influence: float, authority: float, groq_type: str) -> str:
        """Rule-based power type as ground truth, Groq as hint only."""
        gap = influence - authority
        if groq_type in ("hidden_power", "formal_leader", "ignored_authority", "gatekeeper"):
            return groq_type  
        if gap > 1.5:
            return "hidden_power"
        if authority >= 7.5 and abs(gap) <= 1.5:
            return "formal_leader"
        if gap < -1.5:
            return "ignored_authority"
        return "neutral"

    all_nodes = []
    for name, signals in person_signals.items():
        level_raw = str(signals.get("level") or "").lower().strip()
        formal_authority = level_authority.get(level_raw, signals.get("formal_authority", 5.0))
        actual_influence = round(signals.get("influence_score") or 0.0, 2)

        groq_node = groq_node_map.get(name.lower().strip(), {})
        groq_type = groq_node.get("type") or "neutral"
        power_type = _infer_power_type(actual_influence, formal_authority, groq_type)

        all_nodes.append({
            "id": name,
            "name": name,
            "title": signals.get("title") or "",
            "level": signals.get("level") or "",
            "department": signals.get("department") or "",
            "formal_authority": round(formal_authority, 2),
            "actual_influence": actual_influence,
            "type": power_type,
            "evidence": groq_node.get("evidence") or "",
        })

    level_order = ["c-suite", "vp", "director", "manager", "senior ic", "sr ic", "ic", ""]
    all_nodes.sort(key=lambda n: (
        level_order.index(n.get("level", "").lower()) if n.get("level", "").lower() in level_order else 99,
        -n.get("actual_influence", 0)
    ))

    power_structure = {
        "nodes": all_nodes,
        "edges": groq_power.get("edges") or [],
        "clusters": groq_power.get("clusters") or [],
        "hidden_powers": sum(1 for n in all_nodes if n.get("type") == "hidden_power"),
        "ignored_authorities": sum(1 for n in all_nodes if n.get("type") == "ignored_authority"),
    }

    try:
        json.dumps(power_structure)
        analysis.power_structure = power_structure
    except (TypeError, ValueError):
        analysis.power_structure = {"nodes": [], "edges": [], "clusters": []}

    top_influencers = ai_result.get("top_influencers") or []
    if not top_influencers:
        person_signals = ml_signals.get("person_signals") or {}
        top_influencers = [
            {
                "name": name,
                "title": signals.get("title", ""),
                "influence_score": signals.get("influence_score", 0),
                "formal_authority": signals.get("formal_authority", 5.0),
                "gap": (
                    "high" if abs(signals.get("authority_gap", 0)) > 3
                    else "medium" if abs(signals.get("authority_gap", 0)) > 1.5
                    else "low"
                ),
                "type": "neutral",
                "evidence": [],
            }
            for name, signals in sorted(
                person_signals.items(),
                key=lambda x: x[1].get("influence_score", 0),
                reverse=True,
            )[:10]
        ]
    analysis.top_influencers = top_influencers

    gatekeepers = ai_result.get("gatekeepers") or []
    if not gatekeepers:
        gk_signals = ml_signals.get("network_signals", {}).get("gatekeeper_signals") or {}
        classic_gk = (ml_signals.get("classic_ml_scores") or {}).get("ml_gatekeepers") or []
        gatekeepers = [
            {
                "name": name,
                "gatekeeper_type": "information",
                "blocks_count": count,
                "credibility_score": 0.5,
                "power_play_score": 0.5,
                "domains": [],
                "summary": f"Mentioned {count} times as a blocker in communications.",
                "specific_examples": [],
            }
            for name, count in sorted(gk_signals.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    analysis.gatekeepers = gatekeepers

    resilience = ai_result.get("resilience") or {}
    analysis.resilience_score = float(
        resilience.get("resilience_score")
        or computed.get("resilience_score")
        or 5.0
    )
    spofs = resilience.get("single_points_of_failure") or []
    if not spofs:
        res_signals = ml_signals.get("resilience_signals") or {}
        spofs = [
            {
                "name": name,
                "title": "",
                "impact_if_leaves": 7.0,
                "risk_level": "high",
                "estimated_departure_probability": 0.65,
                "reason": "Identified as high flight risk from HR data",
                "knowledge_domains": [],
            }
            for name in (res_signals.get("high_flight_risk_employees") or [])[:5]
        ]
    analysis.resilience_details = {
        "overall": analysis.resilience_score,
        "risk_level": resilience.get("risk_level") or "medium",
        "single_points_of_failure": spofs,
        "knowledge_silos": resilience.get("knowledge_silos") or [],
        "ml_signals": {
            "ownership_gaps": len(
                (ml_signals.get("resilience_signals") or {}).get("ownership_gaps") or []
            ),
            "departure_mentions": (ml_signals.get("resilience_signals") or {}).get(
                "departure_mention_count", 0
            ),
        },
    }

    velocity = ai_result.get("decision_velocity") or {}
    analysis.decision_velocity = {
        "avg_days": float(
            velocity.get("avg_days")
            or computed.get("avg_decision_days")
            or 21
        ),
        "benchmark": velocity.get("benchmark") or "slow",
        "trend": velocity.get("trend") or "stable",
        "trend_data": velocity.get("trend_data") or [],
        "bottleneck_persons": velocity.get("bottleneck_persons") or [],
        "ml_signals": {
            "delay_message_count": (ml_signals.get("velocity_signals") or {}).get(
                "delay_message_count", 0
            ),
            "domain_delays": (ml_signals.get("velocity_signals") or {}).get(
                "domain_delays", {}
            ),
            "approval_chain_count": (ml_signals.get("decision_signals") or {}).get(
                "approval_chain_count", 0
            ),
        },
    }

    diagnosis = ai_result.get("system_diagnosis") or {}
    root_causes = diagnosis.get("root_causes") or []
    if not root_causes:
        conflict = ml_signals.get("conflict_signals") or {}
        if conflict.get("conflict_message_count", 0) > 3:
            root_causes.append({
                "system": "governance",
                "issue": f"Cross-team conflicts detected in {conflict.get('conflict_message_count')} messages",
                "severity": "high",
                "fixable": True,
                "evidence": str(conflict.get("conflict_messages", [{}])[0].get("snippet", ""))[:200],
                "cascade_effects": "Slowing decisions and reducing collaboration",
            })
        vel = ml_signals.get("velocity_signals") or {}
        if vel.get("delay_message_count", 0) > 2:
            root_causes.append({
                "system": "process",
                "issue": f"Decision delays detected across {vel.get('delay_message_count')} messages",
                "severity": "medium",
                "fixable": True,
                "evidence": str((vel.get("delay_snippets") or [""])[0])[:200],
                "cascade_effects": "Blocking execution and frustrating teams",
            })
    analysis.system_diagnosis = {
        "root_causes": root_causes,
        "who_profits_from_gaps": diagnosis.get("who_profits_from_gaps") or [],
        "predicted_if_unchanged": diagnosis.get("predicted_if_unchanged") or "",
        "dysfunction_cost_annual": diagnosis.get("dysfunction_cost_annual"),
    }

    predictions = ai_result.get("predictions") or {}
    attrition_risks = predictions.get("attrition_risk") or []
    if not attrition_risks:
        for person in (computed.get("flight_risk_persons") or []):
            attrition_risks.append({
                "name": person.get("name"),
                "title": person.get("title", ""),
                "probability": person.get("score", 0.3),
                "timeline": "6 months",
                "risk_factors": ["Identified via HR flight risk data"],
                "impact_if_leaves": "Loss of institutional knowledge",
            })
    analysis.predictions = {
        "attrition_risk": attrition_risks,
        "decision_reversals": predictions.get("decision_reversals") or [],
        "velocity_trend": predictions.get("velocity_trend") or "stable",
        "org_health_6mo": float(predictions.get("org_health_6mo") or 5.0),
        "key_risks": predictions.get("key_risks") or [],
    }
    analysis.contradictions = ml_signals.get("contradictions", [])
    analysis.positive_signals = ml_signals.get("positive_signals", [])
    analysis.archetype = ml_signals.get("archetype", {})
    analysis.confidence_metrics = ml_signals.get("confidence_metrics", {})
    recommendations = ai_result.get("recommendations") or []
    analysis.recommendations = recommendations
    analysis.decisions_extracted = len(recommendations)

    if messages:
        try:
            analysis.date_range_start = min(
                (m.timestamp for m in messages if m.timestamp), default=None
            )
            analysis.date_range_end = max(
                (m.timestamp for m in messages if m.timestamp), default=None
            )
        except Exception:
            pass

    deep_intel = ai_result.get("deep_intel") or {}
    if deep_intel:
        analysis.system_diagnosis = analysis.system_diagnosis or {}
        analysis.system_diagnosis["political_map"] = deep_intel.get("political_map") or {}
        analysis.system_diagnosis["culture_toxins"] = deep_intel.get("culture_toxins") or []
        analysis.system_diagnosis["between_the_lines"] = deep_intel.get("between_the_lines") or []
        analysis.system_diagnosis["org_tree_politics"] = deep_intel.get("org_tree_politics") or {}
        analysis.system_diagnosis["alert_signals"] = deep_intel.get("alert_signals") or []
        analysis.system_diagnosis["ceo_briefing"] = deep_intel.get("ceo_briefing") or ""
    await session.commit()
    logger.info(
        f"Saved: health={analysis.org_health_score}, "
        f"influencers={len(analysis.top_influencers or [])}, "
        f"gatekeepers={len(analysis.gatekeepers or [])}, "
        f"recommendations={len(analysis.recommendations or [])}"
    )
