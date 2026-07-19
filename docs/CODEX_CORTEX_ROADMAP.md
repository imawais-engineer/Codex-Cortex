# Codex Cortex – Development Roadmap

**Elevator Pitch:** Your coding agent that never forgets.

Codex Cortex turns disposable coding chats into an enduring development memory layer. It captures the decisions, constraints, debugging discoveries, project conventions, and personal workflow preferences that normally disappear between Codex sessions, then recalls them exactly when they can accelerate the next task.

## Project Overview
- **Hackathon:** OpenAI Build Week
- **Track:** Developer Tools
- **Problem:** Codex sessions are stateless; developers lose context every time they start a new conversation. Important decisions, debugging tricks, and personal preferences vanish, forcing repeated setup, duplicated explanation, and slower iteration.
- **Solution:** A lightweight memory plugin for Codex that automatically captures, stores, and retrieves contextual facts from coding sessions. It uses GPT‑5.6 for memory extraction and semantic recall, giving developers a persistent, private “second brain.”
- **Primary User:** Any developer who uses Codex repeatedly across the same codebase, especially hackathon builders, solo founders, maintainers, and teams with fast-moving implementation details.
- **Product Promise:** Start a new Codex session and immediately regain the useful context from prior sessions without re-explaining architecture, preferences, bugs, decisions, or next steps.
- **Demo Scenario:** A developer teaches Codex that a project uses FastAPI, SQLite, dark-mode-first UI, and a specific workaround for vector serialization. In a later session, the developer asks “continue the memory browser,” and Codex Cortex recalls those facts automatically.

## Alignment with Judging Criteria
1. **Technological Implementation** – Codex Cortex uses Codex as the development and integration surface while GPT‑5.6 performs structured memory extraction from natural-language coding conversations. The backend converts extracted memories into embeddings, stores them locally, and retrieves them with semantic vector search. The plugin integrates capture and recall into the Codex workflow instead of behaving like a separate note-taking app.
2. **Design** – The experience is intentionally low-friction: a capture button for explicit saves, a recall search bar for targeted context, and an unobtrusive memory browser for inspection and cleanup. The UI should feel native to a developer tool, with concise status states, keyboard-friendly search, dark theme styling, and transparent memory cards that show what was saved and why it matters.
3. **Potential Impact** – Developers can save hours each week by eliminating repetitive context setup, avoiding rediscovery of debugging tricks, and preserving project-specific knowledge across sessions. Because the plugin is local-first and lightweight, it can benefit any Codex user without requiring team adoption, hosted infrastructure, or migration to a new IDE.
4. **Quality of Idea** – Codex Cortex addresses a clear gap: coding agents are powerful within a session but forgetful across sessions. The project is distinctive because it combines automatic extraction, private local storage, semantic recall, and Codex-native ergonomics into a persistent cross-session memory system rather than a generic knowledge base.

## Architecture
Codex Cortex uses a focused three-tier architecture optimized for speed, privacy, and demo reliability.

- **Codex Plugin Frontend** – A side-panel UI built with HTML/CSS/JavaScript or React. It includes a capture button, a recall search bar, and a memory browser. The frontend sends current-session snippets or user-selected text to the backend, displays extraction status, and renders retrieved memories as compact cards.
- **Memory Backend** – A Python FastAPI service exposing `/health`, `/capture`, `/recall`, and optionally `/memories` endpoints. The backend validates requests, calls GPT‑5.6 for structured memory extraction, creates embeddings, ranks relevant memories, and returns JSON responses suitable for the plugin UI.
- **Storage** – A local SQLite database stores memory records, metadata, source session IDs, timestamps, tags, confidence scores, and embedding vectors. Vector similarity can be implemented with `sentence-transformers` plus a custom cosine similarity layer, or DashScope embeddings if credits remain.

**Data Flow**
1. Developer clicks **Capture** or auto-capture runs when a session ends.
2. Frontend posts the conversation excerpt to `/capture`.
3. Backend asks GPT‑5.6 to extract durable, actionable memories as structured JSON.
4. Backend embeds each accepted memory and writes it to SQLite.
5. Developer searches with the recall bar in a later session.
6. Backend embeds the query, ranks stored memories by cosine similarity, and returns the most relevant facts.
7. Frontend displays recalled context with enough metadata to build trust.

## Core Features
- Automatic memory extraction from Codex conversations using GPT‑5.6 function calling.
- Semantic search over stored memories so users can ask natural questions like “what workaround fixed the auth test?”
- Memory browser showing all extracted facts, including timestamps, tags, source snippets, and confidence indicators.
- Fully local and private storage with no cloud database dependency.
- Optional auto-capture on every session close or periodic background sync for low-effort memory collection.
- Memory quality controls: deduplication, confidence thresholds, source attribution, and edit/delete actions.
- Hackathon-ready demo path that shows capture in one session and recall in a fresh session.

## Development Levels (build order)
### Level 1 – Minimum Viable Plugin (MVP) – Day 1
- [ ] Scaffold FastAPI backend with `/health` and a `/capture` endpoint.
- [ ] Implement GPT‑5.6 memory extraction using function calling with a strict schema for `fact`, `category`, `tags`, `importance`, and `source_excerpt`.
- [ ] Create SQLite tables for memories, embeddings, sessions, and capture events.
- [ ] Add a simple embedding pipeline using `sentence-transformers` with deterministic local inference.
- [ ] Build a simple HTML frontend with a capture button, textarea or session-context payload, loading state, and success/error status message.
- [ ] Package as a Codex plugin with `manifest.json`, static files, and clear local backend configuration.
- [ ] Add seed sample memories so judges can understand the experience even before running a full capture flow.

### Level 2 – Recall & Search – Day 2
- [ ] Add `/recall` endpoint with semantic search and configurable `top_k` results.
- [ ] Implement query embedding and cosine similarity retrieval against stored memory vectors.
- [ ] Return ranked memories with score, category, tags, created timestamp, and source session metadata.
- [ ] Frontend: add a search bar that displays retrieved memories as readable cards.
- [ ] Add a “Memory Browser” view listing all stored facts with filter chips for architecture, debugging, preferences, decisions, and TODOs.
- [ ] Implement delete and refresh actions so users can correct memory quality during the demo.
- [ ] Add basic pytest coverage for `/capture`, `/recall`, database writes, and empty-result behavior.

### Level 3 – Polish & Demo – Day 3
- [ ] Add auto-capture on session close or periodic background sync if Codex plugin hooks allow it; otherwise provide a reliable manual capture fallback.
- [ ] Improve UI styling with a dark theme, Codex-compatible spacing, accessible contrast, empty states, and concise success toasts.
- [ ] Add privacy messaging that clearly states memories are stored locally in SQLite.
- [ ] Write a comprehensive README with setup instructions, architecture diagram, API examples, and a clear explanation of how Codex and GPT‑5.6 were used.
- [ ] Record a 2-minute demo video showing capture, database persistence, a new session, and cross-session recall.
- [ ] Prepare Devpost assets: project description, screenshots, demo GIF, architecture summary, and judging-criteria bullets.
- [ ] Submit to Devpost with the `/feedback` Codex Session ID.

## Technology Stack
- **AI Model:** GPT‑5.6 via OpenAI API for memory extraction, structured function calling, and optional recall summarization.
- **Backend:** Python with FastAPI for fast iteration, OpenAPI docs, simple JSON endpoints, and easy local execution.
- **Embeddings:** `sentence-transformers` using `all-MiniLM-L6-v2` for local embeddings, or DashScope embedding if credits allow and latency is acceptable.
- **Database:** SQLite with a custom vector similarity layer for hackathon simplicity, with ChromaDB as a fallback if vector management becomes a bottleneck.
- **Frontend:** Vanilla HTML/CSS/JavaScript for fastest plugin delivery, with React reserved for post-MVP polish if time permits.
- **Build Tool:** Codex using GPT‑5.6 for code generation, debugging, documentation, test writing, and packaging guidance.
- **Testing:** `pytest`, FastAPI `TestClient`, lightweight frontend smoke checks, and manual Codex plugin verification.
- **Privacy Posture:** Local database by default, no hosted memory service, no telemetry, and explicit user control over capture.

## File Structure (suggested)
```text
codex-cortex/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── memory.py
│   │   └── models.py
│   ├── requirements.txt
│   └── cortex.db
├── plugin/
│   ├── manifest.json
│   ├── index.html
│   ├── style.css
│   └── script.js
├── docs/
│   └── CODEX_CORTEX_ROADMAP.md
├── README.md
└── .gitignore
```

## Testing & Verification
- Unit tests for extraction and search endpoints using `pytest` and mocked GPT‑5.6 responses.
- Unit tests for database insertion, duplicate detection, embedding serialization, and cosine similarity ranking.
- API smoke test: call `/health`, `/capture`, and `/recall` with representative payloads and verify stable JSON responses.
- Manual end-to-end test: start a Codex conversation, capture a fact, close the session, open a new one, and verify recall.
- Plugin verification: ensure the side panel loads, can reach the local backend, shows capture status, and renders search results.
- Privacy verification: confirm all memory records remain in the local SQLite database and no hosted database or telemetry service is contacted.
- Demo readiness check: run with a clean database, seed or capture memories, restart the backend, and confirm memories persist.

## Timeline (72-hour sprint)
| Day | Focus | Key Deliverables |
|-----|-------|------------------|
| 1 | Backend MVP & Plugin Shell | `/capture` works, plugin loads in Codex, SQLite schema exists, first memory can be saved |
| 2 | Recall & Memory Browser | `/recall` works, semantic ranking returns useful results, UI search and browser are functional |
| 3 | Polish, Demo, Submission | README, privacy messaging, visual polish, tests, 2-minute video, Devpost submission |

## Demo Script
1. Open Codex Cortex in the Codex side panel and show an empty or seeded memory browser.
2. Capture a conversation excerpt containing a project decision, a bug fix, and a developer preference.
3. Show GPT‑5.6 extracting concise structured memories from the raw session context.
4. Restart or simulate a new Codex session to demonstrate persistence.
5. Search for a natural query such as “what did we decide about storage?”
6. Show the retrieved memory cards and use them to continue coding without re-explaining context.
7. Close with the value proposition: Codex now remembers the durable context that developers usually have to repeat.

## Risks & Mitigations
- **Risk:** GPT‑5.6 extracts noisy or overly broad memories. **Mitigation:** Use a strict extraction schema, importance thresholds, source excerpts, and user-visible delete/edit controls.
- **Risk:** Vector search quality is weak with small datasets. **Mitigation:** Combine semantic score with recency, category filters, and keyword fallback.
- **Risk:** Plugin integration hooks are limited during the hackathon. **Mitigation:** Ship a manual capture flow first and frame auto-capture as a stretch goal.
- **Risk:** Local embedding setup slows installation. **Mitigation:** Provide a minimal requirements file, document model download behavior, and include seeded demo data.
- **Risk:** Judges worry about privacy. **Mitigation:** Emphasize local SQLite storage, transparent capture, and no cloud memory backend.

## Success Metrics
- Capture a conversation excerpt and store at least three useful memories in under 10 seconds.
- Recall a relevant memory from a fresh session with a natural-language query.
- Maintain a simple local-first setup that a judge can run with documented commands.
- Demonstrate at least one concrete time-saving moment in the demo video.
- Provide clear evidence that Codex and GPT‑5.6 are central to the implementation, not just mentioned in the pitch.
