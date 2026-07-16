import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_mfa_verified_user
from app.api.dependencies.security import PermissionChecker
from app.application.use_cases.risk_use_cases import RiskAssessorUseCases
from app.infrastructure.database.connection import get_db

router = APIRouter(prefix="/risk", tags=["Risk Metrics"])


@router.get(
    "/{user_id}",
    dependencies=[Depends(PermissionChecker(resource="RISK", action="READ"))]
)
async def get_user_risk_score(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Computes and returns the dynamic user risk metrics and historical security alerts.
    """
    risk_profile = await RiskAssessorUseCases.get_user_risk_profile(db, user_id)
    return risk_profile
