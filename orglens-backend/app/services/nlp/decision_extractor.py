import spacy
from typing import Optional
from loguru import logger
import re

class DecisionExtractor:

    DECISION_KEYWORDS = {
        "approve": ["approved", "approve", "ok", "accepted", "agreed"],
        "reject": ["rejected", "reject", "declined", "denied", "refused", "no"],
        "object": ["concern", "worried", "risky", "issue", "problem", "against", "but i"],
        "stall": ["wait", "postpone", "later", "defer", "hold off", "need more info"],
        "pivot": ["changed", "decided", "going with", "switching to", "now we"],
    }

    DECISION_DOMAINS = {
        "hiring": ["hire", "hire", "recruitment", "candidate", "interview", "onboard", "job", "position"],
        "budget": ["budget", "spend", "cost", "finance", "money", "price", "expense", "allocation"],
        "product": ["feature", "product", "release", "launch", "build", "ship", "roadmap"],
        "process": ["process", "workflow", "policy", "procedure", "system", "change"],
        "strategy": ["strategy", "direction", "pivot", "plan", "goal", "vision"],
        "organization": ["structure", "team", "department", "reorganize", "reporting"],
    }

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Spacy model not found. Using basic tokenization.")
            self.nlp = None

    def extract_decisions(self, text: str) -> list[dict]:
        decisions = []
        text_lower = text.lower()

        sentences = self._split_sentences(text)

        for sentence in sentences:
            sentence_lower = sentence.lower()

            for decision_type, keywords in self.DECISION_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        confidence = self._calculate_decision_confidence(sentence, decision_type)
                        domain = self._detect_domain(sentence)

                        decisions.append({
                            "type": decision_type,
                            "domain": domain,
                            "text": sentence.strip(),
                            "confidence": confidence,
                            "is_decision": confidence > 0.6,
                        })
                        break

        return [d for d in decisions if d["is_decision"]]

    def extract_objections(self, text: str) -> list[dict]:
        objections = []
        sentences = self._split_sentences(text)

        objection_indicators = [
            "concern", "problem", "risk", "worried", "worried about",
            "but", "however", "issue", "against", "shouldn't",
            "don't think", "risky", "not sure"
        ]

        for sentence in sentences:
            sentence_lower = sentence.lower()

            if any(indicator in sentence_lower for indicator in objection_indicators):
                strength = self._calculate_objection_strength(sentence)
                if strength > 0.4:
                    objections.append({
                        "text": sentence.strip(),
                        "strength": strength,
                    })

        return objections

    def extract_influence_signals(self, text: str, sender_title: Optional[str] = None) -> dict:
        text_lower = text.lower()

        conviction_phrases = [
            "must", "need to", "should", "have to", "requires",
            "i've decided", "we're going", "final decision"
        ]

        veto_phrases = [
            "can't", "won't work", "we can't", "not possible", "blocked",
            "this won't", "that won't", "rejected"
        ]

        question_phrases = [
            "have you considered", "what if", "did you think about",
            "question is", "wondering", "curious"
        ]

        suggestion_phrases = [
            "maybe", "perhaps", "could", "might", "think about",
            "should consider", "might want to"
        ]

        conviction_score = sum(1 for phrase in conviction_phrases if phrase in text_lower) / len(conviction_phrases)
        veto_score = sum(1 for phrase in veto_phrases if phrase in text_lower) / len(veto_phrases)
        question_score = sum(1 for phrase in question_phrases if phrase in text_lower) / len(question_phrases)
        suggestion_score = sum(1 for phrase in suggestion_phrases if phrase in text_lower) / len(suggestion_phrases)

        influence_signal = min(
            max(conviction_score, veto_score, question_score, suggestion_score),
            1.0
        )

        return {
            "influence_signal": influence_signal,
            "has_conviction": conviction_score > 0.3,
            "uses_veto": veto_score > 0.3,
            "uses_questions": question_score > 0.3,
            "uses_suggestions": suggestion_score > 0.3,
            "tone": self._determine_tone(conviction_score, veto_score, question_score),
        }


    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]

    def _calculate_decision_confidence(self, sentence: str, decision_type: str) -> float:
        """Score confidence that this is a real decision (0-1)"""
        score = 0.5

        if len(sentence.split()) > 5:
            score += 0.2

        if any(subj in sentence.lower() for subj in ["we ", "i ", "they ", "the team"]):
            score += 0.2

        if any(time in sentence.lower() for time in ["just", "now", "today", "yesterday"]):
            score += 0.1

        return min(score, 1.0)

    def _calculate_objection_strength(self, sentence: str) -> float:
        """Score how strong an objection is (0-1)"""
        sentence_lower = sentence.lower()
        score = 0.4

        strong_indicators = ["concern", "problem", "risk", "against", "shouldn't"]
        if any(ind in sentence_lower for ind in strong_indicators):
            score += 0.4

        if "can't" in sentence_lower or "won't" in sentence_lower:
            score += 0.2

        return min(score, 1.0)

    def _detect_domain(self, text: str) -> Optional[str]:
        """Detect which domain a decision relates to"""
        text_lower = text.lower()

        for domain, keywords in self.DECISION_DOMAINS.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain

        return None

    def _determine_tone(self, conviction: float, veto: float, question: float) -> str:
        """Determine tone: authoritative, blocking, exploratory"""
        if veto > 0.3:
            return "blocking"
        elif conviction > 0.3:
            return "authoritative"
        elif question > 0.3:
            return "exploratory"
        else:
            return "neutral"
