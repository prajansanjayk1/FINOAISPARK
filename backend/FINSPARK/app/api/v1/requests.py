from typing import List
import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_mfa_verified_user
from app.api.dependencies.security import PermissionChecker
from app.application.dto import PAMRequestCreate, PAMRequestResponse
from app.application.use_cases.risk_use_cases import AIGovernanceWorkflow
from app.core.exceptions import EntityNotFoundError
from app.infrastructure.database.connection import get_db
from app.infrastructure.audit.log_service import AuditLogService
from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyPAMRequestRepository

router = APIRouter(prefix="/requests", tags=["PAM Requests"])


@router.post(
    "/",
    response_model=PAMRequestResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_access_request(
    dto: PAMRequestCreate,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_mfa_verified_user)
):
    """
    Submits a privileged access request. Runs policy check and AI Governance Engine evaluation.
    Logs transaction compliance details.
    """
    correlation_id = getattr(http_request.state, "correlation_id", str(uuid.uuid4()))
    trace_id = getattr(http_request.state, "trace_id", str(uuid.uuid4()))
    ip_address = http_request.client.host if http_request.client else "127.0.0.1"

    # Evaluate request via AI Governance Workflow
    pam_request = await AIGovernanceWorkflow.evaluate_and_create_request(db, current_user.id, dto)

    # Log action in the immutable audit trail
    await AuditLogService.log_action(
        db=db,
        user_id=current_user.id,
        role=current_user.roles[0].name if current_user.roles else "User",
        ip_address=ip_address,
        endpoint="/api/v1/requests",
        method="POST",
        correlation_id=correlation_id,
        trace_id=trace_id,
        new_value={
            "request_id": str(pam_request.id),
            "asset_id": str(pam_request.asset_id),
            "action": pam_request.action_requested,
            "status": pam_request.status,
            "justification": pam_request.justification,
        },
        ai_decision_id=pam_request.ai_decision.id if pam_request.ai_decision else None
    )

    return PAMRequestResponse.model_validate(pam_request)


@router.get(
    "/",
    response_model=List[PAMRequestResponse]
)
async def list_access_requests(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_mfa_verified_user)
):
    """
    Retrieves privileged request history.
    Normal users view their own requests; Auditing/SOC Analysts view the complete history.
    """
    repo = SQLAlchemyPAMRequestRepository(db)
    
    # If the user has cross-bank read permissions, load all
    is_compliance_officer = any(
        role.name in ("Chief Information Security Officer (CISO)", "Compliance Officer", "SOC Analyst", "Auditor")
        for role in current_user.roles
    )
    
    if is_compliance_officer:
        requests = await repo.get_all_requests(limit=100)
    else:
        requests = await repo.list_by_user(current_user.id)
        
    return [PAMRequestResponse.model_validate(r) for r in requests]


@router.get(
    "/{request_id}",
    response_model=PAMRequestResponse
)
async def get_request_by_id(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_mfa_verified_user)
):
    """
    Fetches detailed metadata, decisions, and approvals for a specific PAM request.
    """
    repo = SQLAlchemyPAMRequestRepository(db)
    pam_request = await repo.get_by_id(request_id)
    
    if not pam_request:
        raise EntityNotFoundError("PAM access request not found.")

    # Access restriction check
    is_compliance_officer = any(
        role.name in ("Chief Information Security Officer (CISO)", "Compliance Officer", "SOC Analyst", "Auditor")
        for role in current_user.roles
    )
    if not is_compliance_officer and pam_request.requester_id != current_user.id:
        from app.core.exceptions import AuthorizationError
        raise AuthorizationError("Access Denied: You cannot view another user's access requests.")

    return PAMRequestResponse.model_validate(pam_request)
