# Codex Cortex – Modular Architecture

Codex Cortex is designed as a small, local-first Codex memory system with ten cohesive modules. Each module owns one capability, exposes narrow interfaces, and communicates through explicit APIs or function contracts so the project can evolve quickly during a hackathon without turning into a tightly coupled prototype.

## Design Principles
- **Low Coupling:** Modules communicate through well-defined APIs; no direct database access across modules.
- **High Cohesion:** Each module contains all the logic related to one specific capability.
- **Testability:** Every module can be tested independently.
- **Extensibility:** New functionality (e.g., different memory types, cloud sync) can be added without rewriting core modules.

## Module Overview
1. **Plugin Host (Frontend Shell):** Renders the Codex side-panel experience and coordinates navigation between Capture, Recall, Memory Browser, Settings, and Feedback views.
2. **Session Capture:** Collects the active Codex conversation transcript and packages it for memory extraction.
3. **Memory API (Backend Router):** Exposes HTTP endpoints, validates payloads, and routes requests without embedding business logic.
4. **Extraction Engine:** Uses GPT-5.6 function calling to transform raw session text into structured memory candidates.
5. **Embedding Service:** Converts memories and recall queries into comparable vector embeddings.
6. **Search Engine:** Performs similarity search and ranking over stored memory embeddings.
7. **Storage Adapter:** Owns all database and vector-store persistence operations behind a replaceable interface.
8. **Memory Manager (Business Logic):** Orchestrates capture, extraction, embedding, storage, update, conflict, and forgetting workflows.
9. **Configuration & Settings:** Manages user preferences, API keys, model choices, capture behavior, and settings persistence.
10. **Analytics & Feedback:** Computes local usage insights and records user feedback for improving memory quality.

## Module 1: Plugin Host (Frontend Shell)
- **Responsibility:** Render the UI inside Codex’s side panel; manage navigation between Capture, Recall, and Memory Browser views.
- **Dependencies:** None (self-contained).
- **Interfaces:** Communicates with the Memory API module via HTTP.
- **Inputs:** User clicks, search queries, settings changes, and browser lifecycle events from the Codex plugin container.
- **Outputs:** HTTP requests to the backend, rendered memory cards, status messages, empty states, and settings controls.
- **Cohesion Boundary:** Owns presentation and client-side view state only; it does not extract memories, rank results, or access storage directly.
- **Testing Strategy:** Frontend component tests or DOM smoke tests verify navigation, loading states, error states, and rendering of mocked API responses.

## Module 2: Session Capture
- **Responsibility:** Grab the current Codex conversation transcript (via Codex SDK or DOM scraping) and hand it to the Memory API.
- **Dependencies:** Plugin Host (for UI trigger).
- **Interfaces:** Sends conversation text to the Memory API `/capture` endpoint.
- **Inputs:** Capture command from the Plugin Host, active session metadata, and accessible transcript text.
- **Outputs:** A normalized capture payload containing transcript text, session ID, source label, timestamp, and optional user-selected excerpt.
- **Cohesion Boundary:** Owns transcript acquisition and normalization only; it does not decide what is worth remembering.
- **Testing Strategy:** Mock Codex SDK or DOM inputs, verify normalized payload shape, and test fallback behavior when transcript access is unavailable.

## Module 3: Memory API (Backend Router)
- **Responsibility:** Expose REST endpoints (`/capture`, `/recall`, `/memories`). Validate input, route requests to the correct service.
- **Dependencies:** Extraction Engine, Search Engine, Storage Adapter.
- **Interfaces:** FastAPI routes; no business logic inside.
- **Primary Endpoints:**
  - `GET /health` returns service readiness.
  - `POST /capture` accepts transcript payloads and delegates to Memory Manager.
  - `POST /recall` accepts a query and returns ranked memories.
  - `GET /memories` returns paginated memory records for the browser.
  - `DELETE /memories/{id}` delegates forgetting to Memory Manager.
- **Cohesion Boundary:** Owns transport concerns, validation, authentication hooks, and HTTP response formatting only.
- **Testing Strategy:** FastAPI `TestClient` tests verify schemas, status codes, dependency injection, and routing with mocked services.

## Module 4: Extraction Engine
- **Responsibility:** Call GPT-5.6 with a function-calling prompt to extract structured memories from raw conversation text.
- **Dependencies:** GPT-5.6 client (OpenAI SDK).
- **Interfaces:** Receives text, returns a list of memory objects (type, content, importance).
- **Memory Object Contract:** Each extracted memory should include `type`, `content`, `importance`, `tags`, `source_excerpt`, `confidence`, and `reason`.
- **Extraction Rules:** Prefer durable facts, project decisions, debugging discoveries, user preferences, setup instructions, and TODOs; reject generic chatter and sensitive secrets.
- **Cohesion Boundary:** Owns prompt construction, function schema, model invocation, response parsing, and extraction confidence logic.
- **Testing Strategy:** Unit tests mock GPT-5.6 responses and verify schema validation, rejection of low-value facts, and safe handling of malformed model output.

## Module 5: Embedding Service
- **Responsibility:** Convert text (memories and queries) into vector embeddings using a local model or OpenAI embeddings.
- **Dependencies:** Embedding model (`sentence-transformers` or `openai.Embedding`).
- **Interfaces:** Function `embed(text: str) -> List[float]`.
- **Inputs:** Memory content, source excerpts, recall queries, or combined searchable text.
- **Outputs:** Normalized numeric vectors with a consistent dimensionality and optional model metadata.
- **Cohesion Boundary:** Owns model loading, embedding generation, normalization, caching, and provider switching; it does not store vectors or rank results.
- **Testing Strategy:** Unit tests verify deterministic vector dimensions, empty-text handling, provider selection, and mocked embedding responses.

## Module 6: Search Engine
- **Responsibility:** Perform cosine similarity search over stored embeddings; rank and return relevant memories.
- **Dependencies:** Storage Adapter (to fetch all memories and their vectors).
- **Interfaces:** Function `search(query_embedding, top_k) -> List[Memory]`.
- **Inputs:** Query embedding, `top_k`, optional category filters, optional minimum similarity threshold, and optional recency weighting.
- **Outputs:** Ranked memory results containing memory fields, similarity score, and ranking explanation metadata.
- **Cohesion Boundary:** Owns retrieval and ranking only; it does not create embeddings or mutate persisted data.
- **Testing Strategy:** Unit tests use fixed vectors to verify cosine similarity, sorting, threshold behavior, filter behavior, and empty-store behavior.

## Module 7: Storage Adapter
- **Responsibility:** Abstract all database operations (CRUD for memories, vector store). Swap implementations (SQLite, ChromaDB, etc.) without affecting other modules.
- **Dependencies:** Database driver.
- **Interfaces:** Functions like `insert_memory(memory)`, `get_all_memories()`, `delete_memory(id)`.
- **Core Methods:**
  - `insert_memory(memory)` persists a memory and its embedding.
  - `get_memory(id)` retrieves one memory by identifier.
  - `get_all_memories(filters=None)` returns memory rows for search or browsing.
  - `update_memory(id, patch)` edits user-corrected memory content or metadata.
  - `delete_memory(id)` removes a memory and associated vectors.
  - `get_settings()` and `save_settings(settings)` persist local configuration when used by the settings module.
- **Cohesion Boundary:** Owns persistence, migrations, transactions, serialization, and database errors; no other module reads SQLite directly.
- **Testing Strategy:** Repository tests run against temporary SQLite databases and verify migrations, CRUD operations, vector serialization, and transaction rollback.

## Module 8: Memory Manager (Business Logic)
- **Responsibility:** Orchestrate the capture flow: call Extraction Engine, then Embedding Service, then Storage Adapter. Also handle memory updates, conflicts, and forgetting.
- **Dependencies:** Extraction Engine, Embedding Service, Storage Adapter.
- **Interfaces:** Functions `process_conversation(text)` and `forget_memory(id)`.
- **Core Workflows:**
  - `process_conversation(text)` extracts candidates, filters low-confidence memories, embeds accepted memories, deduplicates similar records, and persists final memories.
  - `recall(query, top_k)` embeds the query, delegates ranking to Search Engine, and formats returned context.
  - `forget_memory(id)` validates the request and deletes the memory through Storage Adapter.
  - `update_memory(id, patch)` applies user edits while preserving audit metadata.
- **Cohesion Boundary:** Owns product rules and orchestration; it does not know database internals, HTTP transport, frontend state, or model-specific prompt details.
- **Testing Strategy:** Service tests mock Extraction Engine, Embedding Service, Search Engine, and Storage Adapter to verify orchestration, deduplication, conflict handling, and error recovery.

## Module 9: Configuration & Settings
- **Responsibility:** Manage user preferences (auto-capture on/off, embedding model choice, API keys). Provide a simple settings UI in the plugin.
- **Dependencies:** Plugin Host (for UI), Storage Adapter (to persist settings).
- **Interfaces:** JSON settings file or simple key-value store.
- **Settings Scope:** Auto-capture toggle, capture frequency, embedding provider, local model name, OpenAI API key reference, result count, similarity threshold, privacy mode, and debug logging.
- **Cohesion Boundary:** Owns configuration validation and persistence contracts; it does not execute capture, extraction, search, or analytics workflows.
- **Testing Strategy:** Unit tests validate defaults, schema migration, invalid values, persistence, and redaction of sensitive settings in logs or UI.

## Module 10: Analytics & Feedback
- **Responsibility:** Collect usage statistics (locally) to show the user how many memories are stored, most recalled facts, etc. Also handle the “feedback” mechanism to improve future extraction.
- **Dependencies:** Storage Adapter.
- **Interfaces:** Read-only queries; optional UI in the Plugin Host.
- **Local Metrics:** Total memories, memories by type, recall count, most recently captured facts, most frequently recalled facts, average similarity score, and feedback ratio.
- **Feedback Actions:** Mark memory as useful, mark memory as incorrect, request re-extraction, flag duplicate, or suggest improved wording.
- **Cohesion Boundary:** Owns local insights and feedback records only; it does not change extraction prompts directly without going through Memory Manager or settings-controlled workflows.
- **Testing Strategy:** Unit tests seed temporary storage and verify aggregate counts, feedback persistence, and no network calls.

## Module Interaction Diagram (textual)
A typical capture flow crosses modules in this order:

```text
Plugin Host
  → Session Capture
  → Memory API
  → Memory Manager
  → Extraction Engine
  → Memory Manager
  → Embedding Service
  → Memory Manager
  → Storage Adapter
```

A typical recall flow crosses modules in this order:

```text
Plugin Host
  → Memory API
  → Memory Manager
  → Embedding Service
  → Search Engine
  → Storage Adapter
  → Search Engine
  → Memory Manager
  → Memory API
  → Plugin Host
```

The key architectural rule is that the Plugin Host never accesses storage, the Memory API never performs business logic, and model-specific logic stays inside the Extraction Engine and Embedding Service.

## File Structure Reflection
Each module should map to either one file or a small folder with high internal cohesion. The suggested layout keeps frontend, backend routing, business logic, model integration, search, persistence, settings, and analytics separated.

```text
codex-cortex/
├── backend/
│   ├── app/
│   │   ├── main.py                         # FastAPI app bootstrap and dependency wiring
│   │   ├── api/
│   │   │   └── memory_api.py               # Module 3: Memory API routes
│   │   ├── core/
│   │   │   ├── memory_manager.py           # Module 8: orchestration/business logic
│   │   │   └── settings_service.py         # Module 9: backend settings logic
│   │   ├── extraction/
│   │   │   └── extraction_engine.py        # Module 4: GPT-5.6 structured extraction
│   │   ├── embeddings/
│   │   │   └── embedding_service.py        # Module 5: embedding provider abstraction
│   │   ├── search/
│   │   │   └── search_engine.py            # Module 6: similarity search and ranking
│   │   ├── storage/
│   │   │   ├── storage_adapter.py          # Module 7: storage interface
│   │   │   └── sqlite_storage_adapter.py   # Module 7: SQLite implementation
│   │   ├── analytics/
│   │   │   └── analytics_service.py        # Module 10: local metrics and feedback
│   │   └── models/
│   │       ├── memory.py                   # Shared DTOs and domain models
│   │       └── settings.py                 # Settings schemas
│   ├── tests/
│   │   ├── test_memory_api.py
│   │   ├── test_memory_manager.py
│   │   ├── test_extraction_engine.py
│   │   ├── test_embedding_service.py
│   │   ├── test_search_engine.py
│   │   ├── test_storage_adapter.py
│   │   └── test_analytics_service.py
│   └── requirements.txt
├── plugin/
│   ├── manifest.json
│   ├── index.html                          # Module 1: side-panel shell root
│   ├── src/
│   │   ├── plugin_host.js                  # Module 1: navigation and view composition
│   │   ├── session_capture.js              # Module 2: transcript acquisition
│   │   ├── api_client.js                   # HTTP client for Memory API
│   │   ├── settings_view.js                # Module 9: settings UI
│   │   ├── analytics_view.js               # Module 10: feedback/metrics UI
│   │   └── memory_browser.js               # Browser presentation owned by Plugin Host
│   ├── style.css
│   └── script.js
├── docs/
│   ├── CODEX_CORTEX_ROADMAP.md
│   └── CODEX_CORTEX_ARCHITECTURE.md
├── README.md
└── .gitignore
```

### Dependency Rules by File Area
- `plugin/src/*` may call `api_client.js`, but must not import backend files or access SQLite.
- `backend/app/api/*` may call service interfaces, but must not implement extraction, embedding, search, or persistence logic.
- `backend/app/core/memory_manager.py` may orchestrate services, but must depend on interfaces rather than concrete database or model implementations.
- `backend/app/storage/*` may import database drivers, but other backend modules must access persistence only through `StorageAdapter`.
- `backend/app/extraction/*` and `backend/app/embeddings/*` may depend on model SDKs, but those SDKs must not leak into API route or frontend code.
- `backend/app/analytics/*` should use read-only storage methods by default and should not mutate memories except through explicit feedback records.

## Interface Summary
| Module | Public Interface | Primary Caller | Primary Return Value |
|--------|------------------|----------------|----------------------|
| Plugin Host | UI events and render functions | User | Rendered views and API calls |
| Session Capture | `captureCurrentSession()` | Plugin Host | Normalized transcript payload |
| Memory API | `/capture`, `/recall`, `/memories` | Plugin Host / API Client | JSON responses |
| Extraction Engine | `extract_memories(text)` | Memory Manager | `List[MemoryCandidate]` |
| Embedding Service | `embed(text)` | Memory Manager | `List[float]` |
| Search Engine | `search(query_embedding, top_k)` | Memory Manager | `List[RankedMemory]` |
| Storage Adapter | `insert_memory`, `get_all_memories`, `delete_memory` | Memory Manager / Search Engine / Analytics | Persisted records |
| Memory Manager | `process_conversation`, `recall`, `forget_memory` | Memory API | Domain results |
| Configuration & Settings | `get_settings`, `save_settings` | Plugin Host / Memory API | Settings object |
| Analytics & Feedback | `get_usage_summary`, `record_feedback` | Plugin Host / Memory API | Metrics or feedback record |
