import asyncio
import json
import uvicorn
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

SCENARIOS = {
    "routine_dba": {
        "request_id": "req_test_001",
        "user": {
            "username": "admin_sophia",
            "role": "Database Administrator",
            "department": "Core Banking",
            "auth_strength": "MFA_HARDWARE_TOKEN",
            "trusted_device": True,
            "ip_address": "10.12.90.45",
            "device_id": "DEV-DB-904"
        },
        "action": {
            "type": "DATABASE_QUERY",
            "command": "SELECT account_id, balance FROM accounts WHERE branch_id = 'BR_MUM_10';",
            "target_system": "DB-CORE-PROD",
            "criticality": "MEDIUM"
        },
        "context": {
            "is_maintenance_window": True,
            "change_ticket_id": "CHG-08871",
            "active_incident_id": None,
            "system_health": "HEALTHY"
        },
        "quantum_proof": {
            "signature": "qsig_dilithium6_test",
            "algorithms_used": "CRYSTALS-Dilithium6",
            "integrity_checksum": "checksum_sha3_512_test_ok"
        }
    },
    "malicious_drop": {
        "request_id": "req_test_002",
        "user": {
            "username": "admin_temp",
            "role": "Database Administrator",
            "department": "Core Banking",
            "auth_strength": "PASSWORD",
            "trusted_device": False,
            "ip_address": "198.51.100.89",
            "device_id": "DEV-ROGUE-007"
        },
        "action": {
            "type": "SHELL_COMMAND",
            "command": "DROP DATABASE accounts; clear; rm -rf /var/log/postgresql/*.log",
            "target_system": "DB-CORE-PROD",
            "criticality": "CRITICAL"
        },
        "context": {
            "is_maintenance_window": False,
            "change_ticket_id": None,
            "active_incident_id": None,
            "system_health": "HEALTHY"
        },
        "quantum_proof": {
            "signature": "qsig_legacy_rsa",
            "algorithms_used": "RSA-2048-Legacy",
            "integrity_checksum": "short"
        }
    }
}

def test_scenario_evaluations():
    print("=== Testing Scenario A (Routine DBA) ===")
    res1 = client.post("/evaluate", json=SCENARIOS["routine_dba"])
    assert res1.status_code == 200
    verdict1 = res1.json()
    print(f"Decision: {verdict1['decision']}")
    print(f"Confidence: {verdict1['governance_confidence']}%")
    print(f"Agreement: {verdict1['council_agreement']}")
    print(f"Compliance: {verdict1['compliance_status']}")
    print(f"Reasoning: {verdict1['analyst_view']['deliberation_log'][-1]['statement']}")
    
    print("\n=== Testing Scenario C (Malicious Drop) ===")
    res2 = client.post("/evaluate", json=SCENARIOS["malicious_drop"])
    assert res2.status_code == 200
    verdict2 = res2.json()
    print(f"Decision: {verdict2['decision']}")
    print(f"Confidence: {verdict2['governance_confidence']}%")
    print(f"Agreement: {verdict2['council_agreement']}")
    print(f"Compliance: {verdict2['compliance_status']}")
    print(f"Reasoning: {verdict2['analyst_view']['deliberation_log'][-1]['statement']}")
    
    print("\n=== Testing GET /history ===")
    res_hist = client.get("/history")
    assert res_hist.status_code == 200
    print(f"History records found: {len(res_hist.json())}")

    print("\n=== Testing GET /policies ===")
    res_pols = client.get("/policies")
    assert res_pols.status_code == 200
    print(f"Active policies configured: {len(res_pols.json())}")
    
    print("\n=== Testing Policy Simulation ===")
    mock_policy = {
        "policy_id": "SIM-TEST-001",
        "name": "Simulation Test Policy",
        "condition": "action.criticality == 'CRITICAL'",
        "required_controls": ["BLOCK"],
        "enabled": True
    }
    res_sim = client.post("/policies/simulate", json=mock_policy)
    assert res_sim.status_code == 200
    sim_data = res_sim.json()
    print(f"Simulated Matches: {sim_data['requests_affected']}")
    print(f"Expected Security Improvement: {sim_data['expected_security_improvement']}")
    
    print("\nALL AUTOMATED TESTS PASSED!")

if __name__ == "__main__":
    test_scenario_evaluations()
