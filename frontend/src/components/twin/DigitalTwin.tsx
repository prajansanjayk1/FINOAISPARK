'use client';

import { useMemo, useState, useEffect } from 'react';
import { ReactFlow, Background, Controls, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useMockStore } from '@/store/useMockStore';
import { Server, Database, Globe, Network, Cpu, ShieldAlert, Heart, Calendar, Zap, ArrowRight } from 'lucide-react';
import { Card } from '@/components/ui/card';

const customTwinStyles = {
  background: 'rgba(255, 255, 255, 0.85)',
  color: '#0F172A',
  border: '1px solid rgba(20,20,20,0.06)',
  borderRadius: '24px',
  padding: '16px',
  boxShadow: '0 8px 32px 0 rgba(15,23,42,0.04)',
  backdropFilter: 'blur(20px)',
  fontSize: '12px',
  minWidth: '220px',
  display: 'flex',
  flexDirection: 'column' as const,
  gap: '12px'
};

const TwinNode = ({ data }: { data: any }) => {
  const Icon = data.icon;
  const isCompromised = data.status === 'compromised';
  const isAtRisk = data.status === 'at-risk';

  return (
    <div style={{
      ...customTwinStyles,
      borderColor: isCompromised ? 'rgba(239,68,68,0.3)' : isAtRisk ? 'rgba(245,158,11,0.3)' : 'rgba(16,185,129,0.15)',
      boxShadow: isCompromised ? '0 0 25px rgba(239,68,68,0.1)' : isAtRisk ? '0 0 20px rgba(245,158,11,0.08)' : '0 8px 32px rgba(15,23,42,0.04)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            padding: '6px', 
            borderRadius: '10px',
            backgroundColor: isCompromised ? 'rgba(239,68,68,0.1)' : isAtRisk ? 'rgba(245,158,11,0.1)' : 'rgba(37,99,235,0.08)',
            color: isCompromised ? '#ef4444' : isAtRisk ? '#f59e0b' : '#2563eb'
          }}>
            <Icon size={16} />
          </div>
          <div style={{ fontWeight: 700 }}>{data.label}</div>
        </div>
        {isCompromised && <ShieldAlert size={16} color="#ef4444" className="animate-pulse" />}
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', fontSize: '10px', textTransform: 'uppercase' }}>
          <span>Twin Health</span>
          <span style={{ color: isCompromised ? '#ef4444' : isAtRisk ? '#f59e0b' : '#10b981', fontWeight: 'bold' }}>
            {data.health}%
          </span>
        </div>
        <div style={{ height: '4px', background: 'rgba(0,0,0,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ 
            height: '100%', 
            width: `${data.health}%`, 
            background: isCompromised ? '#ef4444' : isAtRisk ? '#f59e0b' : '#10b981' 
          }} />
        </div>
      </div>
    </div>
  );
};

const nodeTypes = {
  twin: TwinNode,
};

export function DigitalTwin() {
  const { activeEvent, timeMachineIndex } = useMockStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Time Machine health metrics interpolation
  const accountHealth = Math.max(35, 98 - timeMachineIndex * 12.6);
  const deviceHealth = Math.max(12, 92 - timeMachineIndex * 16.0);
  const locationConfidence = Math.max(24, 87 - timeMachineIndex * 12.6);
  const behaviorDeviation = Math.min(96, 34 + timeMachineIndex * 12.4);

  // XYFlow nodes layout calculation
  const isRejected = timeMachineIndex >= 4;
  const isAtRisk = timeMachineIndex >= 2;

  const initialNodes: Node[] = [
    {
      id: 'gateway',
      type: 'twin',
      position: { x: 250, y: 30 },
      data: { label: 'Global API Gateway', icon: Globe, status: isRejected ? 'at-risk' : 'healthy', health: isRejected ? 65 : 100 },
    },
    {
      id: 'auth',
      type: 'twin',
      position: { x: 50, y: 180 },
      data: { label: 'Auth Service (EU)', icon: Cpu, status: 'healthy', health: 100 },
    },
    {
      id: 'target_db',
      type: 'twin',
      position: { x: 450, y: 180 },
      data: { label: activeEvent?.target || 'Database', icon: Database, status: isRejected ? 'compromised' : isAtRisk ? 'at-risk' : 'healthy', health: Math.round(deviceHealth) },
    },
    {
      id: 'core',
      type: 'twin',
      position: { x: 250, y: 320 },
      data: { label: 'Core Ledger', icon: Server, status: isRejected ? 'at-risk' : 'healthy', health: isRejected ? 40 : 100 },
    },
  ];

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: 'gateway', target: 'auth', animated: true, style: { stroke: 'rgba(15,23,42,0.1)' } },
    { id: 'e1-3', source: 'gateway', target: 'target_db', animated: isRejected, style: { stroke: isRejected ? '#ef4444' : 'rgba(15,23,42,0.1)', strokeWidth: isRejected ? 2 : 1 } },
    { id: 'e2-4', source: 'auth', target: 'core', style: { stroke: 'rgba(15,23,42,0.1)' } },
    { id: 'e3-4', source: 'target_db', target: 'core', animated: isRejected, style: { stroke: isRejected ? '#f59e0b' : 'rgba(15,23,42,0.1)', strokeWidth: isRejected ? 2 : 1 } },
  ];

  const nodes = useMemo(() => initialNodes, [timeMachineIndex, activeEvent]);
  const edges = useMemo(() => initialEdges, [timeMachineIndex, activeEvent]);

  if (!mounted) return null;

  return (
    <div className="h-full relative flex flex-col lg:flex-row overflow-hidden bg-[#F5F7FA]">
      
      {/* Left Column: Topology Flow */}
      <div className="flex-1 h-full relative border-r border-[rgba(20,20,20,0.06)] bg-white/40">
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          nodeTypes={nodeTypes}
          fitView
          className="light"
        >
          <Background color="#000000" gap={25} size={1} className="opacity-[0.02]" />
          <Controls className="bg-white border-[rgba(20,20,20,0.06)] fill-slate-900" />
        </ReactFlow>

        {/* Overlay Title */}
        <div className="absolute top-6 left-6 z-10 pointer-events-none">
          <h2 className="text-xs font-bold tracking-wider uppercase flex items-center gap-2 text-[#0F172A]">
            <Network className="w-5 h-5 text-[#2563EB]" />
            Infrastructure digital twin topology
          </h2>
          <p className="text-[9px] text-[#64748B] uppercase tracking-wider mt-1 font-mono">
            Simulating privilege query execution propagation path
          </p>
        </div>
      </div>

      {/* Right Column: Telemetry Rings & Evolution Trends */}
      <div className="w-full lg:w-[400px] p-6 space-y-6 overflow-y-auto shrink-0 bg-white/50 backdrop-blur-xl border-t lg:border-t-0 border-[rgba(20,20,20,0.06)] font-mono text-xs text-[#64748B]">
        
        {/* Telemetry Rings */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-5 space-y-6 shadow-soft">
          <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-1.5">
            <Heart className="w-4 h-4 text-[#2563EB]" />
            Circular Telemetry Rings
          </h3>
          
          <div className="grid grid-cols-2 gap-6 justify-items-center">
            
            {/* Account Twin Ring */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="rgba(20,20,20,0.04)" strokeWidth="4" fill="transparent" />
                  <circle cx="40" cy="40" r="32" stroke="#10B981" strokeWidth="4" fill="transparent" 
                    strokeDasharray="201" strokeDashoffset={201 - (201 * accountHealth) / 100} 
                    className="transition-all duration-300"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center font-bold text-xs text-[#0F172A]">
                  {Math.round(accountHealth)}%
                </div>
              </div>
              <span className="text-[9px] uppercase font-bold text-center">Account Twin</span>
            </div>

            {/* Device Twin Ring */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="rgba(20,20,20,0.04)" strokeWidth="4" fill="transparent" />
                  <circle cx="40" cy="40" r="32" stroke="#F59E0B" strokeWidth="4" fill="transparent" 
                    strokeDasharray="201" strokeDashoffset={201 - (201 * deviceHealth) / 100} 
                    className="transition-all duration-300"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center font-bold text-xs text-[#0F172A]">
                  {Math.round(deviceHealth)}%
                </div>
              </div>
              <span className="text-[9px] uppercase font-bold text-center">Device Twin</span>
            </div>

            {/* Location Twin Ring */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="rgba(20,20,20,0.04)" strokeWidth="4" fill="transparent" />
                  <circle cx="40" cy="40" r="32" stroke="#2563EB" strokeWidth="4" fill="transparent" 
                    strokeDasharray="201" strokeDashoffset={201 - (201 * locationConfidence) / 100} 
                    className="transition-all duration-300"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center font-bold text-xs text-[#0F172A]">
                  {Math.round(locationConfidence)}%
                </div>
              </div>
              <span className="text-[9px] uppercase font-bold text-center">Geovelocity</span>
            </div>

            {/* Behavior Twin Ring */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="rgba(20,20,20,0.04)" strokeWidth="4" fill="transparent" />
                  <circle cx="40" cy="40" r="32" stroke="#7C3AED" strokeWidth="4" fill="transparent" 
                    strokeDasharray="201" strokeDashoffset={201 - (201 * (100 - behaviorDeviation)) / 100} 
                    className="transition-all duration-300"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center font-bold text-xs text-[#0F172A]">
                  {Math.round(100 - behaviorDeviation)}%
                </div>
              </div>
              <span className="text-[9px] uppercase font-bold text-center">Behavior Integrity</span>
            </div>

          </div>
        </Card>

        {/* Evolution Trends */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-5 space-y-4 shadow-soft">
          <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-[#2563EB]" />
            Ecosystem Evolution Trends
          </h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-[rgba(20,20,20,0.04)] shadow-soft">
              <div className="flex flex-col">
                <span className="text-[#64748B] uppercase text-[9px]">Yesterday History</span>
                <span className="text-[10px] text-[#0F172A] font-bold mt-0.5">Baselined Verification</span>
              </div>
              <span className="text-xs text-[#10B981] font-bold uppercase">98% Normal</span>
            </div>
            
            <div className="flex items-center justify-center text-[#64748B]/40 font-bold my-1">
              ▼
            </div>

            <div className="flex items-center justify-between p-3 rounded-2xl bg-[#2563EB]/5 border border-[#2563EB]/25 shadow-soft">
              <div className="flex flex-col">
                <span className="text-[#2563EB] uppercase text-[9px]">Today Real-Time</span>
                <span className="text-[10px] text-[#0F172A] font-bold mt-0.5">Active Execution Delta</span>
              </div>
              <span className="text-xs text-[#F59E0B] font-bold uppercase">At Risk</span>
            </div>

            <div className="flex items-center justify-center text-[#64748B]/40 font-bold my-1">
              ▼
            </div>

            <div className="flex items-center justify-between p-3 rounded-2xl bg-[#EF4444]/5 border border-[#EF4444]/25 shadow-soft">
              <div className="flex flex-col">
                <span className="text-[#EF4444] uppercase text-[9px]">Tomorrow Projection</span>
                <span className="text-[10px] text-[#0F172A] font-bold mt-0.5">Exploit Blast Radius</span>
              </div>
              <span className="text-xs text-[#EF4444] font-bold uppercase">Containment Needed</span>
            </div>
          </div>
        </Card>

      </div>

    </div>
  );
}
