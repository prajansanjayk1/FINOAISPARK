from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, create_refresh_token
from app.application.dto import MfaVerify, MfaSetupResponse, TokenResponse, UserLogin, UserRegister, PAMRequestResponse
from app.application.use_cases.auth_use_cases import AuthUseCases
from app.api.dependencies.auth import get_current_user
from app.infrastructure.database.connection import get_db
from app.domain.entities import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(dto: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Registers a new corporate user and maps initial RBAC security roles.
    """
    user = await AuthUseCases.register_user(db, dto)
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [r.name for r in user.roles]
    }


@router.post("/login", response_model=TokenResponse)
async def login(dto: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticates username and password. If MFA is enabled, returns mfa_required=True.
    """
    res = await AuthUseCases.authenticate_user(db, dto.username, dto.password)
    return TokenResponse(
        access_token=res["access_token"],
        refresh_token=res["refresh_token"],
        mfa_required=res["mfa_required"]
    )


@router.post("/mfa/setup", response_model=MfaSetupResponse)
async def mfa_setup(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a secure secret token for TOTP Authenticator registration.
    """
    secret, uri = await AuthUseCases.setup_mfa(db, user.id)
    return MfaSetupResponse(mfa_secret=secret, provisioning_uri=uri)


@router.post("/mfa/enable", status_code=status.HTTP_200_OK)
async def mfa_enable(
    dto: MfaVerify,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates the initial setup verification code and enables MFA globally on the account.
    """
    if dto.username != user.username:
        raise AuthenticationError("Username mismatch during MFA confirmation.")
    await AuthUseCases.enable_mfa(db, user.id, dto.totp_code)
    return {"message": "Multi-Factor Authentication enabled successfully."}


@router.post("/mfa/verify", response_model=TokenResponse)
async def mfa_verify(dto: MfaVerify, db: AsyncSession = Depends(get_db)):
    """
    Completes logging in by verifying the TOTP code for MFA-enabled accounts.
    Returns access token with mfa_verified=True claim.
    """
    # Run verification
    res = await AuthUseCases.verify_mfa(db, dto.username, dto.totp_code)
    
    # Refresh tokens with mfa_verified claim
    from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyUserRepository
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_username(dto.username)
    
    roles = [r.name for r in user.roles]
    access_token = create_access_token(
        subject=str(user.id),
        roles=roles,
        additional_claims={"mfa_verified": True}
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        mfa_required=False
    )
