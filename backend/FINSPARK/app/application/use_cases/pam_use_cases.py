from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolation, EntityNotFoundError
from app.domain.entities import Approval, Asset, PAMRequest
from app.application.dto import AssetCreate, ApprovalSubmit, PAMRequestCreate
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SQLAlchemyAssetRepository,
    SQLAlchemyPAMRequestRepository,
    SQLAlchemyUserRepository,
)


class PAMUseCases:
    """
    Application service managing privileged assets and request workflows.
    """

    @staticmethod
    async def create_asset(db: AsyncSession, dto: AssetCreate) -> Asset:
        repo = SQLAlchemyAssetRepository(db)
        asset = Asset(
            id=uuid.uuid4(),
            name=dto.name,
            type=dto.type,
            critical_level=dto.critical_level,
            network_address=dto.network_address,
            created_at=datetime.now(timezone.utc),
        )
        return await repo.save(asset)

    @staticmethod
    async def get_asset(db: AsyncSession, asset_id: uuid.UUID) -> Optional[Asset]:
        repo = SQLAlchemyAssetRepository(db)
        return await repo.get_by_id(asset_id)

    @staticmethod
    async def list_assets(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Asset]:
        repo = SQLAlchemyAssetRepository(db)
        return await repo.list_all(skip, limit)

    @staticmethod
    async def get_request(db: AsyncSession, request_id: uuid.UUID) -> Optional[PAMRequest]:
        repo = SQLAlchemyPAMRequestRepository(db)
        return await repo.get_by_id(request_id)

    @staticmethod
    async def approve_request(
        db: AsyncSession,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        dto: ApprovalSubmit
    ) -> PAMRequest:
        """
        Processes a manager approval for an escalated or pending access request.
        Updates the request status based on manager inputs.
        """
        request_repo = SQLAlchemyPAMRequestRepository(db)
        user_repo = SQLAlchemyUserRepository(db)
        
        request = await request_repo.get_by_id(request_id)
        if not request:
            raise EntityNotFoundError("Privileged access request not found.")

        if request.status != "PENDING":
            raise BusinessRuleViolation(f"Cannot approve request in '{request.status}' state.")

        # Verify approver actually exists and holds manager privileges
        approver = await user_repo.get_by_id(approver_id)
        if not approver:
            raise EntityNotFoundError("Approver not found.")
        
        is_manager = any(role.name in ("Manager", "Chief Information Security Officer (CISO)", "Security Administrator") for role in approver.roles)
        if not is_manager:
            raise BusinessRuleViolation("Only designated Managers or Security Administrators can approve PAM requests.")

        # Create Domain Approval
        approval = Approval(
            id=uuid.uuid4(),
            request_id=request_id,
            approver_id=approver_id,
            status=dto.status,  # APPROVED or REJECTED
            comments=dto.comments or "",
            created_at=datetime.now(timezone.utc)
        )

        request.approvals.append(approval)
        
        # Transition State
        if dto.status == "APPROVED":
            request.status = "APPROVED"
        else:
            request.status = "REJECTED"

        request.updated_at = datetime.now(timezone.utc)
        
        return await request_repo.save(request)
