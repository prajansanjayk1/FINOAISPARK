from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse, DeliberationStatement
from typing import List, Dict, Any, Tuple
from datetime import datetime
from prompts import JUDGE_SYSTEM_PROMPT
from services.llm_client import call_llm

class JudgeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Decision Judge Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> None:
        pass
        
    async def resolve_consensus(
        self, 
        request: PrivilegedRequest, 
        agent_responses: List[AgentResponse], 
        policy_violations: List[Dict[str, Any]],
        memory_insight: str
    ) -> Tuple[str, int, str, str, str, str, List[DeliberationStatement]]:
        """
        Consolidates the agent opinions and policy evaluations into the final verdict.
        Returns:
            (Decision, Governance Confidence, Council Agreement, Business Risk, Compliance Status, Identity Trust, Deliberation Logs)
        """
        self.logger.info(f"Resolving consensus for {request.request_id}")
        
        # Build LLM Prompt context
        agent_evals_str = ""
        for ar in agent_responses:
            agent_evals_str += f"\n- {ar.agent_name} Vote: {ar.vote}, Confidence: {ar.confidence}%, Reasoning: {', '.join(ar.reasoning)}\n"
            
        user_prompt = f"""
        Active Incident Request:
        - Request ID: {request.request_id}
        - User: {request.user.username} (Role: {request.user.role}, Dept: {request.user.department})
        - Action: {request.action.type} (Command: {request.action.command})
        - Criticality: {request.action.criticality}
        
        Governance Council Agent Deliberations:
        {agent_evals_str}
        
        Memory Precedent Insights:
        {memory_insight}
        
        Policy Violations:
        {str(policy_violations)}
        """
        
        llm_res = await call_llm(JUDGE_SYSTEM_PROMPT, user_prompt)
        if llm_res:
            try:
                # Map LLM keys to variables
                decision = llm_res.get("decision", "BLOCK")
                gov_conf = int(llm_res.get("governance_confidence", 95))
                agreement = llm_res.get("parliament_agreement", "8 / 9 Votes")
                risk = llm_res.get("business_risk", "CRITICAL")
                compliance = llm_res.get("compliance_status", "FAILED")
                trust = llm_res.get("identity_trust", "LOW")
                
                logs = []
                now_str = datetime.now().strftime("%H:%M:%S")
                for log_item in llm_res.get("deliberation_log", []):
                    logs.append(DeliberationStatement(
                        speaker=log_item.get("speaker", "Agent"),
                        statement=log_item.get("statement", ""),
                        timestamp=log_item.get("timestamp", now_str)
                    ))
                return (decision, gov_conf, agreement, risk, compliance, trust, logs)
            except Exception as e:
                self.logger.warning(f"Error parsing Judge LLM response: {e}. Falling back to default voter.")

        # Default failsafe algorithm if LLM is disabled or fails
        votes = [r.vote for r in agent_responses]
        total_agents = len(agent_responses)
        
        # Identity trust determination
        id_agent = next((r for r in agent_responses if r.agent_name == "Identity Verification Agent"), None)
        identity_trust = "HIGH"
        if id_agent:
            if id_agent.vote in ["BLOCK", "ESCALATE"]:
                identity_trust = "LOW"
            elif id_agent.vote in ["ALLOW_SANDBOX", "ALLOW_APPROVAL"]:
                identity_trust = "MEDIUM"
                
        # Business Risk determination
        biz_agent = next((r for r in agent_responses if r.agent_name == "Business Impact Agent"), None)
        business_risk = "LOW"
        if biz_agent:
            if "CRITICAL" in biz_agent.business_impact_details or request.action.criticality == "CRITICAL":
                business_risk = "CRITICAL"
            elif "HIGH" in biz_agent.business_impact_details or request.action.criticality == "HIGH":
                business_risk = "HIGH"
            elif "MEDIUM" in biz_agent.business_impact_details or request.action.criticality == "MEDIUM":
                business_risk = "MEDIUM"
                
        # Compliance Status determination
        compliance_status = "PASSED"
        comp_agent = next((r for r in agent_responses if r.agent_name == "Compliance Intelligence Agent"), None)
        if comp_agent and comp_agent.vote == "BLOCK":
            compliance_status = "FAILED"
        for violation in policy_violations:
            if violation["status"] == "VIOLATED":
                compliance_status = "FAILED"
                
        # Veto Logic
        block_votes = [v for v in votes if v == "BLOCK"]
        escalate_votes = [v for v in votes if v == "ESCALATE"]
        sandbox_votes = [v for v in votes if v == "ALLOW_SANDBOX"]
        approval_votes = [v for v in votes if v == "ALLOW_APPROVAL"]
        
        if block_votes:
            final_decision = "BLOCK"
            governance_confidence = 90 + len(block_votes)
            governance_confidence = min(governance_confidence, 99)
        elif escalate_votes:
            final_decision = "ESCALATE"
            governance_confidence = 88
        elif sandbox_votes:
            final_decision = "ALLOW_SANDBOX"
            governance_confidence = 85
        elif approval_votes:
            final_decision = "ALLOW_APPROVAL"
            governance_confidence = 90
        elif "ALLOW_SCREEN_RECORD" in votes:
            final_decision = "ALLOW_SCREEN_RECORD"
            governance_confidence = 80
        elif "ALLOW_LIVE_MONITOR" in votes:
            final_decision = "ALLOW_LIVE_MONITOR"
            governance_confidence = 85
        else:
            final_decision = "ALLOW"
            governance_confidence = 95
            
        agreement_count = sum(1 for v in votes if v == final_decision or (final_decision.startswith("ALLOW") and v.startswith("ALLOW")))
        council_agreement = f"{agreement_count} / {total_agents} Votes"
        
        # Create AI Deliberation Engine Transcript
        deliberation_log = []
        now_str = datetime.now().strftime("%H:%M:%S")
        
        deliberation_log.append(DeliberationStatement(
            speaker="Policy Engine",
            statement=f"Policy Studio check loaded. Violated Rules: {[v['name'] for v in policy_violations if v['status'] == 'VIOLATED'] or 'None'}.",
            timestamp=now_str
        ))
        
        for agent in agent_responses:
            statement_text = ""
            if agent.vote == "ALLOW":
                statement_text = f"Verification clear. {agent.recommendation} confidence rating {agent.confidence}%."
            elif agent.vote == "BLOCK":
                statement_text = f"CRITICAL SECURITY ANOMALY! {agent.recommendation} Findings: {', '.join(agent.reasoning[:2])}."
            else:
                statement_text = f"Safety mitigation recommended. {agent.recommendation} Findings: {', '.join(agent.reasoning[:2])}."
                
            deliberation_log.append(DeliberationStatement(
                speaker=agent.agent_name,
                statement=statement_text,
                timestamp=now_str
            ))
            
        deliberation_log.append(DeliberationStatement(
            speaker="Decision Judge Agent",
            statement=(
                f"Consensus achieved. Final Verdict: {final_decision}. "
                f"Governance confidence stands at {governance_confidence}%. Compliance profile is {compliance_status}. "
                f"Downstream risk categorized as {business_risk}. Memory lookup matches: '{memory_insight}'."
            ),
            timestamp=now_str
        ))
        
        return (
            final_decision,
            governance_confidence,
            council_agreement,
            business_risk,
            compliance_status,
            identity_trust,
            deliberation_log
        )
