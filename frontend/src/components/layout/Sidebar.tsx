'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Shield, Activity, Search, Database, Fingerprint, Network, Settings, Building, Menu } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useState } from 'react';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { href: '/', icon: Activity, label: 'Mission Control' },
  { href: '/council', icon: Network, label: 'AI Council' },
  { href: '/investigation', icon: Search, label: 'Investigations' },
  { href: '/intelligence', icon: Database, label: 'AI Lab' },
  { href: '/governance', icon: Shield, label: 'Governance' },
  { href: '/reports', icon: Fingerprint, label: 'Reports' },
  { href: '/admin', icon: Building, label: 'Administration' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={cn(
      "flex flex-col bg-[#EEF2F7] border-r border-[rgba(20,20,20,0.06)] h-screen sticky top-0 transition-all duration-300 z-50",
      collapsed ? "w-20" : "w-64"
    )}>
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-[rgba(20,20,20,0.06)] bg-white/40">
        <div className="flex items-center gap-3 overflow-hidden">
          <Shield className="w-5 h-5 text-[#2563EB] shrink-0" />
          {!collapsed && (
            <span className="font-semibold text-sm tracking-widest text-[#0F172A] uppercase font-sans">
              FINSPARK CORE
            </span>
          )}
        </div>
        <button 
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-black/5 text-[#64748B] transition-colors"
        >
          <Menu className="w-4 h-4" />
        </button>
      </div>
      
      {/* Navigation list */}
      <div className="flex-1 py-6 flex flex-col gap-1.5 px-4 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center px-3 py-2.5 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-200",
                isActive 
                  ? "bg-white text-[#2563EB] shadow-soft border border-[rgba(20,20,20,0.04)]" 
                  : "text-[#64748B] hover:bg-white/50 hover:text-[#0F172A]"
              )}
            >
              <item.icon className={cn("w-4 h-4 shrink-0", collapsed ? "mx-auto" : "mr-3", isActive ? "text-[#2563EB]" : "text-[#64748B]")} />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </div>

      {/* Footer System Config */}
      <div className="p-4 border-t border-[rgba(20,20,20,0.06)] bg-white/20">
        <button className="flex items-center w-full px-3 py-2.5 rounded-xl text-xs font-semibold uppercase tracking-wider text-[#64748B] hover:bg-white/50 hover:text-[#0F172A] transition-colors">
          <Settings className={cn("w-4 h-4 shrink-0", collapsed ? "mx-auto" : "mr-3")} />
          {!collapsed && <span>Config</span>}
        </button>
      </div>
    </div>
  );
}
