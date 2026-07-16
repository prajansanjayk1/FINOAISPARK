'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { FileCheck, UserPlus, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useMockStore } from '@/store/useMockStore';
import { motion } from 'framer-motion';

export function ApprovalWorkflow() {
  const { activeEvent } = useMockStore();

  return (
    <Card className="glass-panel h-full flex flex-col border border-[rgba(20,20,20,0.06)] bg-white/70">
      <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
        <CardTitle className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center">
          <FileCheck className="w-4 h-4 mr-2 text-[#2563EB]" />
          Human-AI Consensus Workflow
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 flex-1 flex flex-col justify-between space-y-6">
        
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-full bg-[#2563EB]/10 border border-[#2563EB]/25 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-[#2563EB]" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#0F172A]">AI Swarm Adjudication</div>
              <div className="text-[10px] text-[#EF4444] font-medium">Rejected automatically by CBDOS Judge</div>
            </div>
            <div className="ml-auto text-[10px] text-[#64748B]/60 font-mono">
              {activeEvent ? new Date(activeEvent.timestamp).toLocaleTimeString() : '--:--:--'}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-full bg-[#F59E0B]/10 border border-[#F59E0B]/25 flex items-center justify-center">
              <span className="w-2 h-2 rounded-full bg-[#F59E0B] animate-ping" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#0F172A]">L2 SOC Analyst Review</div>
              <div className="text-[10px] text-[#F59E0B] font-medium">Awaiting override or containment confirmation</div>
            </div>
          </div>

          <div className="flex items-center gap-4 opacity-40">
            <div className="w-8 h-8 rounded-full bg-slate-100 border border-[rgba(20,20,20,0.06)] flex items-center justify-center">
              <span className="w-2 h-2 rounded-full bg-[#64748B]" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#0F172A]">CISO Escalation</div>
              <div className="text-[10px] text-[#64748B] font-medium">Override protocol standby</div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex gap-3">
          <Button variant="default" className="w-full bg-[#2563EB] hover:bg-[#2563EB]/95 text-white shadow-soft text-xs font-bold uppercase tracking-wider rounded-2xl py-2.5">
            Confirm Threat & Isolate Asset
          </Button>
          <Button variant="outline" className="w-full border-[rgba(20,20,20,0.06)] hover:bg-slate-50 text-[#0F172A] text-xs font-bold uppercase tracking-wider rounded-2xl py-2.5">
            <UserPlus className="w-4 h-4 mr-2" />
            Request CISO Override
          </Button>
        </div>

      </CardContent>
    </Card>
  );
}
