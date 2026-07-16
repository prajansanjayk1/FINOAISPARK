from agents.base import BaseAgent
from models import PrivilegedRequest, AgentResponse, RecoveryPlan, RecoveryStep
from typing import List, Dict, Any
from prompts import RECOVERY_SYSTEM_PROMPT

class RecoveryPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Recovery Planner Agent")
        
    async def evaluate(self, request: PrivilegedRequest, policy_violations: List[Dict[str, Any]]) -> AgentResponse:
        self.logger.info(f"Evaluating request {request.request_id}")
        
        # Try LLM Evaluation first
        llm_res = await self.get_llm_evaluation(RECOVERY_SYSTEM_PROMPT, request, policy_violations)
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
                self.logger.warning(f"Error parsing Recovery LLM response: {e}. Falling back to rules.")
        
        vote = "ALLOW"
        confidence = 90
        evidence = []
        reasoning = []
        
        target = request.action.target_system.upper()
        command = request.action.command.lower()
        criticality = request.action.criticality.upper()
        action_type = request.action.type.upper()
        
        if "drop" in command or "delete" in command or "truncate" in command:
            vote = "ALLOW_SANDBOX"
            evidence.append("Sequence Pattern: Ephemeral Schema Sandbox")
            reasoning.append("Admin requests database drops/deletes. Safe alternative reroutes command to an isolated dynamic container running a sanitized duplicate.")
            alternative = "Clone Database Schema -> Seed Masked Dataset -> Reroute Session to Sandbox Container -> Log Execution Output -> Purge Container"
            
        elif action_type == "DATABASE_RESTART" or "restart" in command:
            vote = "ALLOW_APPROVAL"
            evidence.append("Sequence Pattern: High-Availability Failover Rollout")
            reasoning.append("Admin requests core database restart. Safe alternative requires taking snapshots, standby verification, passive-node restarts, and checks.")
            alternative = "Create Snapshot -> Verify Replication -> Switch Traffic -> Restart Passive Node -> Health Check -> Promote -> Rollback Available"
            
        elif "select *" in command:
            vote = "ALLOW_READ_ONLY"
            evidence.append("Sequence Pattern: Safety Query Constraint Enforcement")
            reasoning.append("Admin queries full tables. Safe alternative enforces paging queries by appending LIMIT constraints to prevent exfiltration.")
            alternative = "Configure Keystroke Record -> Append LIMIT 100 Clause -> Execute Query -> Save to Secure Log Vault"
            
        elif criticality in ["HIGH", "CRITICAL"]:
            vote = "ALLOW_APPROVAL"
            evidence.append("Sequence Pattern: Maker-Checker Multi-Signature Hold")
            reasoning.append("High criticality action requires dual authorization.")
            alternative = "Generate ServiceNow Ticket -> Verify Ticket Status -> Notify Duty Manager -> Validate OTP -> Run Command"
            
        else:
            vote = "ALLOW"
            evidence.append("Sequence Pattern: Direct Session Log")
            reasoning.append("Command has low blast radius. Standard session recording applies.")
            alternative = "Begin standard PAM Session Record -> Execute Query -> Complete Integrity Check"
            
        return AgentResponse(
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            alternative=alternative,
            recommendation=f"Orchestrate sequence: {alternative}"
        )

    def generate_plan(self, request: PrivilegedRequest, vote: str) -> RecoveryPlan:
        command = request.action.command
        target = request.action.target_system
        
        if vote == "ALLOW_SANDBOX":
            return RecoveryPlan(
                safe_alternative="Clone database schema and execute in isolated virtual container sandbox.",
                steps=[
                    RecoveryStep(step_number=1, action="Provision dynamic sandbox container matching target server config.", status="PENDING", rollback_trigger="Container failure"),
                    RecoveryStep(step_number=2, action="Clone target database schema structure (DDL only).", status="PENDING"),
                    RecoveryStep(step_number=3, action="Populate sandbox with masked seed datasets (no production data).", status="PENDING"),
                    RecoveryStep(step_number=4, action=f"Reroute and execute command: '{command}' inside sandbox container.", status="PENDING"),
                    RecoveryStep(step_number=5, action="Log standard output results to security viewer and tear down container.", status="PENDING")
                ],
                rollback_strategy="Purge sandbox environment. Ephemeral containers deleted. No production disk state altered."
            )
            
        elif vote == "ALLOW_APPROVAL":
            if request.action.type == "DATABASE_RESTART" or "restart" in command.lower():
                return RecoveryPlan(
                    safe_alternative="Execute restart using High-Availability Passive Node failover sequence.",
                    steps=[
                        RecoveryStep(step_number=1, action="Create active backup snapshot on target database.", status="PENDING", rollback_trigger="Snapshot failure"),
                        RecoveryStep(step_number=2, action="Verify active-passive database replication synchronization lag is < 1s.", status="PENDING"),
                        RecoveryStep(step_number=3, action="Switch active database traffic path to passive node standby.", status="PENDING"),
                        RecoveryStep(step_number=4, action="Execute database restart command on the passive master node.", status="PENDING"),
                        RecoveryStep(step_number=5, action="Perform system health check (ports check, ping response).", status="PENDING"),
                        RecoveryStep(step_number=6, action="Promote restarted node back to master and restore traffic routes.", status="PENDING")
                    ],
                    rollback_strategy="Rollback standby node target traffic to pre-restart master backup snapshot."
                )
            else:
                return RecoveryPlan(
                    safe_alternative="Execute command following dual manager approval handshake.",
                    steps=[
                        RecoveryStep(step_number=1, action="Trigger incident snapshot backup on target.", status="PENDING", rollback_trigger="Backup failure"),
                        RecoveryStep(step_number=2, action="Halt PAM execution stream. Dispatch approvals push notifications to Duty Manager.", status="PENDING"),
                        RecoveryStep(step_number=3, action="Awaiting dual digital signature validation.", status="PENDING"),
                        RecoveryStep(step_number=4, action=f"Inject Dynamic OTP credentials and run command: '{command}'.", status="PENDING"),
                        RecoveryStep(step_number=5, action="Run automated service response diagnostics.", status="PENDING")
                    ],
                    rollback_strategy="Restore server configurations and directories using the pre-execution backup snapshot."
                )
            
        elif vote == "ALLOW_READ_ONLY":
            safe_cmd = command
            if "select *" in command.lower() and "limit" not in command.lower():
                safe_cmd = command.rstrip("; ") + " LIMIT 100;"
            return RecoveryPlan(
                safe_alternative=f"Enforce query limits: '{safe_cmd}'",
                steps=[
                    RecoveryStep(step_number=1, action="Begin live session keystroke logging.", status="PENDING"),
                    RecoveryStep(step_number=2, action=f"Substitute original request with: '{safe_cmd}'", status="PENDING"),
                    RecoveryStep(step_number=3, action=f"Run query on target system: {target}.", status="PENDING"),
                    RecoveryStep(step_number=4, action="Validate data rows return count and stream log to Audit Vault.", status="PENDING")
                ],
                rollback_strategy="None. Query execution has read-only access. No state changed."
            )
            
        else:
            return RecoveryPlan(
                safe_alternative="Direct execution under standard PAM session recordings.",
                steps=[
                    RecoveryStep(step_number=1, action="Initialize live PAM session video stream logging.", status="PENDING"),
                    RecoveryStep(step_number=2, action=f"Inject temporary credentials and run command on {target}.", status="PENDING"),
                    RecoveryStep(step_number=3, action="Log completed status and flush session credentials cache.", status="PENDING")
                ],
                rollback_strategy="Kill active PAM session socket. Revoke temporary credentials."
            )
