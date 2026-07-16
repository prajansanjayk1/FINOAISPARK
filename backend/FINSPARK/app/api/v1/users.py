from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.security import PermissionChecker
from app.domain.entities import User
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import UserORM
from app.infrastructure.repositories.sqlalchemy_repositories import to_domain_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the details of the currently authenticated session user.
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "mfa_enabled": current_user.mfa_enabled,
        "roles": [r.name for r in current_user.roles],
    }


@router.get(
    "/",
    dependencies=[Depends(PermissionChecker(resource="USER", action="READ"))]
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all corporate users and active roles. Restricted to Auditing & Security Admins.
    """
    stmt = (
        select(UserORM)
        .options(selectinload(UserORM.roles))
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    users = res.scalars().all()
    
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "is_active": u.is_active,
            "roles": [r.name for r in u.roles]
        }
        for u in users
    ]
