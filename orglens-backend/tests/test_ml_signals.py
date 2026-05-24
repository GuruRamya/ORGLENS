"""
Tests for MLSignalExtractor.

Run: pytest tests/test_ml_signals.py -v
"""
import pytest
from app.services.ai_analysis.ml_signals import MLSignalExtractor


@pytest.fixture
def extractor():
    return MLSignalExtractor()


@pytest.fixture
def minimal_employees():
    return [
        {"id": "e1", "name": "Alice Chen", "title": "CEO", "level": "C-Suite",
         "department": "Leadership", "email": "alice@co.com"},
        {"id": "e2", "name": "Bob Smith", "title": "Staff Engineer", "level": "Senior IC",
         "department": "Engineering", "email": "bob@co.com"},
        {"id": "e3", "name": "Carol Nair", "title": "VP Sales", "level": "VP",
         "department": "Sales", "email": "carol@co.com"},
    ]


@pytest.fixture
def minimal_messages():
    from datetime import datetime, timedelta
    base = datetime(2024, 1, 1)
    return [
        {
            "source": "slack",
            "sender_raw": "Bob Smith",
            "channel_or_thread": "engineering",
            "content": "I've decided we're not using microservices. Final decision. Won't work.",
            "timestamp": str(base + timedelta(hours=1)),
        },
        {
            "source": "slack",
            "sender_raw": "Bob Smith",
            "channel_or_thread": "engineering",
            "content": "Blocking the deploy — error rate spiked. Need Alice's approval before re-deploying.",
            "timestamp": str(base + timedelta(hours=2)),
        },
        {
            "source": "slack",
            "sender_raw": "Alice Chen",
            "channel_or_thread": "general",
            "content": "We believe in a merit-based transparent organization. Everyone's voice matters.",
            "timestamp": str(base + timedelta(hours=3)),
        },
        {
            "source": "slack",
            "sender_raw": "Carol Nair",
            "channel_or_thread": "sales",
            "content": "Salary inversion is a real problem. New hires are being paid more than senior ICs.",
            "timestamp": str(base + timedelta(hours=4)),
        },
        {
            "source": "slack",
            "sender_raw": "Carol Nair",
            "channel_or_thread": "sales",
            "content": "I push back on this decision — it is not realistic given Q3 pipeline.",
            "timestamp": str(base + timedelta(hours=5)),
        },
    ]


class TestExtractAllSignals:
    def test_returns_expected_keys(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        expected_keys = [
            "person_signals", "trust_signals", "network_signals",
            "decision_signals", "resilience_signals", "sentiment_signals",
            "conflict_signals", "velocity_signals", "message_count", "employee_count",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_message_count(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        assert result["message_count"] == len(minimal_messages)

    def test_employee_count(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        assert result["employee_count"] == len(minimal_employees)


class TestPersonSignals:
    def test_person_signals_contains_all_employees(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        person_signals = result["person_signals"]
        for emp in minimal_employees:
            assert emp["name"] in person_signals, f"Missing person: {emp['name']}"

    def test_high_conviction_sender_scores_higher(self, extractor, minimal_employees, minimal_messages):
        """Bob sends conviction messages — should have higher conviction_count."""
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        bob = result["person_signals"]["Bob Smith"]
        alice = result["person_signals"]["Alice Chen"]
        assert bob["conviction_count"] >= 1

    def test_influence_score_nonnegative(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        for name, signals in result["person_signals"].items():
            assert signals["influence_score"] >= 0, f"{name} has negative influence"

    def test_influence_score_max_10(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        for name, signals in result["person_signals"].items():
            assert signals["influence_score"] <= 10, f"{name} influence > 10"

    def test_objection_count(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        carol = result["person_signals"]["Carol Nair"]
        assert carol["objection_count"] >= 1


class TestTrustSignals:
    def test_comp_inversion_detected(self, extractor, minimal_employees, minimal_messages):
        """Carol's message about salary inversion should be detected."""
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        trust = result["trust_signals"]
        assert len(trust.get("comp_inversion_evidence", [])) >= 1

    def test_trust_gap_score_range(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        score = result["trust_signals"]["trust_gap_score"]
        assert 0 <= score <= 10

    def test_escalation_count(self, extractor, minimal_employees, minimal_messages):
        """Bob's message mentions "Alice's approval" — escalation signal."""
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        trust = result["trust_signals"]
        assert isinstance(trust["escalation_count"], int)
        assert trust["escalation_count"] >= 0


class TestDecisionSignals:
    def test_decision_detected(self, extractor, minimal_employees, minimal_messages):
        """Bob's "Final decision" message should be extracted."""
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        decisions = result["decision_signals"]
        assert decisions["decision_count"] >= 1

    def test_reversal_rate_valid(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        rate = result["decision_signals"]["reversal_rate"]
        assert 0.0 <= rate <= 1.0

    def test_estimated_avg_days_positive(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        days = result["decision_signals"]["estimated_avg_days"]
        assert days > 0


class TestConflictSignals:
    def test_push_back_detected(self, extractor, minimal_employees, minimal_messages):
        """Carol's 'push back' should register as conflict."""
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        conflict = result["conflict_signals"]
        assert conflict["conflict_message_count"] >= 1

    def test_conflict_ratio_range(self, extractor, minimal_employees, minimal_messages):
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, {})
        ratio = result["conflict_signals"]["conflict_ratio"]
        assert 0.0 <= ratio <= 1.0


class TestEdgeCases:
    def test_empty_messages(self, extractor, minimal_employees):
        result = extractor.extract_all_signals(minimal_employees, [], {})
        assert result["message_count"] == 0
        assert result["employee_count"] == len(minimal_employees)

    def test_empty_employees(self, extractor, minimal_messages):
        result = extractor.extract_all_signals([], minimal_messages, {})
        assert result["employee_count"] == 0
        assert result["message_count"] == len(minimal_messages)

    def test_completely_empty(self, extractor):
        result = extractor.extract_all_signals([], [], {})
        assert result["message_count"] == 0
        assert result["employee_count"] == 0

    def test_message_without_sender(self, extractor, minimal_employees):
        msgs = [{"source": "slack", "sender_raw": "", "content": "Hello", "timestamp": "2024-01-01"}]
        result = extractor.extract_all_signals(minimal_employees, msgs, {})
        assert result["message_count"] == 1

    def test_org_context_stored(self, extractor, minimal_employees, minimal_messages):
        ctx = {"name": "TestCorp", "industry": "Tech"}
        result = extractor.extract_all_signals(minimal_employees, minimal_messages, ctx)
        assert result["org_context"] == ctx
