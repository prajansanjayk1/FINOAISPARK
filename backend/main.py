from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import logging
from typing import List, Dict, Any, Optional

from models import PrivilegedRequest, GovernanceVerdictResponse, PolicyRule, PolicySimulationResult
from database import init_db, get_history_list, get_decision_detail, get_policies, save_policy
from services.council import AIGovernanceCouncilOrchestrator
from policy_engine import PolicyEngine
from counterfactual import CounterfactualSimulator
from agents.business_impact import BusinessImpactAgent
from agents.behavior import BehaviorAgent
from agents.threat import ThreatAgent
from agents.compliance import ComplianceAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nexus.main")

# Initialize database
init_db()

app = FastAPI(
    title="NEXUS ONE — AI Governance Engine for PAM",
    description="Autonomous AI Governance Layer for Privileged Banking Access Control",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate orchestrator
orchestrator = AIGovernanceCouncilOrchestrator()

# Lifespan events / startup
@app.on_event("startup")
async def startup_event():
    logger.info("NEXUS ONE Governance Server Initialized.")

# Serve Static files for UI Dashboard
os.makedirs("static", exist_ok=True)

# 1. Main Core Endpoint: Evaluation
@app.post("/evaluate", response_model=GovernanceVerdictResponse)
async def evaluate_request(request: PrivilegedRequest):
    logger.info(f"Received PAM access request {request.request_id} for user {request.user.username}")
    try:
        verdict = await orchestrator.evaluate_request(request)
        return verdict
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Governance engine failure: {str(e)}")

# 2. Command analysis helper
@app.post("/analyze")
async def analyze_command(payload: Dict[str, Any]):
    cmd = payload.get("command", "")
    criticality = payload.get("criticality", "MEDIUM")
    system = payload.get("target_system", "DB-CORE-PROD")
    
    mock_request = PrivilegedRequest(
        request_id=f"req_anlyz_{os.urandom(4).hex()}",
        user={
            "username": payload.get("username", "admin_analyst"),
            "role": payload.get("role", "Database Administrator"),
            "department": payload.get("department", "Core Banking"),
            "auth_strength": payload.get("auth_strength", "MFA_HARDWARE_TOKEN"),
            "trusted_device": payload.get("trusted_device", True),
            "ip_address": payload.get("ip_address", "192.168.10.12"),
            "device_id": "DEV-ANLYZ-01"
        },
        action={
            "type": payload.get("action_type", "DATABASE_QUERY"),
            "command": cmd,
            "target_system": system,
            "criticality": criticality
        },
        context={
            "is_maintenance_window": payload.get("is_maintenance_window", True),
            "change_ticket_id": payload.get("change_ticket_id", "CHG-10293"),
            "active_incident_id": payload.get("active_incident_id", None),
            "system_health": payload.get("system_health", "HEALTHY")
        },
        quantum_proof={
            "signature": "qsig_dilithium_mock_993f82a71d7",
            "integrity_checksum": "checksum_sha256_mock_a872f2e71762"
        }
    )
    
    return await evaluate_request(mock_request)

# 3. Explain past decisions
@app.post("/explain")
async def explain_decision(payload: Dict[str, str]):
    decision_id = payload.get("decision_id", "")
    detail = get_decision_detail(decision_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Decision record not found in Governance Memory.")
    return detail

# 4. Business Impact Assessment
@app.post("/business-impact")
async def check_business_impact(request: PrivilegedRequest):
    agent = BusinessImpactAgent()
    policy_evals = PolicyEngine.evaluate_rules(request)
    return await agent.evaluate(request, policy_evals)

# 5. Compliance Check
@app.post("/compliance-check")
async def check_compliance(request: PrivilegedRequest):
    agent = ComplianceAgent()
    policy_evals = PolicyEngine.evaluate_rules(request)
    return {
        "policy_evaluations": policy_evals,
        "compliance_agent_response": await agent.evaluate(request, policy_evals)
    }

# 6. Behavior Analysis
@app.post("/behavior-analysis")
async def check_behavior(request: PrivilegedRequest):
    agent = BehaviorAgent()
    policy_evals = PolicyEngine.evaluate_rules(request)
    return await agent.evaluate(request, policy_evals)

# 7. Threat Analysis
@app.post("/threat-analysis")
async def check_threat(request: PrivilegedRequest):
    agent = ThreatAgent()
    policy_evals = PolicyEngine.evaluate_rules(request)
    return await agent.evaluate(request, policy_evals)

# 8. GET history logs
@app.get("/history")
async def get_history(limit: int = 50):
    return get_history_list(limit)

# 9. GET decision detail by ID or list
@app.get("/decision")
async def get_decision_list(limit: int = 50, decision_id: Optional[str] = None):
    if decision_id:
        detail = get_decision_detail(decision_id)
        if not detail:
            raise HTTPException(status_code=404, detail="Decision not found.")
        return detail
    return get_history_list(limit)

@app.get("/decision/{decision_id}")
async def get_decision(decision_id: str):
    detail = get_decision_detail(decision_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Decision not found.")
    return detail

# 10. GET / POST Policies for Governance Policy Studio
@app.get("/policies")
async def fetch_policies():
    return get_policies()

@app.post("/policies")
async def update_policy(policy: PolicyRule):
    save_policy(
        policy_id=policy.policy_id,
        name=policy.name,
        condition=policy.condition,
        required_controls=policy.required_controls,
        enabled=policy.enabled
    )
    return {"status": "SUCCESS", "message": f"Policy {policy.policy_id} updated."}

# 11. Policy Simulator Endpoint
@app.post("/policies/simulate", response_model=PolicySimulationResult)
async def simulate_policy(policy: PolicyRule):
    try:
        res = PolicyEngine.simulate_policy(policy)
        return res
    except Exception as e:
        logger.error(f"Policy simulation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation engine error: {str(e)}")

# HTML Endpoint to serve GUI dashboard
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = "static/index.html"
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return """
    <html>
        <head><title>NEXUS ONE Dashboard Missing</title></head>
        <body style="background:#0b0f19;color:#fff;font-family:sans-serif;padding:50px;text-align:center;">
            <h1>NEXUS ONE - Governance Layer Loaded</h1>
            <p>UI Static Dashboard files not loaded yet. Server endpoints are active.</p>
        </body>
    </html>
    """

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
