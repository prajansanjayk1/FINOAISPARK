import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import Approval, AIDecision, Asset, AuditLog, Device, Permission, Role, User, PAMRequest
from app.domain.repositories import (
    IAssetRepository,
    IAuditLogRepository,
    IPAMRequestRepository,
    IUserRepository,
)
from app.infrastructure.database.models import (
    ApprovalORM,
    AIDecisionORM,
    AssetORM,
    AuditLogORM,
    DeviceORM,
    IPWhitelistORM,
    PermissionORM,
    RoleORM,
    UserORM,
    PAMRequestORM,
)


# ==============================================================================
# DDD MAPPERS (ORM <-> DOMAIN)
# ==============================================================================

def to_domain_permission(orm: PermissionORM) -> Permission:
    return Permission(
        id=orm.id,
        name=orm.name,
        resource=orm.resource,
        action=orm.action,
        description=orm.description,
    )


def to_domain_role(orm: RoleORM) -> Role:
    return Role(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        permissions=[to_domain_permission(p) for p in orm.permissions],
    )


def to_domain_user(orm: UserORM) -> User:
    return User(
        id=orm.id,
        username=orm.username,
        email=orm.email,
        password_hash=orm.password_hash,
        is_active=orm.is_active,
        mfa_secret=orm.mfa_secret,
        mfa_enabled=orm.mfa_enabled,
        department_id=orm.department_id,
        roles=[to_domain_role(r) for r in orm.roles],
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def to_domain_device(orm: DeviceORM) -> Device:
    return Device(
        id=orm.id,
        user_id=orm.user_id,
        fingerprint=orm.fingerprint,
        status=orm.status,
        last_used_at=orm.last_used_at,
        created_at=orm.created_at,
    )


def to_domain_asset(orm: AssetORM) -> Asset:
    return Asset(
        id=orm.id,
        name=orm.name,
        type=orm.type,
        critical_level=orm.critical_level,
        network_address=orm.network_address,
        created_at=orm.created_at,
    )


def to_domain_approval(orm: ApprovalORM) -> Approval:
    return Approval(
        id=orm.id,
        request_id=orm.request_id,
        approver_id=orm.approver_id,
        status=orm.status,
        comments=orm.comments,
        created_at=orm.created_at,
    )


def to_domain_ai_decision(orm: Optional[AIDecisionORM]) -> Optional[AIDecision]:
    if not orm:
        return None
    return AIDecision(
        id=orm.id,
        request_id=orm.request_id,
        decision=orm.decision,
        confidence_score=orm.confidence_score,
        risk_score=orm.risk_score,
        rules_evaluated=orm.rules_evaluated,
        explanation=orm.explanation,
        model_version=orm.model_version,
        created_at=orm.created_at,
    )


def to_domain_pam_request(orm: PAMRequestORM) -> PAMRequest:
    return PAMRequest(
        id=orm.id,
        requester_id=orm.requester_id,
        asset_id=orm.asset_id,
        action_requested=orm.action_requested,
        duration_seconds=orm.duration_seconds,
        status=orm.status,
        justification=orm.justification,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        approvals=[to_domain_approval(appr) for appr in orm.approvals],
        ai_decision=to_domain_ai_decision(orm.ai_decision),
    )


def to_domain_audit_log(orm: AuditLogORM) -> AuditLog:
    return AuditLog(
        id=orm.id,
        timestamp=orm.timestamp,
        user_id=orm.user_id,
        role=orm.role,
        ip_address=orm.ip_address,
        device_id=orm.device_id,
        endpoint=orm.endpoint,
        method=orm.method,
        previous_value=orm.previous_value,
        new_value=orm.new_value,
        ai_decision_id=orm.ai_decision_id,
        correlation_id=orm.correlation_id,
        trace_id=orm.trace_id,
    )


# ==============================================================================
# CONCRETE REPOSITORIES IMPLEMENTATIONS
# ==============================================================================

class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = (
            select(UserORM)
            .options(selectinload(UserORM.roles).selectinload(RoleORM.permissions))
            .where(UserORM.id == user_id)
        )
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()
        return to_domain_user(orm) if orm else None

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = (
            select(UserORM)
            .options(selectinload(UserORM.roles).selectinload(RoleORM.permissions))
            .where(UserORM.username == username)
        )
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()
        return to_domain_user(orm) if orm else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(UserORM)
            .options(selectinload(UserORM.roles).selectinload(RoleORM.permissions))
            .where(UserORM.email == email)
        )
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()
        return to_domain_user(orm) if orm else None

    async def save(self, user: User) -> User:
        # 1. Query role entities first (with permissions) to prevent lazy loading flush triggers later
        db_roles = []
        if user.roles:
            role_names = [role.name for role in user.roles]
            stmt_roles = (
                select(RoleORM)
                .options(selectinload(RoleORM.permissions))
                .where(RoleORM.name.in_(role_names))
            )
            res_roles = await self.db.execute(stmt_roles)
            db_roles = list(res_roles.scalars().all())

        # 2. Check if ORM record already exists
        stmt = (
            select(UserORM)
            .options(selectinload(UserORM.roles).selectinload(RoleORM.permissions))
            .where(UserORM.id == user.id)
        )
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = UserORM(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                is_active=user.is_active,
                mfa_secret=user.mfa_secret,
                mfa_enabled=user.mfa_enabled,
                department_id=user.department_id,
                roles=db_roles
            )
            self.db.add(orm)
        else:
            orm.username = user.username
            orm.email = user.email
            orm.password_hash = user.password_hash
            orm.is_active = user.is_active
            orm.mfa_secret = user.mfa_secret
            orm.mfa_enabled = user.mfa_enabled
            orm.department_id = user.department_id
            orm.roles = db_roles

        await self.db.flush()
        return to_domain_user(orm)

    async def get_device(self, user_id: uuid.UUID, fingerprint: str) -> Optional[Device]:
        stmt = select(DeviceORM).where(
            DeviceORM.user_id == user_id, DeviceORM.fingerprint == fingerprint
        )
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()
        return to_domain_device(orm) if orm else None

    async def save_device(self, device: Device) -> Device:
        stmt = select(DeviceORM).where(DeviceORM.id == device.id)
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = DeviceORM(
                id=device.id,
                user_id=device.user_id,
                fingerprint=device.fingerprint,
                status=device.status,
                last_used_at=device.last_used_at,
                created_at=device.created_at,
            )
            self.db.add(orm)
        else:
            orm.status = device.status
            orm.last_used_at = device.last_used_at

        await self.db.flush()
        return to_domain_device(orm)

    async def is_ip_whitelisted(self, ip_str: str) -> bool:
        # Check direct IP whitelist match or CIDR coverage
        stmt = select(IPWhitelistORM).where(IPWhitelistORM.is_active == True)
        res = await self.db.execute(stmt)
        rules = res.scalars().all()
        
        # If whitelist is empty, we default to block in banking mode
        if not rules:
            return False

        import ipaddress
        client_ip = ipaddress.ip_address(ip_str.strip())
        for rule in rules:
            try:
                network = ipaddress.ip_network(rule.ip_cidr.strip(), strict=False)
                if client_ip in network:
                    return True
            except ValueError:
                continue
        return False


class SQLAlchemyAssetRepository(IAssetRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        stmt = select(AssetORM).where(AssetORM.id == asset_id)
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()
        return to_domain_asset(orm) if orm else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        stmt = select(AssetORM).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return [to_domain_asset(orm) for orm in res.scalars().all()]

    async def save(self, asset: Asset) -> Asset:
        stmt = select(AssetORM).where(AssetORM.id == asset.id)
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = AssetORM(
                id=asset.id,
                name=asset.name,
                type=asset.type,
                critical_level=asset.critical_level,
                network_address=asset.network_address,
            )
            self.db.add(orm)
        else:
            orm.name = asset.name
            orm.type = asset.type
            orm.critical_level = asset.critical_level
            orm.network_address = asset.network_address

        await self.db.flush()
        return to_domain_asset(orm)


class SQLAlchemyPAMRequestRepository(IPAMRequestRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, request_id: uuid.UUID) -> Optional[PAMRequest]:
        stmt = (
            select(PAMRequestORM)
            .options(
                selectinload(PAMRequestORM.approvals),
                selectinload(PAMRequestORM.ai_decision)
            )
            .where(PAMRequestORM.id == request_id)
        )
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()
        return to_domain_pam_request(orm) if orm else None

    async def save(self, request: PAMRequest) -> PAMRequest:
        stmt = select(PAMRequestORM).where(PAMRequestORM.id == request.id)
        res = await self.db.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = PAMRequestORM(
                id=request.id,
                requester_id=request.requester_id,
                asset_id=request.asset_id,
                action_requested=request.action_requested,
                duration_seconds=request.duration_seconds,
                status=request.status,
                justification=request.justification,
            )
            self.db.add(orm)
        else:
            orm.status = request.status
            orm.duration_seconds = request.duration_seconds

        # Save AI decision if generated and not already persisted
        if request.ai_decision:
            stmt_ai = select(AIDecisionORM).where(AIDecisionORM.id == request.ai_decision.id)
            res_ai = await self.db.execute(stmt_ai)
            orm_ai = res_ai.scalar_one_or_none()
            if not orm_ai:
                orm_ai = AIDecisionORM(
                    id=request.ai_decision.id,
                    request_id=request.id,
                    decision=request.ai_decision.decision,
                    confidence_score=request.ai_decision.confidence_score,
                    risk_score=request.ai_decision.risk_score,
                    rules_evaluated=request.ai_decision.rules_evaluated,
                    explanation=request.ai_decision.explanation,
                    model_version=request.ai_decision.model_version,
                )
                self.db.add(orm_ai)
            else:
                orm_ai.decision = request.ai_decision.decision
                orm_ai.confidence_score = request.ai_decision.confidence_score
                orm_ai.risk_score = request.ai_decision.risk_score
                orm_ai.rules_evaluated = request.ai_decision.rules_evaluated
                orm_ai.explanation = request.ai_decision.explanation

        # Save Approvals
        for app_domain in request.approvals:
            stmt_appr = select(ApprovalORM).where(ApprovalORM.id == app_domain.id)
            res_appr = await self.db.execute(stmt_appr)
            orm_appr = res_appr.scalar_one_or_none()
            if not orm_appr:
                orm_appr = ApprovalORM(
                    id=app_domain.id,
                    request_id=request.id,
                    approver_id=app_domain.approver_id,
                    status=app_domain.status,
                    comments=app_domain.comments,
                )
                self.db.add(orm_appr)

        await self.db.flush()
        
        # Reload to ensure all nested relationships are fully populated
        stmt_reload = (
            select(PAMRequestORM)
            .options(
                selectinload(PAMRequestORM.approvals),
                selectinload(PAMRequestORM.ai_decision)
            )
            .where(PAMRequestORM.id == request.id)
        )
        res_reload = await self.db.execute(stmt_reload)
        orm_reloaded = res_reload.scalar_one()
        return to_domain_pam_request(orm_reloaded)

    async def list_by_user(self, user_id: uuid.UUID) -> List[PAMRequest]:
        stmt = (
            select(PAMRequestORM)
            .options(
                selectinload(PAMRequestORM.approvals),
                selectinload(PAMRequestORM.ai_decision)
            )
            .where(PAMRequestORM.requester_id == user_id)
            .order_by(PAMRequestORM.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return [to_domain_pam_request(orm) for orm in res.scalars().all()]

    async def list_pending_approvals(self) -> List[PAMRequest]:
        stmt = (
            select(PAMRequestORM)
            .options(
                selectinload(PAMRequestORM.approvals),
                selectinload(PAMRequestORM.ai_decision)
            )
            .where(PAMRequestORM.status == "PENDING")
            .order_by(PAMRequestORM.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return [to_domain_pam_request(orm) for orm in res.scalars().all()]

    async def get_all_requests(self, skip: int = 0, limit: int = 100) -> List[PAMRequest]:
        stmt = (
            select(PAMRequestORM)
            .options(
                selectinload(PAMRequestORM.approvals),
                selectinload(PAMRequestORM.ai_decision)
            )
            .offset(skip)
            .limit(limit)
            .order_by(PAMRequestORM.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return [to_domain_pam_request(orm) for orm in res.scalars().all()]


class SQLAlchemyAuditLogRepository(IAuditLogRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, log: AuditLog) -> AuditLog:
        orm = AuditLogORM(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            role=log.role,
            ip_address=log.ip_address,
            device_id=log.device_id,
            endpoint=log.endpoint,
            method=log.method,
            previous_value=log.previous_value,
            new_value=log.new_value,
            ai_decision_id=log.ai_decision_id,
            correlation_id=log.correlation_id,
            trace_id=log.trace_id,
        )
        self.db.add(orm)
        await self.db.flush()
        return to_domain_audit_log(orm)

    async def get_logs_by_user(self, user_id: uuid.UUID, limit: int = 50) -> List[AuditLog]:
        stmt = (
            select(AuditLogORM)
            .where(AuditLogORM.user_id == user_id)
            .order_by(AuditLogORM.timestamp.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return [to_domain_audit_log(orm) for orm in res.scalars().all()]

    async def get_logs_by_correlation_id(self, correlation_id: str) -> List[AuditLog]:
        stmt = (
            select(AuditLogORM)
            .where(AuditLogORM.correlation_id == correlation_id)
            .order_by(AuditLogORM.timestamp.asc())
        )
        res = await self.db.execute(stmt)
        return [to_domain_audit_log(orm) for orm in res.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        stmt = (
            select(AuditLogORM)
            .offset(skip)
            .limit(limit)
            .order_by(AuditLogORM.timestamp.desc())
        )
        res = await self.db.execute(stmt)
        return [to_domain_audit_log(orm) for orm in res.scalars().all()]
