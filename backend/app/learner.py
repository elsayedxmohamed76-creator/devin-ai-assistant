"""Neuro-Symbolic Learning Engine — The AI's thinking system.

QLearner: Exploration through Q-value-based state-action mapping.
SymbolicConsolidator: Crystallizes repeated successes into permanent rules.
WebFallback: Searches Wikipedia when confidence is too low.
NeuroSymbolicEngine: Orchestrates the 3-tier system (LTM → Q-Learning → Web).
"""

from __future__ import annotations

import hashlib
import random
import re
import time
from typing import Any, Optional

from app.memory import LongTermMemory, ShortTermMemory
from app.llm_client import llm


# ---------------------------------------------------------------------------
# Q-Learning Explorer
# ---------------------------------------------------------------------------

class QLearner:
    """Epsilon-greedy Q-Learning for action selection."""

    def __init__(
        self,
        ltm: LongTermMemory,
        learning_rate: float = 0.3,
        discount_factor: float = 0.9,
        initial_epsilon: float = 0.8,
        min_epsilon: float = 0.05,
        epsilon_decay: float = 0.995,
    ) -> None:
        self.ltm = ltm
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay
        self._action_space: list[str] = self._load_action_space()

    def _load_action_space(self) -> list[str]:
        """Load known actions from vocabulary + default responses."""
        defaults = [
            "Non lo so ancora, sto imparando.",
            "Puoi spiegarmi meglio?",
            "Interessante, dimmi di più.",
            "Ci sto lavorando!",
            "Ho capito, grazie per l'informazione.",
        ]
        vocab = self.ltm.get_vocabulary()
        for entry in vocab:
            if entry.get("meaning"):
                defaults.append(entry["meaning"])
        return defaults

    def expand_action_space(self, new_action: str) -> None:
        """Add a new possible response/action to the space."""
        if new_action not in self._action_space:
            self._action_space.append(new_action)

    def select_action(self, state: str) -> tuple[str, float]:
        """Epsilon-greedy action selection. Returns (action, confidence)."""
        # Check Q-table for known state-action pairs
        known_actions = self.ltm.get_q_actions(state)

        if known_actions and random.random() > self.epsilon:
            # Exploit: pick best known action
            best = known_actions[0]
            return best["action"], best["q_value"]

        # Explore: pick random action
        if self._action_space:
            action = random.choice(self._action_space)
            return action, 0.0

        return "...", 0.0

    def update(self, state: str, action: str, reward: float) -> None:
        """Update Q-value for a state-action pair."""
        old_q = self.ltm.get_q_value(state, action)
        new_q = old_q + self.lr * (reward - old_q)
        self.ltm.set_q_value(state, action, new_q)

        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    @property
    def exploration_rate(self) -> float:
        return self.epsilon


# ---------------------------------------------------------------------------
# Symbolic Consolidator
# ---------------------------------------------------------------------------

class SymbolicConsolidator:
    """Extracts permanent symbolic rules from repeated successes.

    When the agent gets N consecutive positive rewards for the same
    state→action pattern, the consolidator converts it into a permanent
    rule in the LTM.
    """

    def __init__(self, ltm: LongTermMemory, threshold: int = 3) -> None:
        self.ltm = ltm
        self.threshold = threshold
        self._success_counter: dict[str, int] = {}
        self._last_actions: dict[str, str] = {}

    def record_success(self, state: str, action: str) -> bool:
        """Record a successful interaction. Returns True if consolidation happened."""
        key = f"{state}→{action}"

        if self._last_actions.get(state) == action:
            self._success_counter[key] = self._success_counter.get(key, 0) + 1
        else:
            self._success_counter[key] = 1

        self._last_actions[state] = action

        if self._success_counter[key] >= self.threshold:
            # Consolidate into permanent rule!
            self.ltm.add_rule(state, action, confidence=1.0)
            self._success_counter[key] = 0
            return True

        return False

    def record_failure(self, state: str) -> None:
        """Reset success counter for a state."""
        keys_to_reset = [k for k in self._success_counter if k.startswith(f"{state}→")]
        for k in keys_to_reset:
            self._success_counter[k] = 0


# ---------------------------------------------------------------------------
# Web Fallback (Wikipedia)
# ---------------------------------------------------------------------------

class WebFallback:
    """Searches Wikipedia when the agent's confidence is too low."""

    def __init__(self) -> None:
        self._wiki = None
        self._consecutive_failures: dict[str, int] = {}
        self.failure_threshold = 3

    def _get_wiki(self):
        if self._wiki is None:
            try:
                import wikipediaapi
                self._wiki = wikipediaapi.Wikipedia(
                    user_agent="DevinAI/1.0 (mohamed@devin.ai)",
                    language="it",
                )
            except ImportError:
                return None
        return self._wiki

    def should_search(self, state: str) -> bool:
        """Check if we've failed enough times to trigger web search."""
        return self._consecutive_failures.get(state, 0) >= self.failure_threshold

    def record_failure(self, state: str) -> None:
        self._consecutive_failures[state] = self._consecutive_failures.get(state, 0) + 1

    def record_success(self, state: str) -> None:
        self._consecutive_failures[state] = 0

    def search(self, query: str) -> str | None:
        """Search Wikipedia for information about the query."""
        wiki = self._get_wiki()
        if wiki is None:
            return None

        try:
            # Clean the query for search
            clean_query = re.sub(r'[^\w\s]', '', query).strip()
            if not clean_query:
                return None

            page = wiki.page(clean_query)
            if page.exists():
                summary = page.summary[:500]
                return summary
        except Exception:
            pass

        return None


# ---------------------------------------------------------------------------
# Neuro-Symbolic Engine — the main orchestrator
# ---------------------------------------------------------------------------

def _state_hash(text: str) -> str:
    """Create a compact state key from input text."""
    normalized = text.lower().strip()
    if len(normalized) <= 60:
        return normalized
    return hashlib.md5(normalized.encode()).hexdigest()[:16]


class NeuroSymbolicEngine:
    """Orchestrates the 3-tier neuro-symbolic learning system.

    Decision flow:
        1. LTM: Has a consolidated rule? → Use it immediately.
        2. Q-Learning: Has a confident action? → Use it.
        3. Web Fallback: After repeated failures → Search Wikipedia.
    """

    def __init__(self, ltm: LongTermMemory, stm: ShortTermMemory) -> None:
        self.ltm = ltm
        self.stm = stm
        self.q_learner = QLearner(ltm)
        self.consolidator = SymbolicConsolidator(ltm, threshold=3)
        self.web_fallback = WebFallback()
        self._last_state: str = ""
        self._last_action: str = ""
        self._last_source: str = ""

    def process(self, user_input: str) -> dict[str, Any]:
        """Process user input and generate a response.

        Returns a dict with: response, source, confidence, tools_used, state
        """
        state = _state_hash(user_input)
        self._last_state = state
        context = self.stm.get_context_string()

        # Add user input to STM
        self.stm.add("user", user_input)

        # Learn new words from input
        words = user_input.lower().split()
        for word in words:
            if len(word) > 2:
                self.ltm.learn_word(word, context=user_input[:100])

        # --- Tier 1: LTM rules ---
        rule = self.ltm.get_rule(state)
        if rule:
            response = rule["action"]
            self._last_action = response
            self._last_source = "ltm"
            self.stm.add("assistant", response, {"source": "ltm"})
            return {
                "response": response,
                "source": "ltm",
                "confidence": rule["confidence"],
                "tools_used": [],
                "state": state,
                "learning_info": f"📚 Regola consolidata (usata {rule['times_used']}x)",
            }

        # --- Tier 2: Local LLM ---
        if llm.is_available():
            llm_res = llm.generate(prompt=user_input, context=context)
            if llm_res["success"] and llm_res["text"]:
                response = llm_res["text"]
                self._last_action = response
                self._last_source = "llm"
                self.stm.add("assistant", response, {"source": "llm", "tokens": llm_res["tokens_used"]})
                
                # Still add to action space so Q-learner knows about it
                self.q_learner.expand_action_space(response)
                
                return {
                    "response": response,
                    "source": "llm",
                    "confidence": 0.8, # High confidence for LLM, but less than explicit rule
                    "tools_used": [],
                    "state": state,
                    "learning_info": f"🧠 Risposta da modello LLM locale (Tokens: {llm_res['tokens_used']})",
                }

        # --- Tier 3: Q-Learning ---
        action, q_confidence = self.q_learner.select_action(state)
        if q_confidence > 0.3:
            self._last_action = action
            self._last_source = "q_learning"
            self.stm.add("assistant", action, {"source": "q_learning", "confidence": q_confidence})
            return {
                "response": action,
                "source": "q_learning",
                "confidence": q_confidence,
                "tools_used": [],
                "state": state,
                "learning_info": f"🧠 Risposta neurale (confidenza: {q_confidence:.2f})",
            }

        # --- Tier 4: Web Fallback ---
        if self.web_fallback.should_search(state):
            web_result = self.web_fallback.search(user_input)
            if web_result:
                self._last_action = web_result
                self._last_source = "web"
                self.q_learner.expand_action_space(web_result)
                self.stm.add("assistant", web_result, {"source": "web"})
                return {
                    "response": web_result,
                    "source": "web",
                    "confidence": 0.5,
                    "tools_used": ["web_search"],
                    "state": state,
                    "learning_info": "🌐 Ho cercato su Wikipedia per aiutarti!",
                }

        # --- Fallback 5: Explore ---
        self._last_action = action  # from Q-learning random selection
        self._last_source = "exploration"
        self.stm.add("assistant", action, {"source": "exploration"})
        return {
            "response": action,
            "source": "exploration",
            "confidence": 0.0,
            "tools_used": [],
            "state": state,
            "learning_info": "🔍 Sto esplorando... dammi un feedback con 👍 o 👎!",
        }

    def reward(self, value: int) -> dict[str, Any]:
        """Process a reward signal from the user.

        value: +1 (correct), 0 (neutral), -1 (wrong)
        Returns info about what the agent learned.
        """
        if not self._last_state or not self._last_action:
            return {"learned": False, "message": "Nessuna azione recente da valutare."}

        state = self._last_state
        action = self._last_action

        # Update Q-values
        self.q_learner.update(state, action, float(value))

        # Log the interaction
        self.ltm.update_last_reward(value)

        result: dict[str, Any] = {
            "learned": False,
            "state": state,
            "action": action[:100],
            "reward": value,
            "new_epsilon": self.q_learner.exploration_rate,
        }

        if value > 0:
            # Positive reward — record success
            consolidated = self.consolidator.record_success(state, action)
            self.web_fallback.record_success(state)

            if consolidated:
                result["learned"] = True
                result["message"] = f"✨ CONSOLIDAMENTO! Ho imparato una nuova regola permanente!"
                result["rule"] = {"pattern": state, "action": action[:100]}
            else:
                result["message"] = "👍 Grazie! Sto memorizzando..."

        elif value < 0:
            # Negative reward — record failure
            self.consolidator.record_failure(state)
            self.web_fallback.record_failure(state)
            result["message"] = "👎 Capito, proverò qualcosa di diverso la prossima volta."

        else:
            result["message"] = "Ok, neutro."

        return result

    def get_learning_state(self) -> dict[str, Any]:
        """Get current learning statistics."""
        stats = self.ltm.get_stats()
        stats["exploration_rate"] = round(self.q_learner.exploration_rate, 4)
        stats["stm_size"] = self.stm.size
        stats["last_source"] = self._last_source
        return stats
