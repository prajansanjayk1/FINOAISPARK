import base64
import hashlib
import hmac
import struct
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.config import settings
from app.core.logging import logger

# Initialize Argon2 Password Hasher
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hashes a password using Argon2id with default secure parameters.
    """
    return password_hasher.hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies a plain password against an Argon2id hash.
    """
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception as e:
        logger.error(f"Error during password verification: {str(e)}")
        return False


def create_token(
    subject: Union[str, Any],
    expires_delta: timedelta,
    token_type: str = "access",
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a secure signed HS256 JWT.
    """
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": expire,
        "iss": settings.PROJECT_NAME
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    subject: Union[str, Any],
    roles: list[str],
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a short-lived access token with role mappings.
    """
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = {"roles": roles}
    if additional_claims:
        claims.update(additional_claims)
    return create_token(subject, expires, token_type="access", additional_claims=claims)


def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    Generates a long-lived refresh token for token rotation.
    """
    expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires, token_type="refresh")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT. Raises expired or invalid token errors.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer=settings.PROJECT_NAME
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise


def generate_mfa_secret() -> str:
    """
    Generates a standard 32-character base32 MFA secret for TOTP.
    """
    # 20 random bytes is standard (160 bits)
    import os
    random_bytes = os.urandom(20)
    return base64.b32encode(random_bytes).decode("utf-8")


def verify_totp(secret: str, code: str) -> bool:
    """
    Pure Python verification of Time-Based One-Time Password (TOTP) following RFC 6238.
    Verifies within a time step window of [-1, 0, 1] to tolerate minor clock drift.
    """
    try:
        # Standardize formatting and handle padding
        secret_clean = secret.strip().replace(" ", "")
        missing_padding = len(secret_clean) % 8
        if missing_padding:
            secret_clean += "=" * (8 - missing_padding)

        key = base64.b32decode(secret_clean, casefold=True)
        # Standard interval is 30 seconds
        time_step = int(time.time() / 30)

        for offset in [-1, 0, 1]:
            # Construct 8-byte counter message from step value
            val = struct.pack(">Q", time_step + offset)
            # Create HMAC-SHA1 signature
            hmac_hash = hmac.new(key, val, hashlib.sha1).digest()
            # Dynamic Truncation of SHA1 output
            offset_idx = hmac_hash[-1] & 0x0F
            truncated = struct.unpack(">I", hmac_hash[offset_idx:offset_idx + 4])[0] & 0x7FFFFFFF
            calculated_code = truncated % 1000000
            
            # Format to 6 digits and compare
            if f"{calculated_code:06d}" == code:
                return True
        return False
    except Exception as e:
        logger.error(f"TOTP verification encountered an error: {str(e)}")
        return False
