'use client';

import { useMockStore } from '@/store/useMockStore';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ShieldAlert, AlertTriangle, User, Laptop, Server, Code, Gavel, CheckCircle2, XCircle, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import { ApprovalWorkflow } from '@/components/investigation/ApprovalWorkflow';

export function IncidentOverview() {
  const { activeEvent, timeMachineIndex } = useMockStore();
  if (!activeEvent) return null;

  const isBlocked = activeEvent.status === 'rejected';

  // Time Machine step calculations
  const stepsData = [
    { time: '08:30', name: 'MFA Login', status: 'optimal', desc: 'Authentication parameters matched baseline.', risk: 5, confidence: 99 },
    { time: '08:31', name: 'VPN Route', status: 'monitoring', desc: 'Connection routing via non-standard subnet.', risk: 24, confidence: 85 },
    { time: '08:32', name: 'Privilege Check', status: 'monitoring', desc: 'Query escalation parameters detected.', risk: 48, confidence: 70 },
    { time: '08:34', name: 'Stuffing Match', status: 'intercepted', desc: 'Credential reuse patterns flagged by Threat Intel.', risk: 75, confidence: 91 },
    { time: '08:35', name: 'Payment Exec', status: 'intercepted', desc: 'Critical query target initiated.', risk: 90, confidence: 94 },
    { time: '08:35', name: 'Consensus BLOCK', status: 'blocked', desc: 'AI Swarm Council consensus applied.', risk: 98, confidence: 97 }
  ];

  const currentStep = stepsData[timeMachineIndex];
  
  // Interpolated metrics
  const activeRisk = currentStep.risk;
  const predictionConfidence = currentStep.confidence;
  const evidenceStrength = Math.round(activeRisk * 0.95);
  const modelAgreement = timeMachineIndex === 5 ? 96 : 100;
  const uncertainty = 100 - activeRisk;

  // Recovery Checklist progress based on timeMachineIndex
  const recoverySteps = [
    { name: 'Freeze transaction transfer', activeAt: 5 },
    { name: 'Revoke active SSH/Web session', activeAt: 5 },
    { name: 'Rotate backend API Token keys', activeAt: 5 },
    { name: 'Notify Security SOC dispatch', activeAt: 5 },
    { name: 'Generate Verifiable Forensic report', activeAt: 5 }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Causal Attack Timeline Header */}
      <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/70 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] mb-6 flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#2563EB]" />
          Forensic Causal Attack Timeline
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 relative">
          <div className="absolute top-7 left-6 right-6 h-[1.5px] bg-slate-200 -z-10 hidden md:block" />
          {stepsData.map((step, idx) => {
            const isFuture = idx > timeMachineIndex;
            const isCurrent = idx === timeMachineIndex;
            
            return (
              <div 
                key={step.name} 
                className={cn(
                  "p-3 rounded-2xl border text-center transition-all duration-300 shadow-soft",
                  isCurrent ? "bg-[#2563EB]/10 border-[#2563EB] text-[#2563EB]" :
                  isFuture ? "bg-slate-100/40 border-[rgba(20,20,20,0.03)] text-[#64748B]/40" :
                  "bg-white border-slate-200 text-[#10B981]"
                )}
              >
                <div className="text-[9px] font-mono mb-1">{step.time}</div>
                <div className="text-xs font-bold">{step.name}</div>
                <div className="text-[9px] mt-2 line-clamp-2 leading-relaxed opacity-80">{step.desc}</div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Basic Parameters Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="glass-panel col-span-2 border border-[rgba(20,20,20,0.06)] bg-white/70">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
            <CardTitle className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <ShieldAlert className="w-4 h-4 mr-2 text-[#2563EB]" />
              Incident Summary (State Overview)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <h2 className="text-xl font-extrabold tracking-tight mb-6 text-[#0F172A]">
              {isBlocked ? 'Intercepted Privilege Query Incident' : 'Routine DB Query Execution'}
            </h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 font-mono text-xs text-[#64748B]">
              <div>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Actor</div>
                <div className="text-xs font-bold text-[#0F172A]">{activeEvent.actor.name}</div>
                <div className="text-[9px] text-[#64748B] mt-0.5">{activeEvent.actor.role}</div>
              </div>
              <div>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Context</div>
                <div className="text-xs font-semibold text-[#0F172A]">{activeEvent.actor.ip}</div>
                <div className="text-[9px] text-[#64748B] mt-0.5">{activeEvent.actor.device}</div>
              </div>
              <div>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Target Asset</div>
                <div className="text-xs font-semibold text-[#2563EB] truncate max-w-full">{activeEvent.target}</div>
                <div className="text-[9px] text-[#64748B] mt-0.5">Production Database Cluster</div>
              </div>
              <div>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Action Call</div>
                <div className="text-xs text-[#EF4444] bg-[#EF4444]/10 border border-[#EF4444]/20 px-2 py-0.5 rounded-full inline-block truncate max-w-full">
                  {activeEvent.action}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Calibrated Confidence & Threat Metrix */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/70">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
            <CardTitle className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2 text-[#2563EB]" />
              Risk Calibration
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-3 font-mono text-xs">
            <div className="flex justify-between items-center">
              <span className="text-[#64748B]">Prediction Confidence:</span>
              <span className="text-[#0F172A] font-bold">{predictionConfidence}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#64748B]">Evidence Strength:</span>
              <span className="text-[#0F172A] font-bold">{evidenceStrength}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#64748B]">Model Agreement:</span>
              <span className="text-[#0F172A] font-bold">{modelAgreement}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#64748B]">Uncertainty Margin:</span>
              <span className="text-[#0F172A] font-bold">{uncertainty}%</span>
            </div>
            <div className="pt-2 border-t border-slate-200 flex justify-between items-center text-sm font-bold">
              <span className="text-[#EF4444] font-semibold">Active Threat Risk:</span>
              <span className="text-[#EF4444] font-black">{activeRisk}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Swarm Reasoning, Recovery Actions, and Decision DNA */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Swarm Reasoning Log */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/70">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
            <CardTitle className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <Gavel className="w-4 h-4 mr-2 text-[#2563EB]" />
              AI Swarm Consensus Reasoning
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            {activeEvent.reasoning.map((reason, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.15 }}
                className="flex items-start gap-3 p-3 rounded-2xl bg-slate-50 border border-[rgba(20,20,20,0.04)] shadow-soft"
              >
                <div className="mt-0.5"><XCircle className="w-4 h-4 text-[#EF4444] shrink-0" /></div>
                <div className="text-xs text-[#0F172A] font-medium leading-relaxed">{reason}</div>
              </motion.div>
            ))}
          </CardContent>
        </Card>

        {/* Autonomous Recovery Checklist */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/70">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
            <CardTitle className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <ShieldCheck className="w-4 h-4 mr-2 text-[#2563EB]" />
              Autonomous Containment
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-3 font-mono text-xs">
            {recoverySteps.map((step, idx) => {
              const isChecked = timeMachineIndex >= step.activeAt;
              return (
                <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-[rgba(20,20,20,0.04)] shadow-soft">
                  <span className={cn(isChecked ? "text-[#10B981] font-semibold" : "text-[#64748B]/60")}>
                    {isChecked ? '✓' : '☐'} {step.name}
                  </span>
                  <span className={cn("text-[9px] uppercase px-2 py-0.5 rounded-full font-bold", 
                    isChecked ? "bg-[#10B981]/15 text-[#10B981]" : "bg-slate-200/50 text-[#64748B]/50"
                  )}>
                    {isChecked ? 'Enforced' : 'Pending'}
                  </span>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Decision DNA verification */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/70">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
            <CardTitle className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <Laptop className="w-4 h-4 mr-2 text-[#2563EB]" />
              Decision DNA Fingerprint
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-3 font-mono text-[10px] text-[#64748B]">
            <div>
              <div className="font-semibold uppercase text-[#0F172A] mb-1">Decision Hash ID</div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-[rgba(20,20,20,0.04)] truncate select-all">
                FIN-DNA-SHA256-8a73b22e173e6f92cc8e
              </div>
            </div>
            <div>
              <div className="font-semibold uppercase text-[#0F172A] mb-1">Models Used</div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-[rgba(20,20,20,0.04)] select-all text-[#2563EB] font-bold">
                Swarm LLM v4.2 + Crystals-Dilithium6
              </div>
            </div>
            <div>
              <div className="font-semibold uppercase text-[#0F172A] mb-1">Regulatory Citations</div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-[rgba(20,20,20,0.04)] space-y-1">
                <div className="text-[#EF4444] font-semibold">✗ RBI Rule RB-17 (MFA failure)</div>
                <div className="text-[#EF4444] font-semibold">✗ GDPR Article 32 (Geovelocity Anomaly)</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ApprovalWorkflow />
      </div>
    </div>
  );
}

function cn(...inputs: (string | undefined | null | false)[]) {
  return inputs.filter(Boolean).join(" ");
}

function Activity({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
    </svg>
  );
}
