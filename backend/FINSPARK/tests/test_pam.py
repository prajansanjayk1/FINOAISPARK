import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_privileged_request_workflow(client: AsyncClient):
    # 1. Register CISO (Administrator)
    ciso_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_ciso",
            "email": "ciso@bank.com",
            "password": "Password123!",
            "department_code": "SOC",
            "role_names": ["Chief Information Security Officer (CISO)"]
        }
    )
    assert ciso_reg.status_code == 201
    
    # Login CISO
    ciso_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_ciso", "password": "Password123!"}
    )
    ciso_token = ciso_login.json()["access_token"]
    ciso_headers = {"Authorization": f"Bearer {ciso_token}"}

    # 2. Register Database Administrator (DBA)
    dba_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_dba",
            "email": "dba@bank.com",
            "password": "Password123!",
            "department_code": "DBA",
            "role_names": ["Database Administrator"]
        }
    )
    assert dba_reg.status_code == 201
    
    # Login DBA
    dba_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_dba", "password": "Password123!"}
    )
    dba_token = dba_login.json()["access_token"]
    dba_headers = {"Authorization": f"Bearer {dba_token}"}

    # 3. Create Asset (SWIFT Gateway) - Done by CISO
    asset_res = await client.post(
        "/api/v1/assets/",
        headers=ciso_headers,
        json={
            "name": "SWIFT Payment Engine",
            "type": "SERVER",
            "critical_level": "CRITICAL",
            "network_address": "10.150.1.5"
        }
    )
    assert asset_res.status_code == 201
    asset_id = asset_res.json()["id"]

    # 4. Violation Test: DBA requests access to SERVER (Separation of Duties block)
    req_dba_res = await client.post(
        "/api/v1/requests/",
        headers=dba_headers,
        json={
            "asset_id": asset_id,
            "action_requested": "SSH_ROOT",
            "duration_seconds": 3600,
            "justification": "Urgent database investigation on payment gateway"
        }
    )
    assert req_dba_res.status_code == 201
    dba_request = req_dba_res.json()
    assert dba_request["status"] == "REJECTED"
    assert dba_request["ai_decision"]["decision"] == "DENY"
    assert "Database Administrator" in dba_request["ai_decision"]["explanation"]

    # 5. Escalation Test: CISO requests access to CRITICAL asset (Requires Manager Escalation)
    req_ciso_res = await client.post(
        "/api/v1/requests/",
        headers=ciso_headers,
        json={
            "asset_id": asset_id,
            "action_requested": "SSH_ROOT",
            "duration_seconds": 3600,
            "justification": "Perform critical firmware security upgrades on swift node"
        }
    )
    assert req_ciso_res.status_code == 201
    ciso_request = req_ciso_res.json()
    assert ciso_request["status"] == "PENDING"
    assert ciso_request["ai_decision"]["decision"] == "ESCALATE"
    request_id = ciso_request["id"]

    # 6. Register a Manager to approve
    manager_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_manager",
            "email": "manager@bank.com",
            "password": "Password123!",
            "department_code": "SOC",
            "role_names": ["Manager"]
        }
    )
    assert manager_reg.status_code == 201
    
    # Login Manager
    manager_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_manager", "password": "Password123!"}
    )
    manager_token = manager_login.json()["access_token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}

    # 7. Approve request - Done by Manager
    approval_res = await client.post(
        "/api/v1/approvals/",
        headers=manager_headers,
        json={
            "request_id": request_id,
            "status": "APPROVED",
            "comments": "Confirmed upgrade ticket #4819. Approved."
        }
    )
    assert approval_res.status_code == 200
    approved_request = approval_res.json()
    assert approved_request["status"] == "APPROVED"
    assert len(approved_request["approvals"]) == 1
    assert approved_request["approvals"][0]["comments"] == "Confirmed upgrade ticket #4819. Approved."
