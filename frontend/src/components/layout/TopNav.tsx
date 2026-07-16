'use client';

import { useState, useEffect } from 'react';
import { Bell, Search, Hexagon, ShieldAlert, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useMockStore } from '@/store/useMockStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

const pathToLabel: Record<string, string> = {
  '/': 'Mission Control',
  '/council': 'AI Security Council',
  '/investigation': 'Investigations',
  '/intelligence': 'AI Lab Sandbox',
  '/governance': 'Governance & Policy',
  '/reports': 'Reports & Analytics',
  '/admin': 'Administration',
};

export function TopNav() {
  const pathname = usePathname();
  const label = pathToLabel[pathname] || 'Mission Control';
  const [showNotifications, setShowNotifications] = useState(false);
  const { liveEvents } = useMockStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="h-16 flex items-center justify-between px-8 border-b border-[rgba(20,20,20,0.06)] bg-white/40 backdrop-blur-xl sticky top-0 z-40">
      
      {/* Contextual Breadcrumbs */}
      <div className="flex items-center gap-3 select-none">
        <Hexagon className="w-5 h-5 text-[#2563EB]" />
        <span className="text-[#64748B] text-xs font-semibold uppercase tracking-wider">FINSPARK CORE</span>
        <span className="text-[#64748B]/40">/</span>
        <motion.span 
          key={label}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-[#0F172A] font-bold text-xs uppercase tracking-wider font-sans"
        >
          {label}
        </motion.span>
      </div>

      {/* Global Actions */}
      <div className="flex items-center gap-6">
        {/* Global Search */}
        <div className="relative group">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-[#2563EB] transition-colors" />
          <input 
            type="text" 
            placeholder="Search IPs, nodes, or transaction IDs..." 
            className="w-80 h-9 bg-slate-100/60 border border-[rgba(20,20,20,0.06)] rounded-xl pl-9 pr-4 text-xs font-mono focus:outline-none focus:border-[#2563EB]/40 focus:ring-1 focus:ring-[#2563EB]/20 transition-all placeholder:text-[#64748B]/60 text-[#0F172A]"
          />
        </div>
        
        {/* AI Operating State */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-success/10 border border-success/20 text-success rounded-full text-[10px] font-mono font-bold uppercase tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-ping" />
          Cognitive Core: Active
        </div>

        {/* Notifications Hub */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-[#64748B] hover:text-[#0F172A] transition-colors bg-slate-100/60 hover:bg-slate-200/60 rounded-full border border-[rgba(20,20,20,0.04)]"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-[#EF4444] rounded-full border border-white"></span>
          </button>

          <AnimatePresence>
            {showNotifications && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowNotifications(false)} />
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 top-full mt-3 w-96 bg-white/95 backdrop-blur-2xl border border-[rgba(20,20,20,0.08)] rounded-3xl shadow-large z-50 overflow-hidden"
                >
                  <div className="p-4 border-b border-[rgba(20,20,20,0.06)] flex items-center justify-between bg-slate-50/80">
                    <h3 className="font-bold text-xs uppercase tracking-wider text-[#0F172A]">Core Event alerts</h3>
                    <span className="text-[10px] uppercase font-bold text-[#2563EB] px-2 py-0.5 rounded bg-[#2563EB]/10">
                      {liveEvents.length} Active
                    </span>
                  </div>
                  <div className="max-h-[350px] overflow-y-auto">
                    {liveEvents.map((evt, i) => (
                      <div key={evt.id} className="p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors flex gap-3 items-start cursor-pointer">
                        <div className="mt-0.5">
                          {evt.status === 'rejected' ? <ShieldAlert className="w-4 h-4 text-destructive" /> : 
                           evt.status === 'approved' ? <CheckCircle2 className="w-4 h-4 text-success" /> : 
                           <AlertTriangle className="w-4 h-4 text-warning" />}
                        </div>
                        <div>
                          <div className="text-xs font-bold mb-1 text-[#0F172A]">
                            {evt.status === 'rejected' ? 'AI Intercept Enforced' : 'Access Request Cleared'}
                          </div>
                          <div className="text-[10px] text-[#64748B] mb-2 leading-relaxed">
                            {evt.actor.name} attempted <span className="font-mono text-[#2563EB]">{evt.action}</span> on {evt.target}.
                          </div>
                          <div className="text-[9px] text-[#64748B]/60 font-mono">
                            {mounted ? new Date(evt.timestamp).toLocaleTimeString() : '--:--:--'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {/* User Card */}
        <div className="flex items-center gap-3 pl-6 border-l border-[rgba(20,20,20,0.06)]">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-bold text-[#0F172A] leading-none mb-1">M. Wong</div>
            <div className="text-[9px] text-[#64748B] uppercase tracking-wider font-semibold font-mono">L3 SOC Supervisor</div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-[#2563EB] font-bold border border-[rgba(20,20,20,0.06)]">
            MW
          </div>
        </div>
      </div>
      
    </div>
  );
}
