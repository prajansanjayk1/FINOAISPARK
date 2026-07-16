'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Network, Search, Briefcase, Gavel, Play, FileText, CheckCircle2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

const stages = [
  { id: 'intercept', label: 'API Intercept', icon: Network },
  { id: 'investigation', label: 'AI Investigation', icon: Search },
  { id: 'simulation', label: 'Business Simulation', icon: Briefcase },
  { id: 'judgment', label: 'Judge AI Decision', icon: Gavel },
  { id: 'execution', label: 'Execution/Block', icon: Play },
  { id: 'audit', label: 'Ledger Audit', icon: FileText },
];

export function RiskTimeline() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const sequence = async () => {
      setActiveStage(0);
      for (let i = 1; i < stages.length; i++) {
        await new Promise(resolve => setTimeout(resolve, i === 3 ? 3000 : 1500));
        setActiveStage(i);
      }
    };

    sequence();
    const loop = setInterval(sequence, 15000);
    return () => clearInterval(loop);
  }, []);

  return (
    <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/70 shadow-soft">
      <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-white/30">
        <CardTitle className="text-xs font-bold tracking-wider uppercase flex items-center text-[#64748B]">
          <Network className="w-4 h-4 mr-2 text-[#2563EB]" />
          Event Lifecycle
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="flex justify-between items-start relative select-none">
          {/* Connecting Line Background */}
          <div className="absolute top-5 left-6 right-6 h-[2px] bg-slate-200 -z-10" />
          
          {/* Active Line Progress */}
          <motion.div 
            className="absolute top-5 left-6 h-[2px] bg-[#2563EB] -z-10"
            initial={{ width: '0%' }}
            animate={{ width: `${(activeStage / (stages.length - 1)) * 90}%` }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
          />

          {stages.map((stage, idx) => {
            const isActive = idx === activeStage;
            const isPast = idx < activeStage;
            
            return (
              <div key={stage.id} className="flex flex-col items-center relative">
                <motion.div 
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center border mb-3 transition-colors duration-500 shadow-soft",
                    isPast ? "bg-[#2563EB] border-[#2563EB] text-white" :
                    isActive ? "bg-white border-[#2563EB] text-[#2563EB]" :
                    "bg-white border-slate-200 text-[#64748B]"
                  )}
                  animate={isActive ? {
                    boxShadow: ["0px 0px 0px rgba(37,99,235,0)", "0px 0px 15px rgba(37,99,235,0.4)", "0px 0px 0px rgba(37,99,235,0)"]
                  } : {}}
                  transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
                >
                  {isPast ? <CheckCircle2 className="w-5 h-5 text-white" /> : <stage.icon className="w-4 h-4" />}
                </motion.div>
                <div className="text-center w-24">
                  <span className={cn(
                    "text-[9px] font-bold tracking-wider uppercase transition-colors duration-500",
                    (isActive || isPast) ? "text-[#0F172A]" : "text-[#64748B]/60"
                  )}>
                    {stage.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
