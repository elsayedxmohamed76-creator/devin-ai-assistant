import { useState, useCallback } from "react";
import { sendMessage, sendReward, ChatMessage, LearningInfo, RewardResponse } from "../services/api";

interface UseChatReturn {
  messages: ChatMessage[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
  send: (message: string) => Promise<void>;
  clear: () => void;
  toolsUsed: string[];
  learningInfo: LearningInfo | null;
  lastRewardResult: RewardResponse | null;
  reward: (value: number) => Promise<void>;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toolsUsed, setToolsUsed] = useState<string[]>([]);
  const [learningInfo, setLearningInfo] = useState<LearningInfo | null>(null);
  const [lastRewardResult, setLastRewardResult] = useState<RewardResponse | null>(null);

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
      setLastRewardResult(null);

      try {
        const response = await sendMessage(message, conversationId || undefined);
        setConversationId(response.conversation_id);
        setMessages((prev) => [...prev, response.message]);
        setToolsUsed(response.tools_used);
        setLearningInfo(response.learning_info);
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : "Failed to send message";
        setError(errMsg);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  const reward = useCallback(async (value: number) => {
    try {
      const result = await sendReward(value);
      setLastRewardResult(result);
      // Add reward result as a system message
      if (result.message) {
        const sysMsg: ChatMessage = {
          role: "system",
          content: result.message,
          timestamp: Date.now() / 1000,
        };
        setMessages((prev) => [...prev, sysMsg]);
      }
    } catch (err) {
      console.error("Failed to send reward:", err);
    }
  }, []);

  const clear = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setToolsUsed([]);
    setLearningInfo(null);
    setLastRewardResult(null);
  }, []);

  return {
    messages, conversationId, isLoading, error,
    send, clear, toolsUsed, learningInfo, lastRewardResult, reward,
  };
}
