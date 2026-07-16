from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

# Input Schemas from PAM Gateway (e.g., CyberArk Interceptor)
class UserContext(BaseModel):
    username: str
    role: str
    department: str
    auth_strength: str = Field(description="e.g. PASSWORD, MFA_SMS, MFA_APP, MFA_HARDWARE_TOKEN")
    trusted_device: bool
    ip_address: str
    device_id: str

class ActionDetails(BaseModel):
    type: str = Field(description="e.g., DATABASE_QUERY, DATABASE_RESTART, SHELL_COMMAND, FILE_ACCESS, SERVICE_STOP")
    command: str
    target_system: str
    criticality: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class SystemContext(BaseModel):
    is_maintenance_window: bool
    change_ticket_id: Optional[str] = None
    active_incident_id: Optional[str] = None
    system_health: str = "HEALTHY"

class QuantumProof(BaseModel):
    signature: str
    algorithms_used: str = "CRYSTALS-Dilithium6"
    integrity_checksum: str

class PrivilegedRequest(BaseModel):
    request_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user: UserContext
    action: ActionDetails
    context: SystemContext
    quantum_proof: QuantumProof

# Output/Intermediate Schemas for AI Governance Council
class AgentResponse(BaseModel):
    agent_name: str
    vote: str = Field(description="ALLOW, ALLOW_READ_ONLY, ALLOW_RESTRICTED, ALLOW_SCREEN_RECORD, ALLOW_LIVE_MONITOR, ALLOW_SANDBOX, ALLOW_APPROVAL, DELAY, ESCALATE, BLOCK")
    confidence: int = Field(ge=0, le=100)
    evidence: List[str]
    reasoning: List[str]
    alternative: Optional[str] = None
    recommendation: str
    business_impact_details: Optional[str] = None

# Deliberation Log
class DeliberationStatement(BaseModel):
    speaker: str
    statement: str
    timestamp: str

# Policy Studio configuration schemas
class PolicyRule(BaseModel):
    policy_id: str
    name: str
    condition: str = Field(description="A Python-evaluable expression or description string")
    required_controls: List[str] = Field(description="Controls required if condition matches")
    enabled: bool = True

# Governance Policy Simulation Result
class PolicySimulationResult(BaseModel):
    policy_id: str
    requests_affected: int
    false_positives: int
    expected_security_improvement: str = Field(description="e.g. +18%")
    insights: List[str]

# Governance Memory Match (Pattern Similarity)
class MemoryMatchSummary(BaseModel):
    matched_patterns_count: int
    pattern_similarity: float = Field(description="Similarity percentage e.g. 89.0")
    historical_outcome: str = Field(description="Outcome statistic e.g. '92% Approved'")
    average_risk: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    previous_incident_ref: Optional[str] = Field(default=None, description="E.g. dec_hist_10023")
    insights: List[str]

# Counterfactual Scenario
class CounterfactualScenario(BaseModel):
    scenario_option: str = Field(description="e.g. IF_ALLOWED vs IF_SANDBOXED vs IF_BLOCKED")
    estimated_downtime_minutes: int
    impacted_services: List[str]
    affected_customers: int
    recovery_cost_tier: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    risk_summary: str

# Recovery Plan Step
class RecoveryStep(BaseModel):
    step_number: int
    action: str
    status: str = "PENDING"
    rollback_trigger: Optional[str] = None

class RecoveryPlan(BaseModel):
    safe_alternative: str
    steps: List[RecoveryStep]
    rollback_strategy: str

# Dual explainability views
class ExecutiveView(BaseModel):
    decision: str
    reason: str
    business_impact: str
    recommended_action: str

class AnalystView(BaseModel):
    agent_responses: List[AgentResponse]
    deliberation_log: List[DeliberationStatement]
    policy_evaluations: List[Dict[str, Any]]
    quantum_proof_status: str

# Consolidated Governance Verdict Response
class GovernanceVerdictResponse(BaseModel):
    request_id: str
    timestamp: str
    decision: str
    governance_confidence: int
    council_agreement: str = Field(description="e.g. 7 / 9 Votes")
    business_risk: str
    compliance_status: str
    identity_trust: str
    
    # Dual explainability views
    executive_view: ExecutiveView
    analyst_view: AnalystView
    
    # Shared evaluations
    governance_memory: MemoryMatchSummary
    counterfactuals: List[CounterfactualScenario]
    recovery_plan: RecoveryPlan
    governance_journey: List[Dict[str, str]]
    
    tamper_proof_checksum: str

    # FINSPARK X v2 Swarm Defense Operating System additions
    chain_of_attack_forecast: Optional[List[Dict[str, Any]]] = None
    digital_twin_2: Optional[Dict[str, Any]] = None
    relationship_graph: Optional[Dict[str, Any]] = None
    calibrated_confidence: Optional[Dict[str, Any]] = None
    trust_scores: Optional[Dict[str, Any]] = None
    adaptive_risk: Optional[List[Dict[str, Any]]] = None
    executive_briefing: Optional[str] = None
    regulatory_citations: Optional[List[Dict[str, Any]]] = None
    digital_twin_evolution: Optional[Dict[str, Any]] = None
