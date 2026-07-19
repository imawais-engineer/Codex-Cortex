"""Cosine similarity search over stored memory embeddings."""

from __future__ import annotations

import math

from . import storage


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    dot = sum(left[index] * right[index] for index in range(size))
    left_norm = math.sqrt(sum(value * value for value in left[:size]))
    right_norm = math.sqrt(sum(value * value for value in right[:size]))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    scored = []
    for memory in storage.get_all_memories():
        score = cosine_similarity(query_embedding, memory.get("embedding", []))
        scored.append({"id": memory["id"], "score": score})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]
