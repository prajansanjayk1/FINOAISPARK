from typing import List
import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_mfa_verified_user
from app.api.dependencies.security import PermissionChecker
from app.application.dto import ApprovalSubmit, PAMRequestResponse
from app.application.use_cases.pam_use_cases import PAMUseCases
from app.infrastructure.database.connection import get_db
from app.infrastructure.audit.log_service import AuditLogService
from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyPAMRequestRepository

router = APIRouter(prefix="/approvals", tags=["PAM Approvals"])


@router.post(
    "/",
    response_model=PAMRequestResponse,
    dependencies=[Depends(PermissionChecker(resource="REQUEST", action="APPROVE"))]
)
async def submit_approval(
    dto: ApprovalSubmit,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_mfa_verified_user)
):
    """
    Submits a Manager approval or rejection for a pending privileged request.
    """
    correlation_id = getattr(http_request.state, "correlation_id", str(uuid.uuid4()))
    trace_id = getattr(http_request.state, "trace_id", str(uuid.uuid4()))
    ip_address = http_request.client.host if http_request.client else "127.0.0.1"

    # Process manager approval
    updated_request = await PAMUseCases.approve_request(db, dto.request_id, current_user.id, dto)

    # Log the action in the compliance audit trail
    await AuditLogService.log_action(
        db=db,
        user_id=current_user.id,
        role=current_user.roles[0].name if current_user.roles else "Manager",
        ip_address=ip_address,
        endpoint="/api/v1/approvals",
        method="POST",
        correlation_id=correlation_id,
        trace_id=trace_id,
        previous_value={"status": "PENDING"},
        new_value={
            "request_id": str(updated_request.id),
            "approver_id": str(current_user.id),
            "status": updated_request.status,
            "comments": dto.comments,
        },
        ai_decision_id=updated_request.ai_decision.id if updated_request.ai_decision else None
    )

    return PAMRequestResponse.model_validate(updated_request)


@router.get(
    "/pending",
    response_model=List[PAMRequestResponse],
    dependencies=[Depends(PermissionChecker(resource="REQUEST", action="APPROVE"))]
)
async def list_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_mfa_verified_user)
):
    """
    Lists all privileged requests currently in a PENDING state, awaiting authorization.
    """
    repo = SQLAlchemyPAMRequestRepository(db)
    pending_requests = await repo.list_pending_approvals()
    return [PAMRequestResponse.model_validate(r) for r in pending_requests]
