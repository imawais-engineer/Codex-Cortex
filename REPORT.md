# Codex Cortex Repository Audit

Audit date: 2026-07-19  
Specification compared: docs/CODEX_CORTEX_ROADMAP.md and docs/CODEX_CORTEX_ARCHITECTURE.md  
Requested production specification: .codex/tasks/production_release.md (missing from the repository)

## Validation evidence

- Python source parses successfully.
- Both plugin JavaScript files pass node syntax checks.
- The running service responds to GET http://localhost:8000/health with HTTP 200 and status ok.
- Importing backend.app.main from the repository root fails with ModuleNotFoundError: No module named app.
- Importing app.main only succeeds when backend is manually inserted into the import path.
- A forced capture failure returns a Python tuple containing a 500 value, rather than a FastAPI HTTP 500 response.

## 1. Missing files

### Critical

- .codex/tasks/production_release.md is absent, even though it was named as a source-of-truth specification.
- backend/tests/ and the architecture-required API, manager, extraction, embedding, search, storage, and analytics test modules are absent.

### Required by the architecture or roadmap

- Backend modular boundaries are missing: app/api/memory_api.py, app/core/memory_manager.py, app/core/settings_service.py, app/extraction/extraction_engine.py, app/embeddings/embedding_service.py, app/search/search_engine.py, app/storage/storage_adapter.py, app/storage/sqlite_storage_adapter.py, app/analytics/analytics_service.py, app/models/memory.py, and app/models/settings.py.
- Plugin modules are missing: plugin/src/plugin_host.js, session_capture.js, api_client.js, settings_view.js, analytics_view.js, and memory_browser.js.
- The release artifacts requested for this project are missing: LICENSE, submission_story.md, demo checklist, deployment guide, PROJECT_DOCUMENTATION.md, and PROJECT_TASKS.md.

## 2. Broken imports

### Critical: C-01

- backend/app/main.py and backend/app/analytics.py import app.* as a top-level package. This breaks the documented command python -m backend.app.main from the repository root. The same source only imports when backend is manually made the module root.
- backend/app/init.py appears to be a compatibility placeholder beside the real __init__.py and provides no package behavior; it increases ambiguity around the import layout.

## 3. Incomplete features

- The extraction schema returns only content, type, and importance. The roadmap and architecture require durable-memory fields such as category, tags, source_excerpt, confidence, and reason, plus filtering of low-value and sensitive content.
- Storage has only a minimal memories table. It lacks sessions, capture events, settings, feedback, source attribution, tags, confidence, audit metadata, migrations, filtering, and update support.
- The API lacks DELETE /memories/{id}, update support, settings, feedback, pagination, filtering, configurable recall limits, similarity thresholds, and structured response DTOs.
- The memory manager does not deduplicate, apply a confidence threshold, update memories, record capture events, or manage user corrections.
- Search has no category filters, threshold, recency weighting, keyword fallback, or ranking explanation.
- The analytics implementation only counts memories by type; it does not record recall usage, feedback, recency, or other locally scoped metrics.
- Persistent settings and a settings UI are absent.
- The plugin has no real transcript acquisition, host bridge, session-close auto-capture, settings, feedback, filter chips, delete controls, loading spinner, or success toast. Its capture action always posts a hard-coded sample string.
- The roadmap calls for seeded demo memories and a complete test suite; neither exists.

## 4. Architecture violations

- API routes, request models, CORS policy, static serving, and direct storage access are all combined in backend/app/main.py. This violates the separate Memory API router boundary.
- GET /memories imports and calls storage directly from the route instead of using a service or adapter interface.
- memory_manager.py imports concrete sibling modules rather than depending on storage and service interfaces, contrary to the architecture dependency rules.
- There is no StorageAdapter abstraction or SQLite implementation behind an interface.
- The plugin is a monolithic script rather than the Plugin Host, Session Capture, API Client, Settings, Analytics, and Memory Browser modules specified by the architecture.
- plugin and backend/static contain duplicated frontend assets. They are currently identical, but two editable copies create an avoidable source-of-truth risk.
- Raw dictionaries cross extraction, manager, search, storage, and API boundaries; the shared memory and settings DTOs specified by the architecture do not exist.

## 5. Bugs

### Critical: C-02

- The README start command cannot work: python -m backend.app.main first hits the broken app.* imports and, even if that is corrected, main.py has no Uvicorn entry point.

### Critical: C-03

- The capture and recall exception handlers return ({detail: ...}, 500). FastAPI serializes that as a successful response body instead of sending HTTP 500, so the frontend cannot reliably detect backend failure.

### Critical: C-04

- Memory card content is interpolated into innerHTML. Extracted model output or saved conversation text can inject markup into the plugin page.

### High

- Empty capture and recall strings are accepted. An empty recall query produces a zero vector and can return arbitrary stored memories with zero scores.
- The active CORS policy ignores Settings.cors_origins and combines allow_origins wildcard with credentials enabled, which is unsuitable for a browser credentialed request policy.
- README claims sentence-transformers and all-MiniLM-L6-v2, but the code uses a 128-dimensional hash/random-projection embedding and requirements do not include sentence-transformers.
- The frontend exposes the hard-coded localhost API base and has no explicit host configuration or transcript handoff.
- /memories returns serialized embeddings to the browser even though they are implementation details and can become large.

## 6. Technical debt

- Dependencies are unpinned; numpy is unused; there is no test, lint, format, type-check, or CI configuration.
- SQLite access creates a fresh connection per call, does not provide a transaction around a whole capture, and has no migration or schema-version strategy.
- There is no data-retention, secret-redaction, deduplication, or relevance policy beyond a tiny keyword fallback.
- The model name and embedding-model configuration are not consistently wired through the implementation.
- Documentation contains an inaccurate technology description and an unusable run command.
- No release checklist, deployment guidance, license file, Devpost story artifact, screenshots, or demo materials are tracked.

## Recommended phase order

1. Resolve C-01 through C-04 and establish a real test suite.
2. Add the missing production-release specification and synchronized project documentation/task tracker.
3. Implement the modular architecture and remaining roadmap features behind tested interfaces.
4. Run the full validation suite, then finish the release artifacts.
