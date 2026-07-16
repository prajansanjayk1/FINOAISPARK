from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.security import PermissionChecker
from app.application.dto import AssetCreate, AssetResponse
from app.application.use_cases.pam_use_cases import PAMUseCases
from app.core.exceptions import EntityNotFoundError
from app.infrastructure.database.connection import get_db

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(resource="ASSET", action="CREATE"))]
)
async def create_asset(
    dto: AssetCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new target resource (Server, Database, or Cloud Node).
    Requires Asset Creation clearance.
    """
    asset = await PAMUseCases.create_asset(db, dto)
    return AssetResponse.model_validate(asset)


@router.get(
    "/",
    response_model=List[AssetResponse]
)
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lists all target assets in the bank's active directory network.
    """
    assets = await PAMUseCases.list_assets(db, skip, limit)
    return [AssetResponse.model_validate(a) for a in assets]


@router.get(
    "/{asset_id}",
    response_model=AssetResponse
)
async def get_asset_by_id(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieves network and metadata details of a specific target asset.
    """
    asset = await PAMUseCases.get_asset(db, asset_id)
    if not asset:
        raise EntityNotFoundError(f"Asset with ID '{asset_id}' does not exist.")
    return AssetResponse.model_validate(asset)
