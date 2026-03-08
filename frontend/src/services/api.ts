const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp: number;
}

export interface ChatResponse {
  conversation_id: string;
  message: ChatMessage;
  tools_used: string[];
  plan: { title: string; status: string }[] | null;
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

export async function getTools(): Promise<ToolInfo[]> {
  const res = await fetch(`${API_URL}/api/tools`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data = await res.json();
  return data.tools;
}

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
