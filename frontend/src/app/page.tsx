'use client';

import { useEffect, useState, useRef } from 'react';
import { useMockStore } from '@/store/useMockStore';
import { EnterpriseHealth } from '@/components/mission-control/EnterpriseHealth';
import { AISecurityCouncil } from '@/components/mission-control/AISecurityCouncil';
import { JudgeAIPanel } from '@/components/mission-control/JudgeAIPanel';
import { LiveThreatFeed } from '@/components/mission-control/LiveThreatFeed';
import { RiskTimeline } from '@/components/mission-control/RiskTimeline';
import Link from 'next/link';
import { ArrowRight, Globe, Server, Cpu, Heart, CheckCircle2, Shield, AlertTriangle, Terminal, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface WorldNode {
  name: string;
  category: string;
  status: 'optimal' | 'intercepted' | 'monitoring';
  load: string;
}

const worldNodes: WorldNode[] = [
  { name: 'Core Ledger Core-01', category: 'Core Banking', status: 'optimal', load: '14%' },
  { name: 'ATMs North Subnet', category: 'ATMs', status: 'monitoring', load: '32%' },
  { name: 'UPI Gateway API', category: 'UPI', status: 'intercepted', load: '89%' },
  { name: 'SWIFT Gateway Global', category: 'SWIFT', status: 'optimal', load: '45%' },
  { name: 'Mobile API Endpoints', category: 'Mobile Banking', status: 'monitoring', load: '67%' },
  { name: 'Corporate Netbanking Portal', category: 'Internet Banking', status: 'optimal', load: '22%' },
  { name: 'Visa/MC Payment Rails', category: 'Payment Networks', status: 'optimal', load: '18%' },
  { name: 'Branch Subnets APAC', category: 'Branches', status: 'optimal', load: '5%' },
  { name: 'UPI Merchant Interfaces', category: 'Merchants', status: 'monitoring', load: '58%' },
  { name: 'Employee Active Directory', category: 'Employees', status: 'optimal', load: '12%' },
  { name: 'CyberArk PAM Interceptor', category: 'APIs', status: 'intercepted', load: '95%' },
  { name: 'Cloud Infrastructure (AWS)', category: 'Cloud', status: 'optimal', load: '41%' }
];

interface ThinkingMessage {
  timestamp: string;
  agent: string;
  message: string;
  status: 'pending' | 'success' | 'warning';
}

const thinkingPhrases: ThinkingMessage[] = [
  { timestamp: '12:03:12', agent: 'Identity Agent', message: 'Verifying device fingerprint signatures...', status: 'success' },
  { timestamp: '12:03:13', agent: 'Behavior Agent', message: 'Historical anomaly check initiated...', status: 'warning' },
  { timestamp: '12:03:14', agent: 'Threat Intelligence', message: 'Scanning known cyber attack matrices...', status: 'success' },
  { timestamp: '12:03:15', agent: 'Counterfactual Engine', message: 'Running 12,458 predictive threat scenarios...', status: 'success' },
  { timestamp: '12:03:16', agent: 'Compliance Agent', message: 'Mapping EU-GDPR Article 32 guidelines...', status: 'success' },
  { timestamp: '12:03:18', agent: 'Judge AI', message: 'Summoning AI Security Council consensus...', status: 'pending' }
];

export default function MissionControlPage() {
  const { fetchEvents, liveEvents, activeEvent } = useMockStore();
  const [mounted, setMounted] = useState(false);
  const [thinkingLogs, setThinkingLogs] = useState<ThinkingMessage[]>([]);
  const thinkingContainerRef = useRef<HTMLDivElement | null>(null);

  const selectedEvent = activeEvent || liveEvents[0];

  useEffect(() => {
    setMounted(true);
    fetchEvents();
  }, [fetchEvents]);

  useEffect(() => {
    if (!mounted || !selectedEvent) return;

    // Reset logs whenever the active event changes
    setThinkingLogs([]);

    // Map dynamic phrases from selectedEvent
    const dynamicPhrases: ThinkingMessage[] = (() => {
      if (selectedEvent.rawVerdict && selectedEvent.rawVerdict.analyst_view && selectedEvent.rawVerdict.analyst_view.deliberation_log) {
        return selectedEvent.rawVerdict.analyst_view.deliberation_log.map((log: any) => ({
          timestamp: log.timestamp || new Date().toLocaleTimeString(),
          agent: log.speaker,
          message: log.statement,
          status: log.speaker.toLowerCase().includes('engine') || log.speaker.toLowerCase().includes('judge') ? 'pending' : 'success'
        }));
      }
      
      const actorName = selectedEvent.actor.name;
      const targetName = selectedEvent.target;
      const actType = selectedEvent.action;
      
      return [
        { timestamp: '12:03:12', agent: 'Identity Agent', message: `Verifying device fingerprint signatures for ${actorName}...`, status: 'success' },
        { timestamp: '12:03:13', agent: 'Behavior Agent', message: `Checking historical deviations for command: ${actType}...`, status: 'warning' },
        { timestamp: '12:03:14', agent: 'Threat Intelligence', message: `Scanning vulnerability signatures on ${targetName}...`, status: 'success' },
        { timestamp: '12:03:15', agent: 'Counterfactual Engine', message: `Running 12,458 predictive threat scenarios...`, status: 'success' },
        { timestamp: '12:03:16', agent: 'Compliance Agent', message: `Verifying segregation of duties for ${actorName}...`, status: 'success' },
        { timestamp: '12:03:18', agent: 'Judge AI', message: `Consensus achievement: Verdict resolved to ${selectedEvent.status.toUpperCase()}`, status: 'pending' }
      ];
    })();

    let currentIdx = 0;
    const interval = setInterval(() => {
      if (currentIdx < dynamicPhrases.length) {
        setThinkingLogs(prev => [...prev, dynamicPhrases[currentIdx]]);
        currentIdx++;
      } else {
        clearInterval(interval);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [mounted, selectedEvent]);

  useEffect(() => {
    if (thinkingContainerRef.current) {
      thinkingContainerRef.current.scrollTop = thinkingContainerRef.current.scrollHeight;
    }
  }, [thinkingLogs]);

  if (!mounted) return null;

  return (
    <div className="max-w-[1600px] mx-auto pb-12 space-y-8 px-4 sm:px-8">
      
      {/* Hero Section */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 border-b border-[rgba(20,20,20,0.06)] pb-8 pt-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[9px] tracking-widest font-mono uppercase bg-[#2563EB]/10 text-[#2563EB] border border-[#2563EB]/20 px-2 py-0.5 rounded-full font-bold">
              LAYER 0 COGNITIVE BRAIN
            </span>
            <span className="text-[9px] tracking-widest font-mono uppercase bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20 px-2 py-0.5 rounded-full font-bold">
              OS ONLINE
            </span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-[#0F172A] font-sans">
            FINSPARK CORE
          </h1>
          <p className="text-sm text-[#64748B] font-mono mt-1 uppercase tracking-wide">
            Autonomous Cognitive Banking Defense Operating System
          </p>
        </div>
        <Link 
          href="/investigation"
          className="flex items-center gap-2 bg-[#2563EB] text-white hover:bg-[#2563EB]/95 px-5 py-3 rounded-2xl font-bold text-xs uppercase tracking-wider transition-all shadow-hover"
        >
          Containment Workspace
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Large World Health Canvas */}
      <div className="glass-panel p-8 border border-[rgba(20,20,20,0.06)] bg-white/70 backdrop-blur-xl relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#06B6D4]/5 rounded-full filter blur-3xl pointer-events-none -z-10" />
        
        <div className="flex items-center gap-6">
          <div className="w-24 h-24 rounded-full border-4 border-[#10B981]/10 flex items-center justify-center relative bg-white/80 shadow-soft">
            <div className="absolute inset-2 rounded-full border-2 border-dashed border-[#10B981]/40 animate-spin" style={{ animationDuration: '20s' }} />
            <span className="text-2xl font-black text-[#10B981]">98.4%</span>
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-[#0F172A] tracking-tight">Ecosystem Security Health</h2>
            <p className="text-xs text-[#64748B] font-mono uppercase tracking-wider mt-1">Real-time systemic health assessment</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 w-full md:w-auto">
          <div className="p-4 bg-slate-100/40 rounded-2xl border border-[rgba(20,20,20,0.04)]">
            <div className="text-[10px] uppercase font-bold text-[#64748B] mb-1 font-mono">Protected Assets</div>
            <div className="text-lg font-black text-[#0F172A]">1,543</div>
          </div>
          <div className="p-4 bg-slate-100/40 rounded-2xl border border-[rgba(20,20,20,0.04)]">
            <div className="text-[10px] uppercase font-bold text-[#64748B] mb-1 font-mono">Active Threats</div>
            <div className="text-lg font-black text-[#EF4444]">02</div>
          </div>
          <div className="p-4 bg-slate-100/40 rounded-2xl border border-[rgba(20,20,20,0.04)]">
            <div className="text-[10px] uppercase font-bold text-[#64748B] mb-1 font-mono">AI Agents</div>
            <div className="text-lg font-black text-[#7C3AED]">18</div>
          </div>
          <div className="p-4 bg-slate-100/40 rounded-2xl border border-[rgba(20,20,20,0.04)]">
            <div className="text-[10px] uppercase font-bold text-[#64748B] mb-1 font-mono">Throughput</div>
            <div className="text-lg font-black text-[#2563EB]">14.2k/s</div>
          </div>
        </div>
      </div>

      {/* Two Column Layout: World Model Grid & Live ChatGPT-style Thinking */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Interactive World Model */}
        <div className="lg:col-span-2 glass-panel p-6 border border-[rgba(20,20,20,0.06)] bg-white/70 backdrop-blur-xl">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#2563EB]" />
                Interactive World Model Topology
              </h2>
              <p className="text-[10px] text-[#64748B] uppercase tracking-wide mt-0.5">Real-time state verification across banking endpoints</p>
            </div>
            <div className="text-[9px] font-mono text-[#10B981] flex items-center gap-1.5 bg-[#10B981]/10 px-2.5 py-1 rounded-full border border-[#10B981]/20 font-bold uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-ping" />
              Ecosystem Synced
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {worldNodes.map((node) => (
              <div 
                key={node.name} 
                className="p-4 bg-white/80 border border-[rgba(20,20,20,0.04)] rounded-2xl flex items-center justify-between hover:border-[#2563EB]/20 transition-all shadow-soft"
              >
                <div>
                  <div className="text-[9px] text-[#64748B] font-mono uppercase tracking-widest mb-1">{node.category}</div>
                  <div className="text-xs font-bold text-[#0F172A] truncate max-w-[140px]">{node.name}</div>
                </div>
                <div className="text-right flex flex-col items-end gap-1.5">
                  <div className="text-[9px] font-mono text-[#64748B]">Load: {node.load}</div>
                  <span className={`inline-block w-2.5 h-2.5 rounded-full ${
                    node.status === 'optimal' ? 'bg-[#10B981] shadow-[0_0_10px_rgba(16,185,129,0.3)]' :
                    node.status === 'monitoring' ? 'bg-[#F59E0B] shadow-[0_0_10px_rgba(245,158,11,0.3)] animate-pulse' :
                    'bg-[#EF4444] shadow-[0_0_10px_rgba(239,68,68,0.3)] animate-ping'
                  }`} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live ChatGPT-style Streaming Thinking Panel */}
        <div className="lg:col-span-1 glass-panel p-6 border border-[rgba(20,20,20,0.06)] bg-white/70 backdrop-blur-xl flex flex-col h-[400px]">
          <div className="mb-4 border-b border-[rgba(20,20,20,0.06)] pb-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#7C3AED]" />
              Live Swarm Thinking Terminal
            </h2>
            <p className="text-[10px] text-[#64748B] uppercase tracking-wide mt-0.5">Streaming reasoning model telemetry</p>
          </div>

          <div 
            ref={thinkingContainerRef}
            className="flex-1 overflow-y-auto space-y-4 pr-1 font-mono text-[11px] leading-relaxed scroll-smooth"
          >
            <AnimatePresence>
              {thinkingLogs.map((log, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  className="p-3 bg-slate-100/50 border border-[rgba(20,20,20,0.04)] rounded-xl space-y-1.5 shadow-soft"
                >
                  <div className="flex justify-between items-center border-b border-[rgba(20,20,20,0.04)] pb-1">
                    <span className="text-[#2563EB] font-bold">[{log.agent}]</span>
                    <span className="text-[#64748B]/60 text-[9px]">{log.timestamp}</span>
                  </div>
                  <div className="text-[#0F172A] flex justify-between items-center gap-2">
                    <span>{log.message}</span>
                    {log.status === 'success' && <span className="text-[#10B981] font-bold">✓</span>}
                    {log.status === 'warning' && <span className="text-[#F59E0B] font-bold">⚠</span>}
                    {log.status === 'pending' && <span className="w-2 h-2 bg-[#7C3AED] rounded-full animate-ping" />}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {thinkingLogs.length === 0 && (
              <div className="h-full flex items-center justify-center text-[#64748B]/40 uppercase text-[10px] tracking-widest font-bold">
                Initializing thinking stream...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Swarm Council Consensus debate layout */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 glass-panel p-6 border border-[rgba(20,20,20,0.06)] bg-white/70 backdrop-blur-xl">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-2">
                <Cpu className="w-4 h-4 text-[#2563EB]" />
                Consensus Security Swarm Council
              </h2>
              <p className="text-[10px] text-[#64748B] uppercase tracking-wide mt-0.5">Weighted consensus nodes debating system constraints</p>
            </div>
          </div>
          <AISecurityCouncil />
        </div>
        
        <div className="xl:col-span-1">
          <JudgeAIPanel />
        </div>
      </div>

      {/* Risk timeline lifecycle */}
      <RiskTimeline />

      {/* Live Threat Feed */}
      <LiveThreatFeed />

    </div>
  );
}
