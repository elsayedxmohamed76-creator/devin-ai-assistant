"""AI Assistant engine - manages conversations, tools, and task planning."""

from __future__ import annotations

import time
import uuid
from typing import Any

from app.models import (
    ChatMessage,
    MessageRole,
    TaskInfo,
    TaskStatus,
    ToolInfo,
    ToolResult,
    ToolStatus,
)


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


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolInfo] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults = [
            ToolInfo(
                name="read_file",
                description="Read the contents of a file in the workspace",
                parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
            ),
            ToolInfo(
                name="write_file",
                description="Write content to a file, creating directories as needed",
                parameters={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
            ),
            ToolInfo(
                name="run_shell",
                description="Execute a shell command in the workspace",
                parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
            ),
            ToolInfo(
                name="search_code",
                description="Search for patterns in code files using regex",
                parameters={"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]},
            ),
            ToolInfo(
                name="list_files",
                description="List files in a directory with optional glob filtering",
                parameters={"type": "object", "properties": {"path": {"type": "string"}, "pattern": {"type": "string"}}},
            ),
            ToolInfo(
                name="web_search",
                description="Search the web for documentation, APIs, or technical topics",
                parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            ),
        ]
        for tool in defaults:
            self._tools[tool.name] = tool

    def get_all(self) -> list[ToolInfo]:
        return list(self._tools.values())

    def get(self, name: str) -> ToolInfo | None:
        return self._tools.get(name)

    def execute(self, name: str, parameters: dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {name}", tool_name=name)

        simulations: dict[str, str] = {
            "read_file": f"[Demo] Contents of '{parameters.get('path', 'file.txt')}':\n# File contents would appear here",
            "write_file": f"[Demo] Successfully wrote to '{parameters.get('path', 'file.txt')}'",
            "run_shell": f"[Demo] $ {parameters.get('command', 'echo hello')}\nCommand executed successfully",
            "search_code": f"[Demo] Found 3 matches for '{parameters.get('pattern', '')}'",
            "list_files": "[Demo] Files:\n  src/main.py\n  src/utils.py\n  README.md",
            "web_search": f"[Demo] Search results for '{parameters.get('query', '')}'",
        }
        output = simulations.get(name, f"[Demo] Tool '{name}' executed successfully")
        return ToolResult(status=ToolStatus.SUCCESS, output=output, tool_name=name)


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


class AssistantEngine:
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = {}
        self.tools = ToolRegistry()
        self.planner = TaskPlanner()

    def get_or_create_conversation(self, conversation_id: str | None = None) -> Conversation:
        if conversation_id and conversation_id in self.conversations:
            return self.conversations[conversation_id]
        conv = Conversation(conversation_id)
        self.conversations[conv.id] = conv
        return conv

    def process_message(self, message: str, conversation_id: str | None = None) -> tuple[Conversation, ChatMessage, list[str]]:
        conv = self.get_or_create_conversation(conversation_id)
        conv.add_message(MessageRole.USER, message)
        response_text, tools_used = self._generate_response(message)
        assistant_msg = conv.add_message(MessageRole.ASSISTANT, response_text)
        return conv, assistant_msg, tools_used

    def _generate_response(self, message: str) -> tuple[str, list[str]]:
        msg_lower = message.lower()
        tools_used: list[str] = []

        if any(word in msg_lower for word in ["hello", "hi", "hey", "ciao", "salve"]):
            return (
                "Hello! I'm Devin, your AI coding assistant. I can help you with:\n\n"
                "- **Reading & writing code** - I can navigate and edit your codebase\n"
                "- **Running commands** - Execute shell commands, tests, builds\n"
                "- **Searching code** - Find patterns and references across files\n"
                "- **Planning tasks** - Break down complex tasks into steps\n\n"
                "What would you like to work on today?",
                [],
            )

        if any(word in msg_lower for word in ["read", "open", "show", "view", "file"]):
            tools_used.append("read_file")
            return (
                "I'll read that file for you. Here's what I found:\n\n"
                "```python\ndef main():\n    print('Hello from Devin!')\n    return 0\n```\n\n"
                "Would you like me to make any changes?",
                tools_used,
            )

        if any(word in msg_lower for word in ["write", "create", "edit", "modify"]):
            tools_used.append("write_file")
            return (
                "I've made the changes you requested:\n\n"
                "1. Created/modified the file with the new content\n"
                "2. Ensured proper formatting and imports\n\n"
                "Would you like me to run any tests to verify?",
                tools_used,
            )

        if any(word in msg_lower for word in ["run", "execute", "test", "build", "lint"]):
            tools_used.append("run_shell")
            return (
                "Command executed successfully:\n\n"
                "```\n$ command executed\nAll checks passed!\n```\n\n"
                "Everything looks good!",
                tools_used,
            )

        if any(word in msg_lower for word in ["search", "find", "grep", "where"]):
            tools_used.append("search_code")
            return (
                "Found several matches:\n\n"
                "- `src/main.py:10` - Primary definition\n"
                "- `src/utils.py:25` - Utility usage\n"
                "- `tests/test_main.py:5` - Test reference\n\n"
                "Would you like me to open any of these files?",
                tools_used,
            )

        if any(word in msg_lower for word in ["plan", "task", "step", "break"]):
            return (
                "Here's my plan:\n\n"
                "1. **Analyze** - Understand requirements\n"
                "2. **Plan** - Design the solution\n"
                "3. **Implement** - Write the code\n"
                "4. **Test** - Verify everything works\n"
                "5. **Review** - Final cleanup\n\n"
                "Shall I proceed?",
                [],
            )

        if any(word in msg_lower for word in ["help", "what", "how", "can you"]):
            return (
                "I'm Devin, an AI coding assistant. I can:\n\n"
                "- Read, write, and edit code files\n"
                "- Run shell commands and tests\n"
                "- Search across your codebase\n"
                "- Plan and track complex tasks\n"
                "- Debug errors and suggest fixes\n\n"
                "Just tell me what you need!",
                [],
            )

        return (
            "I understand your request. Let me work on it.\n\n"
            "1. I'll examine the relevant code and context\n"
            "2. Implement the necessary changes\n"
            "3. Verify everything works correctly\n\n"
            "Would you like me to proceed?",
            [],
        )


engine = AssistantEngine()
