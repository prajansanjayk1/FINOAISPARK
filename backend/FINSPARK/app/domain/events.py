from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


@dataclass
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PAMRequestCreatedEvent(DomainEvent):
    request_id: uuid.UUID
    requester_id: uuid.UUID
    asset_id: uuid.UUID
    action: str


@dataclass
class AIDecisionGeneratedEvent(DomainEvent):
    decision_id: uuid.UUID
    request_id: uuid.UUID
    decision: str
    risk_score: float
    confidence_score: float


@dataclass
class PAMRequestApprovedEvent(DomainEvent):
    request_id: uuid.UUID
    approver_id: uuid.UUID
    status: str  # APPROVED or REJECTED


@dataclass
class PolicyViolatedEvent(DomainEvent):
    user_id: uuid.UUID
    asset_id: uuid.UUID
    action: str
    violations: List[str]


@dataclass
class SecurityIncidentDetectedEvent(DomainEvent):
    incident_type: str
    user_id: uuid.UUID
    details: Dict[str, Any]
    risk_score: float
