from fastapi import Depends
from app.core.exceptions import AuthorizationError
from app.domain.entities import User
from app.api.dependencies.auth import get_current_mfa_verified_user


class PermissionChecker:
    """
    FastAPI dependency factory enforcing granular Permission-Based Access Control (PBAC).
    Checks that the current user possesses permission mapping to resource + action.
    """

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, user: User = Depends(get_current_mfa_verified_user)) -> User:
        """
        Validates permission check on caller context.
        """
        if not user.has_permission(self.resource, self.action):
            raise AuthorizationError(
                message=f"Access Denied: Required permission '{self.resource}:{self.action}' is missing.",
                details={"required_resource": self.resource, "required_action": self.action}
            )
        return user
