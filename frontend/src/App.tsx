import { useState, useRef, useEffect } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessageComponent from "./components/chat/ChatMessage";
import ChatInput from "./components/chat/ChatInput";
import ToolBadge from "./components/chat/ToolBadge";
import Sidebar from "./components/chat/Sidebar";
import ToolsPanel from "./components/chat/ToolsPanel";
import InfoPanel from "./components/chat/InfoPanel";
import { Bot, Zap, Code, Terminal, Search, ListTodo, Menu, X } from "lucide-react";

function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-6">
      <div className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-cyan-500/25 animate-pulse">
        <Zap className="w-10 h-10 text-white" />
      </div>
      <h2 className="text-3xl font-bold text-white mb-2">
        Welcome to Devin AI
      </h2>
      <p className="text-gray-400 mb-8 max-w-md">
        Your AI-powered coding assistant. I can help you read, write, and debug
        code, run commands, and plan complex tasks.
      </p>
      <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
        {[
          { icon: <Code className="w-5 h-5" />, label: "Read & Write Code", desc: "Navigate and edit files" },
          { icon: <Terminal className="w-5 h-5" />, label: "Run Commands", desc: "Execute shell commands" },
          { icon: <Search className="w-5 h-5" />, label: "Search Code", desc: "Find patterns in files" },
          { icon: <ListTodo className="w-5 h-5" />, label: "Plan Tasks", desc: "Break down complex work" },
        ].map((item) => (
          <div
            key={item.label}
            className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 text-left hover:border-cyan-500/30 transition-colors"
          >
            <div className="text-cyan-400 mb-2">{item.icon}</div>
            <h3 className="text-sm font-semibold text-white">{item.label}</h3>
            <p className="text-xs text-gray-400 mt-0.5">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function App() {
  const { messages, isLoading, error, send, clear, toolsUsed } = useChat();
  const [activePanel, setActivePanel] = useState("chat");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleNewChat = () => {
    clear();
    setActivePanel("chat");
  };

  return (
    <div className="h-screen flex bg-gray-950 text-white overflow-hidden">
      {/* Mobile menu toggle */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 bg-gray-800 p-2 rounded-lg border border-gray-700"
      >
        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 fixed lg:relative z-40 transition-transform duration-200`}
      >
        <Sidebar
          onNewChat={handleNewChat}
          onShowTools={() => setActivePanel("tools")}
          onShowInfo={() => setActivePanel("info")}
          activePanel={activePanel}
        />
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b border-gray-700 bg-gray-900/80 backdrop-blur-sm px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3 ml-10 lg:ml-0">
            <Bot className="w-5 h-5 text-cyan-400" />
            <h1 className="text-lg font-semibold text-white">
              {activePanel === "chat"
                ? "Chat"
                : activePanel === "tools"
                ? "Tools"
                : "About"}
            </h1>
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
                    <ChatMessageComponent key={i} message={msg} />
                  ))}
                  {toolsUsed.length > 0 && <ToolBadge tools={toolsUsed} />}
                  {isLoading && (
                    <div className="flex gap-3 mb-4 animate-pulse">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
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
