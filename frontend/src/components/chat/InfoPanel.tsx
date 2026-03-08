import { useState, useEffect } from "react";
import {
  Loader2,
  Zap,
  Code,
  Terminal,
  Search,
  ListTodo,
  MessageSquare,
  FolderOpen,
  Globe,
  Monitor,
  Smartphone,
} from "lucide-react";
import { getAgentInfo, AgentInfo } from "../../services/api";

const capabilityIcons: Record<string, React.ReactNode> = {
  code_reading: <Code className="w-4 h-4" />,
  code_writing: <Code className="w-4 h-4" />,
  file_management: <FolderOpen className="w-4 h-4" />,
  shell_execution: <Terminal className="w-4 h-4" />,
  code_search: <Search className="w-4 h-4" />,
  task_planning: <ListTodo className="w-4 h-4" />,
  conversation_memory: <MessageSquare className="w-4 h-4" />,
};

const capabilityLabels: Record<string, string> = {
  code_reading: "Code Reading",
  code_writing: "Code Writing",
  file_management: "File Management",
  shell_execution: "Shell Execution",
  code_search: "Code Search",
  task_planning: "Task Planning",
  conversation_memory: "Conversation Memory",
};

export default function InfoPanel() {
  const [info, setInfo] = useState<AgentInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAgentInfo()
      .then(setInfo)
      .catch(() => setInfo(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Loading info...
      </div>
    );
  }

  if (!info) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        Failed to load agent info
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-500/25">
          <Zap className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">{info.name}</h2>
        <p className="text-gray-400 mt-1">Version {info.version}</p>
      </div>

      {/* Capabilities */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-white mb-4">Capabilities</h3>
        <div className="grid gap-3 md:grid-cols-2">
          {info.capabilities.map((cap) => (
            <div
              key={cap}
              className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl p-3"
            >
              <div className="w-8 h-8 bg-cyan-500/10 rounded-lg flex items-center justify-center text-cyan-400">
                {capabilityIcons[cap] || <Zap className="w-4 h-4" />}
              </div>
              <span className="text-sm text-gray-200">
                {capabilityLabels[cap] || cap}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Platforms */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-white mb-4">
          Cross-Platform Support
        </h3>
        <div className="grid gap-3 md:grid-cols-3">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
            <Globe className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-white">Web</h4>
            <p className="text-xs text-gray-400 mt-1">
              React + TypeScript
            </p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
            <Monitor className="w-8 h-8 text-green-400 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-white">Desktop</h4>
            <p className="text-xs text-gray-400 mt-1">
              Electron (Win/Mac/Linux)
            </p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
            <Smartphone className="w-8 h-8 text-purple-400 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-white">Mobile</h4>
            <p className="text-xs text-gray-400 mt-1">
              Capacitor (iOS/Android)
            </p>
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Tech Stack</h3>
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Backend</span>
            <span className="text-gray-200">Python + FastAPI</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Frontend</span>
            <span className="text-gray-200">React + TypeScript + Tailwind</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">AI Model</span>
            <span className="text-gray-200">{info.model}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Tools</span>
            <span className="text-gray-200">{info.tools.length} available</span>
          </div>
        </div>
      </div>
    </div>
  );
}
