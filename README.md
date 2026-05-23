# BEACON — Bus Emergency Assistance & Companion Operations Network

An AI-powered emergency assistant for King County Metro bus drivers, delivered via iMessage.

When a driver faces an emergency — oil leak, brake failure, assault on board — they need answers in seconds, not minutes of searching through a 300-page operations manual. BEACON listens on iMessage, searches the manual, and replies with clear actionable guidance instantly.

---

## How It Works

```
iMessage → Photon Spectrum → Gateway (TypeScript)
       → Orchestration Bus (Python/FastAPI)
       → RAG Pipeline (RocketRide + Qdrant)
       → MiniMax LLM
       → Reply back to driver via iMessage
```

1. Driver sends a question via iMessage
2. Photon Spectrum receives it and forwards to the TypeScript gateway
3. Gateway dispatches to the Python orchestration bus
4. RAG pipeline embeds the question, searches Qdrant for relevant manual sections
5. MiniMax LLM formats a structured reply
6. Driver receives a clean, actionable response in seconds

---

## Response Format

Every reply is structured for quick reading on a phone:

```
Hello, Driver

🔧 Possible Fixes:
- Step 1
- Step 2

❓ Why This Happened:
- Explanation based on the manual

📞 Contacts:
- Coordinator: 206-XXX-XXXX

📖 Source:
- Section 10.64 — Defective Vehicles

Do you need any other information?

— BEACON Transit Assistant
```

---

## Project Structure

```
├── gateway/                  # TypeScript — iMessage listener (Photon Spectrum)
│   ├── index.ts
│   ├── listener.ts
│   └── parser.ts
├── orchestration/            # TypeScript — dispatcher
│   └── dispatcher.ts
├── shared/                   # TypeScript — shared types
│   └── types.ts
├── pipelines/                # RocketRide pipeline definitions
│   ├── ingestion.pipe        # PDF → chunks → embeddings → Qdrant
│   └── rag_search.pipe       # question → embeddings → Qdrant → documents
├── server/                   # Python backend
│   ├── rag_agent.py          # RAG logic + MiniMax LLM
│   └── orchestration_bus.py  # FastAPI server (port 5565)
├── scripts/                  # Utility scripts
│   ├── check.py              # Connectivity health check
│   ├── ingest.py             # Ingest PDFs into Qdrant
│   └── test_rr.py
├── data/                     # Source documents (not committed)
│   └── the_book.pdf          # King County Metro operations manual
├── .env                      # Environment variables (not committed)
├── env.example               # Environment variable template
├── package.json
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| iMessage gateway | Photon Spectrum + spectrum-ts |
| Vector database | Qdrant |
| RAG pipeline | RocketRide |
| Embeddings | miniLM (sentence-transformers) |
| LLM | MiniMax M2.7 |
| Backend | Python + FastAPI |
| Gateway | TypeScript + Node.js |

---

## Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- RocketRide VS Code extension (starts the RocketRide server)
- Qdrant binary

### 1. Install dependencies

```bash
npm install
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp env.example .env
# Fill in your keys in .env
```

Required variables:
```
ROCKETRIDE_URI=http://localhost:<port>     # auto-updated by check.py
ROCKETRIDE_APIKEY=your-key
MINIMAX_API_KEY=your-key
SPECTRUM_PROJECT_ID=your-id
SPECTRUM_PROJECT_SECRET=your-secret
ROCKETRIDE_QDRANT_HOST=localhost
ROCKETRIDE_QDRANT_COLLECTION=beacon_protocols
```

### 3. Ingest the manual

```bash
python scripts/ingest.py data/the_book.pdf
```

Only needed once — Qdrant persists data across restarts.

### 4. Run

```bash
# Terminal 1 — Qdrant
/path/to/qdrant

# Terminal 2 — Orchestration bus
python server/orchestration_bus.py

# Terminal 3 — iMessage gateway
npx tsx gateway/index.ts
```

### 5. Health check

```bash
python scripts/check.py
```

---

## Built At

HackWithSeattle 2026
