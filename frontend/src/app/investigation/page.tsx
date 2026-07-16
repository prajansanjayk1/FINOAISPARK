'use client';

import { useEffect } from 'react';
import { useMockStore } from '@/store/useMockStore';
import { PrivilegedRequestTable } from '@/components/investigation/PrivilegedRequestTable';
import { IncidentWorkspace } from '@/components/investigation/IncidentWorkspace';
import { AnimatePresence, motion } from 'framer-motion';

export default function InvestigationPage() {
  const { activeEvent, fetchEvents } = useMockStore();

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return (
    <div className="h-full relative overflow-hidden">
      <AnimatePresence mode="wait">
        {!activeEvent ? (
          <motion.div
            key="table"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.4 }}
            className="h-full p-8"
          >
            <div className="mb-8">
              <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">Privileged Request Center</h1>
              <p className="text-muted-foreground">Global queue of intercepted privileged operations requiring human adjudication.</p>
            </div>
            <PrivilegedRequestTable />
          </motion.div>
        ) : (
          <motion.div
            key="workspace"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5, ease: "circOut" }}
            className="h-full"
          >
            <IncidentWorkspace />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
