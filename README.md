# Codex Cortex

**Elevator pitch:** Your coding agent that never forgets.

Codex Cortex is a local-first memory plugin for the OpenAI Build Week hackathon. It captures durable facts from Codex coding sessions, stores them locally, and recalls them semantically in later sessions so developers do not have to repeat project context.

- **Hackathon:** OpenAI Build Week
- **Track:** Developer Tools
- **License:** MIT

## What It Does

Codex Cortex gives Codex a persistent private memory layer:

1. A Codex side-panel plugin captures conversation context.
2. A FastAPI backend extracts structured memories with GPT-5.6 function calling.
3. Memories are embedded with `sentence-transformers` using `all-MiniLM-L6-v2`.
4. SQLite stores memory content and vectors locally.
5. Recall queries use cosine similarity to return the most relevant saved facts.

If OpenAI credentials or local embedding dependencies are unavailable, the prototype falls back to deterministic local extraction and hash embeddings so the MVP remains runnable for demos.

## Project Structure

```text
codex-cortex/
├── backend/
│   ├── app/
│   │   ├── init.py
│   │   ├── main.py
│   │   ├── memory_manager.py
│   │   ├── extraction.py
│   │   ├── embedding.py
│   │   ├── search.py
│   │   ├── storage.py
│   │   ├── config.py
│   │   └── analytics.py
│   ├── requirements.txt
│   └── cortex.db
├── plugin/
│   ├── manifest.json
│   ├── index.html
│   ├── style.css
│   └── script.js
├── docs/
│   ├── CODEX_CORTEX_ROADMAP.md
│   └── CODEX_CORTEX_ARCHITECTURE.md
├── README.md
└── .gitignore
```

## Install and Run

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure OpenAI credentials for GPT-5.6 extraction

```bash
export OPENAI_API_KEY="your-api-key"
```

The app still runs without an API key by using a local fallback extractor for demo reliability.

### 4. Start the FastAPI backend

```bash
python -m backend.app.main
```

The API will be available at `http://localhost:8000`.

### 5. Open the plugin UI

Open `plugin/index.html` in a browser or load it as the Codex plugin side panel. The UI includes:

- **Capture** button that sends sample conversation text to `/capture`.
- **Recall** search bar that sends natural-language queries to `/recall`.
- **Memory Browser** that loads all saved memories from `/memories`.

## API Examples

Health check:

```bash
curl localhost:8000/health
```

Capture a memory:

```bash
curl -X POST localhost:8000/capture \
  -H "Content-Type: application/json" \
  -d '{"conversation_text":"We decided to use FastAPI for the backend and SQLite for storage."}'
```

List memories:

```bash
curl localhost:8000/memories
```

Recall relevant context:

```bash
curl -X POST localhost:8000/recall \
  -H "Content-Type: application/json" \
  -d '{"query":"What database are we using?"}'
```

## How It Uses Codex and GPT-5.6

- **Codex:** The plugin is designed to live inside Codex as a side-panel developer tool. It captures coding-session context and makes recall available without leaving the Codex workflow.
- **GPT-5.6:** The extraction module sends coding conversation text to GPT-5.6 with a function-calling schema named `extract_memories`. The model returns structured memory objects containing `content`, `type`, and `importance`.
- **Local memory:** Extracted memories are embedded and stored in local SQLite, keeping the developer's memory layer private by default.

## Documentation

- [Development Roadmap](docs/CODEX_CORTEX_ROADMAP.md)
- [Modular Architecture](docs/CODEX_CORTEX_ARCHITECTURE.md)

## License

MIT
# test
