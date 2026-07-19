"""Lightweight deterministic embeddings using TF-IDF and random projection."""
import numpy as np
from collections import Counter
import re

# Fixed random projection matrix (seeded for reproducibility)
EMBEDDING_DIM = 384
RANDOM_STATE = 42
_PROJECTION = None

def _get_projection(vocab_size: int) -> np.ndarray:
    """Lazy init a random projection matrix."""
    global _PROJECTION
    if _PROJECTION is None or _PROJECTION.shape[0] < vocab_size:
        rng = np.random.RandomState(RANDOM_STATE)
        _PROJECTION = rng.randn(vocab_size + 2000, EMBEDDING_DIM)  # pad vocab
    return _PROJECTION

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())

def embed_text(text: str) -> list[float]:
    """Convert text to a fixed-length vector using TF-IDF-like weighting + random projection."""
    tokens = _tokenize(text)
    if not tokens:
        return [0.0] * EMBEDDING_DIM
    counter = Counter(tokens)
    vocab = list(counter.keys())
    proj = _get_projection(len(vocab))
    # simple TF-IDF: term frequency * log(total docs / doc freq) — here only one doc, use log(tf+1)
    vector = np.zeros(len(vocab))
    for i, word in enumerate(vocab):
        tf = counter[word]
        vector[i] = np.log1p(tf)  # log(1+tf)
    # normalize
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    # project into embedding space
    embedded = vector @ proj[:len(vocab)]
    return embedded.tolist()
embed_memory = embed_text
embed_query = embed_text
