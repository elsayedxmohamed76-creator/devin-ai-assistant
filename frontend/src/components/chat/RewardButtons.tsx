import { ThumbsUp, ThumbsDown } from "lucide-react";

interface RewardButtonsProps {
  onReward: (value: number) => void;
  disabled?: boolean;
}

export default function RewardButtons({ onReward, disabled }: RewardButtonsProps) {
  return (
    <div className="flex gap-2 mt-2 ml-11">
      <button
        onClick={() => onReward(1)}
        disabled={disabled}
        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-green-900/40 text-green-400 border border-green-700/50 hover:bg-green-800/60 hover:border-green-500/60 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
        title="Risposta corretta!"
      >
        <ThumbsUp className="w-3.5 h-3.5" />
        Giusto
      </button>
      <button
        onClick={() => onReward(-1)}
        disabled={disabled}
        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-900/40 text-red-400 border border-red-700/50 hover:bg-red-800/60 hover:border-red-500/60 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
        title="Risposta sbagliata"
      >
        <ThumbsDown className="w-3.5 h-3.5" />
        Sbagliato
      </button>
    </div>
  );
}
