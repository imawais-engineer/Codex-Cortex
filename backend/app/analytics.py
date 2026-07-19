"""Basic analytics for the memory store."""
from app.storage import get_all_memories
def get_analytics() -> dict:
    memories = get_all_memories()
    types = {}
    for m in memories:
        t = m.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
    return {"total_memories": len(memories), "memories_by_type": types}
