import { HealthStatus, ChatRequestPayload, ChatResponsePayload } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth(): Promise<HealthStatus> {
  const resp = await fetch(`${API_BASE_URL}/api/v1/health`, {
    headers: { 'Accept': 'application/json' },
  });
  if (!resp.ok) {
    throw new Error(`Health check failed with HTTP ${resp.status}`);
  }
  return resp.json();
}

export async function sendChatMessage(payload: ChatRequestPayload): Promise<ChatResponsePayload> {
  const resp = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const errorText = await resp.text();
    throw new Error(`Server returned status ${resp.status}: ${errorText || resp.statusText}`);
  }

  return resp.json();
}
