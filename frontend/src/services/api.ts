const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp: number;
}

export interface LearningInfo {
  source: string;
  confidence: number;
  learning_info: string;
  state: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: ChatMessage;
  tools_used: string[];
  plan: { title: string; status: string }[] | null;
  learning_info: LearningInfo;
}

export interface ToolInfo {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export interface AgentInfo {
  name: string;
  version: string;
  model: string;
  tools: string[];
  capabilities: string[];
}

export interface MemoryStats {
  rules_learned: number;
  vocabulary_size: number;
  facts_known: number;
  total_interactions: number;
  q_table_entries: number;
  average_reward: number;
  exploration_rate: number;
  stm_size: number;
  last_source: string;
  db_path: string;
}

export interface RuleInfo {
  pattern: string;
  action: string;
  confidence: number;
  times_used: number;
}

export interface MemoryResponse {
  stats: MemoryStats;
  rules: RuleInfo[];
  vocabulary: { word: string; meaning: string; times_seen: number }[];
}

export interface RewardResponse {
  learned: boolean;
  message: string;
  state: string;
  action: string;
  reward: number;
  new_epsilon: number;
  rule?: { pattern: string; action: string };
}

// ---- Chat ----

export async function sendMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// ---- Learning / Reward ----

export async function sendReward(value: number): Promise<RewardResponse> {
  const res = await fetch(`${API_URL}/api/reward`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getMemory(): Promise<MemoryResponse> {
  const res = await fetch(`${API_URL}/api/memory`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function resetMemory(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_URL}/api/memory/reset`, { method: "POST" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getLearningState(): Promise<MemoryStats> {
  const res = await fetch(`${API_URL}/api/learning/state`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// ---- Tools ----

export async function getTools(): Promise<ToolInfo[]> {
  const res = await fetch(`${API_URL}/api/tools`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data = await res.json();
  return data.tools;
}

// ---- Agent ----

export async function getAgentInfo(): Promise<AgentInfo> {
  const res = await fetch(`${API_URL}/api/agent`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/healthz`);
    return res.ok;
  } catch {
    return false;
  }
}
