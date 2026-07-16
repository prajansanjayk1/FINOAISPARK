'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Gavel, CheckCircle2, XCircle, Shield, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

import { useMockStore } from '@/store/useMockStore';

type JudgeState = 'idle' | 'waiting' | 'judging' | 'approved' | 'rejected' | 'pending';

export function JudgeAIPanel() {
  const { liveEvents, activeEvent } = useMockStore();
  const selectedEvent = activeEvent || liveEvents[0];
  const isBackendData = selectedEvent && selectedEvent.id.startsWith('req_');

  const [state, setState] = useState<JudgeState>('idle');

  useEffect(() => {
    if (isBackendData && selectedEvent) {
      setState(selectedEvent.status);
      return;
    }

    const sequence = async () => {
      setState('waiting');
      setTimeout(() => setState('judging'), 6500); // After other agents finish
      setTimeout(() => setState('rejected'), 9000); // Final decision
    };

    sequence();
    const loop = setInterval(sequence, 15000);

    return () => clearInterval(loop);
  }, [isBackendData, selectedEvent]);

  // Derived variables for backend rendering
  const isApproved = state === 'approved';
  const isRejected = state === 'rejected';
  const isPending = state === 'pending';

  return (
    <Card className={cn(
      "glass-panel relative overflow-hidden transition-all duration-700 min-h-[400px] flex flex-col border border-[rgba(20,20,20,0.06)] bg-white/70 shadow-soft",
      isRejected && "border-destructive/30",
      isApproved && "border-success/30",
      isPending && "border-warning/30"
    )}>
      
      {/* Dynamic Background Pulse for active states */}
      <AnimatePresence>
        {(state === 'judging' || state === 'waiting') && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-[#2563EB]/5 animate-pulse pointer-events-none"
          />
        )}
      </AnimatePresence>

      <div className="p-6 border-b border-[rgba(20,20,20,0.06)] flex items-center justify-between z-10 relative bg-white/30">
        <div className="flex items-center gap-3">
          <div className={cn(
            "p-3 rounded-2xl transition-colors duration-700",
            state === 'idle' && "bg-slate-100 text-[#64748B]",
            (state === 'waiting' || state === 'judging') && "bg-[#2563EB]/10 text-[#2563EB] animate-pulse",
            isApproved && "bg-[#10B981]/10 text-[#10B981]",
            isRejected && "bg-[#EF4444]/10 text-[#EF4444]",
            isPending && "bg-[#F59E0B]/10 text-[#F59E0B]"
          )}>
            <Gavel className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-extrabold tracking-tight text-[#0F172A] flex items-center gap-2">
              Judge AI 
              <span className="text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full bg-slate-100 text-[#64748B] border border-[rgba(20,20,20,0.04)] font-mono">
                Arbitrator
              </span>
            </h2>
            <p className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold font-mono">Final Decision Node</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[9px] uppercase tracking-widest text-[#64748B] font-bold mb-1">Status</div>
          <div className="text-xs font-mono font-bold">
            {state === 'idle' && <span className="text-[#64748B]">Standby</span>}
            {state === 'waiting' && <span className="text-[#2563EB] animate-pulse">Awaiting Council...</span>}
            {state === 'judging' && <span className="text-[#2563EB] animate-pulse">Debating...</span>}
            {isApproved && <span className="text-[#10B981]">Enforce Clearance</span>}
            {isRejected && <span className="text-[#EF4444]">Enforce Block</span>}
            {isPending && <span className="text-[#F59E0B]">Escalate Request</span>}
          </div>
        </div>
      </div>

      <CardContent className="flex-1 p-6 z-10 relative flex flex-col justify-center bg-white/10">
        <AnimatePresence mode="wait">
          {state === 'waiting' && (
            <motion.div 
              key="waiting"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              className="text-center"
            >
              <Shield className="w-12 h-12 text-[#2563EB]/20 mx-auto mb-4 animate-pulse" />
              <p className="text-xs text-[#64748B] font-mono uppercase tracking-wider">Listening to active streams...</p>
            </motion.div>
          )}

          {state === 'judging' && (
            <motion.div 
              key="judging"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              className="text-center"
            >
              <div className="w-14 h-14 mx-auto mb-6 relative">
                <div className="absolute inset-0 border border-[#2563EB]/30 rounded-full animate-ping" />
                <div className="absolute inset-2 border-2 border-dashed border-[#2563EB]/60 rounded-full animate-spin" style={{ animationDuration: '3s' }} />
                <Gavel className="w-5 h-5 text-[#2563EB] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <h3 className="text-sm font-extrabold text-[#0F172A] mb-1 uppercase tracking-wider">Evaluating Consensus Matrix</h3>
              <p className="text-[10px] text-[#64748B] font-mono uppercase tracking-wide">
                Weighing policy thresholds...
              </p>
            </motion.div>
          )}

          {isRejected && selectedEvent && (
            <motion.div 
              key="rejected"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4 text-left"
            >
              <div className="flex items-start gap-4">
                <XCircle className="w-10 h-10 text-[#EF4444] shrink-0" />
                <div>
                  <h3 className="text-sm font-extrabold text-[#EF4444] mb-1 tracking-wider uppercase">Enforce Containment</h3>
                  <p className="text-xs text-[#0F172A]/90 leading-relaxed">
                    The requested <span className="font-mono bg-slate-100 px-1.5 rounded border border-[rgba(20,20,20,0.04)] text-[#2563EB] font-bold">{selectedEvent.action}</span> action on <span className="font-mono text-[#2563EB]/80">{selectedEvent.target}</span> has been rejected by the AI Security Council. 
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 p-3.5 rounded-2xl bg-slate-50 border border-[rgba(20,20,20,0.06)] shadow-soft font-mono">
                <div>
                  <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Violations</div>
                  <ul className="text-[10px] text-[#EF4444] space-y-0.5">
                    {selectedEvent.reasoning.slice(0, 2).map((r, i) => (
                      <li key={i} className="truncate">✗ {r.split('.')[0]}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Mitigation Plan</div>
                  <div className="text-[10px] text-[#0F172A] flex items-center gap-1.5 mt-1 font-semibold uppercase">
                    <AlertTriangle className="w-3.5 h-3.5 text-[#F59E0B] shrink-0" />
                    Block & Quarantined
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {isApproved && selectedEvent && (
            <motion.div 
              key="approved"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4 text-left"
            >
              <div className="flex items-start gap-4">
                <CheckCircle2 className="w-10 h-10 text-[#10B981] shrink-0" />
                <div>
                  <h3 className="text-sm font-extrabold text-[#10B981] mb-1 tracking-wider uppercase">Enforce Access Clearance</h3>
                  <p className="text-xs text-[#0F172A]/90 leading-relaxed">
                    The requested <span className="font-mono bg-slate-100 px-1.5 rounded border border-[rgba(20,20,20,0.04)] text-[#2563EB] font-bold">{selectedEvent.action}</span> action on <span className="font-mono text-[#2563EB]/80">{selectedEvent.target}</span> has been approved. 
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 p-3.5 rounded-2xl bg-slate-50 border border-[rgba(20,20,20,0.06)] shadow-soft font-mono">
                <div>
                  <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Compliance Check</div>
                  <div className="text-[10px] text-[#10B981] mt-1 font-semibold uppercase">
                    ✓ Policies verified
                  </div>
                </div>
                <div>
                  <div className="text-[9px] uppercase tracking-wider text-[#64748B] font-bold mb-1">Mitigation Status</div>
                  <div className="text-[10px] text-[#10B981] flex items-center gap-1.5 mt-1 font-semibold uppercase">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981] shrink-0" />
                    Bypass containment
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}
