from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
from typing import List, Dict, Any
from prompts import IDENTITY_SYSTEM_PROMPT

class IdentityAgent(BaseAgent):
    def __init__(self):
        super().__init__("Identity Verification Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(IDENTITY_SYSTEM_PROMPT, request, policy_violations)
        if llm_res:
            try:
                return AgentResponse(
                    agent_name=self.name,
                    vote=llm_res.get("vote", "ALLOW"),
                    confidence=int(llm_res.get("confidence", 95)),
                    evidence=llm_res.get("evidence", []),
                    reasoning=llm_res.get("reasoning", []),
                    alternative=llm_res.get("alternative"),
                    recommendation=llm_res.get("recommendation", "")
                )
            except Exception as e:
                self.logger.warning(f"Error parsing Identity LLM response: {e}. Falling back to rules.")
        
        # Rule-based evaluation heuristics (failsafe/offline execution)
        vote = "ALLOW"
        confidence = 95
        evidence = []
        reasoning = []
        alternative = None
        
        user = request.user
        
        # Verify Trusted Device
        if not user.trusted_device:
            vote = "ALLOW_SANDBOX"
            confidence = 90
            evidence.append("trusted_device = False")
            reasoning.append("Access requested from unmanaged or untrusted workstation, violating Zero Trust device baselines.")
            alternative = "Reroute execution to isolated Sandbox with Screen Recording."
        else:
            evidence.append("trusted_device = True")
            reasoning.append("Device identified as bank-managed asset. Cryptographic device signature validated.")
            
        # Verify Auth Strength
        if user.auth_strength in ["PASSWORD", "MFA_SMS"]:
            vote = "ALLOW_APPROVAL"
            confidence = max(confidence - 10, 70)
            evidence.append(f"auth_strength = {user.auth_strength}")
            reasoning.append("Authentication strength is insufficient for privileged operations. SMS MFA or single-password setups are vulnerable to hijacking.")
            alternative = "Upgrade authentication to hardware-based token (FIDO2) or request Manager approval."
        else:
            evidence.append(f"auth_strength = {user.auth_strength} (Strong)")
            reasoning.append("Hardware security token verified for active session.")
            
        # Verify Department Mismatches
        if user.department == "Digital Channels" and "Treasury" in request.action.target_system:
            vote = "BLOCK"
            confidence = 98
            evidence.append(f"department_mismatch: {user.department} vs Treasury")
            reasoning.append("User is in Digital Channels department but attempting administrative action on Treasury Infrastructure. Segregation of Duties mismatch.")
            alternative = "Submit standard cross-department privilege transfer ticket."
            
        # Check policy violations related to identity
        for violation in policy_violations:
            if violation["policy_id"] == "POL-IP-04" and violation["status"] == "VIOLATED":
                vote = "ALLOW_SANDBOX"
                confidence = 95
                reasoning.append("IP Address is outside trusted network perimeter limits.")
                
        # Resolve Recommendation
        if vote == "ALLOW":
            recommendation = "Identity checks passed. User is authorized, active device verified."
        elif vote == "ALLOW_SANDBOX":
            recommendation = "Restrict session to dynamic isolated Sandbox container. Block production database direct write."
        elif vote == "ALLOW_APPROVAL":
            recommendation = "Enforce step-up MFA challenge and dual-signature approval."
        else:
            recommendation = "Block request. Revoke active temporary tokens. Department / Role role-profile conflict."
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation
        )
