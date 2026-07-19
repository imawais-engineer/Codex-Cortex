"""Embedding service for memories and recall queries."""

from __future__ import annotations

import hashlib
import logging
import math
from functools import lru_cache

logger = logging.getLogger(__name__)
MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(MODEL_NAME)
    except Exception as exc:  # pragma: no cover - environment fallback
        logger.warning("Falling back to deterministic hash embeddings: %s", exc)
        return None


def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    tokens = [token.strip(".,;:!?()[]{}\"'").lower() for token in text.split()]
    for token in filter(None, tokens):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def embed_text(text: str) -> list[float]:
    clean_text = (text or "").strip()
    if not clean_text:
        return _hash_embedding("")
    model = _load_model()
    if model is None:
        return _hash_embedding(clean_text)
    return model.encode(clean_text, normalize_embeddings=True).astype(float).tolist()


def embed_memory(memory: dict) -> list[float]:
    return embed_text(memory.get("content", ""))


def embed_query(query: str) -> list[float]:
    return embed_text(query)
