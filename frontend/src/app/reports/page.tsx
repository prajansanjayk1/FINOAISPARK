'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { FileText, Download, Cpu } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function ReportsPage() {
  const reports = [
    { title: 'SWIFT Settlement Integrity Audit', type: 'Forensic PDF', date: 'Jul 16, 2026', size: '2.4 MB' },
    { title: 'EU-GDPR Article 32 Geovelocity Log', type: 'Regulatory CSV', date: 'Jul 15, 2026', size: '890 KB' },
    { title: 'Adversarial Swarm Stress Report', type: 'Technical JSON', date: 'Jul 14, 2026', size: '4.1 MB' },
  ];

  return (
    <div className="max-w-[1600px] mx-auto pb-12 p-8 h-full flex flex-col space-y-6 bg-[#F5F7FA] text-[#0F172A] font-mono text-xs">
      <div className="mb-8 flex justify-between items-end border-b border-[rgba(20,20,20,0.06)] pb-6 bg-white/30">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#0F172A] mb-1 flex items-center gap-3">
            <FileText className="w-8 h-8 text-[#2563EB]" />
            Forensic Reports
          </h1>
          <p className="text-sm text-[#64748B]">Download, generate, and view cryptographically verified security audit logs.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft">
            <CardHeader className="border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50 pb-4">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-[#64748B]">
                Available Forensic Logs
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {reports.map((report, i) => (
                <div key={i} className="flex items-center justify-between p-4 border-b border-slate-100 hover:bg-slate-100/40 transition-all cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-slate-100 border border-[rgba(20,20,20,0.06)] text-[#2563EB]">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#0F172A]">{report.title}</div>
                      <div className="text-[9px] text-[#64748B] uppercase font-mono mt-0.5">{report.type} • {report.date}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-[9px] text-[#64748B] font-mono">{report.size}</span>
                    <Button variant="ghost" size="icon" className="w-8 h-8 border border-[rgba(20,20,20,0.06)] hover:bg-slate-100 rounded-xl">
                      <Download className="w-4 h-4 text-[#2563EB]" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 p-6 space-y-4 shadow-soft">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-[#2563EB] animate-pulse" />
              Verifiable Evidence Ledger
            </h3>
            <p className="text-[#64748B] text-[10px] leading-relaxed uppercase">
              All incident containment plans are committed to an immutable cryptographic ledger (Dilithium-6) for multi-party auditor trust verification.
            </p>
            <Button className="w-full bg-[#2563EB] hover:bg-[#2563EB]/95 text-white h-9 text-xs font-bold uppercase tracking-wider shadow-soft rounded-2xl">
              Validate Ledger Integrity
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
}
