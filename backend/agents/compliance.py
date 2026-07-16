from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
from typing import List, Dict, Any
from prompts import COMPLIANCE_SYSTEM_PROMPT

class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Compliance Intelligence Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(COMPLIANCE_SYSTEM_PROMPT, request, policy_violations)
        if llm_res:
            try:
                return AgentResponse(
                    agent_name=self.name,
                    vote=llm_res.get("vote", "ALLOW"),
                    confidence=int(llm_res.get("confidence", 94)),
                    evidence=llm_res.get("evidence", []),
                    reasoning=llm_res.get("reasoning", []),
                    alternative=llm_res.get("alternative"),
                    recommendation=llm_res.get("recommendation", "")
                )
            except Exception as e:
                self.logger.warning(f"Error parsing Compliance LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 94
        evidence = []
        reasoning = []
        alternative = None
        
        user = request.user
        act = request.action
        ctx = request.context
        
        # Maker-Checker (RBI Guidelines requirement)
        if act.criticality in ["HIGH", "CRITICAL"]:
            vote = "ALLOW_APPROVAL"
            confidence = 95
            evidence.append("Maker-Checker Enforcement (RBI Annexure-A)")
            reasoning.append(f"Action criticality is {act.criticality}. RBI regulatory mandate requires Maker-Checker workflow (Dual-Control authorization).")
            alternative = "Forward execution token to secondary Treasury Manager for confirmation."
            
        # Segregation of Duties (SoD)
        # Developers should not run direct queries on production systems containing transaction tables
        if user.role == "Software Developer" and "PROD" in act.target_system.upper():
            vote = "BLOCK"
            confidence = 98
            evidence.append("Segregation of Duties (SoD) Violation")
            reasoning.append("User with role Software Developer attempting direct command execution on Production Environment. Violates ISO 27001 Control A.9.1.2.")
            alternative = "Run query in pre-production staging environment, or submit a request to the Operations team."
            
        # Check Policy Studio violations
        for violation in policy_violations:
            if violation["policy_id"] == "POL-RBI-01" and violation["status"] == "VIOLATED":
                vote = "ALLOW_APPROVAL"
                confidence = max(confidence, 96)
                reasoning.append(f"Triggered policy compliance check: RBI Maker-Checker Rule. Two managers signatures required.")
            if violation["policy_id"] == "POL-SOD-02" and violation["status"] == "VIOLATED":
                vote = "BLOCK"
                confidence = 99
                reasoning.append(f"Critical Segregation of Duties failure on treasury deals database query.")
                alternative = "Obtain executive approval from CISO office."
                
        # Resolve Recommendation
        if vote == "ALLOW":
            recommendation = "Compliance verification successful. Action conforms to SoD and RBI audit perimeter requirements."
        elif vote == "ALLOW_APPROVAL":
            recommendation = "Maker-checker compliance check triggered. Submit for manager validation."
        else:
            recommendation = "Block request. Execution violates internal Segregation of Duties policy."
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation
        )
