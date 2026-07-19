"""FastAPI entry point for the Codex Cortex memory backend.

The preferred runtime is FastAPI + Uvicorn. For restricted demo environments where
those packages cannot be installed, `python -m app.main` falls back to a
small stdlib HTTP server that exposes the same MVP endpoints.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from app import analytics, memory_manager, storage
from app.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = Settings()
HAS_FASTAPI = importlib.util.find_spec("fastapi") is not None and importlib.util.find_spec("uvicorn") is not None

if HAS_FASTAPI:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field

    class CaptureRequest(BaseModel):
        conversation_text: str = Field(..., min_length=1)

    class RecallRequest(BaseModel):
        query: str = Field(..., min_length=1)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        storage.init_db()
        logger.info("Codex Cortex backend started")
        yield

    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/capture")
    def capture(payload: CaptureRequest) -> dict:
        try:
            memories_stored = memory_manager.process_conversation(payload.conversation_text)
            logger.info("Stored %s memories", memories_stored)
            return {"memories_stored": memories_stored}
        except Exception as exc:
            logger.exception("Capture failed")
            raise HTTPException(status_code=500, detail="Failed to capture memories") from exc

    @app.post("/recall")
    def recall(payload: RecallRequest) -> list[dict]:
        try:
            return memory_manager.recall(payload.query)
        except Exception as exc:
            logger.exception("Recall failed")
            raise HTTPException(status_code=500, detail="Failed to recall memories") from exc

    @app.get("/memories")
    def memories() -> list[dict]:
        try:
            return storage.get_all_memories()
        except Exception as exc:
            logger.exception("Memory listing failed")
            raise HTTPException(status_code=500, detail="Failed to list memories") from exc

    @app.delete("/memories/{memory_id}")
    def delete_memory(memory_id: str) -> dict:
        try:
            deleted = memory_manager.forget_memory(memory_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Memory not found")
            return {"deleted": True}
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Delete failed")
            raise HTTPException(status_code=500, detail="Failed to delete memory") from exc

    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="plugin_ui")
else:
    app = None


class FallbackHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict | list, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _send_static_file(self, filename: str, content_type: str) -> None:
        static_path = os.path.join(os.path.dirname(__file__), "..", "static", filename)
        with open(static_path, "rb") as file_handle:
            body = file_handle.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._send_json({})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/health":
                self._send_json({"status": "ok"})
            elif path == "/memories":
                self._send_json(storage.get_all_memories())
            elif path in ("/", "/index.html"):
                self._send_static_file("index.html", "text/html")
            elif path in ("/style.css", "/script.js"):
                content_type = "text/css" if path.endswith(".css") else "application/javascript"
                self._send_static_file(path.lstrip("/"), content_type)
            else:
                self._send_json({"detail": "Not found"}, 404)
        except Exception:
            logger.exception("GET failed")
            self._send_json({"detail": "Internal server error"}, 500)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/capture":
                text = payload.get("conversation_text", "")
                if not text:
                    self._send_json({"detail": "conversation_text is required"}, 422)
                    return
                self._send_json({"memories_stored": memory_manager.process_conversation(text)})
            elif path == "/recall":
                query = payload.get("query", "")
                if not query:
                    self._send_json({"detail": "query is required"}, 422)
                    return
                self._send_json(memory_manager.recall(query))
            else:
                self._send_json({"detail": "Not found"}, 404)
        except json.JSONDecodeError:
            self._send_json({"detail": "Invalid JSON"}, 400)
        except Exception:
            logger.exception("POST failed")
            self._send_json({"detail": "Internal server error"}, 500)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path.startswith("/memories/"):
            memory_id = path.rsplit("/", 1)[-1]
            deleted = memory_manager.forget_memory(memory_id)
            self._send_json({"deleted": deleted}, 200 if deleted else 404)
            return
        self._send_json({"detail": "Not found"}, 404)


def run() -> None:
    storage.init_db()
    if HAS_FASTAPI:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
    else:
        logger.warning("FastAPI/Uvicorn unavailable; starting stdlib fallback server")
        HTTPServer(("127.0.0.1", 8000), FallbackHandler).serve_forever()


if __name__ == "__main__":
    run()
