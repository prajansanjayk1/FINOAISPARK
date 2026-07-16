'use client';

import { motion } from 'framer-motion';
import { Shield, ShieldAlert, Cpu, Heart } from 'lucide-react';
import { Card } from '@/components/ui/card';

const kpiData = [
  {
    title: 'Global Bank Health',
    value: '97%',
    trend: 'Optimal status',
    icon: Heart,
    color: 'text-[#10B981]',
    bg: 'bg-[#10B981]/10 border-[#10B981]/20',
  },
  {
    title: 'Protected Assets',
    value: '1,543',
    trend: 'Core ledger & APIs',
    icon: Shield,
    color: 'text-[#2563EB]',
    bg: 'bg-[#2563EB]/10 border-[#2563EB]/20',
  },
  {
    title: 'Active Swarm Agents',
    value: '18',
    trend: 'Debating live',
    icon: Cpu,
    color: 'text-[#F59E0B]',
    bg: 'bg-[#F59E0B]/10 border-[#F59E0B]/20',
  },
  {
    title: 'Active Cyber Threats',
    value: '2',
    trend: 'Mitigated by OS',
    icon: ShieldAlert,
    color: 'text-[#EF4444]',
    bg: 'bg-[#EF4444]/10 border-[#EF4444]/20',
  },
];

export function EnterpriseHealth() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {kpiData.map((kpi, idx) => (
        <motion.div
          key={kpi.title}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1, duration: 0.4 }}
        >
          <Card className="glass-panel p-6 border border-[rgba(20,20,20,0.06)] bg-white/70 relative overflow-hidden group shadow-soft">
            <div className="absolute inset-0 bg-gradient-to-br from-[#2563EB]/5 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none" />
            <div className="flex items-start justify-between relative z-10">
              <div>
                <p className="text-[9px] font-bold tracking-wider uppercase text-[#64748B] mb-2">{kpi.title}</p>
                <div className="flex items-baseline gap-2">
                  <h3 className="text-3xl font-extrabold tracking-tight text-[#0F172A]">{kpi.value}</h3>
                  <span className={`text-[9px] font-bold tracking-wide uppercase px-2 py-0.5 rounded-full bg-slate-100 border border-[rgba(20,20,20,0.04)] ${kpi.color}`}>{kpi.trend}</span>
                </div>
              </div>
              <div className={`p-3 rounded-2xl border ${kpi.bg}`}>
                <kpi.icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
            </div>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
