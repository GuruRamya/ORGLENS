"""
Tests for ConfidenceCalculator and ConfidenceMetrics.

Run: pytest tests/test_confidence.py -v
"""
import pytest
from app.services.confidence.confidence_framework import (
    ConfidenceCalculator,
    ConfidenceMetrics,
    ConfidenceLevel,
)


def make_metrics(**kwargs) -> ConfidenceMetrics:
    defaults = dict(
        total_messages=100,
        total_employees=20,
        messages_per_person=5.0,
        date_range_days=30,
        coverage_by_function={"Engineering": 0.8, "Sales": 0.6, "HR": 0.4},
        coverage_by_level={"C-Suite": 0.9, "IC": 0.5},
        confidence_breakdown={},
        strengths_detected=[],
        limitations_detected=[],
        recommended_data_improvements=[],
    )
    defaults.update(kwargs)
    return ConfidenceMetrics(**defaults)


class TestConfidenceCalculation:
    def test_zero_messages_gives_low_confidence(self):
        m = make_metrics(total_messages=0, total_employees=0, messages_per_person=0)
        assert m.calculate_base_confidence() == 0.0

    def test_good_data_gives_high_confidence(self):
        m = make_metrics(
            total_messages=500, total_employees=50,
            messages_per_person=10.0, date_range_days=60,
            coverage_by_function={"Eng": 0.9, "Sales": 0.8, "HR": 0.7},
        )
        conf = m.calculate_base_confidence()
        assert conf >= 0.7, f"Expected high confidence, got {conf}"

    def test_confidence_bounded_0_to_1(self):
        for msgs in [0, 5, 50, 500, 5000]:
            m = make_metrics(total_messages=msgs,
                             messages_per_person=msgs / 20 if msgs else 0)
            conf = m.calculate_base_confidence()
            assert 0 <= conf <= 1.0, f"Confidence out of range: {conf}"

    def test_more_messages_increases_confidence(self):
        low = make_metrics(total_messages=10, messages_per_person=0.5)
        high = make_metrics(total_messages=300, messages_per_person=15.0)
        assert high.calculate_base_confidence() > low.calculate_base_confidence()

    def test_longer_date_range_increases_confidence(self):
        short = make_metrics(date_range_days=5)
        long_ = make_metrics(date_range_days=60)
        assert long_.calculate_base_confidence() > short.calculate_base_confidence()


class TestConfidenceLevel:
    def test_critical_level_for_very_low_data(self):
        m = make_metrics(total_messages=5, messages_per_person=0.25, date_range_days=3,
                         coverage_by_function={"Eng": 0.1})
        assert m.get_confidence_level() == ConfidenceLevel.CRITICAL

    def test_high_level_for_rich_data(self):
        m = make_metrics(
            total_messages=1000, messages_per_person=20.0, date_range_days=90,
            coverage_by_function={"Eng": 0.95, "Sales": 0.85, "HR": 0.75, "Finance": 0.70},
        )
        level = m.get_confidence_level()
        assert level in (ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH)

    def test_level_values_are_strings(self):
        m = make_metrics()
        assert isinstance(m.get_confidence_level().value, str)


class TestWarnings:
    def test_low_message_volume_generates_warning(self):
        m = make_metrics(total_messages=10, messages_per_person=0.5)
        warnings = m.get_warnings()
        assert any("message" in w.lower() for w in warnings)

    def test_low_date_range_generates_warning(self):
        m = make_metrics(date_range_days=5)
        warnings = m.get_warnings()
        assert any("day" in w.lower() for w in warnings)

    def test_no_warnings_for_good_data(self):
        m = make_metrics(
            total_messages=500, messages_per_person=25.0, date_range_days=60,
            coverage_by_function={"Eng": 0.9, "Sales": 0.8},
        )
        warnings = m.get_warnings()
        assert len(warnings) == 0

    def test_warnings_are_strings(self):
        m = make_metrics(total_messages=5, messages_per_person=0.25)
        for w in m.get_warnings():
            assert isinstance(w, str)


class TestStrengthsAndLimitations:
    def test_strengths_for_good_message_count(self):
        m = make_metrics(total_messages=200, messages_per_person=10.0)
        assert len(m.get_strengths()) > 0

    def test_limitations_for_poor_data(self):
        m = make_metrics(total_messages=5, messages_per_person=0.25, date_range_days=3)
        assert len(m.get_limitations()) > 0

    def test_recommendations_for_low_coverage(self):
        m = make_metrics(coverage_by_function={"Eng": 0.1, "Sales": 0.05})
        recs = m.get_improvement_recommendations()
        assert any("coverage" in r.lower() or "representation" in r.lower() for r in recs)


class TestFromMLSignals:
    def test_builds_from_ml_signals(self):
        signals = {
            "message_count": 250,
            "employee_count": 30,
            "date_range": {"start": "2024-01-01", "end": "2024-03-31"},
            "person_signals": {
                "Alice": {"department": "Engineering", "level": "VP"},
                "Bob":   {"department": "Engineering", "level": "IC"},
                "Carol": {"department": "Sales",       "level": "IC"},
            },
        }
        metrics = ConfidenceCalculator.from_ml_signals(signals)
        assert metrics.total_messages == 250
        assert metrics.total_employees == 30
        assert metrics.messages_per_person == pytest.approx(250 / 30, rel=0.01)
        assert metrics.date_range_days > 0

    def test_handles_empty_signals(self):
        metrics = ConfidenceCalculator.from_ml_signals({})
        assert metrics.total_messages == 0
        assert metrics.total_employees == 0
        assert metrics.calculate_base_confidence() == 0.0

    def test_handles_none_signals(self):
        metrics = ConfidenceCalculator.from_ml_signals(None)
        assert metrics.total_messages == 0

    def test_coverage_by_function_computed(self):
        signals = {
            "message_count": 100, "employee_count": 4,
            "person_signals": {
                "A": {"department": "Engineering"},
                "B": {"department": "Engineering"},
                "C": {"department": "Sales"},
                "D": {"department": "HR"},
            },
        }
        metrics = ConfidenceCalculator.from_ml_signals(signals)
        assert "Engineering" in metrics.coverage_by_function
        assert metrics.coverage_by_function["Engineering"] == pytest.approx(0.5, rel=0.01)