'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMockStore } from '@/store/useMockStore';
import { 
  Fingerprint, 
  Activity, 
  Scale, 
  Briefcase, 
  Cpu, 
  Gavel, 
  ShieldAlert, 
  RotateCcw, 
  Network, 
  DollarSign, 
  Box, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle 
} from 'lucide-react';

interface AgentNode {
  id: string;
  name: string;
  icon: any;
  angle: number;
  description: string;
  defaultStatus: 'approved' | 'rejected' | 'warning' | 'idle';
  defaultConfidence: number;
}

const surroundAgents: AgentNode[] = [
  { id: 'identity', name: 'Identity Agent', icon: Fingerprint, angle: 0, description: 'Cryptographic session validation', defaultStatus: 'approved', defaultConfidence: 99 },
  { id: 'behaviour', name: 'Behavior Agent', icon: Activity, angle: 36, description: 'Historical profile velocity match', defaultStatus: 'warning', defaultConfidence: 75 },
  { id: 'threat', name: 'Threat Intel', icon: ShieldAlert, angle: 72, description: 'C2 bot network signature scans', defaultStatus: 'approved', defaultConfidence: 98 },
  { id: 'compliance', name: 'Compliance Agent', icon: Scale, angle: 108, description: 'Regulatory framework alignment', defaultStatus: 'rejected', defaultConfidence: 12 },
  { id: 'business', name: 'Business Impact', icon: Briefcase, angle: 144, description: 'Exposure blast radius simulation', defaultStatus: 'rejected', defaultConfidence: 24 },
  { id: 'recovery', name: 'Recovery Planner', icon: RotateCcw, angle: 180, description: 'Automated containment strategies', defaultStatus: 'idle', defaultConfidence: 0 },
  { id: 'twin', name: 'Digital Twin', icon: Cpu, angle: 216, description: 'Infrastructure clone validation', defaultStatus: 'approved', defaultConfidence: 95 },
  { id: 'network', name: 'Network Traffic', icon: Network, angle: 252, description: 'VPC route & trace analyzer', defaultStatus: 'approved', defaultConfidence: 90 },
  { id: 'financial', name: 'Financial Risk', icon: DollarSign, angle: 288, description: 'Liquidity constraint monitoring', defaultStatus: 'approved', defaultConfidence: 96 },
  { id: 'counterfactual', name: 'Counterfactuals', icon: Box, angle: 324, description: 'Parallel futures modeling', defaultStatus: 'approved', defaultConfidence: 92 }
];

export function AISecurityCouncil() {
  const { liveEvents, activeEvent } = useMockStore();
  const selectedEvent = activeEvent || liveEvents[0];
  const isBlocked = selectedEvent?.status === 'rejected';

  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(surroundAgents[0]);
  const [pulseNodeId, setPulseNodeId] = useState<string>('');

  // Node coordinate generator
  const getCoordinates = (angle: number, radius: number) => {
    const radian = (angle * Math.PI) / 180;
    // center coordinates: cx=250, cy=250
    return {
      x: 250 + radius * Math.cos(radian),
      y: 250 + radius * Math.sin(radian)
    };
  };

  useEffect(() => {
    // Staggered pulsing animation loop to show "Active Thinking / Council Debating"
    const interval = setInterval(() => {
      const randomNode = surroundAgents[Math.floor(Math.random() * surroundAgents.length)];
      setPulseNodeId(randomNode.id);
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col lg:flex-row items-center gap-8 bg-white/40 border border-[rgba(20,20,20,0.04)] p-6 rounded-3xl backdrop-blur-xl">
      
      {/* Neural network SVG canvas */}
      <div className="relative w-full max-w-[500px] aspect-square flex items-center justify-center bg-slate-50/50 rounded-2xl border border-[rgba(20,20,20,0.06)] shadow-soft">
        <svg viewBox="0 0 500 500" className="w-full h-full">
          
          {/* Background grid concentric circles */}
          <circle cx="250" cy="250" r="180" fill="none" stroke="rgba(20, 20, 20, 0.03)" strokeWidth="1" strokeDasharray="5,5" />
          <circle cx="250" cy="250" r="90" fill="none" stroke="rgba(20, 20, 20, 0.02)" strokeWidth="1" />

          {/* Connection paths */}
          {surroundAgents.map((agent) => {
            const coord = getCoordinates(agent.angle, 180);
            const status = isBlocked ? agent.defaultStatus : 'approved';
            const isPulsing = pulseNodeId === agent.id;

            return (
              <g key={agent.id}>
                {/* Connecting link */}
                <line 
                  x1="250" 
                  y1="250" 
                  x2={coord.x} 
                  y2={coord.y} 
                  stroke={status === 'rejected' ? 'rgba(239, 68, 68, 0.3)' : status === 'warning' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(37, 99, 235, 0.15)'}
                  strokeWidth={isPulsing ? 2.5 : 1.5}
                  className="transition-all duration-300"
                />

                {/* Animated traveling particles */}
                <circle r="3.5" fill="#2563EB">
                  <animateMotion 
                    dur={isPulsing ? "1.5s" : "3.5s"} 
                    repeatCount="indefinity" 
                    path={`M 250 250 L ${coord.x} ${coord.y}`} 
                  />
                </circle>
              </g>
            );
          })}

          {/* Surrounding Agent Nodes */}
          {surroundAgents.map((agent) => {
            const coord = getCoordinates(agent.angle, 180);
            const status = isBlocked ? agent.defaultStatus : 'approved';
            const isSelected = selectedNode?.id === agent.id;
            const isPulsing = pulseNodeId === agent.id;
            const Icon = agent.icon;

            return (
              <g 
                key={agent.id} 
                onClick={() => setSelectedNode(agent)}
                className="cursor-pointer group"
              >
                {/* Pulse Glow outer boundary */}
                <circle 
                  cx={coord.x} 
                  cy={coord.y} 
                  r={isSelected ? 26 : 22} 
                  fill={isSelected ? 'rgba(37, 99, 235, 0.08)' : 'rgba(255, 255, 255, 0.8)'}
                  stroke={
                    status === 'rejected' ? 'rgba(239, 68, 68, 0.4)' :
                    status === 'warning' ? 'rgba(245, 158, 11, 0.4)' :
                    isSelected ? '#2563EB' : 'rgba(20, 20, 20, 0.08)'
                  }
                  strokeWidth="1.5"
                  className="transition-all duration-300"
                />

                {/* Animated thinking ring */}
                {isPulsing && (
                  <circle 
                    cx={coord.x} 
                    cy={coord.y} 
                    r="30" 
                    fill="none" 
                    stroke={status === 'rejected' ? '#EF4444' : '#2563EB'} 
                    strokeWidth="1" 
                    className="opacity-40 animate-ping"
                    style={{ animationDuration: '2s' }}
                  />
                )}

                {/* Node icon */}
                <g transform={`translate(${coord.x - 8}, ${coord.y - 8})`} className="pointer-events-none">
                  <Icon 
                    className={`w-4 h-4 ${
                      status === 'rejected' ? 'text-[#EF4444]' :
                      status === 'warning' ? 'text-[#F59E0B]' :
                      isSelected ? 'text-[#2563EB]' : 'text-[#64748B]'
                    }`}
                  />
                </g>
              </g>
            );
          })}

          {/* Central Node: Judge AI */}
          <g>
            <circle 
              cx="250" 
              cy="250" 
              r="34" 
              fill="white" 
              stroke="#2563EB" 
              strokeWidth="2.5" 
              className="shadow-medium"
            />
            <circle 
              cx="250" 
              cy="250" 
              r="38" 
              fill="none" 
              stroke="#2563EB" 
              strokeWidth="1" 
              className="opacity-30 pulse-ring-slow"
            />
            <g transform="translate(238, 238)" className="pointer-events-none">
              <Gavel className="w-6 h-6 text-[#2563EB]" />
            </g>
          </g>

        </svg>
      </div>

      {/* Floating Node Intelligence details panel */}
      <div className="flex-1 w-full space-y-4 font-mono text-xs text-[#64748B]">
        <AnimatePresence mode="wait">
          {selectedNode && (
            <motion.div 
              key={selectedNode.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-5 bg-white/80 border border-[rgba(20,20,20,0.06)] rounded-3xl space-y-4 shadow-soft"
            >
              <div className="flex items-center gap-3 border-b border-[rgba(20,20,20,0.06)] pb-3">
                <div className="p-2 bg-slate-100 rounded-xl text-[#2563EB]">
                  <selectedNode.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm text-[#0F172A]">{selectedNode.name}</h3>
                  <span className="text-[10px] uppercase font-bold text-[#64748B]/60">Platform Micro-Agent</span>
                </div>
              </div>

              <div className="space-y-3 leading-relaxed text-[11px]">
                <p className="text-[#0F172A]/90">{selectedNode.description}</p>
                
                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-[rgba(20,20,20,0.06)]">
                  <div>
                    <span className="text-[9px] uppercase font-bold tracking-wider">Default Verdict</span>
                    <div className={`text-xs font-bold mt-0.5 ${
                      selectedNode.defaultStatus === 'approved' ? 'text-[#10B981]' :
                      selectedNode.defaultStatus === 'rejected' ? 'text-[#EF4444]' :
                      selectedNode.defaultStatus === 'warning' ? 'text-[#F59E0B]' : 'text-[#64748B]'
                    }`}>
                      {selectedNode.defaultStatus.toUpperCase()}
                    </div>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold tracking-wider">Node Confidence</span>
                    <div className="text-xs font-extrabold text-[#2563EB] mt-0.5">
                      {selectedNode.defaultConfidence > 0 ? `${selectedNode.defaultConfidence}%` : 'STANDBY'}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="p-4 bg-slate-100/60 rounded-2xl border border-[rgba(20,20,20,0.04)] text-[10px] leading-relaxed uppercase">
          Click any outer node in the neural SVG connection matrix to inspect properties and vote tallies.
        </div>
      </div>

    </div>
  );
}
