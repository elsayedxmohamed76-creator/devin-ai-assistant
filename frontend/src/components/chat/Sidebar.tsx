import {
  MessageSquare,
  Plus,
  Settings,
  Wrench,
  Info,
  Zap,
  Monitor,
  Smartphone,
  Globe,
} from "lucide-react";

interface SidebarProps {
  onNewChat: () => void;
  onShowTools: () => void;
  onShowInfo: () => void;
  activePanel: string;
}

export default function Sidebar({
  onNewChat,
  onShowTools,
  onShowInfo,
  activePanel,
}: SidebarProps) {
  return (
    <div className="w-64 bg-gray-900 border-r border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Devin AI</h1>
            <p className="text-xs text-gray-400">v0.1.0</p>
          </div>
        </div>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-cyan-500/25"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        <button
          onClick={onNewChat}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            activePanel === "chat"
              ? "bg-gray-800 text-cyan-400"
              : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Chat
        </button>
        <button
          onClick={onShowTools}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            activePanel === "tools"
              ? "bg-gray-800 text-cyan-400"
              : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
          }`}
        >
          <Wrench className="w-4 h-4" />
          Tools
        </button>
        <button
          onClick={onShowInfo}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            activePanel === "info"
              ? "bg-gray-800 text-cyan-400"
              : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
          }`}
        >
          <Info className="w-4 h-4" />
          About
        </button>
      </nav>

      {/* Platform Badges */}
      <div className="p-3 border-t border-gray-700">
        <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wider">
          Platforms
        </p>
        <div className="flex gap-2">
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-gray-800 text-gray-400 text-xs">
            <Globe className="w-3 h-3" />
            Web
          </div>
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-gray-800 text-gray-400 text-xs">
            <Monitor className="w-3 h-3" />
            Desktop
          </div>
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-gray-800 text-gray-400 text-xs">
            <Smartphone className="w-3 h-3" />
            Mobile
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-700">
        <div className="flex items-center gap-2 text-gray-500 text-xs">
          <Settings className="w-3 h-3" />
          <span>Settings</span>
        </div>
      </div>
    </div>
  );
}
