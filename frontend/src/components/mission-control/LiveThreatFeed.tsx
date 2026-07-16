'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useMockStore } from '@/store/useMockStore';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { AlertCircle, CheckCircle2, Shield, XCircle } from 'lucide-react';

const statusIcons = {
  approved: <CheckCircle2 className="w-4 h-4 text-success" />,
  rejected: <XCircle className="w-4 h-4 text-destructive" />,
  pending: <AlertCircle className="w-4 h-4 text-warning" />,
};

export function LiveThreatFeed() {
  const { liveEvents } = useMockStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <Card className="glass-panel h-[400px] flex flex-col border border-[rgba(20,20,20,0.06)] bg-white/70 shadow-soft">
      <CardHeader className="pb-3 border-b border-[rgba(20,20,20,0.06)] bg-white/30">
        <CardTitle className="text-xs font-bold tracking-wider uppercase flex items-center text-[#64748B]">
          <Shield className="w-4 h-4 mr-2 text-[#2563EB]" />
          Live Threat Feed
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto p-0">
        <div className="flex flex-col">
          {liveEvents.map((event, idx) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05, duration: 0.3 }}
              className="flex items-center justify-between p-4 border-b border-slate-100 hover:bg-slate-100/40 transition-colors cursor-pointer group"
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{statusIcons[event.status]}</div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-[#0F172A]">{event.action}</span>
                    <span className="text-[9px] text-[#64748B] font-mono bg-slate-100 border border-[rgba(20,20,20,0.04)] px-2 py-0.5 rounded-full font-bold">
                      {event.id}
                    </span>
                  </div>
                  <div className="text-[10px] text-[#64748B] flex items-center gap-2">
                    <span>{event.actor.name}</span>
                    <span>•</span>
                    <span className="font-mono text-[#2563EB] font-bold">{event.target}</span>
                  </div>
                </div>
              </div>
              <div className="text-right font-mono text-[10px]">
                <div className="text-[#64748B] mb-1">
                  {mounted ? new Date(event.timestamp).toLocaleTimeString() : '--:--:--'}
                </div>
                {event.status === 'rejected' && (
                  <span className="text-[9px] text-[#EF4444] font-bold bg-[#EF4444]/10 border border-[#EF4444]/20 px-2 py-0.5 rounded-full">
                    BLOCKED
                  </span>
                )}
                {event.status === 'approved' && (
                  <span className="text-[9px] text-[#10B981] font-bold bg-[#10B981]/10 border border-[#10B981]/20 px-2 py-0.5 rounded-full">
                    CLEARED
                  </span>
                )}
                {event.status === 'pending' && (
                  <span className="text-[9px] text-[#F59E0B] font-bold bg-[#F59E0B]/10 border border-[#F59E0B]/20 px-2 py-0.5 rounded-full">
                    ESCALATED
                  </span>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
