from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.domain.entities import AIDecision, PAMRequest
from app.domain.policies import PAMAccessPolicy
from app.application.dto import PAMRequestCreate
from app.infrastructure.ai.engine import ai_governance_engine
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SQLAlchemyAssetRepository,
    SQLAlchemyPAMRequestRepository,
    SQLAlchemyUserRepository,
)


class AIGovernanceWorkflow:
    """
    Orchestrates the event-driven AI Governance PAM decision loop.
    Intersects policies and AI classifications.
    """

    @staticmethod
    async def evaluate_and_create_request(
        db: AsyncSession,
        requester_id: uuid.UUID,
        dto: PAMRequestCreate
    ) -> PAMRequest:
        user_repo = SQLAlchemyUserRepository(db)
        asset_repo = SQLAlchemyAssetRepository(db)
        request_repo = SQLAlchemyPAMRequestRepository(db)

        # 1. Fetch related aggregates
        user = await user_repo.get_by_id(requester_id)
        if not user:
            raise EntityNotFoundError("Requester user not found.")

        asset = await asset_repo.get_by_id(dto.asset_id)
        if not asset:
            raise EntityNotFoundError("Target asset not found.")

        # 2. Build initial Request entity
        request = PAMRequest(
            id=uuid.uuid4(),
            requester_id=requester_id,
            asset_id=dto.asset_id,
            action_requested=dto.action_requested,
            duration_seconds=dto.duration_seconds,
            status="PENDING",
            justification=dto.justification,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # 3. Step A: Evaluate Static Organizational Compliance Policies
        policy_decision, policy_violations = PAMAccessPolicy.evaluate(user, asset, request)

        # Immediate hard block if policy violations dictate DENY
        if policy_decision == "DENY":
            request.status = "REJECTED"
            request.ai_decision = AIDecision(
                id=uuid.uuid4(),
                request_id=request.id,
                decision="DENY",
                confidence_score=1.0,
                risk_score=100.0,
                rules_evaluated={"violations": policy_violations},
                explanation=f"Hard policy violation blocked request: {'; '.join(policy_violations)}",
                model_version="static-policy-engine-v1",
                created_at=datetime.now(timezone.utc)
            )
            return await request_repo.save(request)

        # 4. Step B: Invoke the pluggable AI Governance Engine (Risk Scoring & Classifier)
        ai_decision = ai_governance_engine.evaluate_request(user, asset, request)
        request.ai_decision = ai_decision

        # 5. Blend static policy outputs with AI model predictions
        if policy_decision == "ESCALATE" or ai_decision.decision == "ESCALATE":
            request.status = "PENDING"  # Remains pending, awaiting manager approval
        elif ai_decision.decision == "DENY":
            request.status = "REJECTED"
        elif policy_decision == "ALLOW" and ai_decision.decision == "ALLOW":
            request.status = "APPROVED"  # Safe to auto-authorize execution

        # 6. Persist request changes
        saved_request = await request_repo.save(request)

        return saved_request
class RiskAssessorUseCases:
    """
    Handles auxiliary risk operations like retrieving risk history or calculating user scores.
    """
    @staticmethod
    async def get_user_risk_profile(db: AsyncSession, user_id: uuid.UUID) -> dict:
        user_repo = SQLAlchemyUserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User not found.")
        
        # Aggregate request history to construct a virtual risk profile
        request_repo = SQLAlchemyPAMRequestRepository(db)
        history = await request_repo.list_by_user(user_id)
        
        denied_count = sum(1 for r in history if r.status == "REJECTED")
        total_count = len(history)
        
        # Calculate dynamic ratio
        anomaly_ratio = denied_count / total_count if total_count > 0 else 0.0
        calculated_score = min(10.0 + (anomaly_ratio * 90.0), 100.0)

        return {
            "user_id": str(user_id),
            "calculated_risk_score": round(calculated_score, 2),
            "total_requests_evaluated": total_count,
            "failed_compliance_requests": denied_count,
            "risk_tier": "CRITICAL" if calculated_score >= 80 else "HIGH" if calculated_score >= 50 else "MEDIUM" if calculated_score >= 30 else "LOW"
        }
