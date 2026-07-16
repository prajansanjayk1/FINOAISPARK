'use client';

import { useMemo, useState, useEffect } from 'react';
import { ReactFlow, Background, Controls, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card } from '@/components/ui/card';
import { User, Server, Database, Network, Key, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useMockStore } from '@/store/useMockStore';
import { motion, AnimatePresence } from 'framer-motion';

const customNodeStyles = {
  background: 'rgba(255, 255, 255, 0.9)',
  color: '#0F172A',
  border: '1px solid rgba(20,20,20,0.06)',
  borderRadius: '20px',
  padding: '12px 18px',
  boxShadow: '0 8px 32px 0 rgba(15,23,42,0.04)',
  backdropFilter: 'blur(20px)',
  fontSize: '12px',
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  minWidth: '220px'
};

const CustomNode = ({ data }: { data: any }) => {
  const Icon = data.icon;
  return (
    <div style={{ ...customNodeStyles, borderColor: data.isThreat ? 'rgba(239,68,68,0.3)' : 'rgba(37,99,235,0.2)' }}>
      <div style={{ 
        padding: '6px', 
        borderRadius: '10px', 
        backgroundColor: data.isThreat ? 'rgba(239,68,68,0.1)' : 'rgba(37,99,235,0.08)',
        color: data.isThreat ? '#ef4444' : '#2563eb'
      }}>
        <Icon size={16} />
      </div>
      <div>
        <div style={{ fontWeight: 700, color: '#0F172A' }}>{data.label}</div>
        <div style={{ fontSize: '10px', color: '#64748B', fontFamily: 'monospace' }}>{data.sublabel}</div>
      </div>
    </div>
  );
};

const nodeTypes = {
  custom: CustomNode,
};

export function EvidenceExplorer() {
  const { activeEvent } = useMockStore();
  const [mounted, setMounted] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string>('actor');

  useEffect(() => {
    setMounted(true);
  }, []);

  const isBlocked = activeEvent?.status === 'rejected';

  // Force-directed money laundering flow network
  const initialNodes: Node[] = isBlocked ? [
    { id: 'actor', type: 'custom', position: { x: 50, y: 150 }, data: { label: activeEvent?.actor.name || 'Customer', sublabel: 'Identity compromised', icon: User, isThreat: true } },
    { id: 'device', type: 'custom', position: { x: 300, y: 50 }, data: { label: 'Device Spoof', sublabel: 'Android Emulator', icon: Network, isThreat: true } },
    { id: 'vpn', type: 'custom', position: { x: 300, y: 250 }, data: { label: 'VPN Proxy', sublabel: '192.168.45.12', icon: Network, isThreat: true } },
    { id: 'botnet', type: 'custom', position: { x: 550, y: 150 }, data: { label: 'C2 Botnet', sublabel: 'Stuffing pattern', icon: AlertTriangle, isThreat: true } },
    { id: 'merchant', type: 'custom', position: { x: 800, y: 50 }, data: { label: 'Target Merchant', sublabel: 'UPI Interface', icon: Database, isThreat: true } },
    { id: 'wallet', type: 'custom', position: { x: 1050, y: 150 }, data: { label: 'Crypto Wallet', sublabel: 'Cashout sink', icon: Key, isThreat: true } }
  ] : [
    { id: 'actor', type: 'custom', position: { x: 50, y: 150 }, data: { label: activeEvent?.actor.name || 'Customer', sublabel: 'Trusted profile', icon: User, isThreat: false } },
    { id: 'device', type: 'custom', position: { x: 350, y: 50 }, data: { label: 'Managed Device', sublabel: 'MacBook Pro 16', icon: Network, isThreat: false } },
    { id: 'token', type: 'custom', position: { x: 350, y: 250 }, data: { label: 'Session Token', sublabel: 'MFA verified', icon: Key, isThreat: false } },
    { id: 'target', type: 'custom', position: { x: 650, y: 150 }, data: { label: activeEvent?.target || 'Core DB', sublabel: 'Access allowed', icon: Database, isThreat: false } }
  ];

  const initialEdges: Edge[] = isBlocked ? [
    { id: 'e1', source: 'actor', target: 'device', animated: true, style: { stroke: '#ef4444', strokeWidth: 1.5 } },
    { id: 'e2', source: 'actor', target: 'vpn', animated: true, style: { stroke: '#ef4444', strokeWidth: 1.5 } },
    { id: 'e3', source: 'device', target: 'botnet', animated: true, style: { stroke: '#ef4444', strokeWidth: 1.5 } },
    { id: 'e4', source: 'vpn', target: 'botnet', animated: true, style: { stroke: '#ef4444', strokeWidth: 1.5 } },
    { id: 'e5', source: 'botnet', target: 'merchant', animated: true, style: { stroke: '#ef4444', strokeWidth: 1.5 } },
    { id: 'e6', source: 'merchant', target: 'wallet', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 } }
  ] : [
    { id: 'e1', source: 'actor', target: 'device', animated: true, style: { stroke: '#10b981', strokeWidth: 1.5 } },
    { id: 'e2', source: 'actor', target: 'token', animated: true, style: { stroke: '#10b981', strokeWidth: 1.5 } },
    { id: 'e3', source: 'device', target: 'target', style: { stroke: '#10b981' } },
    { id: 'e4', source: 'token', target: 'target', style: { stroke: '#10b981' } }
  ];

  const nodes = useMemo(() => initialNodes, [activeEvent]);
  const edges = useMemo(() => initialEdges, [activeEvent]);

  // Node details lookup
  const nodeMetadata: Record<string, any> = {
    actor: { title: 'Customer Profile', desc: 'Active operator identity details. Heuristics analyze credentials and velocity.', risk: isBlocked ? 'CRITICAL (98%)' : 'SAFE' },
    device: { title: 'Spoofed Device', desc: ' Spoof checks matched emulated configurations. Device fingerprint not on file.', risk: 'CRITICAL' },
    vpn: { title: 'Proxy Node', desc: 'VPN server coordinates trace to an off-shore provider violating data sovereignty rules.', risk: 'WARNING' },
    botnet: { title: 'C2 Network', desc: 'Target credentials and IP velocities match botnet stuffing attack patterns.', risk: 'CRITICAL' },
    merchant: { title: 'Merchant API', desc: 'The destination API interface for the fund transfer operation.', risk: 'MONITORED' },
    wallet: { title: 'Crypto Destination', desc: 'Known cashout ledger sink. Automatic containment block locked outgoing paths.', risk: 'CRITICAL' }
  };

  const selectedNodeInfo = nodeMetadata[selectedNodeId] || nodeMetadata['actor'];

  if (!mounted) return null;

  return (
    <div className="h-full relative flex flex-col lg:flex-row bg-[#F5F7FA]">
      
      {/* ReactFlow Canvas */}
      <div className="flex-1 h-full relative border-r border-[rgba(20,20,20,0.06)] bg-white/40">
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          nodeTypes={nodeTypes}
          onNodeClick={(e, node) => setSelectedNodeId(node.id)}
          fitView
          className="light"
        >
          <Background color="#000000" gap={20} size={1} className="opacity-[0.02]" />
          <Controls className="bg-white border-[rgba(20,20,20,0.06)] fill-slate-900" />
        </ReactFlow>
      </div>

      {/* Trust Scores & Node Properties */}
      <div className="w-full lg:w-[320px] p-6 space-y-6 overflow-y-auto shrink-0 bg-white/50 backdrop-blur-xl border-t lg:border-t-0 border-[rgba(20,20,20,0.06)] font-mono text-xs text-[#64748B]">
        
        {/* Consensus Trust Scores */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-4 shadow-soft">
          <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] mb-4 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#2563EB]" />
            Consensus Trust Scores
          </h3>

          <div className="space-y-3 text-[10px]">
            <div className="space-y-1">
              <div className="flex justify-between uppercase">
                <span>Identity Trust</span>
                <span className={isBlocked ? "text-destructive" : "text-success"}>{isBlocked ? '34%' : '98%'}</span>
              </div>
              <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                <div className={`h-full ${isBlocked ? 'bg-destructive' : 'bg-success'}`} style={{ width: isBlocked ? '34%' : '98%' }} />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between uppercase">
                <span>Behavior Trust</span>
                <span className={isBlocked ? "text-destructive" : "text-success"}>{isBlocked ? '22%' : '95%'}</span>
              </div>
              <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                <div className={`h-full ${isBlocked ? 'bg-destructive' : 'bg-success'}`} style={{ width: isBlocked ? '22%' : '95%' }} />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between uppercase">
                <span>Device Trust</span>
                <span className={isBlocked ? "text-destructive" : "text-success"}>{isBlocked ? '15%' : '84%'}</span>
              </div>
              <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                <div className={`h-full ${isBlocked ? 'bg-destructive' : 'bg-success'}`} style={{ width: isBlocked ? '15%' : '84%' }} />
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200 flex justify-between uppercase font-bold text-xs">
              <span>Overall Trust</span>
              <span className={isBlocked ? "text-destructive" : "text-success"}>{isBlocked ? '29%' : '91%'}</span>
            </div>
          </div>
        </Card>

        {/* Node Properties details */}
        <AnimatePresence mode="wait">
          {selectedNodeInfo && (
            <motion.div 
              key={selectedNodeId}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-4 shadow-soft space-y-3">
                <h4 className="font-extrabold text-xs text-[#0F172A] border-b border-slate-100 pb-2">{selectedNodeInfo.title}</h4>
                <p className="text-[10px] leading-relaxed text-[#64748B]">{selectedNodeInfo.desc}</p>
                <div className="flex justify-between items-center text-[10px] pt-1">
                  <span>Risk Category:</span>
                  <span className="font-bold text-[#EF4444]">{selectedNodeInfo.risk}</span>
                </div>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="p-3 bg-slate-100/60 rounded-2xl border border-[rgba(20,20,20,0.04)] text-[9px] leading-relaxed uppercase text-center">
          Click nodes in the money flow network to fetch metadata logs.
        </div>

      </div>
    </div>
  );
}
