import { useState, useEffect } from "react";
import { Wrench, Loader2 } from "lucide-react";
import { getTools, ToolInfo } from "../../services/api";

export default function ToolsPanel() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTools()
      .then(setTools)
      .catch(() => setTools([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Loading tools...
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <Wrench className="w-6 h-6 text-cyan-400" />
        Available Tools
      </h2>
      <div className="grid gap-4 md:grid-cols-2">
        {tools.map((tool) => (
          <div
            key={tool.name}
            className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-cyan-500/50 transition-colors"
          >
            <h3 className="text-sm font-semibold text-cyan-400 mb-1 font-mono">
              {tool.name}
            </h3>
            <p className="text-sm text-gray-300">{tool.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
