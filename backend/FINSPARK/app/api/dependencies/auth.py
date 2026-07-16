from typing import Any, Dict
import uuid
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, MfaRequiredError
from app.core.security import decode_token
from app.domain.entities import User
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Decodes the Bearer token and returns the corresponding User domain entity.
    """
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Token is missing the subject claim.")
        
        user_uuid = uuid.UUID(user_id_str)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Authorization token has expired.")
    except (jwt.InvalidTokenError, ValueError):
        raise AuthenticationError("Authorization token is invalid.")

    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_id(user_uuid)
    
    if not user:
        raise AuthenticationError("User associated with this token does not exist.")
    
    if not user.is_active:
        raise AuthenticationError("User account is inactive.")

    return user


async def get_current_mfa_verified_user(
    user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Ensures that if the user has MFA enabled, their token contains the mfa_verified claim.
    """
    if user.mfa_enabled:
        try:
            payload = decode_token(token)
            if not payload.get("mfa_verified", False):
                raise MfaRequiredError("Multi-Factor Authentication (MFA) validation is required.")
        except Exception:
            raise MfaRequiredError("Multi-Factor Authentication (MFA) validation is required.")
            
    return user
