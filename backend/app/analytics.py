"""Local usage analytics for Codex Cortex."""

from __future__ import annotations

from collections import Counter

from . import storage


def usage_stats() -> dict:
    memories = storage.get_all_memories()
    by_type = Counter(memory.get("type", "general") for memory in memories)
    return {"total_memories": len(memories), "memories_by_type": dict(by_type)}
