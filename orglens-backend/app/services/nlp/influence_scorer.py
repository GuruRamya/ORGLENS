from typing import Optional
from loguru import logger

class InfluenceScorer:
    def __init__(self):
        self.logger = logger

    def score_message_influence(
        self,
        text: str,
        sender_formal_authority: float,
        sender_title: Optional[str] = None,
        received_responses: int = 0,
        decision_followed: bool = False,
    ) -> float:
        score = 0.0

        content_score = self._score_content_influence(text)  
        score += content_score

        authority_score = sender_formal_authority * 2  
        authority_score += self._infer_informal_authority(text, sender_title)  
        score += authority_score

        reception_score = min(received_responses * 0.5, 2.0)  
        score += reception_score

        if decision_followed:
            score += 2.0

        return min(score, 10.0)

    def score_person_influence(
        self,
        messages_count: int,
        avg_message_influence: float,
        avg_response_rate: float,
        objections_accepted: int,
        objections_total: int,
        decision_outcomes: list[bool],
    ) -> float:
        score = 0.0

        if messages_count > 100:
            activity_score = 2.0  
        elif messages_count > 20:
            activity_score = 1.0
        else:
            activity_score = 0.3

        score += activity_score

        quality_score = (avg_message_influence / 10.0) * 3.0  # 0-3
        score += quality_score

        response_score = avg_response_rate * 2.0  # 0-2
        score += response_score

        if objections_total > 0:
            objection_credibility = (objections_accepted / objections_total) * 2.0  # 0-2
        else:
            objection_credibility = 0.0

        score += objection_credibility

        if decision_outcomes:
            outcome_ratio = sum(decision_outcomes) / len(decision_outcomes)
            outcome_score = outcome_ratio * 2.0  
        else:
            outcome_score = 0.0

        score += outcome_score

        return min(score, 10.0)

    def score_formal_vs_actual_gap(
        self,
        formal_authority: float,
        actual_influence: float,
    ) -> float:
        gap = abs(formal_authority - actual_influence)
        return min(gap, 10.0)

    def identify_influence_type(
        self,
        formal_authority: float,
        actual_influence: float,
        message_tone: str,
        decision_outcomes: list[bool],
    ) -> str:
        authority_gap = actual_influence - formal_authority

        if actual_influence > formal_authority + 2.0:
            return "hidden_power"
        elif formal_authority > actual_influence + 2.0:
            return "ignored_authority"
        elif formal_authority > 6.0 and actual_influence > 6.0:
            return "formal_leader"
        elif message_tone == "blocking" and actual_influence > 5.0:
            return "gatekeeper"
        else:
            return "neutral"

    def calculate_credibility(
        self,
        objections_made: int,
        objections_followed: int,
        decisions_proposed: int,
        decisions_implemented: int,
    ) -> float:
        if objections_made == 0 and decisions_proposed == 0:
            return 0.5

        objection_accuracy = (
            objections_followed / objections_made if objections_made > 0 else 0.5
        )

        implementation_accuracy = (
            decisions_implemented / decisions_proposed if decisions_proposed > 0 else 0.5
        )

        credibility = (objection_accuracy + implementation_accuracy) / 2.0
        return min(credibility, 1.0)


    def _score_content_influence(self, text: str) -> float:
        """Score how influential the content of a message is (0-4)"""
        score = 1.0  

        text_lower = text.lower()

        conviction_phrases = ["must", "need to", "should", "required", "must have"]
        conviction_count = sum(1 for phrase in conviction_phrases if phrase in text_lower)
        score += min(conviction_count * 0.5, 1.0)

        veto_phrases = ["can't", "won't", "not possible", "blocked", "rejected"]
        veto_count = sum(1 for phrase in veto_phrases if phrase in text_lower)
        score += min(veto_count * 0.5, 1.0)

        words = text.split()
        if len(words) > 50:
            score += 0.5
        elif len(words) > 20:
            score += 0.2

        has_numbers = any(char.isdigit() for char in text)
        if has_numbers:
            score += 0.3

        return min(score, 4.0)

    def _infer_informal_authority(
        self,
        text: str,
        sender_title: Optional[str] = None,
    ) -> float:
        """Infer informal authority from message content and role (0-2)"""
        score = 0.0

        text_lower = text.lower()

        expertise_phrases = ["i've seen", "in my experience", "i know", "based on", "years of"]
        expertise_count = sum(1 for phrase in expertise_phrases if phrase in text_lower)
        score += min(expertise_count * 0.3, 0.6)

        consensus_phrases = ["everyone", "the team", "we all", "consensus"]
        consensus_count = sum(1 for phrase in consensus_phrases if phrase in consensus_phrases)
        score += min(consensus_count * 0.3, 0.4)

        if sender_title:
            title_lower = sender_title.lower()
            if "senior" in title_lower or "principal" in title_lower:
                score += 0.4
            elif "lead" in title_lower or "architect" in title_lower:
                score += 0.3

        return min(score, 2.0)
