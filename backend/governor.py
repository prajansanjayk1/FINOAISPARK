from models import PrivilegedRequest, RecoveryPlan, RecoveryStep
from typing import List, Dict, Any

class ExecutionGovernor:
    @staticmethod
    def get_pam_directives(decision: str, request: PrivilegedRequest, recovery_plan: RecoveryPlan) -> List[Dict[str, str]]:
        """
        Translates the final decision and recovery plan into concrete, step-by-step
        adaptive directives that a PAM system (like CyberArk) can execute directly.
        """
        directives = []
        
        # Add basic audit verification
        directives.append({
            "step": "1. Evidence Snapshot",
            "action": f"Cryptographic integrity verification passed for signature {request.quantum_proof.signature[:15]}...",
            "status": "COMPLETED"
        })
        
        if decision == "ALLOW":
            directives.extend([
                {"step": "2. Credential Injection", "action": "Generate and inject dynamic 15-minute temporary credentials.", "status": "PENDING"},
                {"step": "3. Live Recording", "action": "Initialize standard PAM session log audit stream.", "status": "PENDING"},
                {"step": "4. Direct Access", "action": "Grant shell/database access to target system.", "status": "PENDING"}
            ])
            
        elif decision == "ALLOW_READ_ONLY":
            directives.extend([
                {"step": "2. Policy Interception", "action": "Configure database session parser to read-only mode (Deny INSERT, UPDATE, DELETE).", "status": "PENDING"},
                {"step": "3. Direct Access", "action": "Grant query access. Enable screen recording.", "status": "PENDING"}
            ])
            
        elif decision == "ALLOW_SCREEN_RECORD":
            directives.extend([
                {"step": "2. Video Stream Initialization", "action": "Enforce mandatory full-frame screen recording with secure audit vault synchronization.", "status": "PENDING"},
                {"step": "3. Shell Injection", "action": "Inject credentials and spawn administrative console.", "status": "PENDING"}
            ])
            
        elif decision == "ALLOW_LIVE_MONITOR":
            directives.extend([
                {"step": "2. SecOps Hook", "action": "Notify on-duty Security Operations Center (SOC) team.", "status": "PENDING"},
                {"step": "3. Parallel Session Attachment", "action": "Attach live administrative session watcher. Enforce real-time keystroke monitoring.", "status": "PENDING"}
            ])
            
        elif decision == "ALLOW_SANDBOX":
            directives.extend([
                {"step": "2. Sandbox Provisioning", "action": "Clone schema and deploy dynamic ephemeral PostgreSQL/Linux container.", "status": "PENDING"},
                {"step": "3. Mock Sync", "action": "Sanitize and load mock transaction data sets into local sandbox.", "status": "PENDING"},
                {"step": "4. Execution reroute", "action": "Reroute admin shell execution to sandbox container. Enforce absolute host isolation.", "status": "PENDING"},
                {"step": "5. Automated Teardown", "action": "Destroy sandbox container and log final output to Audit Vault.", "status": "PENDING"}
            ])
            
        elif decision == "ALLOW_APPROVAL":
            directives.extend([
                {"step": "2. Authorization Hold", "action": "Suspend execution. Queue access request in PAM portal.", "status": "PENDING"},
                {"step": "3. Escalation Notification", "action": "Send high-priority SMS/Email alerts to 2 on-duty Treasury Managers.", "status": "PENDING"},
                {"step": "4. Checker Verify", "action": "Awaiting Dual-Control (Maker-Checker) digital signatures.", "status": "PENDING"}
            ])
            
        elif decision == "DELAY":
            directives.extend([
                {"step": "2. Time Hold", "action": f"Delay execution until nearest maintenance window starts.", "status": "PENDING"}
            ])
            
        elif decision == "ESCALATE":
            directives.extend([
                {"step": "2. Escalation State", "action": "Escalate request to Bank Chief Information Security Officer (CISO).", "status": "PENDING"}
            ])
            
        else: # BLOCK
            directives.extend([
                {"step": "2. Threat Containment", "action": f"Access blocked. Immediately terminate user active directory login session.", "status": "PENDING"},
                {"step": "3. Network Quarantining", "action": f"Block IP address {request.user.ip_address} on database subnets.", "status": "PENDING"},
                {"step": "4. SecOps Notification", "action": f"Incident triggered. Flag user {request.user.username} for security audit.", "status": "PENDING"}
            ])
            
        return directives
