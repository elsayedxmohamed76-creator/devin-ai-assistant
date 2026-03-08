"""Data models for the Devin AI Assistant API."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: float = Field(default_factory=time.time)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.1


class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    workspace: str = "."


class TaskCreateRequest(BaseModel):
    description: str
    steps: list[str] = Field(default_factory=list)


class TaskUpdateRequest(BaseModel):
    status: TaskStatus
    result: str = ""


class ChatResponse(BaseModel):
    conversation_id: str
    message: ChatMessage
    tools_used: list[str] = Field(default_factory=list)
    plan: Optional[list[dict[str, str]]] = None


class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    status: ToolStatus
    output: str = ""
    error: str = ""
    tool_name: str = ""


class TaskInfo(BaseModel):
    id: str
    title: str
    status: TaskStatus
    subtasks: list[dict[str, str]] = Field(default_factory=list)
    result: str = ""


class ConversationInfo(BaseModel):
    id: str
    message_count: int
    created_at: float
    last_message_at: float
    preview: str = ""


class AgentInfo(BaseModel):
    name: str = "Devin AI Assistant"
    version: str = "0.1.0"
    model: str = "gpt-4"
    tools: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=lambda: [
        "code_reading",
        "code_writing",
        "file_management",
        "shell_execution",
        "code_search",
        "task_planning",
        "conversation_memory",
    ])
