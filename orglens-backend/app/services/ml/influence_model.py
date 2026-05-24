from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np
from typing import Optional, Tuple
from loguru import logger
import pickle
import json


class InfluenceModel:
    """
    Train ML models to predict:
    1. Whether a decision will be reversed based on who objects
    2. Influence scores for individuals
    3. Decision outcomes based on input pattern
    """

    def __init__(self):
        self.decision_reversal_model = None
        self.influence_score_model = None
        self.scaler = StandardScaler()
        self.logger = logger

    def train_decision_reversal_model(
        self,
        training_data: list[dict],
    ) -> dict:
        """
        Train model to predict if decision will be reversed.

        training_data format:
        [{
            "objectors": [...objector_ids...],
            "objector_influence_scores": [...],
            "objector_conviction_levels": [...],
            "decision_domain": "hiring|budget|product|etc",
            "was_reversed": True/False,
        }]

        Returns: {accuracy, feature_importance, model_stats}
        """
        if len(training_data) < 10:
            self.logger.warning("Not enough training data for reversal model")
            return {"status": "insufficient_data"}

        X, y = self._prepare_reversal_features(training_data)

        if len(X) < 5:
            return {"status": "insufficient_data"}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.decision_reversal_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )

        self.decision_reversal_model.fit(X_train, y_train)

        train_accuracy = self.decision_reversal_model.score(X_train, y_train)
        test_accuracy = self.decision_reversal_model.score(X_test, y_test)

        feature_importance = dict(
            zip(
                ["max_influence", "min_influence", "avg_influence", "conviction_avg", "objector_count"],
                self.decision_reversal_model.feature_importances_,
            )
        )

        return {
            "status": "success",
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "feature_importance": {k: float(v) for k, v in feature_importance.items()},
            "samples_trained": len(training_data),
        }

    def train_influence_score_model(
        self,
        training_data: list[dict],
    ) -> dict:
        """
        Train model to predict influence scores for people.

        training_data format:
        [{
            "messages_count": int,
            "avg_message_influence": float,
            "avg_response_count": int,
            "objections_made": int,
            "objections_accepted": int,
            "decisions_proposed": int,
            "decisions_implemented": int,
            "formal_authority": float 0-10,
            "actual_influence": float 0-10,  # TARGET
        }]

        Returns: {r2_score, feature_importance, model_stats}
        """
        if len(training_data) < 10:
            self.logger.warning("Not enough training data for influence model")
            return {"status": "insufficient_data"}

        X, y = self._prepare_influence_features(training_data)

        if len(X) < 5:
            return {"status": "insufficient_data"}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.influence_score_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
        )

        self.influence_score_model.fit(X_train_scaled, y_train)

        train_r2 = self.influence_score_model.score(X_train_scaled, y_train)
        test_r2 = self.influence_score_model.score(X_test_scaled, y_test)

        feature_importance = dict(
            zip(
                [
                    "messages_count", "avg_message_influence", "response_count",
                    "objection_credibility", "proposal_implementation", "formal_authority"
                ],
                self.influence_score_model.feature_importances_,
            )
        )

        return {
            "status": "success",
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "feature_importance": {k: float(v) for k, v in feature_importance.items()},
            "samples_trained": len(training_data),
        }

    def predict_decision_reversal(
        self,
        objector_influence_scores: list[float],
        objector_conviction_levels: list[float],
        decision_domain: str,
    ) -> Tuple[float, dict]:
        """
        Predict probability that a decision will be reversed (0-1).
        Returns: (probability, explanation)
        """
        if self.decision_reversal_model is None:
            return 0.5, {"status": "model_not_trained"}

        features = np.array([[
            max(objector_influence_scores) if objector_influence_scores else 0,
            min(objector_influence_scores) if objector_influence_scores else 0,
            np.mean(objector_influence_scores) if objector_influence_scores else 0,
            np.mean(objector_conviction_levels) if objector_conviction_levels else 0,
            len(objector_influence_scores),
        ]])

        probability = self.decision_reversal_model.predict_proba(features)[0][1]

        explanation = self._explain_reversal_prediction(
            objector_influence_scores,
            objector_conviction_levels,
            probability,
        )

        return float(probability), explanation

    def predict_influence_score(
        self,
        messages_count: int,
        avg_message_influence: float,
        avg_response_count: float,
        objections_made: int,
        objections_accepted: int,
        decisions_proposed: int,
        decisions_implemented: int,
        formal_authority: float,
    ) -> Tuple[float, dict]:
        """
        Predict influence score for a person (0-10).
        Returns: (predicted_influence, explanation)
        """
        if self.influence_score_model is None:
            return formal_authority, {"status": "model_not_trained"}

        objection_credibility = (objections_accepted / max(objections_made, 1)) * 10
        proposal_implementation = (decisions_implemented / max(decisions_proposed, 1)) * 10

        features = np.array([[
            messages_count,
            avg_message_influence,
            avg_response_count,
            objection_credibility,
            proposal_implementation,
            formal_authority,
        ]])

        features_scaled = self.scaler.transform(features)
        predicted = self.influence_score_model.predict(features_scaled)[0]

        predicted = max(0, min(predicted, 10))

        explanation = {
            "predicted_influence": predicted,
            "formal_authority": formal_authority,
            "gap": predicted - formal_authority,
            "drivers": {
                "message_activity": messages_count,
                "message_quality": avg_message_influence,
                "engagement": avg_response_count,
                "objection_credibility": objection_credibility / 10,
                "proposal_success": proposal_implementation / 10,
            },
        }

        return float(predicted), explanation

    def _prepare_reversal_features(self, training_data: list[dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for reversal model"""
        X = []
        y = []

        for record in training_data:
            influence_scores = record.get("objector_influence_scores", [])
            conviction_levels = record.get("objector_conviction_levels", [])

            if not influence_scores:
                continue

            features = [
                max(influence_scores),
                min(influence_scores),
                np.mean(influence_scores),
                np.mean(conviction_levels) if conviction_levels else 0,
                len(influence_scores),
            ]

            X.append(features)
            y.append(1 if record.get("was_reversed") else 0)

        return np.array(X), np.array(y)

    def _prepare_influence_features(self, training_data: list[dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for influence model"""
        X = []
        y = []

        for record in training_data:
            messages = record.get("messages_count", 0)
            avg_influence = record.get("avg_message_influence", 0.5)
            responses = record.get("avg_response_count", 0)
            obj_made = record.get("objections_made", 0)
            obj_accepted = record.get("objections_accepted", 0)
            dec_prop = record.get("decisions_proposed", 0)
            dec_impl = record.get("decisions_implemented", 0)
            formal = record.get("formal_authority", 5)

            objection_cred = (obj_accepted / max(obj_made, 1)) * 10
            proposal_impl = (dec_impl / max(dec_prop, 1)) * 10

            features = [
                messages,
                avg_influence,
                responses,
                objection_cred,
                proposal_impl,
                formal,
            ]

            X.append(features)
            y.append(record.get("actual_influence", 5))

        return np.array(X), np.array(y)

    def _explain_reversal_prediction(
        self,
        influence_scores: list[float],
        conviction_levels: list[float],
        probability: float,
    ) -> dict:
        """Generate human-readable explanation for reversal prediction"""
        max_influence = max(influence_scores) if influence_scores else 0
        avg_influence = np.mean(influence_scores) if influence_scores else 0

        reason = ""
        if probability > 0.7:
            reason = "High probability - strong objectors with high influence"
        elif probability > 0.5:
            reason = "Moderate probability - credible objectors present"
        else:
            reason = "Low probability - objectors lack strong influence"

        return {
            "probability": probability,
            "reason": reason,
            "strongest_objector_influence": max_influence,
            "average_objector_influence": avg_influence,
            "number_of_objectors": len(influence_scores),
        }
