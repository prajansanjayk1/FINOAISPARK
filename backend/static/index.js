// Preset Scenario payloads
const SCENARIOS = {
    routine_dba: {
        request_id: "req_0001A",
        user: {
            username: "admin_sophia",
            role: "Database Administrator",
            department: "Core Banking",
            auth_strength: "MFA_HARDWARE_TOKEN",
            trusted_device: true,
            ip_address: "10.12.90.45",
            device_id: "DEV-DB-904"
        },
        action: {
            type: "DATABASE_QUERY",
            command: "SELECT account_id, balance FROM accounts WHERE branch_id = 'BR_MUM_10';",
            target_system: "DB-CORE-PROD",
            criticality: "MEDIUM",
            parameters: {
                row_limit: 500
            }
        },
        context: {
            is_maintenance_window: true,
            change_ticket_id: "CHG-08871",
            active_incident_id: null,
            system_health: "HEALTHY"
        },
        quantum_proof: {
            signature: "qsig_dilithium6_0x3df0a28efa31",
            algorithms_used: "CRYSTALS-Dilithium6",
            integrity_checksum: "checksum_sha3_512_0xfa892f39df2011"
        }
    },
    untrusted_offhours: {
        request_id: "req_0002B",
        user: {
            username: "dev_raj",
            role: "Software Developer",
            department: "Digital Channels",
            auth_strength: "PASSWORD",
            trusted_device: false,
            ip_address: "192.168.1.150",
            device_id: "DEV-BYOD-881"
        },
        action: {
            type: "DATABASE_QUERY",
            command: "SELECT * FROM treasury_deals WHERE deal_value > 1000000 LIMIT 50;",
            target_system: "DB-TREASURY-01",
            criticality: "HIGH",
            parameters: {}
        },
        context: {
            is_maintenance_window: false,
            change_ticket_id: null,
            active_incident_id: null,
            system_health: "HEALTHY"
        },
        quantum_proof: {
            signature: "qsig_legacy_ecdsa_0x9b32e18fa",
            algorithms_used: "ECDSA-P256-Legacy",
            integrity_checksum: "checksum_sha256_0xae82d19f8f23021"
        }
    },
    malicious_drop: {
        request_id: "req_0003C",
        user: {
            username: "admin_temp",
            role: "Database Administrator",
            department: "Core Banking",
            auth_strength: "PASSWORD",
            trusted_device: false,
            ip_address: "198.51.100.89",
            device_id: "DEV-ROGUE-007"
        },
        action: {
            type: "SHELL_COMMAND",
            command: "DROP DATABASE accounts; clear; rm -rf /var/log/postgresql/*.log",
            target_system: "DB-CORE-PROD",
            criticality: "CRITICAL",
            parameters: {}
        },
        context: {
            is_maintenance_window: false,
            change_ticket_id: null,
            active_incident_id: null,
            system_health: "HEALTHY"
        },
        quantum_proof: {
            signature: "qsig_legacy_rsa_0x8f3e28a",
            algorithms_used: "RSA-2048-Legacy",
            integrity_checksum: "short_bad"
        }
    },
    unscheduled_restart: {
        request_id: "req_0004D",
        user: {
            username: "ops_ananya",
            role: "Systems Administrator",
            department: "IT Operations",
            auth_strength: "MFA_HARDWARE_TOKEN",
            trusted_device: true,
            ip_address: "10.12.90.11",
            device_id: "DEV-OPS-012"
        },
        action: {
            type: "DATABASE_RESTART",
            command: "systemctl restart postgresql",
            target_system: "DB-CORE-PROD",
            criticality: "CRITICAL",
            parameters: {}
        },
        context: {
            is_maintenance_window: false,
            change_ticket_id: null,
            active_incident_id: "INC-09923",
            system_health: "DEGRADED"
        },
        quantum_proof: {
            signature: "qsig_dilithium6_0x83e291ff29",
            algorithms_used: "CRYSTALS-Dilithium6",
            integrity_checksum: "checksum_sha3_512_0x00f72a819b3a012"
        }
    }
};

// UI Element Handles
const scenarioSelect = document.getElementById("scenario-select");
const requestEditor = document.getElementById("request-editor");
const formatBtn = document.getElementById("format-json-btn");
const evaluateBtn = document.getElementById("evaluate-btn");
const journeyStepper = document.getElementById("journey-stepper");
const deliberationTerminal = document.getElementById("deliberation-terminal");

// Explainability Views Toggles
const viewExecBtn = document.getElementById("view-exec-btn");
const viewAnalystBtn = document.getElementById("view-analyst-btn");
const execViewPanel = document.getElementById("exec-view-panel");
const analystViewPanel = document.getElementById("analyst-view-panel");

// Executive View Outputs
const execVerdictDecision = document.getElementById("exec-verdict-decision");
const execReasonVal = document.getElementById("exec-reason-val");
const execImpactVal = document.getElementById("exec-impact-val");
const execActionVal = document.getElementById("exec-action-val");

// Analyst View Outputs
const analystVerdictConfidence = document.getElementById("analyst-verdict-confidence");
const statAgreement = document.getElementById("stat-agreement");
const statIdentity = document.getElementById("stat-identity");
const statCompliance = document.getElementById("stat-compliance");
const statRisk = document.getElementById("stat-risk");

// Governance Memory precedent details
const precSimilarity = document.getElementById("prec-similarity");
const precOutcome = document.getElementById("prec-outcome");
const precRisk = document.getElementById("prec-risk");
const precRef = document.getElementById("prec-ref");
const memoryInsightBox = document.getElementById("memory-insight-box");

// Services, Directives, and Counterfactuals
const impactServicesGrid = document.getElementById("impact-services-grid");
const directivesList = document.getElementById("directives-list");
const counterfactualContainer = document.getElementById("counterfactual-container");

// Policy Studio Tabs
const studioRulesTab = document.getElementById("studio-rules-tab");
const studioSimTab = document.getElementById("studio-sim-tab");
const studioRulesPanel = document.getElementById("studio-rules-panel");
const studioSimPanel = document.getElementById("studio-sim-panel");

const policiesListContainer = document.getElementById("policies-list-container");
const savePoliciesBtn = document.getElementById("save-policies-btn");

// Simulator Form
const simConditionInput = document.getElementById("sim-condition-input");
const simControlsInput = document.getElementById("sim-controls-input");
const simulatePolicyBtn = document.getElementById("simulate-policy-btn");
const simResultsBox = document.getElementById("sim-results-box");

// State variables
let currentPolicies = [];

// App Lifecycle
window.addEventListener("DOMContentLoaded", () => {
    // Load default DBA Scenario
    loadScenario("routine_dba");
    fetchPolicies();
    
    scenarioSelect.addEventListener("change", (e) => {
        loadScenario(e.target.value);
    });
    
    formatBtn.addEventListener("click", formatJSON);
    evaluateBtn.addEventListener("click", runEvaluation);
    savePoliciesBtn.addEventListener("click", savePolicies);
    
    // View toggler logic
    viewExecBtn.addEventListener("click", () => switchExplainView("exec"));
    viewAnalystBtn.addEventListener("click", () => switchExplainView("analyst"));
    
    // Studio tab logic
    studioRulesTab.addEventListener("click", () => switchStudioTab("rules"));
    studioSimTab.addEventListener("click", () => switchStudioTab("sim"));
    
    // Simulation runner
    simulatePolicyBtn.addEventListener("click", runPolicySimulation);
});

function loadScenario(key) {
    const payload = SCENARIOS[key];
    if (payload) {
        requestEditor.value = JSON.stringify(payload, null, 4);
    }
}

function formatJSON() {
    try {
        const raw = requestEditor.value;
        const parsed = JSON.parse(raw);
        requestEditor.value = JSON.stringify(parsed, null, 4);
    } catch (e) {
        alert("Invalid JSON syntax: " + e.message);
    }
}

function switchExplainView(mode) {
    if (mode === "exec") {
        viewExecBtn.classList.add("active");
        viewAnalystBtn.classList.remove("active");
        execViewPanel.classList.add("active-panel");
        analystViewPanel.classList.remove("active-panel");
    } else {
        viewAnalystBtn.classList.add("active");
        viewExecBtn.classList.remove("active");
        analystViewPanel.classList.add("active-panel");
        execViewPanel.classList.remove("active-panel");
    }
}

function switchStudioTab(tab) {
    if (tab === "rules") {
        studioRulesTab.classList.add("active");
        studioSimTab.classList.remove("active");
        studioRulesPanel.classList.add("active-panel");
        studioSimPanel.classList.remove("active-panel");
    } else {
        studioSimTab.classList.add("active");
        studioRulesTab.classList.remove("active");
        studioSimPanel.classList.add("active-panel");
        studioRulesPanel.classList.remove("active-panel");
    }
}

async function fetchPolicies() {
    try {
        const response = await fetch("/policies");
        currentPolicies = await response.json();
        renderPolicies();
    } catch (e) {
        console.error("Failed to fetch policies:", e);
    }
}

function renderPolicies() {
    policiesListContainer.innerHTML = "";
    if (currentPolicies.length === 0) {
        policiesListContainer.innerHTML = '<div class="empty-placeholder">No policies registered.</div>';
        return;
    }
    
    currentPolicies.forEach((policy) => {
        const item = document.createElement("div");
        item.className = "policy-item";
        
        item.innerHTML = `
            <div class="policy-details">
                <span class="policy-title">${policy.policy_id}: ${policy.name}</span>
                <span class="policy-cond">Cond: ${policy.condition}</span>
                <span class="policy-controls">Required Controls: ${JSON.stringify(policy.required_controls)}</span>
            </div>
            <div class="policy-switch">
                <input type="checkbox" class="switch-checkbox" data-id="${policy.policy_id}" ${policy.enabled ? 'checked' : ''}>
                <span class="policy-lbl">${policy.enabled ? 'Active' : 'Disabled'}</span>
            </div>
        `;
        
        item.querySelector(".switch-checkbox").addEventListener("change", (e) => {
            policy.enabled = e.target.checked;
            item.querySelector(".policy-lbl").textContent = policy.enabled ? "Active" : "Disabled";
        });
        
        policiesListContainer.appendChild(item);
    });
}

async function savePolicies() {
    try {
        for (const policy of currentPolicies) {
            await fetch("/policies", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(policy)
            });
        }
        alert("Governance Policy configurations saved.");
    } catch (e) {
        alert("Failed to save policies: " + e.message);
    }
}

async function runPolicySimulation() {
    const condition = simConditionInput.value.trim();
    let controls = simControlsInput.value.trim();
    if (!condition) {
        alert("Please specify a policy condition expression.");
        return;
    }
    
    let parsedControls = [];
    try {
        if (controls) {
            parsedControls = JSON.parse(controls.replace(/'/g, '"'));
        }
    } catch (e) {
        alert("Controls must be formatted as JSON array string, e.g. ['MFA', 'SCREEN_RECORDING']");
        return;
    }
    
    const mockPolicy = {
        policy_id: "SIM-POL-" + Math.floor(Math.random() * 1000),
        name: "Simulated Custom Policy Rule",
        condition: condition,
        required_controls: parsedControls,
        enabled: true
    };
    
    simResultsBox.innerHTML = '<div class="empty-placeholder">Analyzing historical request logs...</div>';
    
    try {
        const response = await fetch("/policies/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(mockPolicy)
        });
        
        if (!response.ok) {
            throw new Error(`Simulation failed: HTTP ${response.status}`);
        }
        
        const simResult = await response.json();
        
        simResultsBox.innerHTML = `
            <div class="sim-metric-row"><span>Affected Requests</span> <span>${simResult.requests_affected}</span></div>
            <div class="sim-metric-row"><span>Operational False Positives</span> <span>${simResult.false_positives}</span></div>
            <div class="sim-metric-row"><span>Security Improvement</span> <span style="color:var(--green);">${simResult.expected_security_improvement}</span></div>
            <div class="sim-insight-list">
                ${simResult.insights.map(i => `<div>• ${i}</div>`).join("")}
            </div>
        `;
    } catch (e) {
        simResultsBox.innerHTML = `<div class="empty-placeholder" style="color:var(--red);">Error: ${e.message}</div>`;
    }
}

async function runEvaluation() {
    let requestPayload;
    try {
        requestPayload = JSON.parse(requestEditor.value);
    } catch (e) {
        alert("Invalid Request JSON: " + e.message);
        return;
    }
    
    resetTimeline();
    deliberationTerminal.innerHTML = '<div class="terminal-placeholder">Initializing AI Governance Council secure session...</div>';
    evaluateBtn.disabled = true;
    evaluateBtn.classList.add("loading");
    
    // Step 0: Ingest
    updateTimelineStep(0, "passed");
    
    try {
        const response = await fetch("/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestPayload)
        });
        
        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }
        
        const verdict = await response.json();
        animateResults(verdict);
        
    } catch (e) {
        deliberationTerminal.innerHTML = `<div class="speech-bubble speaker-judge"><span class="speech-statement" style="color:var(--red);">Orchestrator Exception: ${e.message}</span></div>`;
        updateTimelineStep(0, "failed");
        evaluateBtn.disabled = false;
        evaluateBtn.classList.remove("loading");
    }
}

function resetTimeline() {
    const steps = journeyStepper.querySelectorAll(".step");
    steps.forEach((s) => {
        s.className = "step inactive";
    });
}

function updateTimelineStep(index, status) {
    const steps = journeyStepper.querySelectorAll(".step");
    if (steps[index]) {
        steps[index].className = `step ${status}`;
    }
}

async function animateResults(verdict) {
    const timelineMilestones = [
        { step: 1, delay: 600, status: verdict.compliance_status === "PASSED" ? "passed" : "failed" }, // Policy
        { step: 2, delay: 500, status: verdict.identity_trust === "LOW" ? "failed" : "passed" },      // Identity
        { step: 3, delay: 500, status: "passed" },                                                  // Behavior
        { step: 4, delay: 500, status: "passed" },                                                  // Threat
        { step: 5, delay: 500, status: verdict.business_risk === "CRITICAL" ? "failed" : "passed" },  // Business
        { step: 6, delay: 600, status: "passed" },                                                  // Council Debate
        { step: 7, delay: 700, status: verdict.decision === "BLOCK" ? "failed" : "passed" },         // Consensus
        { step: 8, delay: 600, status: "passed" }                                                   // Directives
    ];
    
    deliberationTerminal.innerHTML = "";
    const debate = verdict.analyst_view.deliberation_log;
    
    for (let i = 0; i < debate.length; i++) {
        const item = debate[i];
        let milestone = timelineMilestones.find(m => m.step === i + 1) || { delay: 400 };
        await sleep(milestone.delay);
        appendTerminalMessage(item);
        
        if (i < timelineMilestones.length) {
            updateTimelineStep(i + 1, timelineMilestones[i].status);
        }
        deliberationTerminal.scrollTop = deliberationTerminal.scrollHeight;
    }
    
    evaluateBtn.disabled = false;
    evaluateBtn.classList.remove("loading");
    
    displayVerdictHUD(verdict);
}

function appendTerminalMessage(item) {
    const bubble = document.createElement("div");
    const speakerClean = item.speaker.toLowerCase().replace(" verification agent", "").replace(" intelligence agent", "").replace(" security agent", "").replace(" planner agent", "").replace(" agent", "").replace(" ", "_");
    bubble.className = `speech-bubble speaker-${speakerClean}`;
    
    bubble.innerHTML = `
        <div class="speech-header">
            <span class="speech-speaker">${item.speaker}</span>
            <span class="speech-time">${item.timestamp}</span>
        </div>
        <div class="speech-statement">${item.statement}</div>
    `;
    
    deliberationTerminal.appendChild(bubble);
}

function displayVerdictHUD(verdict) {
    // 1. Executive Views
    execVerdictDecision.textContent = verdict.decision;
    execVerdictDecision.className = "";
    if (verdict.decision === "ALLOW") {
        execVerdictDecision.classList.add("decision-allow");
    } else if (verdict.decision === "BLOCK") {
        execVerdictDecision.classList.add("decision-block");
    } else if (verdict.decision.includes("APPROVAL")) {
        execVerdictDecision.classList.add("decision-approval");
    } else {
        execVerdictDecision.classList.add("decision-sandbox");
    }
    
    execReasonVal.textContent = verdict.executive_view.reason;
    execImpactVal.textContent = verdict.executive_view.business_impact;
    execActionVal.textContent = verdict.executive_view.recommended_action;
    
    // 2. Analyst Views
    analystVerdictConfidence.textContent = `${verdict.governance_confidence}%`;
    analystVerdictConfidence.className = "";
    if (verdict.governance_confidence >= 90) {
        analystVerdictConfidence.classList.add("decision-block");
    } else if (verdict.governance_confidence >= 80) {
        analystVerdictConfidence.classList.add("decision-approval");
    } else {
        analystVerdictConfidence.classList.add("decision-sandbox");
    }
    
    statAgreement.textContent = verdict.council_agreement;
    statIdentity.textContent = verdict.identity_trust;
    statCompliance.textContent = verdict.compliance_status;
    statRisk.textContent = verdict.business_risk;
    
    statIdentity.style.color = verdict.identity_trust === "HIGH" ? "var(--green)" : (verdict.identity_trust === "LOW" ? "var(--red)" : "var(--amber)");
    statCompliance.style.color = verdict.compliance_status === "PASSED" ? "var(--green)" : "var(--red)";
    statRisk.style.color = verdict.business_risk === "CRITICAL" ? "var(--red)" : (verdict.business_risk === "HIGH" ? "var(--amber)" : "var(--text-primary)");
    
    // 3. Precedent Pattern Matches
    const mem = verdict.governance_memory;
    precSimilarity.textContent = `${mem.pattern_similarity}%`;
    precOutcome.textContent = mem.historical_outcome;
    precRisk.textContent = mem.average_risk;
    precRef.textContent = mem.previous_incident_ref || "None";
    
    // Risk color formatting
    precRisk.style.color = mem.average_risk === "CRITICAL" ? "var(--red)" : (mem.average_risk === "HIGH" ? "var(--amber)" : "var(--green)");
    memoryInsightBox.textContent = mem.insights.join(" | ");
    
    // 4. Business Services Impact Grid
    impactServicesGrid.innerHTML = "";
    const bizResponse = verdict.analyst_view.agent_responses.find(r => r.agent_name === "Business Impact Agent");
    if (bizResponse && bizResponse.evidence) {
        const svcEvidence = bizResponse.evidence.find(e => e.includes("critical_services"));
        const custEvidence = bizResponse.evidence.find(e => e.includes("affected_customers"));
        const timeEvidence = bizResponse.evidence.find(e => e.includes("estimated_downtime"));
        
        const services = svcEvidence ? svcEvidence.split(" = ")[1].split(", ") : [];
        const customers = custEvidence ? parseInt(custEvidence.split(" = ")[1]) : 0;
        const downtime = timeEvidence ? timeEvidence.split(" = ")[1] : "0 Mins";
        
        services.forEach((s) => {
            const card = document.createElement("div");
            card.className = "service-card at-risk";
            card.innerHTML = `
                <span class="service-name">${s}</span>
                <span class="service-meta">${customers.toLocaleString()} Users | ${downtime} downtime</span>
            `;
            impactServicesGrid.appendChild(card);
        });
    } else {
        impactServicesGrid.innerHTML = '<div class="empty-placeholder">No service impact detected.</div>';
    }
    
    // 5. Execution Directives list
    directivesList.innerHTML = "";
    const directives = verdict.recovery_plan.steps;
    directives.forEach((step) => {
        const li = document.createElement("li");
        li.innerHTML = `<strong>Step ${step.step_number}:</strong> ${step.action} <span style="color:var(--cyan);font-size:0.6rem;">[ACTIVE]</span>`;
        directivesList.appendChild(li);
    });
    
    const rollbackLi = document.createElement("li");
    rollbackLi.style.color = "var(--red)";
    rollbackLi.style.listStyleType = "none";
    rollbackLi.style.borderTop = "1px dotted var(--border-glass)";
    rollbackLi.style.paddingTop = "0.3rem";
    rollbackLi.innerHTML = `<strong>Rollback Strategy:</strong> ${verdict.recovery_plan.rollback_strategy}`;
    directivesList.appendChild(rollbackLi);
    
    // 6. Counterfactual Analysis Table
    counterfactualContainer.innerHTML = "";
    verdict.counterfactuals.forEach((cf) => {
        const card = document.createElement("div");
        card.className = `cf-card option-${cf.scenario_option}`;
        
        card.innerHTML = `
            <div class="cf-header">${cf.scenario_option.replace("_", " ")}</div>
            <div class="cf-stat"><span>Downtime:</span> <span>${cf.estimated_downtime_minutes} Mins</span></div>
            <div class="cf-stat"><span>Affected Accounts:</span> <span>${cf.affected_customers.toLocaleString()}</span></div>
            <div class="cf-stat"><span>Cost Tier:</span> <span>${cf.recovery_cost_tier}</span></div>
            <div class="cf-desc">${cf.risk_summary}</div>
        `;
        counterfactualContainer.appendChild(card);
    });
    
    document.getElementById("audit-badge").textContent = `SEAL: ${verdict.tamper_proof_checksum.slice(0, 10).toUpperCase()}`;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
