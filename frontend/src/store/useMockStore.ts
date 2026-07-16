import { create } from 'zustand';
import { fetchBackendHistory, fetchBackendDecision } from '@/lib/api';

export type AgentStatus = 'idle' | 'analyzing' | 'approved' | 'rejected' | 'warning';

export interface GovernanceEvent {
  id: string;
  timestamp: string;
  actor: {
    name: string;
    role: string;
    avatar?: string;
    ip: string;
    device: string;
    location: string;
  };
  action: string;
  target: string;
  status: 'pending' | 'approved' | 'rejected';
  riskScore: number;
  financialExposure: number;
  agents: {
    identity: AgentStatus;
    behaviour: AgentStatus;
    compliance: AgentStatus;
    impact: AgentStatus;
    quantum: AgentStatus;
  };
  reasoning: string[];
  rawVerdict?: any; // To store the full payload from backend
}

interface MockStore {
  liveEvents: GovernanceEvent[];
  activeEvent: GovernanceEvent | null;
  setActiveEvent: (event: GovernanceEvent | null) => void;
  addEvent: (event: GovernanceEvent) => void;
  investigationView: 'overview' | 'evidence' | 'impact' | 'sandbox' | 'twin';
  setInvestigationView: (view: 'overview' | 'evidence' | 'impact' | 'sandbox' | 'twin') => void;
  isFetching: boolean;
  fetchEvents: () => Promise<void>;
  timeMachineIndex: number;
  setTimeMachineIndex: (index: number) => void;
  scenarioMultiplier: number;
  setScenarioMultiplier: (mult: number) => void;
}

const DEFAULT_MOCK_EVENTS: GovernanceEvent[] = [
  {
    id: 'EVT-8923-B',
    timestamp: new Date().toISOString(),
    actor: { 
      name: 'Sarah Chen', 
      role: 'Database Administrator',
      ip: '192.168.45.12',
      device: 'MacBook Pro 16" (Managed)',
      location: 'London, UK (VPN)'
    },
    action: 'DROP TABLE',
    target: 'prod_transactions_eu',
    status: 'rejected',
    riskScore: 98,
    financialExposure: 14500000,
    agents: {
      identity: 'approved',
      behaviour: 'warning',
      compliance: 'rejected',
      impact: 'rejected',
      quantum: 'approved'
    },
    reasoning: [
      'Unprecedented DROP TABLE command outside maintenance window.',
      'Financial exposure exceeds $10M threshold for single-operator actions.',
      'Data sovereignty policy violation (EU-GDPR tier 1 data).'
    ]
  },
  {
    id: 'EVT-8924-A',
    timestamp: new Date(Date.now() - 5000).toISOString(),
    actor: { 
      name: 'Marcus Wong', 
      role: 'System Reliability Engineer',
      ip: '10.0.4.55',
      device: 'ThinkPad X1 (Managed)',
      location: 'Singapore (Office)'
    },
    action: 'UPDATE FIREWALL_RULE',
    target: 'fw_node_apac_3',
    status: 'approved',
    riskScore: 12,
    financialExposure: 0,
    agents: {
      identity: 'approved',
      behaviour: 'approved',
      compliance: 'approved',
      impact: 'approved',
      quantum: 'approved'
    },
    reasoning: [
      'Standard operational baseline verified.',
      'No business disruption detected.',
    ]
  }
];

export const useMockStore = create<MockStore>((set, get) => ({
  investigationView: 'overview',
  setInvestigationView: (view) => set({ investigationView: view }),
  liveEvents: DEFAULT_MOCK_EVENTS,
  activeEvent: null,
  timeMachineIndex: 5,
  setTimeMachineIndex: (index) => set({ timeMachineIndex: index }),
  scenarioMultiplier: 1.0,
  setScenarioMultiplier: (mult) => set({ scenarioMultiplier: mult }),
  isFetching: false,
  setActiveEvent: (event) => set({ activeEvent: event, timeMachineIndex: 5 }), // reset time machine to end step when swapping events
  addEvent: (event) => set((state) => ({ liveEvents: [event, ...state.liveEvents] })),
  
  fetchEvents: async () => {
    if (get().isFetching) return;
    set({ isFetching: true });
    try {
      const historyList = await fetchBackendHistory();
      if (historyList && Array.isArray(historyList) && historyList.length > 0) {
        // Map backend history items to GovernanceEvent models
        const mappedEvents = await Promise.all(
          historyList.map(async (item: any) => {
            const detail = await fetchBackendDecision(item.id);
            
            let statusStr: 'pending' | 'approved' | 'rejected' = 'approved';
            if (item.decision === 'BLOCK') {
              statusStr = 'rejected';
            } else if (item.decision === 'ALLOW_APPROVAL') {
              statusStr = 'pending';
            }

            let reasoningLines = [
              `Governance consensus ruling resolved: ${item.decision}.`,
              `Tally agreement: ${item.agreement || '8/8 votes'}.`
            ];
            
            const agentStatuses = {
              identity: 'approved' as AgentStatus,
              behaviour: 'approved' as AgentStatus,
              compliance: 'approved' as AgentStatus,
              impact: 'approved' as AgentStatus,
              quantum: 'approved' as AgentStatus
            };

            if (detail) {
              if (detail.executive_view) {
                reasoningLines = [
                  detail.executive_view.reason,
                  detail.executive_view.business_impact,
                  `Governance directive: ${detail.executive_view.recommended_action}`
                ];
              }
              
              if (detail.analyst_view && detail.analyst_view.agent_responses) {
                detail.analyst_view.agent_responses.forEach((resp: any) => {
                  const name = resp.agent_name.toLowerCase();
                  let fStatus: AgentStatus = 'approved';
                  if (resp.vote === 'BLOCK') fStatus = 'rejected';
                  else if (resp.vote === 'ALLOW_APPROVAL') fStatus = 'warning';
                  else if (resp.vote === 'ALLOW_SANDBOX') fStatus = 'warning';

                  if (name.includes('identity')) agentStatuses.identity = fStatus;
                  else if (name.includes('behavior')) agentStatuses.behaviour = fStatus;
                  else if (name.includes('compliance')) agentStatuses.compliance = fStatus;
                  else if (name.includes('business') || name.includes('impact')) agentStatuses.impact = fStatus;
                  else if (name.includes('quantum')) agentStatuses.quantum = fStatus;
                });
              }
            }

            return {
              id: item.id,
              timestamp: item.timestamp,
              actor: {
                name: item.username || 'Admin Operator',
                role: item.role || 'Administrator',
                ip: '10.12.90.15',
                device: 'Secure Workstation',
                location: 'Main Banking Subnet'
              },
              action: item.command || item.action_type,
              target: item.target_system || 'Target node',
              status: statusStr,
              riskScore: 100 - (item.confidence || 90),
              financialExposure: 1200000,
              agents: agentStatuses,
              reasoning: reasoningLines,
              rawVerdict: detail
            };
          })
        );
        
        set({ liveEvents: mappedEvents });
      } else {
        // Fallback to default mock events if history is empty
        set({ liveEvents: DEFAULT_MOCK_EVENTS });
      }
    } catch (e) {
      console.warn("Failed to fetch events from FastAPI, fallback to mock data.", e);
      set({ liveEvents: DEFAULT_MOCK_EVENTS });
    } finally {
      set({ isFetching: false });
    }
  }
}));
