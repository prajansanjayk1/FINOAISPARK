from datetime import datetime, timezone
import random
import uuid
from typing import Any, Dict, Tuple
from app.core.config import settings
from app.domain.entities import AIDecision, Asset, PAMRequest, User


class AIGovernanceEngine:
    """
    Core AI Decision Engine for PAM Governance.
    Evaluates request characteristics, calculates risk scores, and outputs
    compliance assessments with natural-language explanation (Explainable AI - XAI).
    """

    def __init__(self):
        self.model_version = settings.AI_MODEL_VERSION
        self.confidence_threshold = settings.AI_DECISION_CONFIDENCE_THRESHOLD

    def evaluate_request(self, user: User, asset: Asset, request: PAMRequest) -> AIDecision:
        """
        Executes AI risk scoring and produces a detailed audit-ready decision.
        """
        # Calculate risk scores based on request attributes (heuristic proxy for classifier model)
        risk_score, details = self._calculate_risk_score(user, asset, request)
        
        # Decide allowance based on risk metrics
        if risk_score >= 80.0:
            decision = "DENY"
            explanation = (
                f"AI Governance model predicted high risk ({risk_score:.1f}/100) exceeding block threshold. "
                f"Factors: {', '.join(details.get('high_risk_triggers', []))}."
            )
        elif risk_score >= 40.0:
            decision = "ESCALATE"
            explanation = (
                f"AI Governance model flagged medium risk ({risk_score:.1f}/100) requiring human-in-the-loop validation. "
                f"Factors: {', '.join(details.get('escalation_triggers', []))}."
            )
        else:
            decision = "ALLOW"
            explanation = f"AI Governance model approved access request with low risk prediction ({risk_score:.1f}/100)."

        # Mock ML Model confidence score (between 0.82 and 0.99)
        # Using a deterministic seed based on request UUID for testing consistency
        random.seed(int(request.id.hex[:8], 16))
        confidence_score = round(random.uniform(0.85, 0.99), 3)

        return AIDecision(
            id=uuid.uuid4(),
            request_id=request.id,
            decision=decision,
            confidence_score=confidence_score,
            risk_score=risk_score,
            rules_evaluated=details,
            explanation=explanation,
            model_version=self.model_version,
            created_at=datetime.now(timezone.utc)
        )

    def _calculate_risk_score(self, user: User, asset: Asset, request: PAMRequest) -> Tuple[float, Dict[str, Any]]:
        """
        AI Classifier heuristic approximation.
        """
        base_score = 10.0
        high_risk_triggers = []
        escalation_triggers = []

        # Factor 1: Asset Criticality
        if asset.critical_level == "CRITICAL":
            base_score += 40.0
            escalation_triggers.append("Target asset critical level is CRITICAL.")
        elif asset.critical_level == "HIGH":
            base_score += 20.0
            escalation_triggers.append("Target asset critical level is HIGH.")

        # Factor 2: Requested session duration
        if request.duration_seconds > 7200:  # > 2 Hours
            base_score += 15.0
            escalation_triggers.append("Requested duration exceeds 2 hours.")
        if request.duration_seconds > 14400:  # > 4 Hours
            base_score += 30.0
            high_risk_triggers.append("Requested duration violates safety bounds (> 4 hours).")

        # Factor 3: Time-of-Day anomalies
        current_hour = datetime.now(timezone.utc).hour
        if current_hour < 6 or current_hour > 20:  # Late night / early morning UTC
            base_score += 20.0
            escalation_triggers.append("Access request made outside normal core operational windows (06:00-20:00 UTC).")

        # Factor 4: Separation of duties checks
        user_roles = {role.name for role in user.roles}
        if "Database Administrator" in user_roles and asset.type != "DATABASE":
            base_score += 50.0
            high_risk_triggers.append("Role 'Database Administrator' trying to access non-database asset.")

        # Factor 5: Justification evaluation
        # Production versions would run NLP sentiment / classification on justification strings
        justification_lower = request.justification.lower()
        if len(justification_lower) < 15:
            base_score += 10.0
            escalation_triggers.append("Justification details are sparse.")
        if any(bad_word in justification_lower for bad_word in ["hack", "bypass", "override", "temp-fix"]):
            base_score += 25.0
            high_risk_triggers.append("Justification contains risk-related override keywords.")

        # Constrain score between 0.0 and 100.0
        risk_score = min(max(base_score, 0.0), 100.0)

        details = {
            "base_risk": base_score,
            "calculated_score": risk_score,
            "high_risk_triggers": high_risk_triggers,
            "escalation_triggers": escalation_triggers,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }

        return risk_score, details


# Global instance
ai_governance_engine = AIGovernanceEngine()
