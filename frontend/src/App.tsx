import { useState, useRef, useEffect } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessageComponent from "./components/chat/ChatMessage";
import ChatInput from "./components/chat/ChatInput";
import ToolBadge from "./components/chat/ToolBadge";
import RewardButtons from "./components/chat/RewardButtons";
import Sidebar from "./components/chat/Sidebar";
import ToolsPanel from "./components/chat/ToolsPanel";
import InfoPanel from "./components/chat/InfoPanel";
import MemoryPanel from "./components/MemoryPanel";
import { Bot, Code, Terminal, Search, ListTodo, Brain } from "lucide-react";

function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-6">
      <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25 animate-pulse">
        <Brain className="w-10 h-10 text-white" />
      </div>
      <h2 className="text-3xl font-bold text-white mb-2">
        Devin AI Assistant
      </h2>
      <p className="text-gray-400 mb-2 text-sm">
        🧠 Motore Neuro-Simbolico • Impara da te
      </p>
      <p className="text-gray-500 mb-8 max-w-md text-sm">
        Sono un'IA che impara dalle tue interazioni. Più mi insegni con 👍 e 👎, più divento intelligente.
        Non dimentico mai quello che imparo!
      </p>
      <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
        {[
          { icon: <Code className="w-5 h-5" />, label: "Leggi & Scrivi Codice", desc: "File reali sul tuo PC" },
          { icon: <Terminal className="w-5 h-5" />, label: "Esegui Comandi", desc: "PowerShell integrato" },
          { icon: <Search className="w-5 h-5" />, label: "Cerca nel Codice", desc: "Regex across files" },
          { icon: <ListTodo className="w-5 h-5" />, label: "Impara & Ricorda", desc: "Memoria permanente" },
        ].map((item) => (
          <div
            key={item.label}
            className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 text-left hover:border-purple-500/30 transition-colors"
          >
            <div className="text-purple-400 mb-2">{item.icon}</div>
            <h3 className="text-sm font-semibold text-white">{item.label}</h3>
            <p className="text-xs text-gray-400 mt-0.5">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function App() {
  const { messages, isLoading, error, send, clear, toolsUsed, learningInfo, reward } = useChat();
  const [activePanel, setActivePanel] = useState("chat");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleNewChat = () => {
    clear();
    setActivePanel("chat");
  };

  const panelTitles: Record<string, string> = {
    chat: "Chat",
    tools: "Strumenti",
    info: "Info",
    memory: "Cervello",
  };

  return (
    <div className="h-screen flex bg-gray-950 text-white overflow-hidden">
      {/* Sidebar */}
      <div className="flex-shrink-0 z-40 bg-gray-900 border-r border-gray-800">
        <Sidebar
          onNewChat={handleNewChat}
          onShowTools={() => setActivePanel("tools")}
          onShowInfo={() => setActivePanel("info")}
          onShowMemory={() => setActivePanel("memory")}
          activePanel={activePanel}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b border-gray-700 bg-gray-900/80 backdrop-blur-sm px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3 ml-10 lg:ml-0">
            <Bot className="w-5 h-5 text-purple-400" />
            <h1 className="text-lg font-semibold text-white">
              {panelTitles[activePanel] || "Chat"}
            </h1>
            {learningInfo && activePanel === "chat" && (
              <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">
                {learningInfo.learning_info}
              </span>
            )}
          </div>
          {activePanel === "chat" && messages.length > 0 && (
            <button
              onClick={handleNewChat}
              className="text-xs text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-gray-700 hover:border-gray-500 transition-colors"
            >
              Clear Chat
            </button>
          )}
        </header>

        {/* Content Area */}
        {activePanel === "chat" ? (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4">
              {messages.length === 0 ? (
                <WelcomeScreen />
              ) : (
                <div className="max-w-4xl mx-auto">
                  {messages.map((msg, i) => (
                    <div key={i}>
                      <ChatMessageComponent message={msg} />
                      {/* Show reward buttons after each AI response */}
                      {msg.role === "assistant" && i === messages.length - 1 && (
                        <RewardButtons onReward={reward} disabled={isLoading} />
                      )}
                    </div>
                  ))}
                  {toolsUsed.length > 0 && <ToolBadge tools={toolsUsed} />}
                  {isLoading && (
                    <div className="flex gap-3 mb-4 animate-pulse">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                      </div>
                    </div>
                  )}
                  {error && (
                    <div className="bg-red-900/30 border border-red-700 rounded-xl px-4 py-3 mb-4 text-sm text-red-300">
                      {error}
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
            <ChatInput onSend={send} isLoading={isLoading} />
          </div>
        ) : activePanel === "tools" ? (
          <div className="flex-1 overflow-y-auto">
            <ToolsPanel />
          </div>
        ) : activePanel === "memory" ? (
          <div className="flex-1 overflow-y-auto">
            <MemoryPanel />
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto">
            <InfoPanel />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
