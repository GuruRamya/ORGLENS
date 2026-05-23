import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
import re
from loguru import logger


class MLSignalExtractor:
    """
    Extracts objective, quantifiable signals from org data.
    These signals feed into Groq for explanation/narrative generation.
    """

    def extract_all_signals(
        self,
        employees: list[dict],
        messages: list[dict],
        org_context: dict,
    ) -> dict:
        """
        Master function. Returns structured ML signals for all 10 cards.
        """
        logger.info(f"Extracting ML signals from {len(messages)} messages, {len(employees)} employees")

        comm_graph = self._build_comm_graph(messages, employees)
        signals = {
            "org_context": org_context,
            "employee_count": len(employees),
            "message_count": len(messages),
            "all_employees": employees,
            "date_range": self._get_date_range(messages),
            "person_signals": self._extract_person_signals(messages, employees, comm_graph),
            "trust_signals": self._extract_trust_signals(messages, employees),
            "network_signals": self._extract_network_signals(comm_graph, messages, employees),
            "decision_signals": self._extract_decision_signals(messages),
            "resilience_signals": self._extract_resilience_signals(messages, employees, comm_graph),
            "sentiment_signals": self._extract_sentiment_signals(messages),
            "conflict_signals": self._extract_conflict_signals(messages),
            "velocity_signals": self._extract_velocity_signals(messages),
        }

        logger.info("ML signal extraction complete")
        return signals

    def _build_comm_graph(self, messages: list[dict], employees: list[dict]) -> dict:
        """Build directed communication graph from messages."""
        name_map = {}
        for emp in employees:
            name = (emp.get("name") or "").lower()
            email = (emp.get("email") or "").lower()
            emp_id = emp.get("id") or emp.get("name")
            if name:
                name_map[name] = emp_id
            if email:
                name_map[email] = emp_id
            if name:
                parts = name.split()
                if len(parts) >= 2:
                    name_map[f"{parts[0]}_{parts[-1]}"] = emp_id

        edges = defaultdict(lambda: defaultdict(int))
        node_messages = defaultdict(list)  

        for msg in messages:
            sender_raw = (msg.get("sender_raw") or "").lower().strip()
            content = msg.get("content") or ""
            channel = msg.get("channel_or_thread") or ""
            sender_id = self._resolve_identity(sender_raw, name_map)
            mentioned = self._find_mentioned_people(content, name_map, employees)

            for recipient in mentioned:
                if recipient != sender_id:
                    edges[sender_id][recipient] += 1

            node_messages[sender_id].append({
                "content": content,
                "channel": channel,
                "timestamp": msg.get("timestamp"),
                "source": msg.get("source"),
            })

        all_nodes = set(list(edges.keys()))
        for sender, recipients in edges.items():
            all_nodes.update(recipients.keys())

        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        for sender, recipients in edges.items():
            for recipient, count in recipients.items():
                out_degree[sender] += count
                in_degree[recipient] += count

        return {
            "edges": dict(edges),
            "node_messages": dict(node_messages),
            "in_degree": dict(in_degree),
            "out_degree": dict(out_degree),
            "all_nodes": list(all_nodes),
            "name_map": name_map,
        }

    def _resolve_identity(self, raw: str, name_map: dict) -> str:
        """Resolve a raw sender string to canonical ID."""
        raw = raw.lower().strip()
        if raw in name_map:
            return name_map[raw]
        if "@" in raw:
            username = raw.split("@")[0]
            if username in name_map:
                return name_map[username]
        for key, val in name_map.items():
            if key in raw or raw in key:
                return val
        return raw  

    def _find_mentioned_people(self, content: str, name_map: dict, employees: list[dict]) -> list[str]:
        """Find all people mentioned in a message."""
        mentioned = []
        content_lower = content.lower()
        for emp in employees:
            name = (emp.get("name") or "").lower()
            if name and name in content_lower:
                emp_id = emp.get("id") or emp.get("name")
                mentioned.append(emp_id)
            first_name = name.split()[0] if name else ""
            if first_name and len(first_name) > 3 and first_name in content_lower:
                emp_id = emp.get("id") or emp.get("name")
                if emp_id not in mentioned:
                    mentioned.append(emp_id)
        return mentioned

    def _extract_person_signals(
        self, messages: list[dict], employees: list[dict], comm_graph: dict
    ) -> dict:
        """Per-person quantified signals."""
        person_signals = {}

        in_deg = comm_graph.get("in_degree", {})
        out_deg = comm_graph.get("out_degree", {})
        node_msgs = comm_graph.get("node_messages", {})
        name_map = comm_graph.get("name_map", {})

        for emp in employees:
            name = emp.get("name") or ""
            emp_id = emp.get("id") or name
            name_lower = name.lower()
            person_id = name_map.get(name_lower, emp_id)
            sent_msgs = node_msgs.get(person_id, [])
            msg_count = len(sent_msgs)
            in_degree = in_deg.get(person_id, 0)
            out_degree = out_deg.get(person_id, 0)
            urgency_keywords = ["urgent", "asap", "blocking", "critical", "immediately", "now", "must", "need to"]
            urgency_count = sum(
                1 for m in sent_msgs
                if any(kw in (m.get("content") or "").lower() for kw in urgency_keywords)
            )
            conviction_keywords = ["we're moving", "i've decided", "this is my call", "not negotiable", "final decision", "i'll cut"]
            conviction_count = sum(
                1 for m in sent_msgs
                if any(kw in (m.get("content") or "").lower() for kw in conviction_keywords)
            )
            objection_keywords = ["push back", "disagree", "concern", "but ", "however", "not realistic", "fair point"]
            objection_count = sum(
                1 for m in sent_msgs
                if any(kw in (m.get("content") or "").lower() for kw in objection_keywords)
            )
            escalation_keywords = ["escalate", "bring to rajiv", "rajiv —", "need exec", "leadership needs", "can we escalate"]
            escalation_count = sum(
                1 for m in sent_msgs
                if any(kw in (m.get("content") or "").lower() for kw in escalation_keywords)
            )
            burnout_keywords = ["burnout", "weekends", "morale", "exhausted", "overcommitted", "stretched", "too much"]
            burnout_signal = sum(
                1 for m in sent_msgs
                if any(kw in (m.get("content") or "").lower() for kw in burnout_keywords)
            )
            flight_risk_raw = emp.get("flight_risk") or emp.get("Flight Risk") or "low"
            flight_risk_score = {"low": 0.15, "medium": 0.45, "high": 0.75}.get(
                str(flight_risk_raw).lower(), 0.15
            )
            level_authority = {
                "c-suite": 9.5, "vp": 8.0, "sr mgr": 6.5, "manager": 5.5,
                "sr ic": 4.5, "ic": 3.0
            }
            level = str(emp.get("level") or "").lower()
            formal_authority = level_authority.get(level, 5.0)
            raw_influence = (
                (in_degree * 2.0) +
                (conviction_count * 1.5) +
                (escalation_count * 1.0) +
                (msg_count * 0.3)
            )
            influence_score = min(raw_influence, 10.0)

            person_signals[name] = {
                "name": (
                    emp.get("name") or 
                    emp.get("Name") or
                    emp.get("full_name") or 
                    emp.get("Full Name") or 
                    emp.get("employee_name") or 
                    emp.get("Employee Name") or 
                    ""
                ),
                "title": (
                    emp.get("title") or 
                    emp.get("Role") or 
                    emp.get("role") or 
                    emp.get("job_title") or 
                    emp.get("Title") or 
                    ""
                ),
                "level": (
                    emp.get("level") or 
                    emp.get("Level") or
                    emp.get("seniority") or 
                    ""
                ),
                "department": (
                    emp.get("department") or 
                    emp.get("Dept") or
                    emp.get("dept") or
                    emp.get("Department") or
                    emp.get("team") or 
                    ""
                ),
                "formal_authority": formal_authority,
                "influence_score": round(influence_score, 2),
                "message_count": msg_count,
                "in_degree": in_degree,
                "out_degree": out_degree,
                "urgency_count": urgency_count,
                "conviction_count": conviction_count,
                "objection_count": objection_count,
                "escalation_count": escalation_count,
                "burnout_signal": burnout_signal,
                "flight_risk_score": flight_risk_score,
                "flight_risk_raw": str(flight_risk_raw),
                "authority_gap": round(influence_score - formal_authority, 2),
                "collaboration_score": float(emp.get("collaboration") or emp.get("Collaboration") or 50) / 10,
                "performance_rating": float(emp.get("performance_rating") or emp.get("Performnce Rating") or 7),
                "tenure_months": int(emp.get("tenure_months") or emp.get("Exp") or 0) * 12,
                "channels_active": list(set(m.get("channel") for m in sent_msgs if m.get("channel"))),
            }

        return person_signals


    def _extract_trust_signals(self, messages: list[dict], employees: list[dict]) -> dict:
        """Compute trust gap signals: stated values vs actual behavior."""

        claim_patterns = {
            "meritocracy": ["merit", "fair", "transparent promotion", "criteria", "equal"],
            "transparency": ["transparent", "open communication", "visible", "shared"],
            "work_life_balance": ["balance", "wellness", "sustainable", "no weekends"],
            "collaboration": ["collaborate", "together", "cross-functional", "aligned"],
            "innovation": ["innovate", "move fast", "experiment", "ship quickly"],
        }

        reality_patterns = {
            "meritocracy_violation": [
                "political", "favoritism", "inconsistent criteria", "perceived", "feels political",
                "salary inversion", "new hires paid more", "equity inversion"
            ],
            "transparency_violation": [
                "no visibility", "unclear", "not clear", "nobody told", "didn't know",
                "decisions before meetings", "approval chain"
            ],
            "burnout_reality": [
                "weekends", "burnout", "morale dropping", "overcommitted", "stretched"
            ],
            "siloed_reality": [
                "cross-team handoff", "no owner", "falls through cracks", "nobody owns",
                "structure issue", "unclear ownership"
            ],
            "slow_reality": [
                "45+ days", "2 weeks", "delayed again", "taking too long",
                "slow", "blocked waiting"
            ],
        }

        all_text = " ".join(m.get("content") or "" for m in messages).lower()

        claim_scores = {}
        for claim, keywords in claim_patterns.items():
            claim_scores[claim] = sum(1 for kw in keywords if kw in all_text)

        reality_scores = {}
        for reality, keywords in reality_patterns.items():
            reality_scores[reality] = sum(1 for kw in keywords if kw in all_text)

        comp_inversion_evidence = []
        for msg in messages:
            content = (msg.get("content") or "").lower()
            if any(kw in content for kw in ["below market", "salary inversion", "new hires paid more", "higher bands"]):
                comp_inversion_evidence.append({
                    "sender": msg.get("sender_raw"),
                    "channel": msg.get("channel_or_thread"),
                    "snippet": (msg.get("content") or "")[:200],
                })

        promotion_complaints = sum(
            1 for m in messages
            if any(kw in (m.get("content") or "").lower()
                   for kw in ["political", "favoritism", "inconsistent", "perceived", "promotion criteria"])
        )

        escalation_count = sum(
            1 for m in messages
            if any(kw in (m.get("content") or "").lower()
                   for kw in ["escalate", "bring to rajiv", "need exec approval", "leadership needs to"])
        )

        total_msgs = max(len(messages), 1)

        return {
            "claim_scores": claim_scores,
            "reality_scores": reality_scores,
            "comp_inversion_evidence": comp_inversion_evidence,
            "promotion_complaint_count": promotion_complaints,
            "escalation_count": escalation_count,
            "escalation_rate": round(escalation_count / total_msgs, 3),
            "trust_gap_score": min(
                (reality_scores.get("meritocracy_violation", 0) * 0.8 +
                 reality_scores.get("transparency_violation", 0) * 0.6 +
                 reality_scores.get("burnout_reality", 0) * 0.4 +
                 escalation_count * 0.3),
                10.0
            ),
        }


    def _extract_network_signals(
        self, comm_graph: dict, messages: list[dict], employees: list[dict]
    ) -> dict:
        """Identify power structure from communication patterns."""

        in_deg = comm_graph.get("in_degree", {})
        out_deg = comm_graph.get("out_degree", {})
        edges = comm_graph.get("edges", {})
        node_msgs = comm_graph.get("node_messages", {})
        name_map = comm_graph.get("name_map", {})

        level_authority = {
            "c-suite": 9.5, "vp": 8.0, "sr mgr": 6.5, "manager": 5.5, "sr ic": 4.5, "ic": 3.0
        }

        bypass_events = []
        for msg in messages:
            sender_raw = (msg.get("sender_raw") or "").lower()
            content = msg.get("content") or ""
            if any(exec_name in content.lower() for exec_name in ["rajiv", "arun kumar", "priya sharma"]):
                if sender_raw not in ["rajiv_menon", "arun_kumar", "priya_sharma"]:
                    bypass_events.append({
                        "sender": msg.get("sender_raw"),
                        "channel": msg.get("channel_or_thread"),
                        "snippet": content[:150],
                    })

        gatekeeper_signals = defaultdict(int)
        gatekeeper_keywords = ["waiting for", "blocked on", "needs approval from", "hasn't responded", "deprioritized"]
        for msg in messages:
            content = (msg.get("content") or "").lower()
            if any(kw in content for kw in gatekeeper_keywords):
                # Find mentioned names
                for emp in employees:
                    name = (emp.get("name") or "").lower()
                    if name and name in content:
                        gatekeeper_signals[emp.get("name")] += 1

        dept_comm = defaultdict(set)
        emp_dept_map = {(emp.get("name") or "").lower(): emp.get("department") or "" for emp in employees}

        for sender, recipients in edges.items():
            sender_dept = emp_dept_map.get(sender, "")
            for recipient in recipients:
                recipient_dept = emp_dept_map.get(recipient, "")
                if sender_dept and recipient_dept and sender_dept != recipient_dept:
                    dept_comm[sender].add(recipient_dept)

        siloed_nodes = [
            node for node, cross_depts in dept_comm.items()
            if len(cross_depts) == 0 and (out_deg.get(node, 0) > 2)
        ]

        sorted_by_in_degree = sorted(in_deg.items(), key=lambda x: x[1], reverse=True)
        top_hubs = sorted_by_in_degree[:5]

        all_nodes = comm_graph.get("all_nodes", [])
        isolated = [
            n for n in all_nodes
            if in_deg.get(n, 0) + out_deg.get(n, 0) <= 1
        ]

        return {
            "bypass_events": bypass_events,
            "bypass_count": len(bypass_events),
            "gatekeeper_signals": dict(gatekeeper_signals),
            "top_hubs": top_hubs,
            "isolated_nodes": isolated,
            "isolated_count": len(isolated),
            "dept_comm": {k: list(v) for k, v in dept_comm.items()},
            "siloed_nodes": siloed_nodes,
            "total_edges": sum(len(v) for v in edges.values()),
            "network_density": round(
                sum(len(v) for v in edges.values()) / max(len(all_nodes) ** 2, 1), 4
            ),
        }


    def _extract_decision_signals(self, messages: list[dict]) -> dict:
        """Measure decision velocity and quality patterns."""

        decision_keywords = ["approved", "decided", "we're going with", "final decision", "this is my call", "moving forward with"]
        block_keywords = ["blocked", "waiting", "can't proceed", "need approval", "on hold", "delayed"]
        reversal_keywords = ["changed", "actually", "we're not doing", "reversed", "scratch that", "update: we"]

        decisions = []
        blocks = []
        reversals = []

        for msg in messages:
            content = (msg.get("content") or "").lower()
            sender = msg.get("sender_raw") or ""
            ts = msg.get("timestamp")

            if any(kw in content for kw in decision_keywords):
                decisions.append({
                    "sender": sender,
                    "snippet": content[:200],
                    "timestamp": str(ts),
                    "channel": msg.get("channel_or_thread"),
                })

            if any(kw in content for kw in block_keywords):
                blocks.append({
                    "sender": sender,
                    "snippet": content[:200],
                    "timestamp": str(ts),
                })

            if any(kw in content for kw in reversal_keywords):
                reversals.append({
                    "sender": sender,
                    "snippet": content[:200],
                    "timestamp": str(ts),
                })

        approval_chain_msgs = [
            msg for msg in messages
            if any(kw in (msg.get("content") or "").lower()
                   for kw in ["need exec approval", "approval", "sign-off", "waiting for"])
        ]

        timestamps = []
        for msg in messages:
            ts = msg.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    timestamps.append(ts)
                except Exception:
                    pass

        avg_response_hours = 0
        if len(timestamps) > 2:
            timestamps.sort()
            gaps = [(timestamps[i+1] - timestamps[i]).total_seconds() / 3600
                    for i in range(len(timestamps)-1)
                    if (timestamps[i+1] - timestamps[i]).total_seconds() < 86400]
            avg_response_hours = round(np.mean(gaps), 2) if gaps else 0

        return {
            "decision_count": len(decisions),
            "block_count": len(blocks),
            "reversal_count": len(reversals),
            "reversal_rate": round(len(reversals) / max(len(decisions), 1), 3),
            "approval_chain_count": len(approval_chain_msgs),
            "avg_response_hours": avg_response_hours,
            "estimated_avg_days": round(avg_response_hours / 8, 1) if avg_response_hours else 21,
            "decisions": decisions[:10],
            "blocks": blocks[:10],
            "reversals": reversals[:5],
        }


    def _extract_resilience_signals(
        self, messages: list[dict], employees: list[dict], comm_graph: dict
    ) -> dict:
        """Identify single points of failure and knowledge silos."""

        in_deg = comm_graph.get("in_degree", {})
        name_map = comm_graph.get("name_map", {})

        high_risk = [
            emp for emp in employees
            if str(emp.get("flight_risk") or emp.get("Flight Risk") or "").lower() == "high"
        ]
        medium_risk = [
            emp for emp in employees
            if str(emp.get("flight_risk") or emp.get("Flight Risk") or "").lower() == "medium"
        ]

        departure_mentions = []
        departure_keywords = ["gave notice", "leaving", "resigned", "departure", "quit", "last day"]
        for msg in messages:
            content = (msg.get("content") or "").lower()
            if any(kw in content for kw in departure_keywords):
                departure_mentions.append({
                    "sender": msg.get("sender_raw"),
                    "snippet": (msg.get("content") or "")[:200],
                })

        ownership_gaps = []
        for msg in messages:
            content = (msg.get("content") or "").lower()
            if any(kw in content for kw in ["no owner", "nobody owns", "unclear ownership", "no one owns", "falls through"]):
                ownership_gaps.append({
                    "sender": msg.get("sender_raw"),
                    "channel": msg.get("channel_or_thread"),
                    "snippet": (msg.get("content") or "")[:200],
                })

        sorted_in_deg = sorted(in_deg.items(), key=lambda x: x[1], reverse=True)
        potential_spofs = [
            {"id": node, "in_degree": deg}
            for node, deg in sorted_in_deg[:5]
            if deg > 2
        ]

        no_succession = [
            emp for emp in employees
            if str(emp.get("succession") or emp.get("Succession ") or "").lower() in ["", "none", "low", "no"]
            and str(emp.get("level") or "").lower() in ["vp", "c-suite", "sr mgr"]
        ]

        return {
            "high_flight_risk_count": len(high_risk),
            "medium_flight_risk_count": len(medium_risk),
            "high_flight_risk_employees": [e.get("name") for e in high_risk],
            "medium_flight_risk_employees": [e.get("name") for e in medium_risk],
            "departure_mentions": departure_mentions,
            "departure_mention_count": len(departure_mentions),
            "ownership_gaps": ownership_gaps,
            "ownership_gap_count": len(ownership_gaps),
            "potential_spofs": potential_spofs,
            "no_succession_count": len(no_succession),
            "no_succession_employees": [e.get("name") for e in no_succession[:5]],
        }


    def _extract_sentiment_signals(self, messages: list[dict]) -> dict:
        """Compute sentiment and emotional signals from messages."""

        negative_keywords = ["frustrated", "problem", "issue", "broken", "failing", "concern", "worried",
                             "burnout", "morale", "stuck", "blocked", "slow", "lost deal", "overcommitted"]
        positive_keywords = ["great", "excited", "progress", "aligned", "solved", "shipped", "success", "good news"]
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "blocking", "now", "today"]

        negative_msgs = []
        positive_msgs = []
        urgent_msgs = []

        for msg in messages:
            content = (msg.get("content") or "").lower()
            neg_count = sum(1 for kw in negative_keywords if kw in content)
            pos_count = sum(1 for kw in positive_keywords if kw in content)
            urg_count = sum(1 for kw in urgent_keywords if kw in content)

            if neg_count > pos_count and neg_count > 0:
                negative_msgs.append({"sender": msg.get("sender_raw"), "neg_score": neg_count, "snippet": content[:150]})
            if pos_count > neg_count and pos_count > 0:
                positive_msgs.append({"sender": msg.get("sender_raw"), "pos_score": pos_count})
            if urg_count > 0:
                urgent_msgs.append({"sender": msg.get("sender_raw"), "urg_score": urg_count, "snippet": content[:100]})

        total = max(len(messages), 1)

        return {
            "negative_message_count": len(negative_msgs),
            "positive_message_count": len(positive_msgs),
            "urgent_message_count": len(urgent_msgs),
            "negative_ratio": round(len(negative_msgs) / total, 3),
            "urgency_ratio": round(len(urgent_msgs) / total, 3),
            "top_negative_senders": sorted(negative_msgs, key=lambda x: x["neg_score"], reverse=True)[:5],
            "top_urgent_senders": sorted(urgent_msgs, key=lambda x: x["urg_score"], reverse=True)[:5],
        }


    def _extract_conflict_signals(self, messages: list[dict]) -> dict:
        """Detect cross-team conflicts and tension points."""

        conflict_keywords = ["push back", "disagree", "not realistic", "that breaks", "we can't",
                             "whoever has the loudest voice", "feel political", "ignored", "deprioritized"]

        conflict_msgs = []
        for msg in messages:
            content = (msg.get("content") or "").lower()
            if any(kw in content for kw in conflict_keywords):
                conflict_msgs.append({
                    "sender": msg.get("sender_raw"),
                    "channel": msg.get("channel_or_thread"),
                    "snippet": (msg.get("content") or "")[:200],
                    "source": msg.get("source"),
                })

        tension_pairs = defaultdict(int)
        cross_team_keywords = ["sales vs", "product vs", "engineering vs", "vs product", "vs sales"]
        for msg in messages:
            content = (msg.get("content") or "").lower()
            for kw in cross_team_keywords:
                if kw in content:
                    tension_pairs[kw] += 1

        return {
            "conflict_message_count": len(conflict_msgs),
            "conflict_ratio": round(len(conflict_msgs) / max(len(messages), 1), 3),
            "conflict_messages": conflict_msgs[:10],
            "tension_pairs": dict(tension_pairs),
            "departments_in_conflict": list(set(
                m.get("channel", "").split("-")[0] for m in conflict_msgs if m.get("channel")
            )),
        }


    def _extract_velocity_signals(self, messages: list[dict]) -> dict:
        """Measure decision and execution velocity."""

        delay_keywords = ["delayed", "still waiting", "2 weeks", "45+ days", "taking too long",
                          "hasn't moved", "no progress", "stuck on"]
        fast_keywords = ["done", "shipped", "completed", "resolved", "fixed", "launched"]

        delay_msgs = [m for m in messages if any(kw in (m.get("content") or "").lower() for kw in delay_keywords)]
        fast_msgs = [m for m in messages if any(kw in (m.get("content") or "").lower() for kw in fast_keywords)]

        domain_delays = defaultdict(int)
        domain_keywords = {
            "hiring": ["hiring", "recruitment", "candidate"],
            "budget": ["budget", "approval", "finance", "sign-off"],
            "product": ["roadmap", "feature", "release", "ship"],
            "support": ["support", "security validation", "sla"],
        }
        for msg in messages:
            content = (msg.get("content") or "").lower()
            if any(kw in content for kw in delay_keywords):
                for domain, dkws in domain_keywords.items():
                    if any(dkw in content for dkw in dkws):
                        domain_delays[domain] += 1

        return {
            "delay_message_count": len(delay_msgs),
            "fast_execution_count": len(fast_msgs),
            "velocity_ratio": round(len(fast_msgs) / max(len(delay_msgs) + len(fast_msgs), 1), 3),
            "domain_delays": dict(domain_delays),
            "delay_snippets": [m.get("content", "")[:150] for m in delay_msgs[:5]],
        }


    def _get_date_range(self, messages: list[dict]) -> dict:
        timestamps = []
        for msg in messages:
            ts = msg.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        if ts.replace(".", "").isdigit():
                            ts = datetime.fromtimestamp(float(ts))
                        else:
                            ts = datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+00:00", ""))
                    elif isinstance(ts, (int, float)):
                        ts = datetime.fromtimestamp(float(ts))
                    timestamps.append(ts)
                except Exception:
                    pass

        avg_response_hours = 0
        estimated_avg_days = 14  
        if len(timestamps) > 2:
            timestamps.sort()
            gaps = [
                (timestamps[i+1] - timestamps[i]).total_seconds() / 3600
                for i in range(len(timestamps)-1)
                if 0.5 < (timestamps[i+1] - timestamps[i]).total_seconds() / 3600 < 168
            ]
            if gaps:
                avg_response_hours = round(np.mean(gaps), 2)
                estimated_avg_days = round(avg_response_hours / 8, 1)
