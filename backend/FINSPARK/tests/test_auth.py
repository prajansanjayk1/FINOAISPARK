import base64
import hashlib
import hmac
import struct
import time
import pytest
from httpx import AsyncClient

# Helper to generate a valid TOTP code for testing
def get_totp_code(secret: str) -> str:
    secret_clean = secret.strip().replace(" ", "")
    missing_padding = len(secret_clean) % 8
    if missing_padding:
        secret_clean += "=" * (8 - missing_padding)
    key = base64.b32decode(secret_clean, casefold=True)
    time_step = int(time.time() / 30)
    val = struct.pack(">Q", time_step)
    hmac_hash = hmac.new(key, val, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0F
    truncated = struct.unpack(">I", hmac_hash[offset:offset + 4])[0] & 0x7FFFFFFF
    otp = truncated % 1000000
    return f"{otp:06d}"


@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_analyst",
            "email": "test_analyst@bank.com",
            "password": "Password123!",
            "department_code": "SOC",
            "role_names": ["SOC Analyst"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test_analyst"
    assert "SOC Analyst" in data["roles"]


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient):
    # 1. Register User
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_user",
            "email": "login_user@bank.com",
            "password": "Password123!",
            "department_code": "SOC",
            "role_names": ["SOC Analyst"]
        }
    )

    # 2. Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "login_user",
            "password": "Password123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["mfa_required"] is False


@pytest.mark.asyncio
async def test_user_login_invalid_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "non_existent_user",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
    assert response.json()["error"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_mfa_workflow(client: AsyncClient):
    # 1. Register and Login to get access token
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "mfa_user",
            "email": "mfa_user@bank.com",
            "password": "Password123!",
            "department_code": "SOC",
            "role_names": ["SOC Analyst"]
        }
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "mfa_user", "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup MFA
    setup_res = await client.post("/api/v1/auth/mfa/setup", headers=headers)
    assert setup_res.status_code == 200
    secret = setup_res.json()["mfa_secret"]

    # 3. Enable MFA using valid TOTP
    code = get_totp_code(secret)
    enable_res = await client.post(
        "/api/v1/auth/mfa/enable",
        headers=headers,
        json={
            "username": "mfa_user",
            "totp_code": code
        }
    )
    assert enable_res.status_code == 200

    # 4. Successive logins must now flag mfa_required=True
    login_mfa_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "mfa_user", "password": "Password123!"}
    )
    assert login_mfa_res.status_code == 200
    assert login_mfa_res.json()["mfa_required"] is True
    assert login_mfa_res.json()["access_token"] == ""

    # 5. Complete login via MFA verification
    mfa_verify_code = get_totp_code(secret)
    verify_res = await client.post(
        "/api/v1/auth/mfa/verify",
        json={
            "username": "mfa_user",
            "totp_code": mfa_verify_code
        }
    )
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert "access_token" in data
    assert data["mfa_required"] is False
