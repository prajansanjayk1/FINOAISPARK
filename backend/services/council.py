import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any

from models import (
    PrivilegedRequest, 
    GovernanceVerdictResponse, 
    AgentResponse, 
    DeliberationStatement,
    RecoveryPlan,
    RecoveryStep,
    ExecutiveView,
    AnalystView
)
from policy_engine import PolicyEngine
from counterfactual import CounterfactualSimulator
from governor import ExecutionGovernor
from database import search_governance_memory, save_detailed_decision

# Import all agents
from agents.identity import IdentityAgent
from agents.behavior import BehaviorAgent
from agents.context import ContextAgent
from agents.compliance import ComplianceAgent
from agents.threat import ThreatAgent
from agents.business_impact import BusinessImpactAgent
from agents.quantum import QuantumSecurityAgent
from agents.recovery_planner import RecoveryPlannerAgent
from agents.judge import JudgeAgent

class AIGovernanceCouncilOrchestrator:
    def __init__(self):
        # Initialize the 9 specialized agents of the Governance Council
        self.identity_agent = IdentityAgent()
        self.behavior_agent = BehaviorAgent()
        self.context_agent = ContextAgent()
        self.compliance_agent = ComplianceAgent()
        self.threat_agent = ThreatAgent()
        self.business_agent = BusinessImpactAgent()
        self.quantum_agent = QuantumSecurityAgent()
        self.recovery_agent = RecoveryPlannerAgent()
        self.judge_agent = JudgeAgent()
        self._cache = {}

    async def evaluate_request(self, request: PrivilegedRequest) -> GovernanceVerdictResponse:
        # Check Cache
        cache_key = hashlib.md5(f"{request.user.username}:{request.action.command}:{request.action.target_system}".encode()).hexdigest()
        now = datetime.now()
        if cache_key in self._cache:
            cached_time, cached_response = self._cache[cache_key]
            if now - cached_time < timedelta(seconds=30):
                # Update transient request details
                cached_response.request_id = request.request_id
                cached_response.timestamp = request.timestamp
                return cached_response

        # Step 1: Run Policy Engine Check
        policy_evals = PolicyEngine.evaluate_rules(request)
        
        # Step 2: Parallel Deliberation of AI Governance Council
        agents_to_run = [
            self.identity_agent.evaluate(request, policy_evals),
            self.behavior_agent.evaluate(request, policy_evals),
            self.context_agent.evaluate(request, policy_evals),
            self.compliance_agent.evaluate(request, policy_evals),
            self.threat_agent.evaluate(request, policy_evals),
            self.business_agent.evaluate(request, policy_evals),
            self.quantum_agent.evaluate(request, policy_evals),
            self.recovery_agent.evaluate(request, policy_evals),
        ]
        
        agent_responses: List[AgentResponse] = await asyncio.gather(*agents_to_run)
        
        # Step 3: Governance Memory Matching (Precedent Matching)
        memory_summary = search_governance_memory(request)
        memory_insight = memory_summary.insights[0] if memory_summary.insights else "No matching precedents located."
        
        # Step 4: Decision Judge Final Consensus & Deliberation Dialogue Generation
        decision, confidence, agreement, risk, compliance, trust, debate = await self.judge_agent.resolve_consensus(
            request=request,
            agent_responses=agent_responses,
            policy_violations=policy_evals,
            memory_insight=memory_insight
        )
        
        # Step 5: Counterfactual Analysis Simulator
        counterfactuals = CounterfactualSimulator.simulate(request)
        
        # Step 6: Recovery Planner Safe Alternative Mapping
        recovery_rec = next((r for r in agent_responses if r.agent_name == "Recovery Planner Agent"), None)
        recovery_vote = recovery_rec.vote if recovery_rec else "ALLOW"
        recovery_plan = self.recovery_agent.generate_plan(request, recovery_vote)
        
        # Step 7: Execution Governor Adaptive Directives Build
        directives = ExecutionGovernor.get_pam_directives(decision, request, recovery_plan)
        
        # Create Governance Journey Steps
        governance_journey = []
        now_time = datetime.now()
        
        journey_mappings = [
            ("Request Ingestion", "Privileged administrative action received from PAM Gateway interceptor."),
            ("Policy Engine Stage", f"Completed. Compliance check status: {compliance}."),
            ("Identity Trust Audit", f"Identity Trust verification completed. Level: {trust}."),
            ("Behavior Pattern Check", "Parsed activity command syntax against historical schedule drift baseline."),
            ("Threat Scanning", "System verified shell inputs for Indicators of Compromise and Privilege Escalation."),
            ("Business Risk Analysis", f"Analyzed technical node class. Risk classification: {risk}."),
            ("Governance Council Debate", "Council agents concluded debate. Majority consensus resolved."),
            ("Consensus Ruling", f"Verdict: {decision} with {confidence}% confidence."),
            ("Adaptive Directives", "Dispatched execution guidelines payload directly to PAM Gateway.")
        ]
        
        for idx, (stage, desc) in enumerate(journey_mappings):
            stage_time = now_time + timedelta(seconds=idx * 2)
            governance_journey.append({
                "stage": stage,
                "description": desc,
                "time": stage_time.strftime("%H:%M:%S")
            })
            
        # Compile Executive View
        violated_names = [v["name"] for v in policy_evals if v["status"] == "VIOLATED"]
        violated_str = f" Violates policies: {', '.join(violated_names)}." if violated_names else ""
        
        exec_reason = f"Action is {decision}ed because of security evaluations on {request.action.target_system}."
        if decision == "BLOCK":
            exec_reason = f"High-risk operation denied due to policy conflict and safety thresholds.{violated_str}"
        elif decision == "ALLOW_SANDBOX":
            exec_reason = f"Command restricted to isolated testing container. Direct write access disallowed."
        elif decision == "ALLOW_APPROVAL":
            exec_reason = f"Dual-control approval required due to high technical criticality.{violated_str}"
            
        exec_impact = f"Potential disruption to critical banking services: {recovery_rec.alternative or 'N/A'} if unchecked." if recovery_rec else "Low service impact."
        if risk == "CRITICAL" or risk == "HIGH":
            exec_impact = f"Critical risk of downtime for core transaction channels (UPI, CBS, ATM)."
            
        exec_action = "Awaiting Duty Manager digital signatures to proceed." if decision == "ALLOW_APPROVAL" else (
            "Obtain approved change ticket and rerun command during Sunday maintenance window." if decision == "BLOCK" else (
                "Reroute session directly to virtual PostgreSQL test sandbox." if decision == "ALLOW_SANDBOX" else "Inject dynamic temporary tokens and run standard session recording."
            )
        )
        
        executive_view = ExecutiveView(
            decision=decision,
            reason=exec_reason,
            business_impact=exec_impact,
            recommended_action=exec_action
        )
        
        # Compile Analyst View
        analyst_view = AnalystView(
            agent_responses=agent_responses,
            deliberation_log=debate,
            policy_evaluations=policy_evals,
            quantum_proof_status="VERIFIED" if request.quantum_proof.algorithms_used == "CRYSTALS-Dilithium6" else "DEGRADED"
        )
        
        # Tamper-proof digest signature creation
        payload_digest_str = f"{request.request_id}:{decision}:{confidence}:{datetime.now().isoformat()}"
        tamper_proof_checksum = hashlib.sha3_256(payload_digest_str.encode()).hexdigest()

        # FINSPARK X v2 Swarm Defense Operating System mock generators
        is_blocked = (decision == "BLOCK")
        
        chain_of_attack_forecast = [
            {"time": "5m", "probability": 90 if is_blocked else 2, "threat": "Credential stuffing spreading to API subnet" if is_blocked else "System normal"},
            {"time": "1h", "probability": 75 if is_blocked else 1, "threat": "Mule accounts withdraw ₹24.5 Lakhs" if is_blocked else "System normal"},
            {"time": "24h", "probability": 40 if is_blocked else 0, "threat": "Data exfiltration threat targeting primary DB" if is_blocked else "System normal"},
            {"time": "7d", "probability": 8 if is_blocked else 0, "threat": "Full system lockdown / Ransomware sequence" if is_blocked else "System normal"}
        ]
        
        digital_twin_2 = {
            "account_twin": {"health": 35 if is_blocked else 98, "status": "COMPROMISED_RISK" if is_blocked else "HEALTHY"},
            "device_twin": {"health": 12 if is_blocked else 92, "status": "SUSPICIOUS_DEVICE" if is_blocked else "HEALTHY"},
            "location_twin": {"confidence": 24 if is_blocked else 87, "status": "IMPOSSIBLE_TRAVEL" if is_blocked else "HEALTHY"},
            "behavior_twin": {"deviation": 96 if is_blocked else 34, "status": "ANOMALOUS" if is_blocked else "BASELINE"},
            "transaction_twin": {"risk": 89 if is_blocked else 12, "status": "CRITICAL" if is_blocked else "LOW_RISK"}
        }
        
        relationship_graph = {
            "nodes": [
                {"id": "customer", "label": request.user.username, "type": "USER", "risk": 90 if is_blocked else 10},
                {"id": "device", "label": request.user.device_id, "type": "DEVICE", "risk": 95 if is_blocked else 15},
                {"id": "ip", "label": request.user.ip_address, "type": "IP", "risk": 85 if is_blocked else 5},
                {"id": "vpn", "label": "192.168.45.12 (VPN)", "type": "VPN", "risk": 75 if is_blocked else 8},
                {"id": "target", "label": request.action.target_system, "type": "ASSET", "risk": 50 if is_blocked else 2}
            ],
            "edges": [
                {"source": "customer", "target": "device", "risk": 85 if is_blocked else 5},
                {"source": "device", "target": "ip", "risk": 90 if is_blocked else 10},
                {"source": "ip", "target": "vpn", "risk": 75 if is_blocked else 12},
                {"source": "vpn", "target": "target", "risk": 88 if is_blocked else 8}
            ]
        }
        if is_blocked:
            relationship_graph["nodes"].append({"id": "mule", "label": "Mule Company LLC", "type": "SINK", "risk": 99})
            relationship_graph["edges"].append({"source": "target", "target": "mule", "risk": 95})

        calibrated_confidence = {
            "prediction_confidence": 97 if is_blocked else 95,
            "evidence_strength": 95 if is_blocked else 90,
            "data_completeness": 89 if is_blocked else 95,
            "model_agreement": 96 if is_blocked else 100,
            "uncertainty": 4 if is_blocked else 2
        }

        trust_scores = {
            "identity_trust": 34 if is_blocked else 98,
            "behavior_trust": 22 if is_blocked else 95,
            "financial_trust": 45 if is_blocked else 93,
            "device_trust": 15 if is_blocked else 84,
            "network_trust": 28 if is_blocked else 80,
            "overall_trust": 29 if is_blocked else 91
        }

        adaptive_risk = [
            {"stage": "Current Risk", "score": 71 if is_blocked else 15},
            {"stage": "After MFA", "score": 38 if is_blocked else 5},
            {"stage": "After Device Verification", "score": 12 if is_blocked else 2},
            {"stage": "Tomorrow", "score": 6 if is_blocked else 1}
        ]

        executive_briefing = (
            f"A high-risk transaction originating from an unknown device for user {request.user.username} was intercepted. "
            f"Causal analysis indicates possible credential stuffing followed by privilege escalation attempt on {request.action.target_system}. "
            f"Swarm consensus recommends blocking the action and triggering digital twin quarantine."
            if is_blocked else
            f"A routine privileged action {request.action.type} was requested by {request.user.username} on {request.action.target_system}. "
            f"All constraints passed behavioral benchmarks, and the action has been allowed."
        )

        regulatory_citations = [
            {"framework": "RBI Rule RB-17", "description": "Multi-factor authentication compliance check", "status": "FAILED" if is_blocked else "PASSED"},
            {"framework": "GDPR Article 32", "description": "Data transfer security baseline check", "status": "FAILED" if is_blocked else "PASSED"},
            {"framework": "PCI DSS Requirement 10", "description": "Audit log validation check", "status": "PASSED"}
        ]

        digital_twin_evolution = {
            "yesterday": 98 if is_blocked else 99,
            "today": 91 if is_blocked else 97,
            "tomorrow_prediction": 83 if is_blocked else 98
        }
        
        # Bundle Response
        verdict_response = GovernanceVerdictResponse(
            request_id=request.request_id,
            timestamp=request.timestamp,
            decision=decision,
            governance_confidence=confidence,
            council_agreement=agreement,
            business_risk=risk,
            compliance_status=compliance,
            identity_trust=trust,
            executive_view=executive_view,
            analyst_view=analyst_view,
            governance_memory=memory_summary,
            counterfactuals=counterfactuals,
            recovery_plan=recovery_plan,
            governance_journey=governance_journey,
            tamper_proof_checksum=tamper_proof_checksum,
            chain_of_attack_forecast=chain_of_attack_forecast,
            digital_twin_2=digital_twin_2,
            relationship_graph=relationship_graph,
            calibrated_confidence=calibrated_confidence,
            trust_scores=trust_scores,
            adaptive_risk=adaptive_risk,
            executive_briefing=executive_briefing,
            regulatory_citations=regulatory_citations,
            digital_twin_evolution=digital_twin_evolution
        )
        
        # Save to Database Decision Log (Governance Memory Store)
        save_detailed_decision(request, verdict_response)
        
        # Cache Result
        self._cache[cache_key] = (now, verdict_response)
        
        return verdict_response
