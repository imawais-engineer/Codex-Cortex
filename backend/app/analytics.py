"""Local usage analytics for Codex Cortex."""

from __future__ import annotations

from app.storage import get_all_memories


def get_analytics() -> dict:
    memories = get_all_memories()
    types = {}
    for memory in memories:
        memory_type = memory.get("type", "unknown")
        types[memory_type] = types.get(memory_type, 0) + 1
    return {"total_memories": len(memories), "memories_by_type": types}


def usage_stats() -> dict:
    return get_analytics()
