from datetime import datetime, time, timezone
from typing import List, Tuple
from app.domain.entities import Asset, PAMRequest, User
from app.domain.value_objects import TimeRange

# Define standard core business banking hours (08:00 - 18:00 UTC)
BANKING_HOURS = TimeRange(time(8, 0), time(18, 0))


class PAMAccessPolicy:
    """
    Evaluates business policy compliance for a privileged access request.
    """

    @staticmethod
    def evaluate(user: User, asset: Asset, request: PAMRequest) -> Tuple[str, List[str]]:
        """
        Evaluates the PAM request against static organizational governance rules.
        Returns:
            Tuple of (PolicyDecision, List of ViolationReasons)
            PolicyDecision can be: "ALLOW", "DENY", "ESCALATE"
        """
        reasons: List[str] = []
        decision = "ALLOW"

        # Rule 1: Maximum duration check (Tier 1 banks strictly restrict session lengths)
        # Maximum allowed duration is 4 hours (14400 seconds)
        MAX_DURATION_SECONDS = 14400
        if request.duration_seconds > MAX_DURATION_SECONDS:
            decision = "DENY"
            reasons.append(f"Requested duration {request.duration_seconds}s exceeds maximum limit of {MAX_DURATION_SECONDS}s.")

        # Rule 2: Asset Criticality vs Business Hours
        current_time = datetime.now(timezone.utc)
        is_business_hours = BANKING_HOURS.contains(current_time)

        if not is_business_hours:
            if asset.critical_level in ("HIGH", "CRITICAL"):
                # Outside business hours, critical assets require escalation
                if decision != "DENY":
                    decision = "ESCALATE"
                reasons.append("Access request to high/critical asset outside core business hours requires multi-manager escalation.")

        # Rule 3: Role and Asset Type mapping (Separation of Duties)
        # DBAs cannot access infrastructure/servers; Sysadmins cannot access customer databases
        user_roles = {role.name for role in user.roles}
        
        # Check DBAs
        if "Database Administrator" in user_roles and asset.type != "DATABASE":
            decision = "DENY"
            reasons.append("Database Administrator is restricted from accessing non-database assets.")
        
        # Check Infrastructure Admins
        if "Infrastructure Administrator" in user_roles and asset.type == "DATABASE":
            decision = "DENY"
            reasons.append("Infrastructure Administrator is restricted from accessing database assets.")

        # Rule 4: Critical Asset Default Escalation
        if asset.critical_level == "CRITICAL" and decision == "ALLOW":
            decision = "ESCALATE"
            reasons.append("Access to assets designated as CRITICAL automatically escalates to management approval.")

        return decision, reasons
