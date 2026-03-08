import {
  MessageSquare,
  Plus,
  Settings,
  Wrench,
  Info,
  Brain,
  Monitor,
  Zap,
} from "lucide-react";

interface SidebarProps {
  onNewChat: () => void;
  onShowTools: () => void;
  onShowInfo: () => void;
  onShowMemory: () => void;
  activePanel: string;
}

export default function Sidebar({
  onNewChat,
  onShowTools,
  onShowInfo,
  onShowMemory,
  activePanel,
}: SidebarProps) {
  const navItems = [
    { id: "chat", icon: <MessageSquare className="w-4 h-4" />, label: "Chat", onClick: onNewChat },
    { id: "memory", icon: <Brain className="w-4 h-4" />, label: "Cervello", onClick: onShowMemory },
    { id: "tools", icon: <Wrench className="w-4 h-4" />, label: "Strumenti", onClick: onShowTools },
    { id: "info", icon: <Info className="w-4 h-4" />, label: "Info", onClick: onShowInfo },
  ];

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Devin AI</h1>
            <p className="text-xs text-gray-400">v1.0.0 • Neuro-Simbolico</p>
          </div>
        </div>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-purple-500/25"
        >
          <Plus className="w-4 h-4" />
          Nuova Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={item.onClick}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
              activePanel === item.id
                ? "bg-gray-800 text-purple-400"
                : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
            }`}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </nav>

      {/* Platform Badge */}
      <div className="p-3 border-t border-gray-700">
        <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-gray-800 text-gray-400 text-xs w-fit">
          <Monitor className="w-3 h-3" />
          Windows Desktop
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-700">
        <div className="flex items-center gap-2 text-gray-500 text-xs">
          <Settings className="w-3 h-3" />
          <span>Impostazioni</span>
        </div>
      </div>
    </div>
  );
}
