'use client';

import { useMockStore } from '@/store/useMockStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { 
  ArrowLeft, 
  Activity, 
  Network, 
  Box, 
  Cpu, 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight, 
  History,
  Terminal,
  ShieldAlert,
  Sliders,
  Layers
} from 'lucide-react';
import { IncidentOverview } from '@/components/investigation/IncidentOverview';
import { EvidenceExplorer } from '@/components/evidence/EvidenceExplorer';
import { ExecutionSandbox } from '@/components/sandbox/ExecutionSandbox';
import { DigitalTwin } from '@/components/twin/DigitalTwin';
import { AICopilot } from '@/components/investigation/AICopilot';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useState, useEffect } from 'react';

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

const views = [
  { id: 'overview', label: 'Overview', icon: ShieldAlert },
  { id: 'evidence', label: 'Causal Graph', icon: Network },
  { id: 'impact', label: 'Simulation', icon: Box },
  { id: 'twin', label: 'Digital Twin', icon: Cpu },
] as const;

const timeSteps = [
  { time: '08:30', event: 'MFA Login verified', desc: 'Authorized credential validation complete.' },
  { time: '08:31', event: 'VPN Subnet detected', desc: 'Impossible travel delta triggered.' },
  { time: '08:32', event: 'Privilege Query check', desc: 'Unusual query target audit.' },
  { time: '08:34', event: 'Stuffing pattern matching', desc: 'Credential reusing heuristics.' },
  { time: '08:35', event: 'Critical transaction call', desc: 'Maker-checker override required.' },
  { time: '08:35', event: 'Consensus BLOCK applied', desc: 'Asset containment executed.' }
];

export function IncidentWorkspace() {
  const { activeEvent, setActiveEvent, investigationView, setInvestigationView, timeMachineIndex, setTimeMachineIndex } = useMockStore();
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeExplainTier, setActiveExplainTier] = useState<string>('business');

  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeMachineIndex((timeMachineIndex + 1) % 6);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, timeMachineIndex, setTimeMachineIndex]);

  if (!activeEvent) return null;

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-[#F5F7FA] text-[#0F172A]">
      
      {/* Workspace Subheader */}
      <header className="h-16 border-b border-[rgba(20,20,20,0.06)] flex items-center justify-between px-6 shrink-0 bg-white/60 backdrop-blur-md relative z-20">
        <div className="flex items-center gap-6">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setActiveEvent(null)}
            className="text-[#64748B] hover:text-[#0F172A] hover:bg-black/5 rounded-xl font-bold uppercase tracking-wider text-[10px]"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Queue
          </Button>
          <div className="h-6 w-px bg-slate-200" />
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-[#2563EB] bg-[#2563EB]/10 px-2 py-0.5 rounded-full border border-[#2563EB]/20 font-bold">
              {activeEvent.id}
            </span>
            <span className={cn(
              "text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border",
              activeEvent.status === 'rejected' ? 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30' :
              activeEvent.status === 'approved' ? 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/30' :
              'bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30'
            )}>
              {activeEvent.status === 'rejected' ? 'Blocked' : activeEvent.status === 'approved' ? 'Approved' : 'Evaluating'}
            </span>
          </div>
        </div>

        {/* Dynamic Navigation Tabs */}
        <div className="flex items-center gap-1 bg-slate-200/50 p-1 rounded-2xl border border-[rgba(20,20,20,0.04)]">
          {views.map(view => (
            <button
              key={view.id}
              onClick={() => setInvestigationView(view.id as any)}
              className={cn(
                "flex items-center gap-2 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all duration-200",
                investigationView === view.id 
                  ? "bg-white text-[#2563EB] shadow-soft border border-[rgba(20,20,20,0.04)]" 
                  : "text-[#64748B] hover:text-[#0F172A] hover:bg-white/50"
              )}
            >
              <view.icon className="w-3.5 h-3.5" />
              {view.label}
            </button>
          ))}
        </div>
      </header>

      {/* Forensic Time Machine Control Strip */}
      <div className="h-14 bg-white/40 border-b border-[rgba(20,20,20,0.06)] px-6 flex items-center gap-6 shrink-0 select-none">
        <span className="text-[9px] uppercase font-bold tracking-widest text-[#2563EB] font-mono shrink-0 flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#2563EB] animate-pulse" />
          Time Machine Replay
        </span>
        
        <div className="flex items-center gap-1.5 shrink-0">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-8 h-8 rounded-full border border-[rgba(20,20,20,0.06)] hover:bg-black/5"
          >
            {isPlaying ? <Pause className="w-4 h-4 text-[#2563EB]" /> : <Play className="w-4 h-4 text-[#2563EB]" />}
          </Button>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => { setIsPlaying(false); setTimeMachineIndex(0); }}
            className="w-8 h-8 rounded-full border border-[rgba(20,20,20,0.06)] hover:bg-black/5"
          >
            <RotateCcw className="w-4 h-4 text-[#64748B]" />
          </Button>
        </div>

        {/* Timeline Slider Scrub */}
        <div className="flex-1 flex items-center gap-4">
          <input 
            type="range" 
            min="0" 
            max="5" 
            value={timeMachineIndex} 
            onChange={(e) => { setIsPlaying(false); setTimeMachineIndex(parseInt(e.target.value)); }}
            className="w-full accent-[#2563EB] bg-slate-200 h-1.5 rounded-lg cursor-pointer"
          />
          <div className="flex justify-between w-full max-w-[450px] text-[9px] font-mono text-[#64748B] shrink-0 uppercase">
            <span className={cn(timeMachineIndex === 0 && "text-[#2563EB] font-bold")}>08:30 (Login)</span>
            <span className={cn(timeMachineIndex === 2 && "text-[#F59E0B] font-bold")}>08:32 (Query)</span>
            <span className={cn(timeMachineIndex === 5 && "text-[#EF4444] font-bold")}>08:35 (Verdict)</span>
          </div>
        </div>
      </div>

      {/* VS Code + Figma resizable Three-Column layout */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Column: Forensic Timeline Tree */}
        <aside className="w-80 border-r border-[rgba(20,20,20,0.06)] bg-white/30 flex flex-col shrink-0 select-none">
          <div className="p-4 border-b border-[rgba(20,20,20,0.06)] bg-white/40 flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-2">
              <History className="w-4 h-4 text-[#2563EB]" />
              Replay Timeline
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {timeSteps.map((step, idx) => {
              const isFuture = idx > timeMachineIndex;
              const isCurrent = idx === timeMachineIndex;
              
              return (
                <div 
                  key={step.event}
                  onClick={() => { setIsPlaying(false); setTimeMachineIndex(idx); }}
                  className={cn(
                    "p-3 rounded-2xl border transition-all duration-200 cursor-pointer text-left shadow-soft",
                    isCurrent ? "bg-white border-[#2563EB] text-[#0F172A]" :
                    isFuture ? "bg-slate-100/40 border-[rgba(20,20,20,0.03)] text-[#64748B]/40" :
                    "bg-white border-slate-200 text-[#64748B]"
                  )}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[9px] font-mono font-bold">{step.time}</span>
                    {isCurrent && <span className="w-1.5 h-1.5 bg-[#2563EB] rounded-full animate-ping" />}
                  </div>
                  <div className="text-xs font-bold">{step.event}</div>
                  <p className="text-[10px] leading-relaxed mt-1">{step.desc}</p>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Center Canvas: Interactive Investigation Canvas */}
        <main className="flex-1 relative overflow-hidden bg-white/10">
          <AnimatePresence mode="wait">
            {investigationView === 'overview' && (
              <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="h-full overflow-y-auto">
                <IncidentOverview />
              </motion.div>
            )}
            {investigationView === 'evidence' && (
              <motion.div key="evidence" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full">
                <EvidenceExplorer />
              </motion.div>
            )}
            {investigationView === 'impact' && (
              <motion.div key="impact" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.98 }} className="h-full overflow-y-auto">
                <ExecutionSandbox />
              </motion.div>
            )}
            {investigationView === 'twin' && (
              <motion.div key="twin" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full">
                <DigitalTwin />
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Right Column: AI Assistant & Explainability Pyramid */}
        <aside className="w-[360px] border-l border-[rgba(20,20,20,0.06)] bg-white/40 flex flex-col shrink-0 overflow-y-auto p-4 space-y-4">
          
          {/* Explainability Pyramid Panel */}
          <div className="p-4 bg-white border border-[rgba(20,20,20,0.06)] rounded-3xl space-y-4 shadow-soft">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#2563EB]" />
              Explainability Pyramid
            </div>

            <div className="flex flex-col gap-1.5 font-mono text-[10px] uppercase text-center font-bold">
              {/* Business Summary */}
              <button 
                onClick={() => setActiveExplainTier('business')}
                className={cn(
                  "p-2 rounded-xl border transition-all",
                  activeExplainTier === 'business' ? 'bg-[#2563EB]/10 border-[#2563EB] text-[#2563EB]' : 'bg-slate-100/50 border-[rgba(20,20,20,0.04)] text-[#64748B]'
                )}
              >
                Business Summary
              </button>
              
              <div className="text-[#64748B]/40 text-center">▼</div>

              {/* Evidence Signals */}
              <button 
                onClick={() => setActiveExplainTier('evidence')}
                className={cn(
                  "p-2 rounded-xl border transition-all",
                  activeExplainTier === 'evidence' ? 'bg-[#2563EB]/10 border-[#2563EB] text-[#2563EB]' : 'bg-slate-100/50 border-[rgba(20,20,20,0.04)] text-[#64748B]'
                )}
              >
                Evidence Signals
              </button>

              <div className="text-[#64748B]/40 text-center">▼</div>

              {/* Swarm Debate */}
              <button 
                onClick={() => setActiveExplainTier('debate')}
                className={cn(
                  "p-2 rounded-xl border transition-all",
                  activeExplainTier === 'debate' ? 'bg-[#2563EB]/10 border-[#2563EB] text-[#2563EB]' : 'bg-slate-100/50 border-[rgba(20,20,20,0.04)] text-[#64748B]'
                )}
              >
                AI Swarm Debate
              </button>

              <div className="text-[#64748B]/40 text-center">▼</div>

              {/* Technical Logs */}
              <button 
                onClick={() => setActiveExplainTier('logs')}
                className={cn(
                  "p-2 rounded-xl border transition-all",
                  activeExplainTier === 'logs' ? 'bg-[#2563EB]/10 border-[#2563EB] text-[#2563EB]' : 'bg-slate-100/50 border-[rgba(20,20,20,0.04)] text-[#64748B]'
                )}
              >
                Technical Logs
              </button>
            </div>

            {/* Dynamic explain tier description */}
            <div className="p-3 bg-slate-50 border border-[rgba(20,20,20,0.04)] rounded-2xl text-[10px] leading-relaxed text-[#64748B] font-mono">
              <AnimatePresence mode="wait">
                {activeExplainTier === 'business' && (
                  <motion.div key="b" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="font-bold text-[#0F172A] mb-1">Business Impact:</div>
                    Financial exposure categorized as CRITICAL. Downstream risk simulation indicates possible data residency violations.
                  </motion.div>
                )}
                {activeExplainTier === 'evidence' && (
                  <motion.div key="e" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="font-bold text-[#0F172A] mb-1">Evidence Signals:</div>
                    Device spoofing heuristics verified (100% profile mismatch). Non-residential VPN routing detected.
                  </motion.div>
                )}
                {activeExplainTier === 'debate' && (
                  <motion.div key="d" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="font-bold text-[#0F172A] mb-1">Council Debate:</div>
                    Compliance & Business agents voted BLOCK. Identity verified MFA parameters but was overruled.
                  </motion.div>
                )}
                {activeExplainTier === 'logs' && (
                  <motion.div key="l" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="font-bold text-[#0F172A] mb-1">Technical Payload:</div>
                    Query: DROP TABLE prod_transactions_eu; IP: 192.168.45.12. Dilithium quantum checksum checks verified.
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Copilot Assistant sidebar */}
          <AICopilot />
        </aside>

      </div>
    </div>
  );
}
