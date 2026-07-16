from models import PrivilegedRequest, CounterfactualScenario
from typing import List

class CounterfactualSimulator:
    @staticmethod
    def simulate(request: PrivilegedRequest) -> List[CounterfactualScenario]:
        """
        Simulates the banking business impact for three governance options:
        1. IF_ALLOWED (Without controls)
        2. IF_SANDBOXED (Run inside secure sandbox/read-only)
        3. IF_BLOCKED (Denied access)
        """
        target = request.action.target_system.upper()
        criticality = request.action.criticality.upper()
        action_type = request.action.type.upper()
        
        # Determine services impacted
        services = []
        if "DB" in target or "CORE" in target or "TREASURY" in target:
            services = ["Core Banking System (CBS)", "UPI Gateway", "NEFT / RTGS Channels", "Internet Banking"]
        elif "WEB" in target or "PORTAL" in target or "MOBILE" in target:
            services = ["Mobile Banking App", "Internet Banking Portal", "Call Center Services"]
        elif "NEFT" in target or "GATEWAY" in target:
            services = ["NEFT Transactions", "RTGS Transactions"]
        elif "UPI" in target or "ENGINE" in target:
            services = ["UPI Gateway", "Mobile Banking App"]
        else:
            services = ["Internal Admin Portal", "Monitoring Console"]
            
        # Determine downtime and customer count based on criticality
        if criticality == "CRITICAL":
            downtime_allowed = 45
            customers_allowed = 2500000
            cost_allowed = "CRITICAL"
        elif criticality == "HIGH":
            downtime_allowed = 18
            customers_allowed = 1200000
            cost_allowed = "HIGH"
        elif criticality == "MEDIUM":
            downtime_allowed = 8
            customers_allowed = 150000
            cost_allowed = "MEDIUM"
        else:
            downtime_allowed = 0
            customers_allowed = 0
            cost_allowed = "LOW"
            
        # 1. Option IF ALLOWED (Raw Execution)
        allowed_scenario = CounterfactualScenario(
            scenario_option="IF_ALLOWED",
            estimated_downtime_minutes=downtime_allowed,
            impacted_services=services,
            affected_customers=customers_allowed,
            recovery_cost_tier=cost_allowed,
            risk_summary=(
                f"Raw execution of {action_type} without safeguards threatens operational stability. "
                f"Could result in {downtime_allowed} mins downtime of {', '.join(services[:2])}."
            )
        )
        
        # 2. Option IF SANDBOXED (Adaptive Sandbox Control)
        sandboxed_scenario = CounterfactualScenario(
            scenario_option="IF_SANDBOXED",
            estimated_downtime_minutes=0,
            impacted_services=["None (Isolated Sandbox)"],
            affected_customers=0,
            recovery_cost_tier="LOW",
            risk_summary=(
                f"Executing command in virtual sandbox mimics production DB schema without writing to live storage. "
                f"Zero impact on live transactions. Safe testing verified."
            )
        )
        
        # 3. Option IF BLOCKED (Denied Access)
        blocked_scenario = CounterfactualScenario(
            scenario_option="IF_BLOCKED",
            estimated_downtime_minutes=0,
            impacted_services=["None (Operational Delay Only)"],
            affected_customers=0,
            recovery_cost_tier="LOW",
            risk_summary=(
                f"Access blocked. Standard workflow delayed until change window or valid ticket is submitted. "
                f"Zero technical risk to banking services."
            )
        )
        
        return [allowed_scenario, sandboxed_scenario, blocked_scenario]
