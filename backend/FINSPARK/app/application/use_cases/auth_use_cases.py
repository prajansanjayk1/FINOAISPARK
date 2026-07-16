import uuid
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import AuthenticationError, EntityNotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_mfa_secret,
    hash_password,
    verify_password,
    verify_totp,
)
from app.domain.entities import User, Role
from app.application.dto import UserRegister
from app.infrastructure.database.models import DepartmentORM, RoleORM
from app.infrastructure.repositories.sqlalchemy_repositories import SQLAlchemyUserRepository


class AuthUseCases:
    """
    Application service orchestrating authentication and MFA registry workflows.
    """

    @staticmethod
    async def register_user(db: AsyncSession, dto: UserRegister) -> User:
        user_repo = SQLAlchemyUserRepository(db)

        # Validate duplicate details
        existing_user = await user_repo.get_by_username(dto.username)
        if existing_user:
            raise AuthenticationError("Username already registered.")
        
        existing_email = await user_repo.get_by_email(dto.email)
        if existing_email:
            raise AuthenticationError("Email address already registered.")

        # Extract or create department (supporting rapid bootstrap)
        stmt_dept = select(DepartmentORM).where(DepartmentORM.code == dto.department_code)
        res_dept = await db.execute(stmt_dept)
        dept = res_dept.scalar_one_or_none()
        if not dept:
            dept = DepartmentORM(name=f"{dto.department_code} Department", code=dto.department_code)
            db.add(dept)
            await db.flush()

        # Seed roles if they don't exist in system
        for role_name in dto.role_names:
            stmt_role = select(RoleORM).where(RoleORM.name == role_name)
            res_role = await db.execute(stmt_role)
            if not res_role.scalar_one_or_none():
                new_role = RoleORM(name=role_name, description=f"Default role for {role_name}")
                db.add(new_role)
        await db.flush()

        # Build Domain User
        domain_roles = [Role(id=uuid.uuid4(), name=r, description="") for r in dto.role_names]
        user = User(
            id=uuid.uuid4(),
            username=dto.username,
            email=dto.email,
            password_hash=hash_password(dto.password),
            is_active=True,
            mfa_secret=None,
            mfa_enabled=False,
            department_id=dept.id,
            roles=domain_roles
        )

        return await user_repo.save(user)

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, plain_password: str) -> Dict[str, Any]:
        """
        Authenticates credentials.
        If user has MFA enabled, returns metadata signaling that MFA code is required.
        """
        user_repo = SQLAlchemyUserRepository(db)
        user = await user_repo.get_by_username(username)

        if not user or not user.is_active:
            raise AuthenticationError("Invalid username or password.")

        if not verify_password(user.password_hash, plain_password):
            raise AuthenticationError("Invalid username or password.")

        # MFA enforcement check
        if user.mfa_enabled:
            return {"mfa_required": True, "access_token": "", "refresh_token": ""}

        # Generate standard tokens directly
        roles = [r.name for r in user.roles]
        access_token = create_access_token(subject=str(user.id), roles=roles)
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "mfa_required": False,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @staticmethod
    async def verify_mfa(db: AsyncSession, username: str, totp_code: str) -> Dict[str, Any]:
        """
        Validates TOTP token for login completion.
        """
        user_repo = SQLAlchemyUserRepository(db)
        user = await user_repo.get_by_username(username)

        if not user or not user.is_active or not user.mfa_secret:
            raise AuthenticationError("MFA verification is invalid.")

        if not verify_totp(user.mfa_secret, totp_code):
            raise AuthenticationError("Invalid TOTP verification code.")

        roles = [r.name for r in user.roles]
        access_token = create_access_token(subject=str(user.id), roles=roles)
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "mfa_required": False,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @staticmethod
    async def setup_mfa(db: AsyncSession, user_id: uuid.UUID) -> Tuple[str, str]:
        """
        Generates and saves a raw secret key, returning QR code provisioning URI.
        """
        user_repo = SQLAlchemyUserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise EntityNotFoundError("User not found.")

        secret = generate_mfa_secret()
        user.mfa_secret = secret
        await user_repo.save(user)

        provisioning_uri = f"otpauth://totp/FinSpark:{user.email}?secret={secret}&issuer=FinSpark"
        return secret, provisioning_uri

    @staticmethod
    async def enable_mfa(db: AsyncSession, user_id: uuid.UUID, code: str) -> None:
        """
        Confirms setup by validating initial code and activates MFA globally.
        """
        user_repo = SQLAlchemyUserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if not user or not user.mfa_secret:
            raise AuthenticationError("MFA setup is not initialized.")

        if not verify_totp(user.mfa_secret, code):
            raise AuthenticationError("MFA confirmation code is incorrect.")

        user.mfa_enabled = True
        await user_repo.save(user)
