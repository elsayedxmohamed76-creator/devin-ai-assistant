"""AI Assistant engine — integrates the neuro-symbolic learning system.

This is the main orchestrator that connects the learning engine,
memory system, tools, and conversation management.
"""

from __future__ import annotations

import re
import time
import uuid
from typing import Any, Optional

from app.learner import NeuroSymbolicEngine
from app.memory import LongTermMemory, ShortTermMemory
from app.models import (
    ChatMessage,
    MessageRole,
    TaskInfo,
    TaskStatus,
    ToolInfo,
    ToolResult,
    ToolStatus,
)
from app.tools_real import TOOL_REGISTRY, execute_tool, get_all_tools


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------

class Conversation:
    def __init__(self, conversation_id: str | None = None) -> None:
        self.id = conversation_id or str(uuid.uuid4())
        self.messages: list[ChatMessage] = []
        self.created_at: float = time.time()
        self.last_message_at: float = time.time()

    def add_message(self, role: MessageRole, content: str) -> ChatMessage:
        msg = ChatMessage(role=role, content=content)
        self.messages.append(msg)
        self.last_message_at = time.time()
        return msg

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def preview(self) -> str:
        if self.messages:
            return self.messages[-1].content[:100]
        return ""


# ---------------------------------------------------------------------------
# Task Planner
# ---------------------------------------------------------------------------

class TaskPlanner:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskInfo] = {}

    def create_task(self, description: str, steps: list[str]) -> TaskInfo:
        task_id = str(uuid.uuid4())[:8]
        subtasks = [{"title": step, "status": TaskStatus.PENDING.value} for step in steps]
        task = TaskInfo(id=task_id, title=description, status=TaskStatus.PENDING, subtasks=subtasks)
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> TaskInfo | None:
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[TaskInfo]:
        return list(self._tasks.values())

    def update_task(self, task_id: str, status: TaskStatus, result: str = "") -> TaskInfo | None:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
            task.result = result
        return task

    def clear(self) -> None:
        self._tasks.clear()


# ---------------------------------------------------------------------------
# Tool detection — parse user messages for tool invocations
# ---------------------------------------------------------------------------

_TOOL_PATTERNS: dict[str, list[str]] = {
    "read_file": ["leggi", "read", "open", "apri", "mostra", "show", "view", "vedi"],
    "write_file": ["scrivi", "write", "crea", "create", "salva", "save"],
    "run_shell": ["esegui", "run", "lancia", "execute", "comando", "command", "terminal"],
    "search_code": ["cerca", "search", "find", "trova", "grep"],
    "list_files": ["lista", "list", "elenca", "files", "directory", "cartella"],
    "web_search": ["wikipedia", "web", "internet", "cerca online"],
}


def _detect_tool_intent(message: str) -> tuple[str | None, dict[str, Any]]:
    """Detect if the user is requesting a tool operation."""
    msg_lower = message.lower()

    for tool_name, keywords in _TOOL_PATTERNS.items():
        for kw in keywords:
            if kw in msg_lower:
                params = _extract_tool_params(tool_name, message)
                if params:
                    return tool_name, params
    return None, {}


def _extract_tool_params(tool_name: str, message: str) -> dict[str, Any]:
    """Try to extract parameters from natural language."""
    # Look for file paths (quoted or with common extensions)
    path_match = re.search(r'["\']([^"\']+)["\']', message)
    if not path_match:
        path_match = re.search(r'(\S+\.\w{1,5})', message)

    if tool_name in ("read_file", "write_file", "list_files"):
        path = path_match.group(1) if path_match else None
        if path:
            params: dict[str, Any] = {"path": path}
            if tool_name == "write_file":
                # Try to extract content after ":" or "content:"
                content_match = re.search(r'(?:content|contenuto|testo)[:\s]+(.+)', message, re.DOTALL | re.IGNORECASE)
                params["content"] = content_match.group(1).strip() if content_match else ""
            return params

    if tool_name == "run_shell":
        # Look for command in backticks or after "command:"
        cmd_match = re.search(r'`([^`]+)`', message)
        if not cmd_match:
            cmd_match = re.search(r'(?:command|comando|esegui)[:\s]+(.+)', message, re.IGNORECASE)
        if cmd_match:
            return {"command": cmd_match.group(1).strip()}

    if tool_name == "search_code":
        query_match = re.search(r'(?:for|per|pattern)[:\s]+["\']?([^"\']+)["\']?', message, re.IGNORECASE)
        if not query_match:
            query_match = re.search(r'["\']([^"\']+)["\']', message)
        if query_match:
            return {"pattern": query_match.group(1).strip()}

    if tool_name == "web_search":
        query_match = re.search(r'(?:about|su|per|search|cerca)[:\s]+(.+)', message, re.IGNORECASE)
        if query_match:
            return {"query": query_match.group(1).strip()}

    return {}


# ---------------------------------------------------------------------------
# Assistant Engine — main controller
# ---------------------------------------------------------------------------

class AssistantEngine:
    """Main engine integrating conversations, tools, and neuro-symbolic learning."""

    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = {}
        self.planner = TaskPlanner()

        # Initialize the learning brain
        self.ltm = LongTermMemory()
        self.stm = ShortTermMemory(max_size=30)
        self.brain = NeuroSymbolicEngine(self.ltm, self.stm)

    def get_or_create_conversation(self, conversation_id: str | None = None) -> Conversation:
        if conversation_id and conversation_id in self.conversations:
            return self.conversations[conversation_id]
        conv = Conversation(conversation_id)
        self.conversations[conv.id] = conv
        return conv

    def process_message(
        self, message: str, conversation_id: str | None = None
    ) -> tuple[Conversation, ChatMessage, list[str], dict[str, Any]]:
        """Process a user message through the learning engine.

        Returns: (conversation, assistant_message, tools_used, learning_info)
        """
        conv = self.get_or_create_conversation(conversation_id)
        conv.add_message(MessageRole.USER, message)

        tools_used: list[str] = []
        learning_info: dict[str, Any] = {}

        # --- Step 1: Check for tool invocation ---
        tool_name, tool_params = _detect_tool_intent(message)
        tool_output = ""
        if tool_name and tool_params:
            result = execute_tool(tool_name, tool_params)
            tools_used.append(tool_name)
            if result.status == ToolStatus.SUCCESS:
                tool_output = f"\n\n**🔧 Tool `{tool_name}`:**\n```\n{result.output[:2000]}\n```"
            else:
                tool_output = f"\n\n**❌ Tool `{tool_name}` error:** {result.error}"

        # --- Step 2: Generate response through the learning engine ---
        brain_result = self.brain.process(message)
        response_text = brain_result["response"]
        learning_info = {
            "source": brain_result["source"],
            "confidence": brain_result["confidence"],
            "learning_info": brain_result.get("learning_info", ""),
            "state": brain_result.get("state", ""),
        }
        tools_used.extend(brain_result.get("tools_used", []))

        # Append tool output if any
        if tool_output:
            response_text += tool_output

        # --- Step 3: Log interaction ---
        self.ltm.log_interaction(message, response_text, tools_used=tools_used)

        assistant_msg = conv.add_message(MessageRole.ASSISTANT, response_text)
        return conv, assistant_msg, tools_used, learning_info

    def reward(self, value: int) -> dict[str, Any]:
        """Send a reward signal to the learning engine."""
        return self.brain.reward(value)

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory and learning statistics."""
        return self.brain.get_learning_state()

    def get_all_rules(self) -> list[dict[str, Any]]:
        """Get all consolidated rules."""
        return self.ltm.get_all_rules()

    def get_vocabulary(self) -> list[dict[str, Any]]:
        """Get known vocabulary."""
        return self.ltm.get_vocabulary()


# Singleton engine instance
engine = AssistantEngine()
