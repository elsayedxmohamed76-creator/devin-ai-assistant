import { useState, useCallback } from "react";
import { sendMessage, ChatMessage } from "../services/api";

interface UseChatReturn {
  messages: ChatMessage[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
  send: (message: string) => Promise<void>;
  clear: () => void;
  toolsUsed: string[];
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toolsUsed, setToolsUsed] = useState<string[]>([]);

  const send = useCallback(
    async (message: string) => {
      const userMsg: ChatMessage = {
        role: "user",
        content: message,
        timestamp: Date.now() / 1000,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendMessage(message, conversationId || undefined);
        setConversationId(response.conversation_id);
        setMessages((prev) => [...prev, response.message]);
        setToolsUsed(response.tools_used);
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : "Failed to send message";
        setError(errMsg);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  const clear = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setToolsUsed([]);
  }, []);

  return { messages, conversationId, isLoading, error, send, clear, toolsUsed };
}
