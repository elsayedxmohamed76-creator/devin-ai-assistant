import { Bot, User } from "lucide-react";
import { ChatMessage as ChatMessageType } from "../../services/api";

interface ChatMessageProps {
  message: ChatMessageType;
}

function formatMarkdown(text: string): string {
  // Simple markdown formatting: bold, code blocks, inline code, lists
  let html = text
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="bg-gray-900 text-green-400 p-3 rounded-lg my-2 overflow-x-auto text-sm font-mono"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="bg-gray-700 text-cyan-300 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^- (.+)$/gm, '<li class="ml-4">$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4"><span class="text-cyan-400 font-semibold">$1.</span> $2</li>');

  // Wrap consecutive <li> elements in <ul>
  html = html.replace(/((?:<li[^>]*>.*?<\/li>\s*)+)/g, '<ul class="my-1 space-y-1">$1</ul>');
  
  // Convert newlines to <br> (but not inside pre tags)
  const parts = html.split(/(<pre[\s\S]*?<\/pre>)/g);
  html = parts.map((part, i) => {
    if (i % 2 === 0) {
      return part.replace(/\n/g, "<br/>");
    }
    return part;
  }).join("");

  return html;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""} mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? "bg-gradient-to-br from-blue-500 to-blue-600"
            : "bg-gradient-to-br from-cyan-500 to-teal-600"
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white"
            : "bg-gray-800 border border-gray-700 text-gray-100"
        }`}
      >
        <div className="text-xs text-gray-400 mb-1 font-medium">
          {isUser ? "You" : "Devin AI"}
        </div>
        <div
          className="text-sm leading-relaxed prose prose-invert max-w-none"
          dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
        />
      </div>
    </div>
  );
}
