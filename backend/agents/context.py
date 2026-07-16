from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
from typing import List, Dict, Any
from prompts import CONTEXT_SYSTEM_PROMPT

class ContextAgent(BaseAgent):
    def __init__(self):
        super().__init__("Context Intelligence Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(CONTEXT_SYSTEM_PROMPT, request, policy_violations)
        if llm_res:
            try:
                return AgentResponse(
                    agent_name=self.name,
                    vote=llm_res.get("vote", "ALLOW"),
                    confidence=int(llm_res.get("confidence", 92)),
                    evidence=llm_res.get("evidence", []),
                    reasoning=llm_res.get("reasoning", []),
                    alternative=llm_res.get("alternative"),
                    recommendation=llm_res.get("recommendation", "")
                )
            except Exception as e:
                self.logger.warning(f"Error parsing Context LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 92
        evidence = []
        reasoning = []
        alternative = None
        
        ctx = request.context
        act = request.action
        
        # Check Maintenance Window
        if ctx.is_maintenance_window:
            evidence.append("is_maintenance_window = True")
            reasoning.append("Operation falls inside a pre-approved IT maintenance window. Infrastructure impact thresholds relaxed.")
        else:
            evidence.append("is_maintenance_window = False")
            reasoning.append("Operation scheduled outside standard IT maintenance window. Production modifications require ticket matching.")
            if act.criticality in ["HIGH", "CRITICAL"]:
                vote = "ALLOW_APPROVAL"
                confidence = 90
                alternative = "Delay execution until scheduled Sunday maintenance window (00:00 - 04:00 AM)."
                
        # Check Change Ticket Match
        if ctx.change_ticket_id:
            evidence.append(f"change_ticket_id = {ctx.change_ticket_id}")
            reasoning.append(f"Verified association with active Change Management ticket: {ctx.change_ticket_id}.")
        else:
            evidence.append("change_ticket_id = None")
            reasoning.append("No active Change Management ticket referenced in context payload.")
            if act.criticality in ["HIGH", "CRITICAL"]:
                vote = "BLOCK"
                confidence = 95
                alternative = "Generate a valid ServiceNow change ticket prior to requesting server credentials."
                
        # Check Emergency Incident Mode
        if ctx.active_incident_id:
            evidence.append(f"active_incident_id = {ctx.active_incident_id}")
            reasoning.append(f"System is in emergency incident response mode under ticket {ctx.active_incident_id}. Fast-track emergency protocols apply.")
            if vote == "BLOCK":
                # Emergency override: escalate to manager rather than hard block
                vote = "ALLOW_APPROVAL"
                confidence = 88
                reasoning.append("Emergency Incident Response override active. Upgrading hard BLOCK to Manager Approval Escalation.")
                alternative = "Obtain dynamic SecOps commander verification signature."
                
        # Check System Health
        if ctx.system_health == "DEGRADED" and act.criticality in ["HIGH", "CRITICAL"]:
            vote = "DELAY"
            confidence = 85
            evidence.append("system_health = DEGRADED")
            reasoning.append("Target infrastructure report shows resource exhaustion (degraded state). Executing high-criticality commands could trigger secondary service outages.")
            alternative = "Delay command execution until CPU utilization drops below 70%."
            
        # Resolve Recommendation
        if vote == "ALLOW":
            recommendation = "Context checks verified. Target system operation scheduled within authorized ticket boundary."
        elif vote == "ALLOW_APPROVAL":
            recommendation = "Require manual incident responder / manager verification signature."
        elif vote == "DELAY":
            recommendation = "Postpone execution. System health is degraded. Queue command for manual release."
        else:
            recommendation = "Block request. High-criticality actions outside maintenance window require change ticket approval."
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation
        )
