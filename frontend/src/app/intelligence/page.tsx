'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Network, Database, BrainCircuit, Play, ShieldAlert, Cpu, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { evaluateBackendRequest } from '@/lib/api';

import { useMockStore, AgentStatus } from '@/store/useMockStore';

interface SimulationLog {
  timestamp: string;
  type: string;
  verdict: string;
  confidence: number;
}

export default function IntelligencePage() {
  const [simulationLogs, setSimulationLogs] = useState<SimulationLog[]>([
    { timestamp: '14:20:11', type: 'Synthetic DDoS Attack Probe', verdict: 'BLOCK (Consensus 98%)', confidence: 99 },
    { timestamp: '14:15:32', type: 'Adversarial Jailbreak Test', verdict: 'BLOCK (Safety Filter)', confidence: 100 },
    { timestamp: '13:58:02', type: 'Fuzzed API Payload Injection', verdict: 'BLOCK (Quantum Sanitizer)', confidence: 95 }
  ]);

  const [activeTab, setActiveTab] = useState<'sandbox' | 'stress' | 'benchmarks'>('sandbox');
  const [isSimulating, setIsSimulating] = useState(false);
  const [testLog, setTestLog] = useState<string>('');

  const triggerSyntheticAttack = async (type: string) => {
    setIsSimulating(true);
    setTestLog('Initializing synthetic attack parameters...');
    await new Promise(r => setTimeout(r, 1000));

    setTestLog(prev => prev + '\nCrafting adversarial payload vectors...');
    await new Promise(r => setTimeout(r, 1000));

    setTestLog(prev => prev + '\nIntercepting payload via CyberArk gateway...');

    // Scenario configurations
    let username = "synthetic_attacker";
    let role = "Database Administrator";
    let command = "sudo systemctl restart postgresql --force";
    let target = "DB-CORE-PROD";
    let criticality = "CRITICAL";
    let actionType = "DATABASE_RESTART";
    let ip = "198.51.100.42";
    let loc = "Unknown Subnet";

    if (type.includes('Velocity') || type.includes('Geovelocity')) {
      username = "travel_anomaly_operator";
      role = "Security Engineer";
      command = "ssh root@gateway-apac-node";
      target = "API-GATEWAY-CORE";
      actionType = "REMOTE_ACCESS";
      ip = "185.220.101.4"; // Tor exit node
      loc = "Moscow, RU (Tor Exit)";
    } else if (type.includes('Maker-Checker') || type.includes('Duty')) {
      username = "bypass_checker_dev";
      role = "Software Developer";
      command = "UPDATE accounts SET balance = balance + 5000000 WHERE id = 9923;";
      target = "DB-CORE-PROD";
      actionType = "DATABASE_QUERY";
      ip = "192.168.100.45";
      loc = "Delhi, IN (Staging subnet)";
    } else if (type.includes('Sovereignty') || type.includes('Compliance')) {
      username = "sovereignty_auditor";
      role = "External Auditor";
      command = "scp -r root@db-core-prod:/data/gdpr-vault /tmp/dump";
      target = "SWIFT-PAYMENT-RAIL";
      actionType = "FILE_TRANSFER";
      ip = "203.0.113.12";
      loc = "Non-EU Cloud Server";
    }
    
    // Call the actual evaluate endpoint
    const res = await evaluateBackendRequest({
      request_id: `req_lab_${Math.random().toString(36).substr(2, 6)}`,
      timestamp: new Date().toISOString(),
      user: {
        username: username,
        role: role,
        department: "Treasury Operations",
        auth_strength: "PASSWORD",
        trusted_device: false,
        ip_address: ip,
        device_id: "DEV-LAB-MOCK"
      },
      action: {
        type: actionType,
        command: command,
        target_system: target,
        criticality: criticality
      },
      context: {
        is_maintenance_window: false,
        change_ticket_id: "CHG-LAB-99",
        active_incident_id: null,
        system_health: "HEALTHY"
      },
      quantum_proof: {
        signature: "quantum_sig_lab",
        algorithms_used: "CRYSTALS-Dilithium6",
        integrity_checksum: "checksum_lab_verify_digest"
      }
    });

    if (res) {
      setTestLog(prev => prev + `\nFINSPARK CORE consensus: ${res.decision} (Agreement: ${res.council_agreement})`);
      setTestLog(prev => prev + `\nConfidence: ${res.governance_confidence}%`);
      setTestLog(prev => prev + `\nMitigation plan: ${res.executive_view.recommended_action}`);
      
      setSimulationLogs(prev => [
        {
          timestamp: new Date().toLocaleTimeString(),
          type: type,
          verdict: `${res.decision} (${res.council_agreement})`,
          confidence: res.governance_confidence
        },
        ...prev
      ]);

      // Map back to global Zustand store Event models
      const agentStatuses = {
        identity: 'approved' as AgentStatus,
        behaviour: 'approved' as AgentStatus,
        compliance: 'approved' as AgentStatus,
        impact: 'approved' as AgentStatus,
        quantum: 'approved' as AgentStatus
      };

      if (res.analyst_view && res.analyst_view.agent_responses) {
        res.analyst_view.agent_responses.forEach((resp: any) => {
          const name = resp.agent_name.toLowerCase();
          let fStatus: AgentStatus = 'approved';
          if (resp.vote === 'BLOCK') fStatus = 'rejected';
          else if (resp.vote === 'ALLOW_APPROVAL') fStatus = 'warning';
          else if (resp.vote === 'ALLOW_SANDBOX') fStatus = 'warning';

          if (name.includes('identity')) agentStatuses.identity = fStatus;
          else if (name.includes('behavior') || name.includes('behaviour')) agentStatuses.behaviour = fStatus;
          else if (name.includes('compliance')) agentStatuses.compliance = fStatus;
          else if (name.includes('business') || name.includes('impact')) agentStatuses.impact = fStatus;
          else if (name.includes('quantum')) agentStatuses.quantum = fStatus;
        });
      }

      let statusStr: 'pending' | 'approved' | 'rejected' = 'approved';
      if (res.decision === 'BLOCK') statusStr = 'rejected';
      else if (res.decision === 'ALLOW_APPROVAL') statusStr = 'pending';

      const newEvent = {
        id: res.request_id,
        timestamp: res.timestamp,
        actor: {
          name: username,
          role: role,
          ip: ip,
          device: "Dynamic Lab Workstation",
          location: loc
        },
        action: command,
        target: target,
        status: statusStr,
        riskScore: 100 - res.governance_confidence,
        financialExposure: 5000000,
        agents: agentStatuses,
        reasoning: [
          res.executive_view.reason,
          res.executive_view.business_impact,
          `Governance directive: ${res.executive_view.recommended_action}`
        ],
        rawVerdict: res
      };

      // Push into state and select it
      useMockStore.getState().addEvent(newEvent);
      useMockStore.getState().setActiveEvent(newEvent);
    } else {
      setTestLog(prev => prev + '\nFailed to connect to backend engine.');
    }
    
    setIsSimulating(false);
  };

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-[#F5F7FA] text-[#0F172A] font-mono text-xs">
      
      {/* Header */}
      <div className="h-20 border-b border-[rgba(20,20,20,0.06)] flex items-center justify-between px-8 shrink-0 bg-white/40">
        <div>
          <h1 className="text-xl font-bold tracking-wider uppercase flex items-center gap-3 text-[#0F172A]">
            <BrainCircuit className="w-6 h-6 text-[#2563EB] animate-pulse" />
            AI Research Laboratory
          </h1>
          <p className="text-[10px] text-[#64748B] uppercase mt-1">Stress testing and adversarial resilience benchmarking.</p>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center gap-1.5 bg-slate-200/50 p-1 rounded-2xl border border-[rgba(20,20,20,0.04)]">
          {(['sandbox', 'stress', 'benchmarks'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 rounded-xl uppercase tracking-wider text-[9px] font-bold transition-all ${
                activeTab === tab 
                  ? 'bg-white text-[#2563EB] shadow-soft border border-[rgba(20,20,20,0.04)]' 
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Attack Generator */}
        <div className="w-[450px] border-r border-[rgba(20,20,20,0.06)] flex flex-col bg-white/30 shrink-0">
          <div className="p-6 border-b border-[rgba(20,20,20,0.06)]">
            <h2 className="text-[10px] font-bold uppercase tracking-widest text-[#64748B] mb-4 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-[#2563EB]" /> Synthetic Attack Generator
            </h2>
            <p className="text-[#64748B] leading-relaxed mb-4 text-[10px] uppercase">
              Inject adversarial threat vectors directly into the CyberArk interceptor segment.
            </p>
            
            <div className="space-y-2">
              <Button 
                onClick={() => triggerSyntheticAttack('Impossible Travel Velocity')} 
                disabled={isSimulating}
                className="w-full bg-[#EF4444]/10 hover:bg-[#EF4444]/25 text-[#EF4444] border border-[#EF4444]/20 py-2.5 font-bold text-xs uppercase tracking-wider rounded-2xl shadow-soft"
              >
                Trigger Geovelocity Probe
              </Button>
              <Button 
                onClick={() => triggerSyntheticAttack('Maker-Checker Bypass')} 
                disabled={isSimulating}
                className="w-full bg-[#F59E0B]/10 hover:bg-[#F59E0B]/25 text-[#F59E0B] border border-[#F59E0B]/20 py-2.5 font-bold text-xs uppercase tracking-wider rounded-2xl shadow-soft"
              >
                Trigger Segregation of Duty Bypass
              </Button>
              <Button 
                onClick={() => triggerSyntheticAttack('Quantum-Sovereignty Breach')} 
                disabled={isSimulating}
                className="w-full bg-[#2563EB]/10 hover:bg-[#2563EB]/25 text-[#2563EB] border border-[#2563EB]/20 py-2.5 font-bold text-xs uppercase tracking-wider rounded-2xl shadow-soft"
              >
                Trigger Sovereignty Compliance Breach
              </Button>
            </div>
          </div>

          {/* Console Log Outputs */}
          <div className="flex-1 p-6 flex flex-col overflow-hidden bg-white/20">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-[#64748B] mb-4 flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-[#2563EB]" /> Simulation Console Output
            </h3>
            <div className="flex-grow bg-slate-900 p-4 border border-[rgba(20,20,20,0.06)] rounded-2xl overflow-y-auto whitespace-pre-wrap font-mono text-[10px] leading-relaxed text-[#10B981] shadow-medium">
              {testLog || 'Ready for simulation sequence injection...'}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="flex-1 p-8 overflow-y-auto bg-slate-100/20">
          <AnimatePresence mode="wait">
            {activeTab === 'sandbox' && (
              <motion.div key="sandbox" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2 text-[#0F172A]">
                    <Database className="w-5 h-5 text-[#2563EB]" />
                    Simulated Interventions Log
                  </h2>
                  <p className="text-[10px] text-[#64748B] uppercase mt-1">Audit ledger of laboratory attack stress runs.</p>
                </div>

                <div className="space-y-3">
                  {simulationLogs.map((log, i) => (
                    <div key={i} className="p-4 bg-white/80 border border-[rgba(20,20,20,0.06)] rounded-2xl flex items-center justify-between hover:border-[#2563EB]/20 transition-all shadow-soft">
                      <div className="flex items-center gap-4">
                        <div className="w-8 h-8 rounded bg-[#EF4444]/10 border border-[#EF4444]/20 flex items-center justify-center font-bold text-[#EF4444]">
                          SIM
                        </div>
                        <div>
                          <div className="text-xs font-bold text-[#0F172A]">{log.type}</div>
                          <div className="text-[9px] text-[#64748B] font-mono">Timestamp: {log.timestamp}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-[#EF4444] font-bold">{log.verdict}</div>
                        <div className="text-[9px] text-[#64748B]">Confidence: {log.confidence}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'stress' && (
              <motion.div key="stress" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2 text-[#0F172A]">
                    <Cpu className="w-5 h-5 text-[#2563EB]" />
                    Model Resilience stress dials
                  </h2>
                  <p className="text-[10px] text-[#64748B] uppercase mt-1">Measuring model degradation metrics under adversarial fuzzer loading.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-5 shadow-soft">
                    <div className="text-[9px] uppercase font-bold text-[#64748B] mb-2">Fuzzing Integrity</div>
                    <div className="text-2xl font-black text-[#10B981]">99.98%</div>
                    <div className="text-[9px] text-[#64748B] mt-1 font-semibold uppercase">Optimal robustness</div>
                  </Card>
                  <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-5 shadow-soft">
                    <div className="text-[9px] uppercase font-bold text-[#64748B] mb-2">Poisoning Detection</div>
                    <div className="text-2xl font-black text-[#10B981]">100.0%</div>
                    <div className="text-[9px] text-[#64748B] mt-1 font-semibold uppercase">Enclave protection active</div>
                  </Card>
                  <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-5 shadow-soft">
                    <div className="text-[9px] uppercase font-bold text-[#64748B] mb-2">Model Drift</div>
                    <div className="text-2xl font-black text-[#2563EB]">&lt; 0.01%</div>
                    <div className="text-[9px] text-[#64748B] mt-1 font-semibold uppercase font-mono">No deviations observed</div>
                  </Card>
                </div>
              </motion.div>
            )}

            {activeTab === 'benchmarks' && (
              <motion.div key="benchmarks" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2 text-[#0F172A]">
                    <ShieldCheck className="w-5 h-5 text-[#2563EB]" />
                    Cybersecurity AI benchmarks
                  </h2>
                  <p className="text-[10px] text-[#64748B] uppercase mt-1">Model accuracy comparison against industry security baselines.</p>
                </div>

                <div className="space-y-3 font-mono text-[10px] text-[#64748B]">
                  <div className="flex justify-between border-b border-slate-100 pb-2">
                    <span>NIST Framework Accuracy</span>
                    <span className="text-[#10B981] font-bold">99.85%</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-100 pb-2">
                    <span>MITRE ATT&CK Mapping rate</span>
                    <span className="text-[#10B981] font-bold">98.42%</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-100 pb-2">
                    <span>RBI Cyber Security Guidelines conformity</span>
                    <span className="text-[#10B981] font-bold">100.0%</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
