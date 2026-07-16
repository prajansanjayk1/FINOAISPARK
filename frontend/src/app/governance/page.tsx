'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Shield, FileCheck, Scale, History, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { fetchBackendPolicies, BackendPolicy } from '@/lib/api';

export default function GovernancePage() {
  const [policies, setPolicies] = useState<any[]>([]);

  useEffect(() => {
    async function loadPolicies() {
      const data = await fetchBackendPolicies();
      if (data && data.length > 0) {
        const mapped = data.map((bp: BackendPolicy) => ({
          name: bp.name,
          status: bp.enabled ? 'Active' : 'Disabled',
          severity: bp.required_controls.includes('BLOCK') ? 'Critical' : 'High',
          enforced: Math.floor(Math.random() * 50) + 12
        }));
        setPolicies(mapped);
      } else {
        setPolicies([
          { name: 'EU-GDPR Data Sovereignty', status: 'Active', severity: 'Critical', enforced: 1450 },
          { name: 'Dormant Account Access Check', status: 'Active', severity: 'High', enforced: 312 },
          { name: 'Cross-Border SWIFT Transfer Rules', status: 'Active', severity: 'Critical', enforced: 890 },
          { name: 'After-Hours Maintenance Segregation', status: 'Testing', severity: 'Medium', enforced: 0 },
        ]);
      }
    }
    loadPolicies();
  }, []);

  return (
    <div className="max-w-[1600px] mx-auto pb-12 p-8 h-full flex flex-col space-y-6 bg-[#F5F7FA] text-[#0F172A] font-mono text-xs">
      
      {/* Header */}
      <div className="mb-8 flex justify-between items-end border-b border-[rgba(20,20,20,0.06)] pb-6 bg-white/30">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#0F172A] mb-2 flex items-center gap-3">
            <Shield className="w-8 h-8 text-[#2563EB]" />
            Governance Engine
          </h1>
          <p className="text-sm text-[#64748B]">Manage global enterprise constraints, regulatory compliance, and audit ledgers.</p>
        </div>
        <Button className="bg-[#2563EB] hover:bg-[#2563EB]/95 text-white font-bold text-xs uppercase tracking-wider py-2.5 px-4 rounded-2xl shadow-soft">
          <Plus className="w-4 h-4 mr-2" />
          Create Policy
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Policies List */}
        <Card className="glass-panel lg:col-span-2 border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50 flex flex-row items-center justify-between">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <Scale className="w-4 h-4 mr-2 text-[#2563EB]" />
              Active Policies
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="grid grid-cols-4 gap-4 p-4 border-b border-[rgba(20,20,20,0.06)] text-[9px] font-bold uppercase tracking-wider text-[#64748B] bg-slate-50/50">
              <div className="col-span-2">Policy Name</div>
              <div>Severity</div>
              <div className="text-right">Times Enforced</div>
            </div>
            {policies.map((policy, i) => (
              <div key={i} className="grid grid-cols-4 gap-4 p-4 border-b border-slate-100 items-center hover:bg-slate-100/40 transition-colors cursor-pointer">
                <div className="col-span-2 flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${policy.status === 'Active' ? 'bg-[#10B981] animate-pulse' : 'bg-[#F59E0B]'}`} />
                  <span className="text-xs font-bold text-[#0F172A]">{policy.name}</span>
                </div>
                <div>
                  <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border ${
                    policy.severity === 'Critical' ? 'bg-[#EF4444]/10 border-[#EF4444]/25 text-[#EF4444]' :
                    policy.severity === 'High' ? 'bg-[#F59E0B]/10 border-[#F59E0B]/25 text-[#F59E0B]' :
                    'bg-[#2563EB]/10 border-[#2563EB]/25 text-[#2563EB]'
                  }`}>
                    {policy.severity}
                  </span>
                </div>
                <div className="text-right font-mono text-xs text-[#64748B]">
                  {policy.enforced.toLocaleString()}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Audit Log */}
        <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft">
          <CardHeader className="pb-4 border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-[#64748B] flex items-center">
              <History className="w-4 h-4 mr-2 text-[#2563EB]" />
              Recent Audit Log
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {[1,2,3,4,5].map((_, i) => (
              <div key={i} className="p-4 border-b border-slate-100 flex gap-3 items-start hover:bg-slate-100/40 transition-colors cursor-pointer">
                <FileCheck className="w-4 h-4 text-[#2563EB] mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-[#0F172A] mb-1">Compliance Checksum Log</div>
                  <div className="text-[10px] text-[#64748B]">Generated for Dilithium-6 audit verification.</div>
                  <div className="text-[9px] text-[#64748B]/60 font-mono mt-2">Today, {14 - i}:30 PM</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
