'use client';

import { useMockStore } from '@/store/useMockStore';
import { AISecurityCouncil } from '@/components/mission-control/AISecurityCouncil';
import { JudgeAIPanel } from '@/components/mission-control/JudgeAIPanel';
import { Card } from '@/components/ui/card';
import { Network, ArrowRight, MessageSquare, Terminal } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function CouncilPage() {
  const { liveEvents, activeEvent, fetchEvents } = useMockStore();
  const selectedEvent = activeEvent || liveEvents[0];
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetchEvents();
  }, [fetchEvents]);

  if (!mounted) return null;

  // Extract debate logs
  const debateLogs = selectedEvent?.rawVerdict?.analyst_view?.deliberation_log || [
    { speaker: "Identity Agent", statement: "MFA verified successfully via biometric match (Confidence: 99.8%)" },
    { speaker: "Behavior Agent", statement: "Warning: Request originates from non-standard geographic IP (Confidence: 75.2%)" },
    { speaker: "Compliance Agent", statement: "CRITICAL: Data sovereignty violation detected for EU-GDPR target." }
  ];

  return (
    <div className="max-w-[1600px] mx-auto pb-12 p-8 h-full flex flex-col space-y-6 bg-[#F5F7FA] text-[#0F172A] font-mono text-xs">
      {/* Header */}
      <div className="flex justify-between items-end border-b border-[rgba(20,20,20,0.06)] pb-6 bg-white/30">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#0F172A] mb-1 flex items-center gap-3">
            <Network className="w-8 h-8 text-[#2563EB]" />
            Swarm Council Debate
          </h1>
          <p className="text-sm text-[#64748B]">
            Multi-agent weighted consensus voting and active debate transcripts.
          </p>
        </div>
        <Link 
          href="/investigation"
          className="flex items-center gap-2 bg-[#2563EB] text-white px-4 py-2.5 rounded-2xl font-bold text-xs uppercase tracking-wider hover:bg-[#2563EB]/95 transition-all shadow-soft"
        >
          Containment Workspace
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 flex-grow">
        <div className="xl:col-span-3 flex flex-col h-full space-y-6">
          {/* Swarm Neural SVG Network */}
          <Card className="glass-panel p-6 border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-6 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#2563EB]" />
              Swarm Nodes connection matrix
            </h3>
            <AISecurityCouncil />
          </Card>
          
          {/* Deliberation Log */}
          <Card className="glass-panel p-6 border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft flex-1">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-6 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-[#2563EB]" />
              Consensus Debate Transcript Logs
            </h3>
            
            <div className="space-y-4 font-mono text-xs max-h-[350px] overflow-y-auto pr-2">
              {debateLogs.map((log: any, idx: number) => (
                <div key={idx} className="flex gap-4 border-b border-slate-100 pb-3 items-start hover:bg-slate-100/40 p-2 rounded-xl transition-all cursor-pointer">
                  <span className="text-[#2563EB] font-bold w-36 shrink-0">[{log.speaker}]</span>
                  <span className="text-[#0F172A] leading-relaxed">{log.statement}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
        
        <div className="xl:col-span-1 h-full">
          <JudgeAIPanel />
        </div>
      </div>
    </div>
  );
}
