"""Lightweight TF-IDF plus random projection embeddings for Codex Cortex."""

from __future__ import annotations

import hashlib
import math
import random
import re
from collections import Counter

_DIMENSIONS = 128
_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text or "")]


def _projection_for_token(token: str) -> list[float]:
    seed = int.from_bytes(hashlib.sha256(token.encode("ascii", errors="ignore")).digest()[:8], "big")
    rng = random.Random(seed)
    return [rng.gauss(0.0, 1.0) for _ in range(_DIMENSIONS)]


def embed_text(text: str) -> list[float]:
    """Tokenize text and return a deterministic list of float embedding values."""

    tokens = _tokenize(text)
    if not tokens:
        return [0.0] * _DIMENSIONS

    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    vector = [0.0] * _DIMENSIONS

    for token, count in counts.items():
        tf = count / total
        idf = 1.0 + math.log(1.0 + (total / count))
        weight = tf * idf
        projection = _projection_for_token(token)
        for index, value in enumerate(projection):
            vector[index] += weight * value

    norm = math.sqrt(sum(value * value for value in vector))
    if norm > 0:
        vector = [value / norm for value in vector]
    return [float(value) for value in vector]


embed_memory = embed_text
embed_query = embed_text
