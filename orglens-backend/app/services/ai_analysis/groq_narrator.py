"""
Groq Narrator - takes ML signals and generates explanations/narratives.
Groq ONLY explains what ML found. It cannot invent scores.
"""
import json
import os
from groq import Groq
from loguru import logger


GROQ_SCHEMA = {
    "org_health": {
        "org_health_score": "float (USE ml_signals.computed_health_score EXACTLY)",
        "grade": "A/B/C/D/F",
        "summary": "2-3 sentences grounded in evidence",
        "health_breakdown": {
            "trust": "float derived from trust_signals.trust_gap_score inverted",
            "resilience": "float derived from resilience signals",
            "decision_velocity": "float derived from velocity signals",
            "decision_quality": "float derived from reversal_rate",
            "alignment": "float derived from conflict signals",
            "information_flow": "float derived from network density"
        }
    },
    "trust_gap": {
        "trust_gap_score": "USE ml_signals.trust_signals.trust_gap_score EXACTLY",
        "severity": "low/medium/high/critical",
        "alignment_score": "float 0-10",
        "trend": "widening/stable/narrowing",
        "claims": [{"claim": "str", "reality": "str", "gap": "float", "evidence": "quote from data"}]
    },
    "power_structure": {
        "nodes": [{"id": "str", "name": "str", "title": "str", "formal_authority": "float",
                   "actual_influence": "USE person_signals[name].influence_score",
                   "type": "hidden_power/formal_leader/ignored_authority/neutral/gatekeeper",
                   "evidence": "specific message quote"}],
        "edges": [{"from": "str", "to": "str", "weight": "float", "type": "str", "description": "str"}],
        "clusters": [{"name": "str", "members": ["str"], "description": "str"}],
        "hidden_powers": "int count",
        "ignored_authorities": "int count"
    },
    "top_influencers": [{"name": "str", "title": "str",
                         "influence_score": "USE person_signals[name].influence_score",
                         "formal_authority": "USE person_signals[name].formal_authority",
                         "gap": "high/medium/low", "type": "str",
                         "evidence": [{"behavior": "str", "impact": "str", "source": "str"}]}],
    "gatekeepers": [{"name": "str", "title": "str", "gatekeeper_type": "decision/information/both",
                     "blocks_count": "int from gatekeeper_signals", "credibility_score": "float",
                     "power_play_score": "float", "domains": ["str"], "summary": "str",
                     "specific_examples": ["quote from actual messages"]}],
    "resilience": {
        "resilience_score": "float 0-10",
        "risk_level": "low/medium/high/critical",
        "single_points_of_failure": [{"name": "str", "title": "str", "impact_if_leaves": "float",
                                       "risk_level": "str", "estimated_departure_probability": "float from flight_risk_score",
                                       "reason": "str", "knowledge_domains": ["str"]}],
        "knowledge_silos": [{"domain": "str", "owned_by": "str", "backup": "bool", "risk": "str"}]
    },
    "decision_velocity": {
        "avg_days": "USE decision_signals.estimated_avg_days",
        "benchmark": "fast/normal/slow/critical",
        "trend": "improving/stable/worsening",
        "trend_data": [],
        "bottleneck_persons": [{"name": "str", "avg_delay_days": "float", "reason": "str"}]
    },
    "system_diagnosis": {
        "root_causes": [{"system": "str", "issue": "str", "severity": "str", "fixable": "bool",
                         "evidence": "quote from ML signals", "cascade_effects": "str"}],
        "who_profits_from_gaps": [{"name": "str", "how": "str", "motivation_to_maintain": "str"}],
        "predicted_if_unchanged": "paragraph",
        "dysfunction_cost_annual": "str estimate"
    },
    "predictions": {
        "attrition_risk": [{"name": "str", "title": "str",
                            "probability": "USE flight_risk_score from person_signals",
                            "timeline": "str", "risk_factors": ["str"], "impact_if_leaves": "str"}],
        "decision_reversals": [{"decision": "str", "reversal_probability": "float", "reason": "str"}],
        "velocity_trend": "str",
        "org_health_6mo": "float",
        "key_risks": ["str"]
    },
    "recommendations": [{"id": "int", "title": "str", "description": "str",
                          "impact": "low/medium/high/critical", "effort": "low/medium/high",
                          "timeline_weeks": "int", "cost_estimate": "str", "expected_roi": "str",
                          "confidence": "float", "cost_if_ignored": "str", "priority_rank": "int",
                          "addresses": ["root cause ref"]}]
}


class GroqNarrator:
    """
    Uses Groq to generate narratives and explanations from ML signals.
    Groq is FORBIDDEN from inventing scores — it must use ML-computed values.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in environment")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate_analysis(self, ml_signals: dict) -> dict:
        """
        Two-call strategy:
        Call 1: Generate all 9 analysis cards (org health through predictions)
        Call 2: Generate recommendations based on Call 1 findings
        """
        computed_scores = self._compute_scores_from_signals(ml_signals)

        # Call 1: Core analysis
        logger.info("Groq Call 1: Core analysis...")
        core_result = self._call_groq_core(ml_signals, computed_scores)

        # Call 2: Recommendations based on findings
        logger.info("Groq Call 2: Recommendations...")
        recommendations = self._call_groq_recommendations(ml_signals, computed_scores, core_result)
        core_result["recommendations"] = recommendations

        # Call 3: Deep political/cultural reading
        logger.info("Groq Call 3: Deep org intelligence...")
        deep_intel = self._call_groq_deep_intel(ml_signals, core_result)
        core_result["deep_intel"] = deep_intel

        logger.info(
            f"Final: influencers={len(core_result.get('top_influencers') or [])}, "
            f"recommendations={len(recommendations)}, "
            f"deep_intel_sections={len(deep_intel)}"
        )
        return core_result

    def _parse_groq_response(self, raw_response: str) -> dict:
        """
        Parse Groq response with comprehensive control character handling.
        
        Issues this fixes:
        1. Unescaped newlines inside JSON strings
        2. Tab characters in values
        3. Carriage returns
        4. Other control characters (x00-x1f, x7f)
        5. Markdown code fences
        6. Trailing/leading whitespace
        """
        if not raw_response:
            logger.warning("Empty response from Groq")
            return {}
        
        raw = raw_response.strip()
        
        # Step 1: Remove markdown code fences
        if raw.startswith("```"):
            # Extract content between ``` markers
            parts = raw.split("```")
            if len(parts) >= 2:
                raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:].lstrip()
        
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        
        raw = raw.strip()
        
        # Step 2: Remove ALL control characters (except within valid JSON strings)
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
        
        # Step 3: Fix common unescaped newlines and tabs that still made it through
        parts = cleaned.split('"')
        for i in range(1, len(parts), 2):  # Odd indices are string contents
            parts[i] = parts[i].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        cleaned = '"'.join(parts)
        
        # Step 4: Try to parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed after cleaning: {e}")
            logger.debug(f"Cleaned response (first 500 chars): {cleaned[:500]}")
            
            # Step 5: Last resort — try to extract valid JSON from the response
            brace_start = cleaned.find('{')
            bracket_start = cleaned.find('[')
            
            start_pos = -1
            if brace_start >= 0 and bracket_start >= 0:
                start_pos = min(brace_start, bracket_start)
            elif brace_start >= 0:
                start_pos = brace_start
            elif bracket_start >= 0:
                start_pos = bracket_start
            
            if start_pos >= 0:
                partial = cleaned[start_pos:]
                try:
                    for end_pos in range(len(partial), 0, -1):
                        try:
                            return json.loads(partial[:end_pos])
                        except json.JSONDecodeError:
                            continue
                except Exception:
                    pass
            
            logger.error(f"Could not recover valid JSON from response")
            return {}

    def _call_groq_core(self, ml_signals: dict, computed_scores: dict) -> dict:
        """Call 1: Generate 9 analysis cards."""
        f"""## LOCKED SCORES — YOU MUST USE THESE EXACT VALUES, NO DEVIATION:
        ```json
        {json.dumps(computed_scores, indent=2)}
        ```
        Any numeric score you generate that contradicts these values will cause a validation error.
        """
        groq_input = {
            "computed_scores": computed_scores,
            "org_context": ml_signals.get("org_context", {}),
            "message_count": ml_signals.get("message_count", 0),
            "employee_count": ml_signals.get("employee_count", 0),
            "trust_signals": ml_signals.get("trust_signals", {}),
            "network_signals": {
                k: v for k, v in ml_signals.get("network_signals", {}).items()
                if k != "dept_comm"
            },
            "decision_signals": ml_signals.get("decision_signals", {}),
            "resilience_signals": ml_signals.get("resilience_signals", {}),
            "sentiment_signals": ml_signals.get("sentiment_signals", {}),
            "conflict_signals": ml_signals.get("conflict_signals", {}),
            "velocity_signals": ml_signals.get("velocity_signals", {}),
            "person_signals": ml_signals.get("person_signals", {}),
            "all_employees": ml_signals.get("all_employees", []),
        }

        prompt = f"""You are an organizational psychologist analyzing a company's communication data.

    ## ML SIGNALS:
    {json.dumps(groq_input, indent=2, default=str)[:10000]}

    ## PINNED SCORES (use EXACTLY these values):
    - org_health_score: {computed_scores['health_score']}
    - trust_gap_score: {computed_scores['trust_gap_score']}
    - resilience_score: {computed_scores['resilience_score']}
    - avg_decision_days: {computed_scores['avg_decision_days']}

    Generate a JSON object with these exact keys. Name real people. Quote real messages.
    Be psychologically sharp — what is really happening beneath the surface?

    {{
    "org_health": {{
        "org_health_score": {computed_scores['health_score']},
        "grade": "<A/B/C/D/F>",
        "summary": "<3-4 sentences about what is really happening in this org>",
        "health_breakdown": {json.dumps(computed_scores['health_breakdown'])}
    }},
    "trust_gap": {{
        "trust_gap_score": {computed_scores['trust_gap_score']},
        "severity": "<low/medium/high/critical>",
        "alignment_score": <float>,
        "trend": "<widening/stable/narrowing>",
        "claims": [
        {{
            "claim": "<what this org claims to value>",
            "reality": "<what the data actually shows>",
            "gap": <float 0-10>,
            "evidence": "<exact quote or specific behavior from the data>"
        }}
        ]
    }},
    "power_structure": {{
        "nodes": [
        {{
            "id": "<name>",
            "name": "<full name from all_employees>",
            "title": "<title>",
            "level": "<C-Suite/VP/Director/Manager/Senior IC/IC>",
            "department": "<department>",
            "formal_authority": <float based on level>,
            "actual_influence": <float from person_signals[name].influence_score if exists, else estimate>,
            "type": "<hidden_power/formal_leader/ignored_authority/neutral/gatekeeper>",
            "evidence": "<specific thing they said or did, or N/A if no messages>"
        }}
        ],
        "edges": [
        {{
            "from": "<name>",
            "to": "<name>",
            "weight": <float>,
            "type": "<influences/blocks/bypasses/reports_to>",
            "description": "<what this relationship looks like in practice>"
        }}
        ],
        "clusters": [
        {{
            "name": "<e.g. Real Decision Makers / Frustrated Middle Layer / Ignored Experts>",
            "members": ["<name1>", "<name2>"],
            "description": "<what unites this cluster and their political position>"
        }}
        ],
        "hidden_powers": <int>,
        "ignored_authorities": <int>
    }},
    "top_influencers": [
        {{
        "name": "<full name>",
        "title": "<title>",
        "influence_score": <float from person_signals>,
        "formal_authority": <float>,
        "gap": "<high/medium/low>",
        "type": "<hidden_power/formal_leader/ignored_authority/gatekeeper>",
        "evidence": [
            {{
            "behavior": "<specific thing they said/did>",
            "impact": "<what happened as a result>",
            "source": "<email/slack-engineering/slack-general/slack-sales>"
            }}
        ]
        }}
    ],
    "gatekeepers": [
        {{
        "name": "<full name>",
        "title": "<title>",
        "gatekeeper_type": "<decision/information/both>",
        "blocks_count": <int>,
        "credibility_score": <float 0-1>,
        "power_play_score": <float 0-1>,
        "domains": ["<what they control>"],
        "summary": "<1-2 sentences on how they gate information or decisions>",
        "specific_examples": ["<exact quote showing gatekeeping behavior>"]
        }}
    ],
    "resilience": {{
        "resilience_score": {computed_scores['resilience_score']},
        "risk_level": "<low/medium/high/critical>",
        "single_points_of_failure": [
        {{
            "name": "<full name>",
            "title": "<title>",
            "impact_if_leaves": <float>,
            "risk_level": "<low/medium/high/critical>",
            "estimated_departure_probability": <float>,
            "reason": "<why losing them would be damaging>",
            "knowledge_domains": ["<what only they know>"]
        }}
        ],
        "knowledge_silos": [
        {{
            "domain": "<area of knowledge>",
            "owned_by": "<name>",
            "backup": false,
            "risk": "<what breaks if they leave>"
        }}
        ]
    }},
    "decision_velocity": {{
        "avg_days": {computed_scores['avg_decision_days']},
        "benchmark": "<fast/normal/slow/critical>",
        "trend": "<improving/stable/worsening>",
        "trend_data": [],
        "bottleneck_persons": [
        {{
            "name": "<who slows decisions>",
            "avg_delay_days": <float>,
            "reason": "<why they slow things down>"
        }}
        ]
    }},
    "system_diagnosis": {{
        "root_causes": [
        {{
            "system": "<governance/culture/structure/process/leadership>",
            "issue": "<specific dysfunction>",
            "severity": "<low/medium/high/critical>",
            "fixable": <bool>,
            "evidence": "<quote or signal from data>",
            "cascade_effects": "<what else this causes>"
        }}
        ],
        "who_profits_from_gaps": [
        {{
            "name": "<full name>",
            "how": "<how this dysfunction benefits them>",
            "motivation_to_maintain": "<high/medium/low>"
        }}
        ],
        "predicted_if_unchanged": "<paragraph: what happens in 6-12 months>",
        "dysfunction_cost_annual": "<estimated cost>"
    }},
    "predictions": {{
        "attrition_risk": [
        {{
            "name": "<full name>",
            "title": "<title>",
            "probability": <float from flight_risk_score>,
            "timeline": "<3 months/6 months/12 months>",
            "risk_factors": ["<factor1>", "<factor2>"],
            "impact_if_leaves": "<what the org loses>"
        }}
        ],
        "decision_reversals": [
        {{
            "decision": "<which decision may be reversed>",
            "reversal_probability": <float>,
            "reason": "<why it might flip>"
        }}
        ],
        "velocity_trend": "<improving/stable/worsening>",
        "org_health_6mo": <float>,
        "key_risks": ["<risk1>", "<risk2>", "<risk3>"]
    }}
    }}

    Return ONLY valid JSON. No markdown. No explanation outside the JSON."""

        return self._execute_groq_call(prompt)


    def _call_groq_recommendations(
        self, ml_signals: dict, computed_scores: dict, core_result: dict
    ) -> list:
        """Call 2: Generate specific actionable recommendations."""

        prompt = f"""You are an organizational consultant. Based on this diagnosis, generate 8-10 specific recommendations.

    ## ORGANIZATION DIAGNOSIS:
    Health Score: {computed_scores['health_score']}/10
    Trust Gap: {computed_scores['trust_gap_score']}/10
    Resilience: {computed_scores['resilience_score']}/10

    Root Causes Found:
    {json.dumps((core_result.get('system_diagnosis') or {}).get('root_causes') or [], indent=2)}

    Top Influencers:
    {json.dumps(core_result.get('top_influencers') or [], indent=2, default=str)[:2000]}

    Attrition Risks:
    {json.dumps((core_result.get('predictions') or {}).get('attrition_risk') or [], indent=2)}

    Trust Gap Claims:
    {json.dumps((core_result.get('trust_gap') or {}).get('claims') or [], indent=2)}

    Conflict Signals:
    {json.dumps(ml_signals.get('conflict_signals', {}).get('conflict_messages') or [], indent=2, default=str)[:1500]}

    Generate a JSON array of recommendations. Each must be specific, named, and actionable.
    Reference real people and real issues found in the diagnosis.

    [
    {{
        "id": 1,
        "title": "<specific action title>",
        "description": "<3-4 sentences: what to do, who does it, how>",
        "impact": "<low/medium/high/critical>",
        "effort": "<low/medium/high>",
        "timeline_weeks": <int>,
        "cost_estimate": "<$X-Y or internal>",
        "expected_roi": "<specific measurable outcome>",
        "confidence": <float 0-1>,
        "cost_if_ignored": "<what happens if this is not done>",
        "priority_rank": <int>,
        "addresses": ["<which root cause this fixes>"],
        "owner": "<who should drive this>"
    }}
    ]

    Order by priority (highest impact + lowest effort first).
    Return ONLY the JSON array. No markdown."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an organizational consultant. Return only valid JSON arrays."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0]
            result = json.loads(raw.strip())
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Recommendations Groq call failed: {e}")
            return []


    def _call_groq_deep_intel(self, ml_signals: dict, core_result: dict) -> dict:
        """
        Call 3: Deep political and cultural intelligence.
        The between-the-lines reading that tells the CEO what's really happening.
        """
        person_signals = ml_signals.get("person_signals", {})
        conflict_msgs = ml_signals.get("conflict_signals", {}).get("conflict_messages") or []
        trust_signals = ml_signals.get("trust_signals", {})
        sentiment = ml_signals.get("sentiment_signals", {})

        prompt = f"""You are a senior organizational psychologist and political analyst embedded in this company.
    You have read every email and Slack message. Now write the real intelligence report.

    ## DATA:
    Person Signals: {json.dumps(person_signals, default=str)[:3000]}
    Conflict Messages: {json.dumps(conflict_msgs[:10], default=str)[:2000]}
    Trust Signals: {json.dumps(trust_signals, default=str)[:1000]}
    Sentiment: {json.dumps(sentiment, default=str)[:500]}
    Core Findings: {json.dumps({
        'top_influencers': core_result.get('top_influencers', [])[:5],
        'gatekeepers': core_result.get('gatekeepers', [])[:3],
        'root_causes': (core_result.get('system_diagnosis') or {}).get('root_causes', [])[:3],
    }, default=str)[:2000]}

    Write the deep intelligence report as JSON:

    {{
    "political_map": {{
        "real_power_center": "<who actually runs this org, not on paper but in practice>",
        "official_vs_reality": "<how the org chart differs from actual power>",
        "power_factions": [
        {{
            "name": "<faction name e.g. Arun's Tech Coalition>",
            "leader": "<name>",
            "members": ["<name1>", "<name2>"],
            "agenda": "<what they want>",
            "tactics": "<how they operate>",
            "threat_level": "<low/medium/high>"
        }}
        ],
        "upcoming_conflicts": [
        {{
            "between": ["<party1>", "<party2>"],
            "over": "<what the conflict is about>",
            "likely_winner": "<who and why>",
            "timeline": "<when this will surface>"
        }}
        ]
    }},
    "culture_toxins": [
        {{
        "toxin": "<name of cultural problem e.g. fear-based escalation, credit hoarding>",
        "evidence": "<specific behavior showing this>",
        "carriers": ["<who spreads this behavior>"],
        "impact": "<what this is doing to the org>",
        "antidote": "<specific cultural intervention>"
        }}
    ],
    "between_the_lines": [
        {{
        "surface_message": "<what was officially said>",
        "real_meaning": "<what was actually communicated>",
        "who_said_it": "<name>",
        "political_implication": "<what this reveals about power dynamics>",
        "source": "<email subject or slack channel>"
        }}
    ],
    "org_tree_politics": {{
        "description": "<paragraph describing the real org structure with politics>",
        "layers": [
        {{
            "layer": "<e.g. C-Suite / VP Layer / Manager Layer>",
            "official_role": "<what they are supposed to do>",
            "actual_role": "<what they actually do>",
            "political_dynamics": "<tensions, alliances, sidelines within this layer>",
            "key_people": ["<name1>", "<name2>"]
        }}
        ]
    }},
    "alert_signals": [
        {{
        "signal": "<specific early warning sign>",
        "severity": "<low/medium/high/critical>",
        "evidence": "<what in the data shows this>",
        "action_needed": "<what to do immediately>"
        }}
    ],
    "ceo_briefing": "<A 3-4 paragraph executive briefing written directly to the CEO. Honest. Specific. Name names. Tell them what they need to know but might not want to hear. Reference actual communications.>"
    }}

    Be brutally honest. This is confidential. Name real people. Quote real messages.
    Return ONLY valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior organizational psychologist with 20 years experience. "
                            "You give honest, specific, politically sharp analysis. "
                            "You name names. You quote evidence. You never generalize. "
                            "Return only valid JSON."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0]
            raw = raw.strip()
            import re
            cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw.strip())
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Deep intel Groq call failed: {e}")
            return {}


    def _execute_groq_call(self, prompt: str) -> dict:
        """Execute a Groq call and parse JSON response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an organizational psychologist. "
                            "Return only valid JSON. No markdown. No text outside JSON."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=6000,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0]
            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Groq call failed: {e}")
            return {}

    def _compute_scores_from_signals(self, ml_signals: dict) -> dict:
        trust_signals = ml_signals.get("trust_signals", {})
        network_signals = ml_signals.get("network_signals", {})
        decision_signals = ml_signals.get("decision_signals", {})
        resilience_signals = ml_signals.get("resilience_signals", {})
        sentiment_signals = ml_signals.get("sentiment_signals", {})
        conflict_signals = ml_signals.get("conflict_signals", {})
        velocity_signals = ml_signals.get("velocity_signals", {})
        person_signals = ml_signals.get("person_signals", {})

        total_msgs = max(ml_signals.get("message_count", 1), 1)

        # Trust gap: normalize properly, cap at 8 unless extreme evidence
        trust_gap_raw = trust_signals.get("trust_gap_score", 3.0)
        trust_gap_score = min(trust_gap_raw, 8.5)

        # Resilience: penalize per risk signal but don't go below 3
        high_risk = min(resilience_signals.get("high_flight_risk_count", 0), 3)
        ownership_gaps = min(resilience_signals.get("ownership_gap_count", 0), 3)
        departures = min(resilience_signals.get("departure_mention_count", 0), 2)
        resilience_score = max(3.0, 10 - (high_risk * 1.0) - (ownership_gaps * 0.5) - (departures * 0.8))
        resilience_score = round(min(resilience_score, 9.0), 2)

        # Decision velocity days — use ML signal, fallback to 14
        avg_days = decision_signals.get("estimated_avg_days", 14)
        if avg_days < 1:
            avg_days = 14  # guard against 0.2 type values

        # Network density → info flow
        network_density = network_signals.get("network_density", 0.05)
        info_flow_score = min(network_density * 100, 8.0)  # scale up

        # Conflict ratio → alignment
        conflict_ratio = conflict_signals.get("conflict_ratio", 0.05)
        alignment_score = max(2.0, 10 - (conflict_ratio * 25))

        # Reversal rate → decision quality
        reversal_rate = decision_signals.get("reversal_rate", 0.05)
        decision_quality = max(3.0, 10 - (reversal_rate * 15))

        # Velocity score
        if avg_days <= 5:
            velocity_score = 9.0
        elif avg_days <= 10:
            velocity_score = 7.5
        elif avg_days <= 20:
            velocity_score = 6.0
        elif avg_days <= 30:
            velocity_score = 4.5
        else:
            velocity_score = 2.5

        # Sentiment penalty
        negative_ratio = sentiment_signals.get("negative_ratio", 0.1)
        sentiment_penalty = min(negative_ratio * 10, 2.0)

        # Health score — weighted, with sentiment penalty
        trust_health = 10.0 - trust_gap_score
        health_score = round(
            max(2.0, min(9.5,
                trust_health * 0.25 +
                resilience_score * 0.20 +
                velocity_score * 0.20 +
                decision_quality * 0.15 +
                alignment_score * 0.15 +
                info_flow_score * 0.05 -
                sentiment_penalty
            )),
            2
        )

        # Top influencers sorted by ML influence score
        sorted_influencers = sorted(
            person_signals.items(),
            key=lambda x: x[1].get("influence_score", 0),
            reverse=True
        )

        return {
            "health_score": health_score,
            "trust_gap_score": round(trust_gap_score, 2),
            "resilience_score": resilience_score,
            "avg_decision_days": avg_days,
            "alignment_score": round(alignment_score, 2),
            "decision_quality_score": round(decision_quality, 2),
            "info_flow_score": round(info_flow_score, 2),
            "velocity_score": velocity_score,
            "health_breakdown": {
                "trust": round(trust_health, 2),
                "resilience": resilience_score,
                "decision_velocity": velocity_score,
                "decision_quality": round(decision_quality, 2),
                "alignment": round(alignment_score, 2),
                "information_flow": round(info_flow_score, 2),
            },
            "top_influencer_names": [name for name, _ in sorted_influencers[:10]],
            "flight_risk_persons": [
                {
                    "name": name,
                    "score": signals.get("flight_risk_score", 0.15),
                    "title": signals.get("title", "")
                }
                for name, signals in person_signals.items()
                if signals.get("flight_risk_score", 0) > 0.3
            ],
        }

    def _build_prompt(self, ml_signals: dict, computed_scores: dict) -> str:
        # Serialize only what Groq needs (keep it focused)
        groq_input = {
            "computed_scores": computed_scores,
            "org_context": ml_signals.get("org_context", {}),
            "message_count": ml_signals.get("message_count", 0),
            "employee_count": ml_signals.get("employee_count", 0),
            "trust_signals": ml_signals.get("trust_signals", {}),
            "network_signals": {
                k: v for k, v in ml_signals.get("network_signals", {}).items()
                if k != "dept_comm"  # skip large objects
            },
            "decision_signals": ml_signals.get("decision_signals", {}),
            "resilience_signals": ml_signals.get("resilience_signals", {}),
            "sentiment_signals": ml_signals.get("sentiment_signals", {}),
            "conflict_signals": ml_signals.get("conflict_signals", {}),
            "velocity_signals": ml_signals.get("velocity_signals", {}),
            "person_signals": ml_signals.get("person_signals", {}),
            "output_schema": GROQ_SCHEMA,
        }

        return f"""You have received pre-computed ML organizational signals for {ml_signals.get('org_context', {}).get('name', 'this organization')}.

## ML SIGNALS (source of truth — do not contradict these):
{json.dumps(groq_input, indent=2, default=str)[:12000]}

## YOUR TASK:
Generate the complete 10-card organizational analysis JSON.

CRITICAL RULES:
1. org_health.org_health_score MUST equal computed_scores.health_score = {computed_scores['health_score']}
2. trust_gap.trust_gap_score MUST equal computed_scores.trust_gap_score = {computed_scores['trust_gap_score']}
3. resilience.resilience_score MUST equal computed_scores.resilience_score = {computed_scores['resilience_score']}
4. decision_velocity.avg_days MUST equal computed_scores.avg_decision_days = {computed_scores['avg_decision_days']}
5. Each top_influencer influence_score MUST come from person_signals[name].influence_score
6. Each attrition_risk probability MUST come from person_signals[name].flight_risk_score
7. Every gatekeeper must cite actual message snippets from gatekeeper_signals or conflict_messages
8. Every trust gap claim must cite evidence from comp_inversion_evidence or conflict_messages
9. power_structure.nodes MUST include ALL {len(ml_signals.get('all_employees', []))} employees from all_employees, not just those with messages

Name real people. Quote real messages. Reference specific behaviors.
The CEO will read this. Make it honest and specific.

Return ONLY the JSON object matching the output_schema. No markdown."""