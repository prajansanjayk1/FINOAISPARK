'use client';

import { useMockStore } from '@/store/useMockStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Box, Play, CheckCircle2, XCircle, RotateCcw, AlertTriangle, ShieldCheck, Sliders, Network } from 'lucide-react';
import { useState, useEffect } from 'react';

interface FutureSim {
  id: number;
  name: string;
  loss: string;
  probability: number;
  status: 'safe' | 'warning' | 'critical';
  details: string;
}

export function ExecutionSandbox() {
  const { activeEvent } = useMockStore();
  const [simulationState, setSimulationState] = useState<'idle' | 'simulating' | 'complete'>('idle');
  const [progress, setProgress] = useState(0);
  const [transferValue, setTransferValue] = useState(5000000); // 50 Lakhs default
  const [mfaSuccess, setMfaSuccess] = useState(false);

  useEffect(() => {
    if (simulationState === 'simulating') {
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 100) {
            clearInterval(interval);
            setSimulationState('complete');
            return 100;
          }
          return p + 4;
        });
      }, 30);
      return () => clearInterval(interval);
    }
  }, [simulationState]);

  if (!activeEvent) return null;

  // Dynamic futures based on inputs
  const simulatedFutures: FutureSim[] = [
    {
      id: 1,
      name: 'Scenario A: Operations Baseline',
      loss: '₹0',
      probability: mfaSuccess ? 85 : 67,
      status: 'safe',
      details: 'No business disruption detected. Rollback logs verified.'
    },
    {
      id: 2,
      name: 'Scenario B: Account Takeover Leak',
      loss: '₹24.5 Lakhs',
      probability: mfaSuccess ? 10 : 21,
      status: 'warning',
      details: 'Data exfiltration and lateral API exploitation.'
    },
    {
      id: 3,
      name: 'Scenario C: Money Laundering Cycle',
      loss: '₹50.0 Lakhs',
      probability: transferValue > 10000000 ? 12 : 4,
      status: 'critical',
      details: 'Structuring patterns flag AML thresholds.'
    },
    {
      id: 4,
      name: 'Scenario D: Active Ransomware Chain',
      loss: '₹2.4 Crores',
      probability: mfaSuccess ? 1 : 8,
      status: 'critical',
      details: 'Core Database encryption and domain lock.'
    }
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 bg-[#F5F7FA] font-mono text-xs text-[#64748B]">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[rgba(20,20,20,0.06)] pb-6 bg-white/30">
        <div>
          <h2 className="text-sm font-extrabold tracking-wider uppercase flex items-center gap-3 text-[#0F172A]">
            <Box className="w-5 h-5 text-[#2563EB] animate-pulse" />
            Autonomous Simulation Enclave
          </h2>
          <p className="text-[9px] text-[#64748B] uppercase mt-1">
            Running 10,000 parallel futures inside isolated memory enclaves.
          </p>
        </div>
        {simulationState === 'idle' && (
          <button 
            onClick={() => { setProgress(0); setSimulationState('simulating'); }}
            className="flex items-center gap-2 bg-[#2563EB] text-white border border-[#2563EB]/30 px-4 py-2 rounded-2xl font-bold text-xs hover:bg-[#2563EB]/95 transition-all shadow-soft uppercase tracking-wider"
          >
            <Play className="w-4 h-4" />
            Run 10k simulations
          </button>
        )}
      </div>

      {/* Parameter Sandbox Recalculator */}
      <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-6 shadow-soft">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] mb-4 flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-[#2563EB]" />
          Interactive Parameter Sandbox Recalculator
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <div className="flex justify-between uppercase text-[9px] text-[#64748B] font-bold">
              <span>Transfer Amount:</span>
              <span className="text-[#2563EB] font-bold">₹{(transferValue / 100000).toFixed(1)} Lakhs</span>
            </div>
            <input 
              type="range" 
              min="100000" 
              max="50000000" 
              step="100000" 
              value={transferValue} 
              onChange={(e) => setTransferValue(parseInt(e.target.value))}
              className="w-full accent-[#2563EB] bg-slate-200 h-1.5 rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-3.5 bg-slate-50 border border-[rgba(20,20,20,0.04)] rounded-2xl shadow-soft">
            <div>
              <div className="font-bold text-[#0F172A] uppercase text-[9px]">Step-Up MFA Success</div>
              <div className="text-[9px] text-[#64748B] uppercase">Simulate operator passing MFA checks</div>
            </div>
            <input 
              type="checkbox" 
              checked={mfaSuccess} 
              onChange={(e) => setMfaSuccess(e.target.checked)}
              className="w-4 h-4 accent-[#2563EB] cursor-pointer"
            />
          </div>
        </div>
      </Card>

      <AnimatePresence mode="wait">
        {simulationState === 'simulating' && (
          <motion.div 
            key="simulating"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="flex flex-col items-center justify-center py-20 glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft"
          >
            <div className="w-16 h-16 relative mb-6">
              <div className="absolute inset-0 border border-[#2563EB]/25 rounded-full animate-ping" />
              <div className="absolute inset-2 border-2 border-dashed border-[#2563EB]/60 rounded-full animate-spin" style={{ animationDuration: '3s' }} />
            </div>
            <h3 className="text-xs font-bold mb-4 uppercase tracking-wider text-[#0F172A]">Running 10,000 futures in sandbox...</h3>
            <div className="w-full max-w-md h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-ai rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-[9px] text-[#2563EB] mt-3 font-mono font-bold">{progress}% Complete</p>
          </motion.div>
        )}

        {simulationState === 'complete' && (
          <motion.div 
            key="complete"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Causal Explainability Tree */}
            <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-6 shadow-soft">
              <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] mb-4 flex items-center gap-1.5">
                <Network className="w-3.5 h-3.5 text-[#2563EB]" />
                Causal AI Inference Tree
              </h3>
              
              <div className="flex flex-col md:flex-row items-center justify-between gap-3 p-4 rounded-2xl bg-slate-50 border border-[rgba(20,20,20,0.04)] text-center shadow-soft">
                <div className="p-3 border border-[rgba(20,20,20,0.04)] rounded-xl bg-white w-full md:w-auto shadow-soft">
                  <div className="text-[8px] text-[#64748B] uppercase font-bold">Trigger</div>
                  <div className="font-bold text-[#0F172A] text-xs mt-0.5">Unknown Device</div>
                </div>
                <div className="text-[#64748B] font-bold">→</div>
                <div className="p-3 border border-[rgba(20,20,20,0.04)] rounded-xl bg-white w-full md:w-auto shadow-soft">
                  <div className="text-[8px] text-[#64748B] uppercase font-bold">Proxy check</div>
                  <div className="font-bold text-[#F59E0B] text-xs mt-0.5">VPN Route</div>
                </div>
                <div className="text-[#64748B] font-bold">→</div>
                <div className="p-3 border border-[rgba(20,20,20,0.04)] rounded-xl bg-white w-full md:w-auto shadow-soft">
                  <div className="text-[8px] text-[#64748B] uppercase font-bold">Velocity check</div>
                  <div className="font-bold text-[#F59E0B] text-xs mt-0.5">Impossible Travel</div>
                </div>
                <div className="text-[#64748B] font-bold">→</div>
                <div className="p-3 border border-[rgba(20,20,20,0.04)] rounded-xl bg-white w-full md:w-auto shadow-soft">
                  <div className="text-[8px] text-[#64748B] uppercase font-bold">Verdict</div>
                  <div className="font-bold text-[#EF4444] text-xs mt-0.5">Consensus BLOCK</div>
                </div>
              </div>
            </Card>

            {/* Predictive Futures Matrix */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {simulatedFutures.map((future) => (
                <Card key={future.id} className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-4 space-y-2 shadow-soft">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                    <span className="font-bold text-[#0F172A] text-xs">{future.name}</span>
                    <span className={`text-[8px] font-bold px-2 py-0.5 rounded-full border ${
                      future.status === 'safe' ? 'bg-[#10B981]/10 border-[#10B981]/25 text-[#10B981]' :
                      future.status === 'warning' ? 'bg-[#F59E0B]/10 border-[#F59E0B]/25 text-[#F59E0B]' :
                      'bg-[#EF4444]/10 border-[#EF4444]/25 text-[#EF4444]'
                    }`}>
                      {future.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-left">
                    <div>
                      <div className="text-[8px] text-[#64748B] uppercase font-bold">Estimated Loss</div>
                      <div className="text-sm font-extrabold text-[#0F172A] mt-0.5">{future.loss}</div>
                    </div>
                    <div>
                      <div className="text-[8px] text-[#64748B] uppercase font-bold">Probability</div>
                      <div className="text-sm font-extrabold text-[#2563EB] mt-0.5">{future.probability}%</div>
                    </div>
                  </div>
                  <div className="text-[10px] text-[#64748B] leading-relaxed pt-1.5">
                    {future.details}
                  </div>
                </Card>
              ))}
            </div>

            <div className="flex justify-end pt-4">
              <button 
                onClick={() => setSimulationState('idle')}
                className="text-[9px] text-[#64748B] hover:text-[#0F172A] transition-colors uppercase font-bold"
              >
                Reset Sandbox
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
