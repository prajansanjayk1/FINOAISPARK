'use client';

import { useMockStore } from '@/store/useMockStore';
import { Card } from '@/components/ui/card';
import { ShieldAlert, CheckCircle2, ChevronRight, XCircle, Search, Filter } from 'lucide-react';

export function PrivilegedRequestTable() {
  const { liveEvents, setActiveEvent } = useMockStore();

  return (
    <Card className="glass-panel overflow-hidden flex flex-col h-[calc(100vh-200px)]">
      {/* Toolbar */}
      <div className="p-4 border-b border-border flex items-center justify-between bg-gray-50">
        <div className="flex gap-4 items-center w-full max-w-md">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search by ID, Actor, or Target..."
              className="w-full bg-gray-50 border border-border rounded-md py-1.5 pl-9 pr-3 text-sm focus:outline-none focus:border-primary/50 text-foreground"
            />
          </div>
          <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-muted-foreground border border-border rounded-md hover:bg-gray-50 transition-colors">
            <Filter className="w-4 h-4" /> Filters
          </button>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-12 gap-4 p-4 border-b border-border text-xs font-semibold uppercase tracking-wider text-muted-foreground bg-gray-50">
        <div className="col-span-2">Event ID</div>
        <div className="col-span-2">Requester</div>
        <div className="col-span-2">Target Asset</div>
        <div className="col-span-2">Action</div>
        <div className="col-span-2">AI Recommendation</div>
        <div className="col-span-2 text-right">Time</div>
      </div>

      {/* Table Body */}
      <div className="flex-1 overflow-y-auto">
        {liveEvents.map((event) => (
          <div 
            key={event.id}
            onClick={() => setActiveEvent(event)}
            className="grid grid-cols-12 gap-4 p-4 border-b border-border items-center hover:bg-white/[0.03] cursor-pointer transition-colors group"
          >
            <div className="col-span-2 font-mono text-sm text-primary/80 group-hover:text-primary transition-colors flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" />
              {event.id}
            </div>
            
            <div className="col-span-2">
              <div className="text-sm font-medium text-foreground">{event.actor.name}</div>
              <div className="text-xs text-muted-foreground line-clamp-1">{event.actor.role}</div>
            </div>
            
            <div className="col-span-2">
              <div className="text-sm font-mono bg-gray-50 px-2 py-0.5 rounded text-foreground/80 inline-block truncate max-w-full">
                {event.target}
              </div>
            </div>
            
            <div className="col-span-2 text-sm text-foreground/80">{event.action}</div>
            
            <div className="col-span-2 flex items-center gap-2">
              {event.status === 'approved' && <CheckCircle2 className="w-4 h-4 text-success" />}
              {event.status === 'rejected' && <XCircle className="w-4 h-4 text-destructive" />}
              {event.status === 'pending' && <span className="w-2 h-2 rounded-full bg-warning animate-pulse" />}
              <span className={`text-sm font-medium ${
                event.status === 'approved' ? 'text-success' : 
                event.status === 'rejected' ? 'text-destructive' : 'text-warning'
              }`}>
                {event.status === 'approved' ? 'Safe to Execute' : 
                 event.status === 'rejected' ? 'Block & Investigate' : 'Evaluating...'}
              </span>
            </div>
            
            <div className="col-span-2 flex items-center justify-end gap-4 text-sm text-muted-foreground">
              {new Date(event.timestamp).toLocaleTimeString()}
              <ChevronRight className="w-4 h-4 text-muted-foreground/50 group-hover:text-primary transition-colors" />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
