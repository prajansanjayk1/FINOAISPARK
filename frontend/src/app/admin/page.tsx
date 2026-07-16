'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Building, Users, Key, MonitorSmartphone, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function AdminPage() {
  const users = [
    { name: 'Sarah Chen', role: 'Database Administrator', status: 'Active', lastLogin: '10m ago' },
    { name: 'Marcus Wong', role: 'System Reliability Engineer', status: 'Active', lastLogin: '1h ago' },
    { name: 'David Smith', role: 'L1 SOC Analyst', status: 'Suspended', lastLogin: '14d ago' },
  ];

  return (
    <div className="max-w-[1600px] mx-auto pb-12 p-8 h-full flex flex-col space-y-6 bg-[#F5F7FA] text-[#0F172A] font-mono text-xs">
      <div className="mb-8 flex justify-between items-end border-b border-[rgba(20,20,20,0.06)] pb-6 bg-white/30">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#0F172A] mb-1 flex items-center gap-3">
            <Building className="w-8 h-8 text-[#2563EB]" />
            Administration
          </h1>
          <p className="text-sm text-[#64748B]">Manage platform users, roles, connected assets, and system configurations.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-2">
          <Button variant="ghost" className="w-full justify-start bg-[#2563EB]/10 text-[#2563EB] border border-[#2563EB]/25 hover:bg-[#2563EB]/15 rounded-2xl py-2.5 font-bold uppercase tracking-wider text-xs">
            <Users className="w-4 h-4 mr-3" /> User Management
          </Button>
          <Button variant="ghost" className="w-full justify-start text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100 rounded-2xl py-2.5 font-bold uppercase tracking-wider text-xs">
            <Key className="w-4 h-4 mr-3" /> Role & Permissions
          </Button>
          <Button variant="ghost" className="w-full justify-start text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100 rounded-2xl py-2.5 font-bold uppercase tracking-wider text-xs">
            <MonitorSmartphone className="w-4 h-4 mr-3" /> Connected Assets
          </Button>
          <Button variant="ghost" className="w-full justify-start text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100 rounded-2xl py-2.5 font-bold uppercase tracking-wider text-xs">
            <Settings className="w-4 h-4 mr-3" /> System Preferences
          </Button>
        </div>

        <div className="lg:col-span-3 space-y-6">
          <Card className="glass-panel border border-[rgba(20,20,20,0.06)] bg-white/80 shadow-soft">
            <CardHeader className="border-b border-[rgba(20,20,20,0.06)] bg-slate-50/50 pb-4 flex flex-row items-center justify-between">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-[#64748B]">
                Active Personnel
              </CardTitle>
              <Button size="sm" className="bg-[#2563EB] hover:bg-[#2563EB]/95 text-white h-8 text-xs font-bold uppercase tracking-wider rounded-xl shadow-soft">Add User</Button>
            </CardHeader>
            <CardContent className="p-0">
              <div className="grid grid-cols-12 gap-4 p-4 border-b border-[rgba(20,20,20,0.06)] text-[9px] font-bold uppercase tracking-wider text-[#64748B] bg-slate-50/50">
                <div className="col-span-4">User</div>
                <div className="col-span-4">Role</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-2 text-right">Last Login</div>
              </div>
              {users.map((user, i) => (
                <div key={i} className="grid grid-cols-12 gap-4 p-4 border-b border-slate-100 items-center hover:bg-slate-100/40 transition-colors cursor-pointer">
                  <div className="col-span-4 font-bold text-xs text-[#0F172A] flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-slate-100 flex items-center justify-center text-[#2563EB] font-bold border border-[rgba(20,20,20,0.06)]">
                      {user.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    {user.name}
                  </div>
                  <div className="col-span-4 text-xs text-[#64748B]">{user.role}</div>
                  <div className="col-span-2">
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${
                      user.status === 'Active' ? 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/30' : 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30'
                    }`}>
                      {user.status}
                    </span>
                  </div>
                  <div className="col-span-2 text-right text-xs font-mono text-[#64748B]">
                    {user.lastLogin}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
