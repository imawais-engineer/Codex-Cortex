"""Codex Cortex – memory plugin for Codex."""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import Settings; settings = Settings()
from app.memory_manager import process_conversation, recall
from app.analytics import get_analytics

logger = logging.getLogger(__name__)

app = FastAPI(title="Codex Cortex", version="0.1.0")

# CORS – allow plugin to call from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# API routes (must be defined BEFORE the static mount)
# ---------------------------------------------------------------------------

class CaptureRequest(BaseModel):
    conversation_text: str


class RecallRequest(BaseModel):
    query: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/capture")
async def capture(payload: CaptureRequest):
    try:
        count = process_conversation(payload.conversation_text)
        logger.info("Stored %d memories", count)
        return {"memories_stored": count}
    except Exception:
        logger.exception("Capture failed")
        return {"detail": "Failed to capture memories"}, 500


@app.post("/recall")
async def recall_endpoint(payload: RecallRequest):
    try:
        memories = recall(payload.query)
        return {"memories": memories}
    except Exception:
        logger.exception("Recall failed")
        return {"detail": "Failed to recall memories"}, 500


@app.get("/memories")
async def list_memories():
    from app.storage import get_all_memories
    memories = get_all_memories()
    analytics = get_analytics()
    return {"memories": memories, "analytics": analytics}


# ---------------------------------------------------------------------------
# Serve the plugin frontend (must be the LAST mount, with a unique name)
# ---------------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="plugin_ui")
