from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
from typing import List, Dict, Any
from prompts import BUSINESS_SYSTEM_PROMPT

class BusinessImpactAgent(BaseAgent):
    def __init__(self):
        super().__init__("Business Impact Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(BUSINESS_SYSTEM_PROMPT, request, policy_violations)
        if llm_res:
            try:
                return AgentResponse(
                    agent_name=self.name,
                    vote=llm_res.get("vote", "ALLOW"),
                    confidence=int(llm_res.get("confidence", 90)),
                    evidence=llm_res.get("evidence", []),
                    reasoning=llm_res.get("reasoning", []),
                    alternative=llm_res.get("alternative"),
                    recommendation=llm_res.get("recommendation", ""),
                    business_impact_details=llm_res.get("business_impact_details", "No business impact details provided.")
                )
            except Exception as e:
                self.logger.warning(f"Error parsing Business LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 90
        evidence = []
        reasoning = []
        alternative = None
        
        target = request.action.target_system.upper()
        criticality = request.action.criticality.upper()
        
        # Core banking service mapping
        impacted_services = []
        customers = 0
        recovery_minutes = 15
        complexity = "MEDIUM"
        
        if "CORE" in target or "CBS" in target or "DB-CORE-PROD" in target:
            impacted_services = ["Core Banking System (CBS)", "ATM Network", "UPI Gateway", "Internet Banking"]
            customers = 2500000
            recovery_minutes = 30
            complexity = "CRITICAL"
        elif "TREASURY" in target:
            impacted_services = ["Treasury Deal Engine", "RTGS Settlement Channels", "NEFT Gateway"]
            customers = 1200000
            recovery_minutes = 18
            complexity = "HIGH"
        elif "UPI" in target:
            impacted_services = ["UPI Gateway", "Mobile Banking App", "Fraud Engine"]
            customers = 1800000
            recovery_minutes = 12
            complexity = "HIGH"
        elif "WEB" in target or "PORTAL" in target:
            impacted_services = ["Internet Banking", "Mobile Banking App"]
            customers = 500000
            recovery_minutes = 10
            complexity = "MEDIUM"
        else:
            impacted_services = ["Internal IT Dashboard", "Admin Logging Server"]
            customers = 0
            recovery_minutes = 5
            complexity = "LOW"
            
        evidence.append(f"critical_services = {', '.join(impacted_services)}")
        evidence.append(f"affected_customers = {customers}")
        evidence.append(f"estimated_downtime = {recovery_minutes} Minutes")
        evidence.append(f"recovery_complexity = {complexity}")
        
        if criticality in ["HIGH", "CRITICAL"] and complexity in ["HIGH", "CRITICAL"]:
            vote = "ALLOW_APPROVAL"
            confidence = 95
            reasoning.append(
                f"Core services {', '.join(impacted_services)} are supported by {target}. "
                f"Estimated recovery complexity is {complexity} with {recovery_minutes} mins downtime, impacting {customers:,} customers."
            )
            alternative = "Run command inside Sandbox (isolated virtual schema) to prevent direct write downtime risk."
        else:
            vote = "ALLOW"
            confidence = 85
            reasoning.append(
                f"Target system {target} has Low recovery complexity. Core customer transaction services are not directly at risk."
            )
            
        if vote == "ALLOW":
            recommendation = "Business services verification cleared. System recovery profile is within acceptable boundaries."
        else:
            recommendation = f"Request requires approval hold. Downstream impact compromises {complexity} complexity banking nodes."
            
        details_str = f"Services: {', '.join(impacted_services)} | Downtime: {recovery_minutes} mins | Customers: {customers:,} | Complexity: {complexity}"
        
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation,
            business_impact_details=details_str
        )
