from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.api.dependencies.security import PermissionChecker
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import AIDecisionORM, AssetORM, PAMRequestORM

router = APIRouter(prefix="/dashboard", tags=["Analyst Dashboard"])


@router.get(
    "/",
    dependencies=[Depends(PermissionChecker(resource="DASHBOARD", action="READ"))]
)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Compiles live security KPIs, request statuses, and AI risk telemetry.
    """
    # 1. Total count query
    stmt_counts = (
        select(PAMRequestORM.status, func.count(PAMRequestORM.id))
        .group_by(PAMRequestORM.status)
    )
    res_counts = await db.execute(stmt_counts)
    counts = dict(res_counts.all())

    total_requests = sum(counts.values())
    pending_requests = counts.get("PENDING", 0)
    approved_requests = counts.get("APPROVED", 0) + counts.get("EXECUTED", 0)
    rejected_requests = counts.get("REJECTED", 0)

    # 2. Average Risk Score
    stmt_avg_risk = select(func.avg(AIDecisionORM.risk_score))
    res_avg_risk = await db.execute(stmt_avg_risk)
    avg_risk = res_avg_risk.scalar() or 0.0

    # 3. Critical Assets requested
    stmt_critical = (
        select(func.count(PAMRequestORM.id))
        .join(AssetORM, PAMRequestORM.asset_id == AssetORM.id)
        .where(AssetORM.critical_level == "CRITICAL")
    )
    res_critical = await db.execute(stmt_critical)
    critical_requests = res_critical.scalar() or 0

    return {
        "kpis": {
            "total_requests_processed": total_requests,
            "pending_manager_approvals": pending_requests,
            "auto_approved_or_executed": approved_requests,
            "policy_rejected_requests": rejected_requests,
            "average_ai_governance_risk": round(float(avg_risk), 2),
            "critical_infrastructure_requests": critical_requests,
        },
        "system_status": "OPERATIONAL",
        "ai_engine_health": "OPTIMAL"
    }
