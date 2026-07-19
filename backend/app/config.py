"""Configuration helpers for Codex Cortex."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Codex Cortex"
    cors_origins: tuple[str, ...] = ("http://localhost", "http://localhost:3000", "http://localhost:5173", "null")
    openai_model: str = "gpt-5.6"
    embedding_model: str = "all-MiniLM-L6-v2"


def get_settings() -> Settings:
    origins = os.getenv("CODEX_CORTEX_CORS_ORIGINS")
    if origins:
        return Settings(cors_origins=tuple(origin.strip() for origin in origins.split(",") if origin.strip()))
    return Settings()
