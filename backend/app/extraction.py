"""GPT-5.6 based memory extraction with a local fallback."""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)
SYSTEM_PROMPT = "You are a memory extraction assistant. Extract factual statements about the developer's decisions, preferences, and technical context from the coding conversation. Do not extract generic code snippets."


def _fallback_extract(text: str) -> list[dict]:
    clean = " ".join((text or "").split())
    if not clean:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    keywords = ("decided", "use", "using", "prefer", "backend", "storage", "database", "api", "fastapi", "sqlite")
    memories = []
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords):
            memories.append({"content": sentence.strip(), "type": "technical_context", "importance": 0.8})
    if not memories:
        memories.append({"content": clean[:500], "type": "general", "importance": 0.5})
    return memories[:5]


def extract_memories(text: str) -> list[dict]:
    try:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-5.6",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "extract_memories",
                        "description": "Extract durable developer memories from a coding conversation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "memories": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "content": {"type": "string"},
                                            "type": {"type": "string"},
                                            "importance": {"type": "number"},
                                        },
                                        "required": ["content", "type", "importance"],
                                    },
                                }
                            },
                            "required": ["memories"],
                        },
                    },
                }
            ],
            tool_choice={"type": "function", "function": {"name": "extract_memories"}},
        )
        tool_calls = response.choices[0].message.tool_calls or []
        if not tool_calls:
            return []
        arguments = json.loads(tool_calls[0].function.arguments)
        return arguments.get("memories", [])
    except Exception as exc:
        logger.warning("OpenAI extraction failed; using local fallback: %s", exc)
        return _fallback_extract(text)
