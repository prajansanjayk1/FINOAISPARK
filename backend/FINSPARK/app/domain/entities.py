from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class Permission:
    id: uuid.UUID
    name: str  # e.g., "DATABASE_READ"
    resource: str  # e.g., "DATABASE"
    action: str  # e.g., "READ"
    description: str


@dataclass
class Role:
    id: uuid.UUID
    name: str  # e.g., "SOC Analyst", "Chief Information Security Officer"
    description: str
    permissions: List[Permission] = field(default_factory=list)


@dataclass
class User:
    id: uuid.UUID
    username: str
    email: str
    password_hash: str
    is_active: bool
    mfa_secret: Optional[str]
    mfa_enabled: bool
    department_id: Optional[uuid.UUID]
    roles: List[Role] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def has_permission(self, resource: str, action: str) -> bool:
        """
        Evaluates whether user holds a role mapping to the specified permission.
        """
        # CISO/Security Admins can do anything
        admin_roles = {"Security Administrator", "Chief Information Security Officer (CISO)"}
        for role in self.roles:
            if role.name in admin_roles:
                return True
            for perm in role.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        return False


@dataclass
class Device:
    id: uuid.UUID
    user_id: uuid.UUID
    fingerprint: str
    status: str  # "TRUSTED", "UNTRUSTED", "BLOCKED"
    last_used_at: datetime
    created_at: datetime


@dataclass
class Asset:
    id: uuid.UUID
    name: str
    type: str  # "SERVER", "DATABASE", "CLOUD_RESOURCE"
    critical_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    network_address: str  # IP or CIDR range
    created_at: datetime


@dataclass
class Approval:
    id: uuid.UUID
    request_id: uuid.UUID
    approver_id: uuid.UUID
    status: str  # "APPROVED", "REJECTED"
    comments: str
    created_at: datetime


@dataclass
class AIDecision:
    id: uuid.UUID
    request_id: uuid.UUID
    decision: str  # "ALLOW", "DENY", "ESCALATE"
    confidence_score: float
    risk_score: float
    rules_evaluated: Dict[str, Any]
    explanation: str
    model_version: str
    created_at: datetime


@dataclass
class PAMRequest:
    id: uuid.UUID
    requester_id: uuid.UUID
    asset_id: uuid.UUID
    action_requested: str  # e.g., "READ", "SSH_ROOT", "WRITE"
    duration_seconds: int
    status: str  # "PENDING", "APPROVED", "REJECTED", "EXPIRED", "EXECUTED"
    justification: str
    created_at: datetime
    updated_at: datetime
    approvals: List[Approval] = field(default_factory=list)
    ai_decision: Optional[AIDecision] = None

    def is_expired(self) -> bool:
        """Checks if session validity duration from approval has passed."""
        delta = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return delta > self.duration_seconds


@dataclass
class RiskScore:
    id: uuid.UUID
    user_id: uuid.UUID
    asset_id: uuid.UUID
    score: float  # 0.0 to 100.0
    factor_details: Dict[str, Any]
    calculated_at: datetime


@dataclass
class AuditLog:
    id: uuid.UUID
    timestamp: datetime
    user_id: uuid.UUID
    role: str
    ip_address: str
    device_id: Optional[str]
    endpoint: str
    method: str
    previous_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ai_decision_id: Optional[uuid.UUID]
    correlation_id: str
    trace_id: str
