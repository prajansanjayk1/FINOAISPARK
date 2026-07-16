from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse
from datetime import datetime
import re
from typing import List, Dict, Any
from prompts import BEHAVIOR_SYSTEM_PROMPT

class BehaviorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Behavior Intelligence Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(BEHAVIOR_SYSTEM_PROMPT, request, policy_violations)
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
                self.logger.warning(f"Error parsing Behavior LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 90
        evidence = []
        reasoning = []
        alternative = None
        
        command = request.action.command.lower()
        
        # Check command sequences hazard
        dangerous_patterns = [
            (r"\brm\s+-rf\b", "Recursive deletion command 'rm -rf' detected"),
            (r"\bdrop\s+database\b", "Database deletion command 'DROP DATABASE' detected"),
            (r"\btruncate\b", "Table truncate command detected"),
            (r"\bdelete\s+from\b", "Unbounded record deletion query detected"),
            (r"\bformat\b", "Disk formatting attempt detected"),
            (r"\bmkfs\b", "Filesystem creation command detected")
        ]
        
        hazard_found = False
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, command):
                vote = "BLOCK"
                confidence = 98
                evidence.append(f"command_hazard = {desc}")
                reasoning.append(f"Destructive operation signature identified in command string: '{request.action.command}'.")
                alternative = "Run command on database backup clone or execute inside local staging environment."
                hazard_found = True
                break
                
        if not hazard_found:
            evidence.append("command_hazard = NONE")
            reasoning.append("Command syntax conforms to standard read/write queries. No direct OS shell injection commands found.")
            
        # Parse timestamp to evaluate scheduling anomalies (off-hours)
        try:
            req_time = datetime.fromisoformat(request.timestamp.replace("Z", ""))
            hour = req_time.hour
            # Flag off-hours if not between 8:00 AM and 6:00 PM (18:00)
            if hour < 8 or hour >= 18:
                evidence.append(f"execution_time = {hour}:00 (Off-Hours)")
                reasoning.append(f"Admin user executing commands at {hour}:00. Standard administrative profile activity is between 08:00 and 18:00.")
                if vote == "ALLOW":
                    vote = "ALLOW_SCREEN_RECORD"
                    confidence = 85
                    alternative = "Schedule execution for next business morning or initiate session recording."
            else:
                evidence.append(f"execution_time = {hour}:00 (Business Hours)")
                reasoning.append("Execution time aligns with standard business hours.")
        except Exception as e:
            evidence.append("execution_time = UNKNOWN")
            reasoning.append(f"Unable to parse request timestamp: {str(e)}")
            
        # Check policy violations related to behavior
        for violation in policy_violations:
            if violation["policy_id"] == "POL-ZT-03" and violation["status"] == "VIOLATED":
                # Off hours zero trust rule violation
                if vote == "ALLOW":
                    vote = "ALLOW_SCREEN_RECORD"
                confidence = max(confidence, 90)
                reasoning.append("Zero Trust policy mandates session monitoring for off-hours operations.")
                
        # Resolve Recommendation
        if vote == "ALLOW":
            recommendation = "Behavior checks consistent. Command signature aligns with user role profile."
        elif vote == "ALLOW_SCREEN_RECORD":
            recommendation = "Operation allowed under enforced PAM session video recording."
        elif vote == "ALLOW_SANDBOX":
            recommendation = "Deny live DB update. Allow execution inside read-only schema sandbox."
        else:
            recommendation = "Block execution. High destructive payload risk identified."
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=recommendation
        )
