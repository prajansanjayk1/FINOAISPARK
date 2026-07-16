const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface BackendPolicy {
  policy_id: string;
  name: string;
  condition: string;
  required_controls: string[];
  enabled: boolean;
}

export interface BackendSimulationResult {
  policy_id: string;
  requests_affected: number;
  false_positives: number;
  expected_security_improvement: string;
  insights: string[];
}

export async function fetchBackendHistory() {
  try {
    const res = await fetch(`${API_BASE_URL}/history`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return await res.json();
  } catch (e) {
    console.warn('FastAPI backend not reachable, using mock fallback. Error:', e);
    return null;
  }
}

export async function fetchBackendDecision(id: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/decision/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch decision ${id}`);
    return await res.json();
  } catch (e) {
    console.warn(`FastAPI backend not reachable for decision ${id}, using mock fallback. Error:`, e);
    return null;
  }
}

export async function fetchBackendPolicies(): Promise<BackendPolicy[] | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/policies`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return await res.json();
  } catch (e) {
    console.warn('FastAPI backend not reachable for policies, using mock fallback. Error:', e);
    return null;
  }
}

export async function saveBackendPolicy(policy: BackendPolicy) {
  try {
    const res = await fetch(`${API_BASE_URL}/policies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(policy),
    });
    if (!res.ok) throw new Error('Failed to save policy');
    return await res.json();
  } catch (e) {
    console.warn('FastAPI backend not reachable for saving policy. Error:', e);
    return null;
  }
}

export async function simulateBackendPolicy(policy: BackendPolicy): Promise<BackendSimulationResult | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/policies/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(policy),
    });
    if (!res.ok) throw new Error('Failed to run simulation');
    return await res.json();
  } catch (e) {
    console.warn('FastAPI backend not reachable for policy simulation. Error:', e);
    return null;
  }
}

export async function evaluateBackendRequest(requestPayload: any) {
  try {
    const res = await fetch(`${API_BASE_URL}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestPayload),
    });
    if (!res.ok) throw new Error('Failed to evaluate request');
    return await res.json();
  } catch (e) {
    console.warn('FastAPI backend not reachable for evaluate. Error:', e);
    return null;
  }
}
