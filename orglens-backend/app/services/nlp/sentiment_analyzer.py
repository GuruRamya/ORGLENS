from textblob import TextBlob
from typing import Optional
import re


class SentimentAnalyzer:
    """
    Analyze sentiment and urgency of messages.
    Returns sentiment scores (-1 to 1) and urgency levels (0-1).
    """

    def __init__(self):
        pass

    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of text.
        Returns: {sentiment_score: -1 to 1, sentiment_label: negative/neutral/positive}
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  
            subjectivity = blob.sentiment.subjectivity  

            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"

            return {
                "sentiment_score": polarity,
                "sentiment_label": label,
                "subjectivity": subjectivity,
                "is_objective": subjectivity < 0.4,
                "is_subjective": subjectivity > 0.6,
            }
        except Exception:
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "subjectivity": 0.5,
                "is_objective": False,
                "is_subjective": False,
            }

    def analyze_urgency(self, text: str) -> dict:
        """
        Analyze urgency signals in text.
        Returns: {urgency_score: 0-1, urgency_level: low/medium/high/critical}
        """
        text_lower = text.lower()
        score = 0.0

        critical_phrases = [
            "asap", "urgent", "critical", "emergency", "immediately",
            "now", "right away", "blocking", "cannot wait", "blocked"
        ]
        for phrase in critical_phrases:
            if phrase in text_lower:
                score = 0.9
                break

        if score < 0.8:
            high_phrases = [
                "soon", "deadline", "week", "sprint", "ship",
                "launch", "needs", "must", "should", "today"
            ]
            high_count = sum(1 for phrase in high_phrases if phrase in text_lower)
            score = max(score, min(high_count * 0.15, 0.7))

        exclamation_count = text.count("!")
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

        if exclamation_count > 2:
            score = max(score, 0.6)

        if caps_ratio > 0.3:  
            score = max(score, 0.5)

        if score > 0.75:
            level = "critical"
        elif score > 0.5:
            level = "high"
        elif score > 0.25:
            level = "medium"
        else:
            level = "low"

        return {
            "urgency_score": min(score, 1.0),
            "urgency_level": level,
        }

    def analyze_tone(self, text: str) -> dict:
        """
        Analyze tone of communication.
        Returns: {tone_type, is_formal, is_aggressive, is_questioning, is_collaborative}
        """
        text_lower = text.lower()

        formal_indicators = ["therefore", "pursuant", "moreover", "accordingly", "hereby"]
        is_formal = sum(1 for ind in formal_indicators if ind in text_lower) > 0

        aggressive_indicators = [
            "can't", "won't", "never", "absolutely not", "blocked",
            "this won't work", "that's wrong", "don't"
        ]
        is_aggressive = sum(1 for ind in aggressive_indicators if ind in text_lower) >= 2

        is_questioning = (
            text.count("?") > 2 or
            sum(1 for ind in ["what if", "could we", "have you considered", "question is"]
                if ind in text_lower) >= 1
        )

        collaborative_indicators = [
            "we", "us", "together", "collaborate", "team", "let's", "can we",
            "what do you think", "your input"
        ]
        is_collaborative = sum(1 for ind in collaborative_indicators if ind in text_lower) >= 2

        if is_aggressive:
            tone = "blocking"
        elif is_questioning:
            tone = "exploratory"
        elif is_collaborative:
            tone = "collaborative"
        elif is_formal:
            tone = "formal"
        else:
            tone = "neutral"

        return {
            "tone_type": tone,
            "is_formal": is_formal,
            "is_aggressive": is_aggressive,
            "is_questioning": is_questioning,
            "is_collaborative": is_collaborative,
        }

    def analyze_confidence(self, text: str) -> dict:
        """
        Analyze confidence level in the message.
        Returns: {confidence_score: 0-1, is_confident, uses_qualifiers}
        """
        text_lower = text.lower()

        confident_phrases = [
            "definitely", "certainly", "absolutely", "no doubt", "clearly",
            "obviously", "without question", "of course"
        ]
        confidence_count = sum(1 for phrase in confident_phrases if phrase in text_lower)

        uncertainty_phrases = [
            "maybe", "perhaps", "might", "could", "possibly", "seems like",
            "i think", "might be", "sort of", "kind of", "a bit", "not sure"
        ]
        uncertainty_count = sum(1 for phrase in uncertainty_phrases if phrase in text_lower)

        score = 0.5  # Base
        score += min(confidence_count * 0.15, 0.3)
        score -= min(uncertainty_count * 0.1, 0.3)

        score = max(0.0, min(score, 1.0))

        return {
            "confidence_score": score,
            "is_confident": score > 0.6,
            "uses_qualifiers": uncertainty_count > 2,
            "qualifier_count": uncertainty_count,
        }

    def analyze_specificity(self, text: str) -> dict:
        """
        Analyze how specific/concrete a message is.
        Returns: {specificity_score: 0-1, has_numbers, has_examples, is_abstract}
        """
        text_lower = text.lower()
        words = text.split()

        has_numbers = bool(re.search(r'\d+', text))
        has_dates = bool(re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|q1|q2|q3|q4|\d{4})', text_lower))

        specific_phrases = ["example", "specifically", "for instance", "such as", "case"]
        has_examples = sum(1 for phrase in specific_phrases if phrase in text_lower) > 0

        abstract_phrases = ["things", "stuff", "generally", "usually", "sometimes", "sort of"]
        is_abstract = sum(1 for phrase in abstract_phrases if phrase in text_lower) >= 2

        score = 0.4  
        if has_numbers:
            score += 0.2
        if has_dates:
            score += 0.15
        if has_examples:
            score += 0.15
        if is_abstract:
            score -= 0.2

        score = max(0.0, min(score, 1.0))

        return {
            "specificity_score": score,
            "has_numbers": has_numbers,
            "has_dates": has_dates,
            "has_examples": has_examples,
            "is_abstract": is_abstract,
        }
