from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
import re
from typing import List, Dict, Any
from prompts import THREAT_SYSTEM_PROMPT

class ThreatAgent(BaseAgent):
    def __init__(self):
        super().__init__("Threat Intelligence Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(THREAT_SYSTEM_PROMPT, request, policy_violations)
        if llm_res:
            try:
                return AgentResponse(
                    agent_name=self.name,
                    vote=llm_res.get("vote", "ALLOW"),
                    confidence=int(llm_res.get("confidence", 90)),
                    evidence=llm_res.get("evidence", []),
                    reasoning=llm_res.get("reasoning", []),
                    alternative=llm_res.get("alternative"),
                    recommendation=llm_res.get("recommendation", "")
                )
            except Exception as e:
                self.logger.warning(f"Error parsing Threat LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 90
        evidence = []
        reasoning = []
        alternative = None
        
        command = request.action.command.lower()
        
        # 1. Privilege Escalation Indicators
        if "sudo" in command or "chmod" in command or "chown" in command or "su " in command:
            vote = "ALLOW_LIVE_MONITOR"
            confidence = 88
            evidence.append("Threat: Privilege Escalation Signature")
            reasoning.append("Command contains system administration privilege escalation tokens (e.g., sudo/chmod). Risks OS-level root compromise.")
            alternative = "Run command inside confined admin profile shell or request explicit privilege token."
            
        # 2. Defense Evasion Indicators
        if "clear" in command or "history -c" in command or "/var/log" in command or "auditd" in command:
            vote = "BLOCK"
            confidence = 98
            evidence.append("Threat: Defense Evasion Signature")
            reasoning.append("Attempt to edit or clear audit logs or shell history detected. Indicative of malicious clean-up phase.")
            alternative = "All server operations must run with active syslog auditing enabled."
            
        # 3. Mass Exfiltration / Lateral Movement Indicators
        if ("select *" in command and "limit" not in command) or "scp " in command or "rsync" in command or "curl " in command:
            vote = "BLOCK"
            confidence = 95
            evidence.append("Threat: Mass Data Exfiltration Signature")
            reasoning.append("Query requests unbounded table dumps ('SELECT *' without LIMIT) or file copy utilities, indicating possible customer data harvest.")
            alternative = "Append a LIMIT clause to query or execute dump via secure bulk backup job."
            
        # 4. Credential Mismatches
        if not request.user.trusted_device and request.action.criticality == "CRITICAL":
            vote = "BLOCK"
            confidence = 96
            evidence.append("Threat: Session Hijacking Risk")
            reasoning.append("Critical command initiated from untrusted device. Potential compromise of admin credentials.")
            alternative = "Authenticate via hardware security token from a managed banking workstation."
            
        # Resolve Recommendation
        if vote == "ALLOW":
            recommendation = "No active Indicators of Compromise (IoC) detected in session profile."
        elif vote == "ALLOW_LIVE_MONITOR":
            recommendation = "Escalate request to active Live Keystroke Monitoring. Enforce security log duplication."
        else:
            recommendation = "Immediately block PAM session. Alert Bank Security Incident Response (CSIRT) team."
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation
        )
