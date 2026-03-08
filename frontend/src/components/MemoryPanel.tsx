import { useState, useEffect } from "react";
import { Brain, BookOpen, Sparkles, Hash, Loader2, RotateCcw } from "lucide-react";
import { getMemory, resetMemory, MemoryResponse } from "../services/api";

export default function MemoryPanel() {
  const [data, setData] = useState<MemoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);

  const loadMemory = () => {
    setLoading(true);
    getMemory()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadMemory(); }, []);

  const handleReset = async () => {
    if (!confirm("⚠️ Sei sicuro? L'AI perderà TUTTA la sua memoria e ripartirà da zero!")) return;
    setResetting(true);
    try {
      await resetMemory();
      loadMemory();
    } catch (e) {
      console.error(e);
    } finally {
      setResetting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Caricamento memoria...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        Backend non raggiungibile
      </div>
    );
  }

  const { stats, rules, vocabulary } = data;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Brain className="w-6 h-6 text-purple-400" />
          Cervello dell'AI
        </h2>
        <div className="flex gap-2">
          <button
            onClick={loadMemory}
            className="text-xs text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-gray-700 hover:border-gray-500 transition-colors"
          >
            Aggiorna
          </button>
          <button
            onClick={handleReset}
            disabled={resetting}
            className="text-xs text-red-400 hover:text-red-300 px-3 py-1.5 rounded-lg border border-red-800/50 hover:border-red-600 transition-colors flex items-center gap-1"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-3 grid-cols-2 md:grid-cols-4 mb-8">
        {[
          { label: "Regole Apprese", value: stats.rules_learned, icon: <Sparkles className="w-4 h-4" />, color: "text-yellow-400" },
          { label: "Vocabolario", value: stats.vocabulary_size, icon: <BookOpen className="w-4 h-4" />, color: "text-blue-400" },
          { label: "Interazioni", value: stats.total_interactions, icon: <Hash className="w-4 h-4" />, color: "text-green-400" },
          { label: "Reward Medio", value: stats.average_reward.toFixed(2), icon: <Brain className="w-4 h-4" />, color: "text-purple-400" },
        ].map((s) => (
          <div key={s.label} className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
            <div className={`${s.color} mb-1 flex justify-center`}>{s.icon}</div>
            <div className="text-2xl font-bold text-white">{s.value}</div>
            <div className="text-xs text-gray-400 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Exploration Rate */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Tasso di Esplorazione</h3>
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-400">Esplorazione vs Sfruttamento</span>
            <span className="text-cyan-400 font-mono">{(stats.exploration_rate * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-cyan-500 to-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${stats.exploration_rate * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {stats.exploration_rate > 0.5
              ? "🔍 L'AI sta ancora esplorando — insegnale con i feedback!"
              : stats.exploration_rate > 0.1
              ? "🧠 L'AI sta iniziando a capire — continua ad insegnare!"
              : "✨ L'AI è molto sicura delle sue risposte!"}
          </p>
        </div>
      </div>

      {/* Rules */}
      {rules.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-400" />
            Regole Consolidate ({rules.length})
          </h3>
          <div className="space-y-2">
            {rules.map((rule, i) => (
              <div key={i} className="bg-gray-800 border border-gray-700 rounded-xl p-3 flex justify-between items-center">
                <div>
                  <span className="text-cyan-400 font-mono text-sm">{rule.pattern}</span>
                  <span className="text-gray-500 mx-2">→</span>
                  <span className="text-green-400 text-sm">{String(rule.action).substring(0, 80)}</span>
                </div>
                <span className="text-xs text-gray-500">{rule.times_used}x</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vocabulary */}
      {vocabulary.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-400" />
            Vocabolario ({stats.vocabulary_size} parole)
          </h3>
          <div className="flex flex-wrap gap-2">
            {vocabulary.slice(0, 40).map((v, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-900/40 text-blue-300 border border-blue-700/40"
                title={v.meaning || ""}
              >
                {v.word} <span className="text-blue-500">({v.times_seen})</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
