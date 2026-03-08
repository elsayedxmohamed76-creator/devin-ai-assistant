"""API routes for the Devin AI Assistant."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engine import engine
from app.models import (
    AgentInfo,
    ChatRequest,
    ChatResponse,
    ConversationInfo,
    MemoryStats,
    RewardRequest,
    RewardResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
    ToolExecuteRequest,
)
from app.tools_real import execute_tool, get_all_tools

router = APIRouter()


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conv, assistant_msg, tools_used, learning_info = engine.process_message(
        message=request.message,
        conversation_id=request.conversation_id,
    )
    plan = None
    tasks = engine.planner.get_all_tasks()
    if tasks:
        plan = [{"title": t.title, "status": t.status.value} for t in tasks]
    return ChatResponse(
        conversation_id=conv.id,
        message=assistant_msg,
        tools_used=tools_used,
        plan=plan,
        learning_info=learning_info,
    )


# ---------------------------------------------------------------------------
# Learning / Reward
# ---------------------------------------------------------------------------

@router.post("/api/reward", response_model=RewardResponse)
async def send_reward(request: RewardRequest):
    """Send a reward signal (+1, 0, -1) to the learning engine."""
    result = engine.reward(request.value)
    return RewardResponse(**result)


@router.get("/api/memory")
async def get_memory():
    """Get memory stats, rules, and vocabulary."""
    stats = engine.get_memory_stats()
    rules = engine.get_all_rules()
    vocab = engine.get_vocabulary()[:50]  # Limit to top 50
    return {
        "stats": MemoryStats(**stats).model_dump(),
        "rules": rules,
        "vocabulary": vocab,
    }


@router.post("/api/memory/reset")
async def reset_memory():
    """Reset the AI's memory (dangerous!)."""
    import os
    from app.memory import LongTermMemory
    engine.ltm.close()
    db_path = engine.ltm.db_path
    if db_path.exists():
        os.remove(db_path)
    engine.ltm = LongTermMemory(db_path)
    engine.brain.ltm = engine.ltm
    engine.brain.q_learner.ltm = engine.ltm
    engine.brain.consolidator.ltm = engine.ltm
    return {"status": "reset", "message": "Memory has been reset. The AI starts fresh."}


@router.get("/api/learning/state")
async def get_learning_state():
    """Get current learning statistics."""
    return engine.get_memory_stats()


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@router.get("/api/conversations")
async def list_conversations():
    conversations = []
    for conv in engine.conversations.values():
        conversations.append(
            ConversationInfo(
                id=conv.id,
                message_count=conv.message_count,
                created_at=conv.created_at,
                last_message_at=conv.last_message_at,
                preview=conv.preview,
            )
        )
    return {"conversations": conversations}


@router.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = engine.conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": conv.id,
        "messages": [msg.model_dump() for msg in conv.messages],
        "created_at": conv.created_at,
        "last_message_at": conv.last_message_at,
    }


@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if conversation_id not in engine.conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    del engine.conversations[conversation_id]
    return {"status": "deleted", "id": conversation_id}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@router.get("/api/tools")
async def list_tools():
    tools = get_all_tools()
    return {"tools": [t.model_dump() for t in tools]}


@router.post("/api/tools/execute")
async def execute_tool_endpoint(request: ToolExecuteRequest):
    result = execute_tool(request.tool_name, request.parameters)
    return result.model_dump()


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@router.post("/api/tasks")
async def create_task(request: TaskCreateRequest):
    task = engine.planner.create_task(request.description, request.steps)
    return task.model_dump()


@router.get("/api/tasks")
async def list_tasks():
    tasks = engine.planner.get_all_tasks()
    return {"tasks": [t.model_dump() for t in tasks]}


@router.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    task = engine.planner.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()


@router.patch("/api/tasks/{task_id}")
async def update_task(task_id: str, request: TaskUpdateRequest):
    task = engine.planner.update_task(task_id, request.status, request.result)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()


# ---------------------------------------------------------------------------
# Agent Info
# ---------------------------------------------------------------------------

@router.get("/api/agent")
async def get_agent_info():
    tool_names = [t.name for t in get_all_tools()]
    return AgentInfo(tools=tool_names).model_dump()
