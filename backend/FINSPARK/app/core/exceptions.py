from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class DomainError(Exception):
    """Base class for all domain-specific business exceptions."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EntityNotFoundError(DomainError):
    """Raised when a requested domain entity (User, Asset, etc.) does not exist."""
    pass


class AuthenticationError(DomainError):
    """Raised for authentication failures (e.g., bad passwords, expired sessions)."""
    pass


class MfaRequiredError(DomainError):
    """Raised when an action requires MFA validation before proceeding."""
    pass


class AccountLockedError(DomainError):
    """Raised when a user account has been locked due to brute force protection."""
    pass


class AuthorizationError(DomainError):
    """Raised when user lacks proper permissions (RBAC or PBAC) to access a resource."""
    pass


class DeviceNotTrustedError(DomainError):
    """Raised when a request is made from an unregistered/untrusted device."""
    pass


class IPNotWhitelistedError(DomainError):
    """Raised when the request originates from a non-whitelisted IP address."""
    pass


class BusinessRuleViolation(DomainError):
    """Raised when a policy or business rule check fails (e.g., PAM constraints)."""
    pass


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers to map custom domain exceptions into
    well-formatted HTTP response payloads.
    """

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "RESOURCE_NOT_FOUND", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "AUTHENTICATION_FAILED", "message": exc.message, "details": exc.details},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(MfaRequiredError)
    async def mfa_required_handler(request: Request, exc: MfaRequiredError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "MFA_REQUIRED", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(AccountLockedError)
    async def account_locked_handler(request: Request, exc: AccountLockedError):
        return JSONResponse(
            status_code=status.HTTP_423_LOCKED,
            content={"error": "ACCOUNT_LOCKED", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "ACCESS_DENIED", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(DeviceNotTrustedError)
    async def device_untrusted_handler(request: Request, exc: DeviceNotTrustedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "DEVICE_UNTRUSTED", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(IPNotWhitelistedError)
    async def ip_untrusted_handler(request: Request, exc: IPNotWhitelistedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "IP_RESTRICTED", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(BusinessRuleViolation)
    async def rule_violation_handler(request: Request, exc: BusinessRuleViolation):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "POLICY_VIOLATION", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(Exception)
    async def global_fallback_handler(request: Request, exc: Exception):
        # Capture trace/correlation info and log internal server errors securely
        logger.exception("An unhandled internal server error occurred")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred. Please contact the administrator."},
        )
