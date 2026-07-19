"""Business logic orchestration for Codex Cortex memories."""

from __future__ import annotations

from . import embedding, extraction, search, storage


def process_conversation(text: str) -> int:
    memories = extraction.extract_memories(text)
    stored = 0
    for memory in memories:
        content = (memory.get("content") or "").strip()
        if not content:
            continue
        memory["content"] = content
        memory["type"] = memory.get("type") or "general"
        memory["importance"] = float(memory.get("importance", 0.5))
        memory["embedding"] = embedding.embed_memory(memory["content"])
        storage.insert_memory(memory)
        stored += 1
    return stored


def recall(query: str) -> list[dict]:
    query_embedding = embedding.embed_query(query)
    matches = search.search(query_embedding, top_k=5)
    memories = storage.get_memories_by_ids([match["id"] for match in matches])
    scores = {match["id"]: match["score"] for match in matches}
    for memory in memories:
        memory["score"] = scores.get(memory["id"], 0.0)
    return memories


def forget_memory(id: str) -> bool:
    return storage.delete_memory(id)
