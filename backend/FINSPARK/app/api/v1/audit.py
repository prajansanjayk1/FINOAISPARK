from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.security import PermissionChecker
from app.application.dto import AuditLogResponse
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyAuditLogRepository

router = APIRouter(prefix="/audit", tags=["Compliance Audit Logs"])


@router.get(
    "/",
    response_model=List[AuditLogResponse],
    dependencies=[Depends(PermissionChecker(resource="AUDIT", action="READ"))]
)
async def list_audit_trail(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Queries corporate system logs. Used for regulatory exams and security audits.
    """
    repo = SQLAlchemyAuditLogRepository(db)
    logs = await repo.list_all(skip, limit)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get(
    "/correlation/{correlation_id}",
    response_model=List[AuditLogResponse],
    dependencies=[Depends(PermissionChecker(resource="AUDIT", action="READ"))]
)
async def trace_by_correlation_id(
    correlation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Traces and groups logs relating to a single transaction request.
    """
    repo = SQLAlchemyAuditLogRepository(db)
    logs = await repo.get_logs_by_correlation_id(correlation_id)
    return [AuditLogResponse.model_validate(log) for log in logs]
