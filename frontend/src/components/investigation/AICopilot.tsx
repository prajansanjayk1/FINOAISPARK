'use client';

import { useState } from 'react';
import { useMockStore } from '@/store/useMockStore';
import { Bot, Send, BrainCircuit, Sparkles, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';

type Audience = 'executive' | 'technical' | 'auditor' | 'rbi';

export function AICopilot() {
  const { activeEvent } = useMockStore();
  const [audience, setAudience] = useState<Audience>('executive');
  const [briefText, setBriefText] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);

  const getDynamicBrief = (aud: Audience) => {
    if (!activeEvent) return "No active event selected for Jarvis briefing.";

    const name = activeEvent.actor.name;
    const role = activeEvent.actor.role;
    const ip = activeEvent.actor.ip;
    const device = activeEvent.actor.device;
    const loc = activeEvent.actor.location;
    const action = activeEvent.action;
    const target = activeEvent.target;
    const risk = activeEvent.riskScore;
    const status = activeEvent.status === 'rejected' ? 'BLOCK' : 'APPROVE';
    const reasons = activeEvent.reasoning.join(' ');

    switch (aud) {
      case 'executive':
        return `Jarvis OS Executive Summary: A risk score of ${risk}% was flagged for an operation by ${name} (${role}) from device ${device} located at ${loc}. The user attempted action "${action}" on asset "${target}". The AI Swarm recommends to ${status} this request based on the following anomalies: ${reasons}`;
      case 'technical':
        return `Jarvis OS Technical Intel: Intercepted call "${action}" targeting system node "${target}" from source IP ${ip} (${loc}). Device configuration is identified as: ${device}. Threat level is assessed at ${risk}%. Swarm response vectors matching: ${reasons}`;
      case 'auditor':
        return `Jarvis OS Auditor Report: Cryptographic fingerprint checks for session trace of ${name} (${role}) validated. Operational action "${action}" was routed to ${target}. The decision to ${status} this operation was made under regulatory guidelines (RBI/GDPR). Log hash: FIN-DNA-${activeEvent.id}-${Math.floor(Math.random()*100000)}. Trace notes: ${reasons}`;
      case 'rbi':
        return `Jarvis OS Regulatory Report (RBI conformity): Privileged action "${action}" targeted critical banking server "${target}". Baseline profile mismatch detected. Zero-trust containment playbook engaged to ${status} operation. Evidence files and geovelocity anomaly details logged under central audit database. Details: ${reasons}`;
      default:
        return "";
    }
  };

  const handleGenerate = () => {
    setIsGenerating(true);
    setBriefText('');
    let index = 0;
    const fullText = getDynamicBrief(audience);
    
    const interval = setInterval(() => {
      setBriefText(prev => prev + fullText.charAt(index));
      index++;
      if (index >= fullText.length) {
        clearInterval(interval);
        setIsGenerating(false);
      }
    }, 10);
  };

  return (
    <div className="flex flex-col h-full w-full border-t border-[rgba(20,20,20,0.06)] bg-white/20">
      <div className="h-14 flex items-center px-4 border-b border-[rgba(20,20,20,0.06)] bg-white/60 shrink-0">
        <Bot className="w-5 h-5 text-[#2563EB] mr-3 animate-pulse" />
        <span className="font-extrabold text-xs uppercase tracking-wider text-[#0F172A]">Jarvis OS Copilot</span>
        <div className="ml-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
          <span className="text-[9px] uppercase font-mono text-[#2563EB] font-bold">Layer 0</span>
        </div>
      </div>

      <div className="flex-grow p-4 space-y-4">
        {/* Audience Selector */}
        <div className="p-4 bg-white border border-[rgba(20,20,20,0.06)] rounded-3xl space-y-3 shadow-soft">
          <div className="text-[10px] uppercase font-bold tracking-wider text-[#64748B]">Audience Selector Dial</div>
          <div className="grid grid-cols-2 gap-1.5 text-[9px] font-mono">
            {(['executive', 'technical', 'auditor', 'rbi'] as Audience[]).map(aud => (
              <button
                key={aud}
                onClick={() => { setAudience(aud); setBriefText(''); }}
                className={`py-1.5 px-2 rounded-xl border uppercase tracking-wider transition-all duration-200 ${
                  audience === aud 
                    ? 'bg-[#2563EB]/10 border-[#2563EB] text-[#2563EB] font-bold' 
                    : 'bg-slate-50 border-[rgba(20,20,20,0.04)] text-[#64748B] hover:bg-slate-100'
                }`}
              >
                {aud}
              </button>
            ))}
          </div>
          <Button 
            onClick={handleGenerate} 
            disabled={isGenerating}
            className="w-full mt-2 bg-[#2563EB] hover:bg-[#2563EB]/95 text-white py-2 text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 rounded-2xl shadow-soft"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Generate Brief
          </Button>
        </div>

        {/* Streaming output */}
        <AnimatePresence mode="wait">
          {briefText && (
            <motion.div 
              key="brief-output"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-white border border-[rgba(20,20,20,0.06)] rounded-3xl space-y-3 font-mono text-[11px] leading-relaxed text-[#0F172A] shadow-soft"
            >
              <div className="flex items-center gap-2 text-[#2563EB] font-bold uppercase tracking-wider text-[9px] border-b border-slate-100 pb-2">
                <FileText className="w-3.5 h-3.5" />
                Briefing ({audience})
              </div>
              <p className="whitespace-pre-wrap leading-relaxed">{briefText}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input Chat Area */}
      <div className="p-4 border-t border-[rgba(20,20,20,0.06)] bg-white/60 shrink-0">
        <div className="relative flex items-center">
          <input 
            type="text" 
            placeholder="Ask Jarvis OS Analyst..." 
            className="w-full bg-slate-100 border border-[rgba(20,20,20,0.06)] rounded-2xl py-2.5 pl-4 pr-10 text-xs focus:outline-none focus:border-[#2563EB]/40 text-[#0F172A] placeholder:text-[#64748B]/50 font-mono"
          />
          <button className="absolute right-2 p-1.5 text-[#2563EB] hover:bg-[#2563EB]/15 rounded-full transition-all">
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="mt-3 flex items-center justify-center gap-2 text-[9px] font-mono text-[#64748B]/60">
          <BrainCircuit className="w-3 h-3 text-[#2563EB] animate-pulse" />
          Cognitive Banking Brain v2.0
        </div>
      </div>
    </div>
  );
}
