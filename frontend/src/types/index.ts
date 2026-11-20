export interface Citation {
  chunk_id: string;
  domain: string;
  source_url: string;
  section: string;
  quote: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  citations?: Citation[];
  grounded?: boolean;
  modelUsed?: string;
  isError?: boolean;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  vector_store_ready: boolean;
  total_chunks: number;
  openrouter_configured: boolean;
  model_name: string;
}

export interface ChatRequestPayload {
  message: string;
  history: Array<{ role: string; content: string }>;
  top_k?: number;
}

export interface ChatResponsePayload {
  answer: string;
  citations: Citation[];
  grounded: boolean;
  model_used: string;
}
