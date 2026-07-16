import sqlite3
import json
import uuid
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Tuple
from models import PrivilegedRequest, GovernanceVerdictResponse, MemoryMatchSummary

DB_FILE = "nexus_memory.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Decisions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            username TEXT,
            role TEXT,
            department TEXT,
            action_type TEXT,
            command TEXT,
            target_system TEXT,
            criticality TEXT,
            decision TEXT,
            confidence INTEGER,
            agreement TEXT,
            response_json TEXT
        )
    """)
    
    # Custom Policies Table (Governance Policy Studio)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id TEXT PRIMARY KEY,
            name TEXT,
            condition TEXT,
            required_controls TEXT,
            enabled INTEGER
        )
    """)
    
    # Check if we need to seed historical decisions for Governance Memory
    cursor.execute("SELECT COUNT(*) FROM decisions")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_historical_decisions(cursor)
        seed_default_policies(cursor)
        
    conn.commit()
    conn.close()

def seed_default_policies(cursor):
    default_policies = [
        ("POL-RBI-01", "RBI Maker-Checker Guideline", "action.criticality == 'CRITICAL' or action.type == 'DATABASE_RESTART'", '["TWO_MANAGERS", "MFA"]', 1),
        ("POL-SOD-02", "Segregation of Duties - Treasury", "user.department == 'Treasury Operations' and user.role == 'Database Administrator' and 'deal' in action.command.lower()", '["BLOCK"]', 1),
        ("POL-ZT-03", "Zero Trust - Off-Hours Execution", "not context.is_maintenance_window and (action.criticality in ['HIGH', 'CRITICAL'])", '["MFA", "SCREEN_RECORDING", "LIVE_MONITOR"]', 1),
        ("POL-IP-04", "Untrusted Network Access Restriction", "not user.trusted_device", '["ALLOW_SANDBOX", "SCREEN_RECORDING"]', 1),
        ("POL-RBI-05", "RBI Audit Trail Compliance", "action.type in ['SHELL_COMMAND', 'DATABASE_QUERY']", '["SCREEN_RECORDING"]', 1)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO policies (policy_id, name, condition, required_controls, enabled)
        VALUES (?, ?, ?, ?, ?)
    """, default_policies)

def seed_historical_decisions(cursor):
    """
    Seeds ~150 historical records to build a realistic Governance Memory.
    """
    users = [
        {"username": "admin_sophia", "role": "Database Administrator", "department": "Core Banking"},
        {"username": "dev_raj", "role": "Software Developer", "department": "Digital Channels"},
        {"username": "sec_ops_harsh", "role": "Security Engineer", "department": "Cyber Security"},
        {"username": "ops_ananya", "role": "Systems Administrator", "department": "IT Operations"}
    ]
    
    actions = [
        {"type": "DATABASE_QUERY", "command": "SELECT account_id, balance FROM accounts WHERE branch_id = 'BR_MUM_10';", "target_system": "DB-CORE-PROD", "criticality": "MEDIUM"},
        {"type": "DATABASE_QUERY", "command": "SELECT * FROM treasury_deals LIMIT 50;", "target_system": "DB-TREASURY-01", "criticality": "HIGH"},
        {"type": "DATABASE_RESTART", "command": "systemctl restart postgresql", "target_system": "DB-CORE-PROD", "criticality": "CRITICAL"},
        {"type": "SHELL_COMMAND", "command": "tail -n 100 /var/log/nginx/access.log", "target_system": "WEB-PORTAL-02", "criticality": "LOW"},
        {"type": "FILE_ACCESS", "command": "cat /etc/hosts", "target_system": "APP-NEFT-GATEWAY", "criticality": "LOW"},
        {"type": "SHELL_COMMAND", "command": "sudo rm -rf /tmp/cache_*", "target_system": "APP-UPI-ENGINE", "criticality": "MEDIUM"},
        {"type": "SHELL_COMMAND", "command": "iptables -L", "target_system": "SEC-FIREWALL-01", "criticality": "HIGH"}
    ]
    
    decisions = ["ALLOW", "ALLOW_SCREEN_RECORD", "ALLOW_APPROVAL", "ALLOW_SANDBOX", "BLOCK", "MFA"]
    now = datetime.now()
    
    for i in range(150):
        user = random.choice(users)
        action = random.choice(actions)
        
        # Heuristic decision making for seeds to ensure memory pattern checks find logical associations
        if action["criticality"] == "CRITICAL":
            decision = random.choice(["BLOCK", "ALLOW_APPROVAL", "ALLOW_SANDBOX"])
        elif action["criticality"] == "HIGH":
            decision = random.choice(["ALLOW_SCREEN_RECORD", "ALLOW_APPROVAL", "MFA", "BLOCK"])
        else:
            decision = "ALLOW"
            
        confidence = random.randint(80, 100)
        agreement = f"{random.randint(6, 9)} / 9 Votes"
        
        dec_id = f"dec_hist_{10000 + i}"
        timestamp = (now - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))).isoformat()
        
        cursor.execute("""
            INSERT INTO decisions (
                id, timestamp, username, role, department, action_type, command, target_system, criticality, decision, confidence, agreement, response_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dec_id,
            timestamp,
            user["username"],
            user["role"],
            user["department"],
            action["type"],
            action["command"],
            action["target_system"],
            action["criticality"],
            decision,
            confidence,
            agreement,
            json.dumps({"seeded": True})
        ))

def search_governance_memory(request: PrivilegedRequest) -> MemoryMatchSummary:
    """
    Search historical decisions to detect patterns of execution.
    Matches similar action types, target systems, or criticality levels.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We look for records with either same action type, target system, or similar command keywords
    cmd_words = [w for w in request.action.command.replace(";", "").split() if len(w) > 3][:3]
    like_clauses = " OR ".join(["command LIKE ?" for _ in cmd_words])
    
    query = f"""
        SELECT id, decision, criticality FROM decisions 
        WHERE action_type = ? 
        OR target_system = ?
        OR ({like_clauses})
        ORDER BY timestamp DESC
        LIMIT 100
    """
    
    params = [request.action.type, request.action.target_system] + [f"%{w}%" for w in cmd_words]
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    total = len(rows)
    if total == 0:
        return MemoryMatchSummary(
            matched_patterns_count=0,
            pattern_similarity=0.0,
            historical_outcome="0% Approved",
            average_risk="LOW",
            previous_incident_ref=None,
            insights=["No matching precedents located in Governance Memory. System baseline limits apply."]
        )
        
    counts = {"ALLOW": 0, "BLOCK": 0, "MFA": 0}
    critical_count = 0
    ref_id = None
    
    for row in rows:
        dec = row["decision"]
        crit = row["criticality"]
        if not ref_id:
            ref_id = row["id"]
        if "ALLOW" in dec:
            counts["ALLOW"] += 1
        elif "BLOCK" in dec:
            counts["BLOCK"] += 1
        else:
            counts["MFA"] += 1
            
        if crit == "CRITICAL" or crit == "HIGH":
            critical_count += 1
            
    approval_rate = round((counts["ALLOW"] / total) * 100, 1)
    
    # Calculate custom pattern similarity percentage
    similarity = 70.0 + min(total * 0.5, 25.0) + (5.0 if request.action.criticality == rows[0]["criticality"] else 0.0)
    similarity = min(similarity, 99.0)
    
    # Map average risk
    if critical_count / total > 0.5:
        avg_risk = "CRITICAL"
    elif critical_count / total > 0.25:
        avg_risk = "HIGH"
    elif counts["BLOCK"] / total > 0.1:
        avg_risk = "MEDIUM"
    else:
        avg_risk = "LOW"
        
    insights = [
        f"Precedent Match: Action pattern matches {similarity}% to historical incident {ref_id}.",
        f"Historical decisions indicate {approval_rate}% of matching actions were approved."
    ]
    
    return MemoryMatchSummary(
        matched_patterns_count=total,
        pattern_similarity=similarity,
        historical_outcome=f"{approval_rate}% Approved",
        average_risk=avg_risk,
        previous_incident_ref=ref_id,
        insights=insights
    )

def save_detailed_decision(request: PrivilegedRequest, verdict: GovernanceVerdictResponse):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO decisions (
            id, timestamp, username, role, department, action_type, command, target_system, criticality, decision, confidence, agreement, response_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        verdict.request_id,
        verdict.timestamp,
        request.user.username,
        request.user.role,
        request.user.department,
        request.action.type,
        request.action.command,
        request.action.target_system,
        request.action.criticality,
        verdict.decision,
        verdict.governance_confidence,
        verdict.council_agreement,
        json.dumps(verdict.dict())
    ))
    conn.commit()
    conn.close()

def get_history_list(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, username, role, action_type, command, target_system, decision, confidence, agreement FROM decisions ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_decision_detail(decision_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, username, role, department, action_type, command, target_system, criticality, decision, confidence, agreement, response_json 
        FROM decisions WHERE id = ?
    """, (decision_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = json.loads(row["response_json"])
        if "seeded" in data or "executive_view" not in data:
            # Dynamically build a detailed mock response for the seeded record to prevent frontend crashes
            decision = row["decision"]
            confidence = row["confidence"]
            username = row["username"]
            role = row["role"]
            cmd = row["command"]
            tgt = row["target_system"]
            is_blocked = (decision == "BLOCK")
            
            agent_responses = [
                {
                    "agent_name": "Identity verification agent",
                    "vote": "ALLOW",
                    "confidence": 98,
                    "evidence": ["Biometric session validated"],
                    "reasoning": ["MFA token clean", "Biometric verification match"],
                    "recommendation": "Maintain session access"
                },
                {
                    "agent_name": "Behavior intelligence agent",
                    "vote": "BLOCK" if is_blocked else "ALLOW",
                    "confidence": 95 if is_blocked else 90,
                    "evidence": ["Unusual query parameter structure" if is_blocked else "Matches standard DBA baseline"],
                    "reasoning": ["Command deviates from typical schema access" if is_blocked else "Command matches past DBA historical patterns"],
                    "recommendation": "Deny execution and isolate" if is_blocked else "Allow execution"
                },
                {
                    "agent_name": "Compliance intelligence agent",
                    "vote": "BLOCK" if is_blocked else "ALLOW",
                    "confidence": 99 if is_blocked else 100,
                    "evidence": ["Access to critical payment ledger" if is_blocked else "No compliance breaches detected"],
                    "reasoning": ["Violates regulatory segregation of duty policy" if is_blocked else "Conforms to internal policies"],
                    "recommendation": "Enforce policy intervention" if is_blocked else "Allow execution"
                },
                {
                    "agent_name": "Business impact agent",
                    "vote": "BLOCK" if is_blocked else "ALLOW",
                    "confidence": 90,
                    "evidence": ["Core table deletion would impact 24k active transactions" if is_blocked else "Routine administrative access"],
                    "reasoning": ["Est. downtime recovery exceeds threshold" if is_blocked else "No blast radius impact forecasted"],
                    "recommendation": "Block execution" if is_blocked else "Allow execution"
                },
                {
                    "agent_name": "Quantum security agent",
                    "vote": "ALLOW",
                    "confidence": 100,
                    "evidence": ["Dilithium quantum signature verified"],
                    "reasoning": ["Payload integrity verified via SHA3 checksum"],
                    "recommendation": "Cryptographically secure"
                }
            ]
            
            debate = [
                {"speaker": "Identity Agent", "statement": "Session context verified successfully.", "timestamp": row["timestamp"]},
                {"speaker": "Behavior Agent", "statement": "Anomalous command execution detected." if is_blocked else "Transaction matches past patterns.", "timestamp": row["timestamp"]},
                {"speaker": "Compliance Agent", "statement": "CRITICAL: Violates internal maker-checker constraints." if is_blocked else "No active policy rules breached.", "timestamp": row["timestamp"]},
                {"speaker": "Business Agent", "statement": "Blast radius simulation projects high service downtime." if is_blocked else "Business disruption index at 0%.", "timestamp": row["timestamp"]},
                {"speaker": "Judge Agent", "statement": "Consensus resolved: Block action." if is_blocked else "Consensus resolved: Allow action.", "timestamp": row["timestamp"]}
            ]
            
            chain_of_attack = [
                {"time": "5m", "probability": 90 if is_blocked else 2, "threat": "Credential stuffing spreading to API subnet" if is_blocked else "System normal"},
                {"time": "1h", "probability": 75 if is_blocked else 1, "threat": "Mule accounts withdraw ₹24.5 Lakhs" if is_blocked else "System normal"},
                {"time": "24h", "probability": 40 if is_blocked else 0, "threat": "Data exfiltration threat targeting primary DB" if is_blocked else "System normal"},
                {"time": "7d", "probability": 8 if is_blocked else 0, "threat": "Full system lockdown / Ransomware sequence" if is_blocked else "System normal"}
            ]

            digital_twin_2 = {
                "account_twin": {"health": 35 if is_blocked else 98, "status": "COMPROMISED_RISK" if is_blocked else "HEALTHY"},
                "device_twin": {"health": 12 if is_blocked else 92, "status": "SUSPICIOUS_DEVICE" if is_blocked else "HEALTHY"},
                "location_twin": {"confidence": 24 if is_blocked else 87, "status": "IMPOSSIBLE_TRAVEL" if is_blocked else "HEALTHY"},
                "behavior_twin": {"deviation": 96 if is_blocked else 34, "status": "ANOMALOUS" if is_blocked else "BASELINE"},
                "transaction_twin": {"risk": 89 if is_blocked else 12, "status": "CRITICAL" if is_blocked else "LOW_RISK"}
            }

            relationship_graph = {
                "nodes": [
                    {"id": "customer", "label": username, "type": "USER", "risk": 90 if is_blocked else 10},
                    {"id": "device", "label": "DEV-ID-88123", "type": "DEVICE", "risk": 95 if is_blocked else 15},
                    {"id": "ip", "label": "10.12.90.15", "type": "IP", "risk": 85 if is_blocked else 5},
                    {"id": "vpn", "label": "192.168.45.12 (VPN)", "type": "VPN", "risk": 75 if is_blocked else 8},
                    {"id": "target", "label": tgt, "type": "ASSET", "risk": 50 if is_blocked else 2}
                ],
                "edges": [
                    {"source": "customer", "target": "device", "risk": 85 if is_blocked else 5},
                    {"source": "device", "target": "ip", "risk": 90 if is_blocked else 10},
                    {"source": "ip", "target": "vpn", "risk": 75 if is_blocked else 12},
                    {"source": "vpn", "target": "target", "risk": 88 if is_blocked else 8}
                ]
            }
            if is_blocked:
                relationship_graph["nodes"].append({"id": "mule", "label": "Mule Company LLC", "type": "SINK", "risk": 99})
                relationship_graph["edges"].append({"source": "target", "target": "mule", "risk": 95})

            calibrated_confidence = {
                "prediction_confidence": 97 if is_blocked else 95,
                "evidence_strength": 95 if is_blocked else 90,
                "data_completeness": 89 if is_blocked else 95,
                "model_agreement": 96 if is_blocked else 100,
                "uncertainty": 4 if is_blocked else 2
            }

            trust_scores = {
                "identity_trust": 34 if is_blocked else 98,
                "behavior_trust": 22 if is_blocked else 95,
                "financial_trust": 45 if is_blocked else 93,
                "device_trust": 15 if is_blocked else 84,
                "network_trust": 28 if is_blocked else 80,
                "overall_trust": 29 if is_blocked else 91
            }

            adaptive_risk = [
                {"stage": "Current Risk", "score": 71 if is_blocked else 15},
                {"stage": "After MFA", "score": 38 if is_blocked else 5},
                {"stage": "After Device Verification", "score": 12 if is_blocked else 2},
                {"stage": "Tomorrow", "score": 6 if is_blocked else 1}
            ]

            executive_briefing = (
                f"A high-risk transaction originating from an unknown device for user {username} was intercepted. "
                f"Causal analysis indicates possible credential stuffing followed by privilege escalation attempt on {tgt}. "
                f"Swarm consensus recommends blocking the action and triggering digital twin quarantine."
                if is_blocked else
                f"A routine privileged action {row['action_type']} was requested by {username} on {tgt}. "
                f"All constraints passed behavioral benchmarks, and the action has been allowed."
            )

            regulatory_citations = [
                {"framework": "RBI Rule RB-17", "description": "Multi-factor authentication compliance check", "status": "FAILED" if is_blocked else "PASSED"},
                {"framework": "GDPR Article 32", "description": "Data transfer security baseline check", "status": "FAILED" if is_blocked else "PASSED"},
                {"framework": "PCI DSS Requirement 10", "description": "Audit log validation check", "status": "PASSED"}
            ]

            digital_twin_evolution = {
                "yesterday": 98 if is_blocked else 99,
                "today": 91 if is_blocked else 97,
                "tomorrow_prediction": 83 if is_blocked else 98
            }

            return {
                "request_id": row["id"],
                "timestamp": row["timestamp"],
                "decision": decision,
                "governance_confidence": confidence,
                "council_agreement": row["agreement"],
                "business_risk": "CRITICAL" if is_blocked else "LOW",
                "compliance_status": "FAILED" if is_blocked else "PASSED",
                "identity_trust": "UNTRUSTED" if is_blocked else "SECURE",
                "executive_view": {
                    "decision": decision,
                    "reason": "Regulatory rule violation" if is_blocked else "Normal baseline checked",
                    "business_impact": "Core operations at risk" if is_blocked else "No operational downtime projected",
                    "recommended_action": "Freeze accounts immediately" if is_blocked else "Execution allowed"
                },
                "analyst_view": {
                    "agent_responses": agent_responses,
                    "deliberation_log": debate,
                    "policy_evaluations": [],
                    "quantum_proof_status": "VERIFIED"
                },
                "governance_memory": {
                    "matched_patterns_count": 5,
                    "pattern_similarity": 95.0,
                    "historical_outcome": "92% Approved",
                    "average_risk": "LOW",
                    "insights": ["Matches historical incident pattern dec_hist_10023."]
                },
                "counterfactuals": [
                    {
                        "scenario_option": "IF_ALLOWED",
                        "estimated_downtime_minutes": 120 if is_blocked else 0,
                        "impacted_services": ["Payment Services" if is_blocked else "None"],
                        "affected_customers": 24000 if is_blocked else 0,
                        "recovery_cost_tier": "CRITICAL" if is_blocked else "LOW",
                        "risk_summary": "High risk profile" if is_blocked else "Standard profile"
                    }
                ],
                "recovery_plan": {
                    "safe_alternative": "Enforce MFA authentication" if is_blocked else "None required",
                    "steps": [
                        {"step_number": 1, "action": "Freeze target account", "status": "COMPLETED" if is_blocked else "SKIPPED"},
                        {"step_number": 2, "action": "Trigger forensic review", "status": "COMPLETED" if is_blocked else "SKIPPED"}
                    ],
                    "rollback_strategy": "Automatic snapshot restore"
                },
                "governance_journey": [],
                "tamper_proof_checksum": "seeded_record_checksum",
                "chain_of_attack_forecast": chain_of_attack,
                "digital_twin_2": digital_twin_2,
                "relationship_graph": relationship_graph,
                "calibrated_confidence": calibrated_confidence,
                "trust_scores": trust_scores,
                "adaptive_risk": adaptive_risk,
                "executive_briefing": executive_briefing,
                "regulatory_citations": regulatory_citations,
                "digital_twin_evolution": digital_twin_evolution
            }
        return data
    return None

def get_policies() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT policy_id, name, condition, required_controls, enabled FROM policies")
    rows = cursor.fetchall()
    conn.close()
    return [{"policy_id": r["policy_id"], "name": r["name"], "condition": r["condition"], "required_controls": json.loads(r["required_controls"]), "enabled": bool(r["enabled"])} for r in rows]

def save_policy(policy_id: str, name: str, condition: str, required_controls: List[str], enabled: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO policies (policy_id, name, condition, required_controls, enabled)
        VALUES (?, ?, ?, ?, ?)
    """, (policy_id, name, condition, json.dumps(required_controls), 1 if enabled else 0))
    conn.commit()
    conn.close()
