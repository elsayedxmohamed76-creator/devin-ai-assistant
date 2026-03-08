import { Wrench } from "lucide-react";

interface ToolBadgeProps {
  tools: string[];
}

export default function ToolBadge({ tools }: ToolBadgeProps) {
  if (tools.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-4 mb-2">
      {tools.map((tool) => (
        <span
          key={tool}
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-900/50 text-purple-300 border border-purple-700/50"
        >
          <Wrench className="w-3 h-3" />
          {tool}
        </span>
      ))}
    </div>
  );
}
