from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==============================================================================
# IDENTITY DTOs
# ==============================================================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["soc_analyst_1"])
    email: EmailStr = Field(..., examples=["analyst@bank.com"])
    password: str = Field(..., min_length=8, examples=["P@ssword1234!"])
    department_code: str = Field(..., examples=["SOC"])
    role_names: List[str] = Field(default_factory=list, examples=[["SOC Analyst"]])


class UserLogin(BaseModel):
    username: str = Field(..., examples=["soc_analyst_1"])
    password: str = Field(..., examples=["P@ssword1234!"])


class MfaSetupResponse(BaseModel):
    mfa_secret: str
    provisioning_uri: str


class MfaVerify(BaseModel):
    username: str
    totp_code: str = Field(..., min_length=6, max_length=6, examples=["123456"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    mfa_required: bool = False


# ==============================================================================
# ASSETS DTOs
# ==============================================================================

class AssetCreate(BaseModel):
    name: str = Field(..., examples=["SWIFT Core Gateway"])
    type: str = Field(..., examples=["SERVER"])  # SERVER, DATABASE, CLOUD_RESOURCE
    critical_level: str = Field(..., examples=["CRITICAL"])  # LOW, MEDIUM, HIGH, CRITICAL
    network_address: str = Field(..., examples=["10.150.2.14"])


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    critical_level: str
    network_address: str
    created_at: datetime


# ==============================================================================
# PAM REQUESTS & AI GOVERNANCE DTOs
# ==============================================================================

class PAMRequestCreate(BaseModel):
    asset_id: uuid.UUID
    action_requested: str = Field(..., examples=["SSH_ROOT"])  # READ, WRITE, SSH_ROOT
    duration_seconds: int = Field(..., gt=0, le=86400, examples=[3600])
    justification: str = Field(..., min_length=10, max_length=500, examples=["Urgent SWIFT patch deploy for security advisory"])


class ApprovalSubmit(BaseModel):
    request_id: uuid.UUID
    status: str = Field(..., examples=["APPROVED"])  # APPROVED, REJECTED
    comments: Optional[str] = Field(None, max_length=255, examples=["Valid justification verified against ticket #9482"])


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    approver_id: uuid.UUID
    status: str
    comments: Optional[str]
    created_at: datetime


class AIDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    decision: str
    confidence_score: float
    risk_score: float
    rules_evaluated: Dict[str, Any]
    explanation: str
    model_version: str
    created_at: datetime


class PAMRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requester_id: uuid.UUID
    asset_id: uuid.UUID
    action_requested: str
    duration_seconds: int
    status: str
    justification: str
    created_at: datetime
    updated_at: datetime
    approvals: List[ApprovalResponse] = Field(default_factory=list)
    ai_decision: Optional[AIDecisionResponse] = None


# ==============================================================================
# COMPLIANCE & TELEMETRY DTOs
# ==============================================================================

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: datetime
    user_id: uuid.UUID
    role: str
    ip_address: str
    endpoint: str
    method: str
    ai_decision_id: Optional[uuid.UUID]
    correlation_id: str
    trace_id: str


class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    asset_id: uuid.UUID
    score: float
    factor_details: Dict[str, Any]
    calculated_at: datetime
