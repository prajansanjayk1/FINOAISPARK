'use client';

import { useMockStore } from '@/store/useMockStore';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Activity, AlertTriangle, Landmark, CreditCard, Users, Clock, ArrowDownToLine, Zap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function BusinessImpactEngine() {
  const { activeEvent } = useMockStore();

  const services = [
    { name: 'Core Banking', impact: 100, status: 'Critical Failure', icon: Landmark },
    { name: 'UPI / Payments', impact: 85, status: 'Severe Degradation', icon: Zap },
    { name: 'Internet Banking', impact: 90, status: 'Offline', icon: Activity },
    { name: 'ATM Network', impact: 40, status: 'Partial Outage', icon: CreditCard },
  ];

  const chartData = [
    { time: 'T+0', loss: 0 },
    { time: 'T+15m', loss: 2.5 },
    { time: 'T+30m', loss: 6.8 },
    { time: 'T+45m', loss: 10.2 },
    { time: 'T+60m', loss: 14.5 },
  ];

  if (!activeEvent) return null;

  const isRejected = activeEvent.status === 'rejected';

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <Activity className="w-6 h-6 text-primary" />
          Business Impact Simulation
        </h2>
        <p className="text-muted-foreground mt-1 text-sm">
          Predictive blast radius analysis for <span className="font-mono text-primary">{activeEvent.action}</span> on <span className="font-mono text-primary">{activeEvent.target}</span>.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass-panel border-destructive/30 bg-destructive/5 relative overflow-hidden group">
          <div className="absolute inset-0 bg-destructive/10 animate-pulse opacity-50" />
          <CardContent className="p-6 relative z-10">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 rounded bg-destructive/20 text-destructive"><AlertTriangle className="w-5 h-5"/></div>
            </div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Financial Exposure</p>
            <h3 className="text-3xl font-bold text-destructive">${(activeEvent.financialExposure / 1000000).toFixed(1)}M</h3>
            <p className="text-xs text-destructive/80 mt-1 font-mono">Estimated loss per hour</p>
          </CardContent>
        </Card>
        
        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 rounded bg-warning/20 text-warning"><Users className="w-5 h-5"/></div>
            </div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Customers Affected</p>
            <h3 className="text-3xl font-bold text-foreground">1.2M+</h3>
            <p className="text-xs text-muted-foreground mt-1 font-mono">Across EU region</p>
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 rounded bg-primary/20 text-primary"><Clock className="w-5 h-5"/></div>
            </div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Recovery Time (RTO)</p>
            <h3 className="text-3xl font-bold text-foreground">4h 15m</h3>
            <p className="text-xs text-muted-foreground mt-1 font-mono">Database restore from cold backup</p>
          </CardContent>
        </Card>

        <Card className="glass-panel border-primary/30">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 rounded bg-primary/20 text-primary"><ArrowDownToLine className="w-5 h-5"/></div>
            </div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Final Recommendation</p>
            <h3 className="text-xl font-bold text-foreground mt-2">DO NOT EXECUTE</h3>
            <p className="text-xs text-primary mt-1 font-mono">Catastrophic risk detected</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-panel">
          <CardHeader className="border-b border-border bg-gray-50">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Service Availability Prediction</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {services.map((service, idx) => (
              <div key={service.name} className="flex items-center justify-between p-4 border-b border-border hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-md bg-gray-50 text-muted-foreground"><service.icon className="w-4 h-4"/></div>
                  <div>
                    <div className="text-sm font-medium text-foreground">{service.name}</div>
                    <div className="text-xs font-mono text-destructive">{service.status}</div>
                  </div>
                </div>
                <div className="w-32">
                  <div className="flex justify-between text-[10px] mb-1">
                    <span className="text-muted-foreground">Availability</span>
                    <span className="text-destructive font-mono font-semibold">{100 - service.impact}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-50 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-destructive"
                      initial={{ width: '100%' }}
                      animate={{ width: `${100 - service.impact}%` }}
                      transition={{ delay: 0.5 + (idx * 0.2), duration: 1 }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardHeader className="border-b border-border bg-gray-50">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Financial Loss Trajectory</CardTitle>
          </CardHeader>
          <CardContent className="p-6 h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="time" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}M`} />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: 'rgba(10,15,26,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#e11d48', fontWeight: 'bold' }}
                />
                <Bar dataKey="loss" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === chartData.length - 1 ? '#e11d48' : 'rgba(225,29,72,0.5)'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
