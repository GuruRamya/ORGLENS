from typing import Optional
from loguru import logger
import numpy as np
from datetime import datetime, timedelta

class Predictor:

    def __init__(self, influence_model=None):
        self.influence_model = influence_model
        self.logger = logger

    def predict_attrition_risk(
        self,
        employee_id: str,
        influence_score: float,
        formal_authority: float,
        avg_message_influence: float,
        objections_accepted_ratio: float,
        tenure_months: int,
        department_turnover_rate: float,
    ) -> dict:
        probability = 0.15 

        authority_gap = abs(influence_score - formal_authority)
        if authority_gap > 3:
            if influence_score > formal_authority:
                probability += 0.15
            else:
                probability += 0.20

        if objections_accepted_ratio < 0.3:
            probability += 0.15

        if 18 <= tenure_months <= 36:
            probability += 0.10
        elif tenure_months < 12:
            probability += 0.05

        probability += department_turnover_rate * 0.2

        probability = min(probability, 0.95)

        if probability > 0.6:
            risk_level = "critical"
        elif probability > 0.4:
            risk_level = "high"
        elif probability > 0.25:
            risk_level = "medium"
        else:
            risk_level = "low"

        risk_factors = []
        if authority_gap > 3:
            risk_factors.append({
                "factor": "authority_gap",
                "description": f"Authority gap of {authority_gap:.1f} points",
                "type": "ignored_authority" if influence_score < formal_authority else "hidden_power",
            })

        if objections_accepted_ratio < 0.3:
            risk_factors.append({
                "factor": "low_credibility",
                "description": "Opinions rarely listened to",
                "credibility": objections_accepted_ratio,
            })

        if 18 <= tenure_months <= 36:
            risk_factors.append({
                "factor": "high_flight_risk_tenure",
                "description": f"At peak flight risk (tenure: {tenure_months} months)",
            })

        return {
            "probability": float(probability),
            "risk_level": risk_level,
            "timeline_months": 12,
            "risk_factors": risk_factors,
            "actions_to_mitigate": self._get_attrition_mitigation_actions(risk_factors),
        }

    def predict_decision_reversal_probability(
        self,
        proposer_influence: float,
        proposer_conviction: float,
        objectors: list[dict],  
        decision_domain: str,
    ) -> dict:
        objector_influences = [obj.get("influence", 0) for obj in objectors]
        objector_convictions = [obj.get("conviction", 0) for obj in objectors]

        if self.influence_model and self.influence_model.decision_reversal_model:
            prob, explanation = self.influence_model.predict_decision_reversal(
                objector_influences,
                objector_convictions,
                decision_domain,
            )
        else:
            max_objector_influence = max(objector_influences) if objector_influences else 0
            avg_objector_conviction = np.mean(objector_convictions) if objector_convictions else 0

            prob = 0.0
            if max_objector_influence > proposer_influence:
                prob += 0.5
            if avg_objector_conviction > 0.6:
                prob += 0.3
            if len(objectors) > 2:
                prob += 0.1

            prob = min(prob, 1.0)
            explanation = {
                "strongest_objector": max_objector_influence,
                "proposer_influence": proposer_influence,
            }

        return {
            "probability": float(prob),
            "likely_reversal": prob > 0.6,
            "explanation": explanation,
            "confidence": 0.75 if self.influence_model else 0.45,
        }

    def predict_organization_health_trend(
        self,
        current_health_scores: dict, 
        historical_scores: list[dict],  
    ) -> dict:
        forecast = {
            "overall_health_6mo": 5.0,  
            "metric_forecasts": {},
            "trend": "stable",
            "risk_areas": [],
        }

        for metric, current_score in current_health_scores.items():
            if len(historical_scores) < 2:
                forecast["metric_forecasts"][metric] = {
                    "current": current_score,
                    "predicted_6mo": current_score,
                    "trend": "unknown",
                }
                continue

            historical_values = [s.get(metric, current_score) for s in historical_scores[-6:]]
            if len(historical_values) > 1:
                trend_direction = np.polyfit(range(len(historical_values)), historical_values, 1)[0]
            else:
                trend_direction = 0

            periods_ahead = 6
            forecast_value = current_score + (trend_direction * periods_ahead)
            forecast_value = max(0, min(forecast_value, 10))

            if trend_direction > 0.1:
                trend_label = "improving"
            elif trend_direction < -0.1:
                trend_label = "declining"
            else:
                trend_label = "stable"

            forecast["metric_forecasts"][metric] = {
                "current": current_score,
                "predicted_6mo": forecast_value,
                "trend": trend_label,
                "trend_slope": trend_direction,
            }

            if forecast_value < 3:
                forecast["risk_areas"].append({
                    "metric": metric,
                    "concern": f"Projected to drop to {forecast_value:.1f}/10",
                    "severity": "critical" if forecast_value < 2 else "high",
                })

        overall_current = np.mean(list(current_health_scores.values()))
        overall_trend = np.mean([s.get("trend_slope", 0) for s in forecast["metric_forecasts"].values()])

        overall_forecast = overall_current + (overall_trend * 6)
        overall_forecast = max(0, min(overall_forecast, 10))

        if overall_trend > 0.1:
            overall_trend_label = "improving"
        elif overall_trend < -0.1:
            overall_trend_label = "declining"
        else:
            overall_trend_label = "stable"

        forecast["overall_health_6mo"] = overall_forecast
        forecast["trend"] = overall_trend_label

        return forecast

    def predict_velocity_trend(
        self,
        current_avg_days: float,
        historical_days: list[float],
    ) -> dict:
        if len(historical_days) < 2:
            return {
                "current_avg_days": current_avg_days,
                "forecast_avg_days": current_avg_days,
                "trend": "unknown",
            }

        historical = list(historical_days[-6:])
        trend_slope = np.polyfit(range(len(historical)), historical, 1)[0]

        forecast_days = current_avg_days + (trend_slope * 3)  
        forecast_days = max(1, forecast_days)

        if trend_slope > 0.5:
            trend = "slowing"
        elif trend_slope < -0.5:
            trend = "accelerating"
        else:
            trend = "stable"

        return {
            "current_avg_days": current_avg_days,
            "forecast_avg_days": forecast_days,
            "trend": trend,
            "trend_slope": trend_slope,
            "recommendation": self._velocity_recommendation(forecast_days, trend),
        }


    def _get_attrition_mitigation_actions(self, risk_factors: list[dict]) -> list[str]:
        """Generate action items to mitigate attrition risk"""
        actions = []

        for factor in risk_factors:
            if factor["factor"] == "authority_gap":
                if factor["type"] == "hidden_power":
                    actions.append("Formalize role; acknowledge hidden authority explicitly")
                else:
                    actions.append("Redistribute authority; give formal recognition of influence")

            elif factor["factor"] == "low_credibility":
                actions.append("Review past decisions; understand why opinions aren't valued")

            elif factor["factor"] == "high_flight_risk_tenure":
                actions.append("Schedule career development conversation; discuss growth opportunities")

        return actions

    def _velocity_recommendation(self, forecast_days: float, trend: str) -> str:
        """Generate recommendation based on velocity forecast"""
        if forecast_days > 30:
            return "URGENT: Decision process is critical bottleneck. Streamline approval chains."
        elif forecast_days > 20 and trend == "slowing":
            return "Investigate why decisions are slowing. Address bottlenecks proactively."
        elif trend == "accelerating":
            return "Good trend. Continue current process improvements."
        else:
            return "Monitor velocity. Current pace is acceptable."
