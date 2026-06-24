# StakeAI Backend

AI-facilitated deliberation platform for precision livestock farming (PLF) policy, grounded in curated research evidence.

## Stack

- **FastAPI** — REST API
- **Supabase** — Postgres + pgvector for documents, sessions, and embeddings
- **LangChain + LangGraph** — agent orchestration and retrieval
- **OpenAI** — `gpt-4o` (LLM) and `text-embedding-3-small` (embeddings)

## Prerequisites

- Python 3.11+
- Supabase project with pgvector enabled
- OpenAI API key

## 1. Supabase Setup

1. Create a project at [supabase.com](https://supabase.com).
2. In the SQL Editor, run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Apply the schema migration from [`supabase/migrations/001_initial_schema.sql`](supabase/migrations/001_initial_schema.sql) (copy/paste into SQL Editor or use Supabase CLI).
4. From **Project Settings → API**, copy:
   - Project URL → `SUPABASE_URL`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (backend only; never expose to clients)

## 2. Environment

```bash
cp .env.example .env
```

Fill in:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
FUTUREKIND_DOCS_PATH=Futurekind Research
RETRIEVAL_TOP_K=5
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 3. Install & Run

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -e .
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## 4. Ingest Research Corpus

Load PDFs from `Futurekind Research/` into Supabase (one-time, or `--force` to re-ingest):

```bash
python -m scripts.ingest
python -m scripts.ingest --force   # re-ingest existing documents
```

## 5. API Usage

### List topics

```bash
curl http://localhost:8000/api/v1/topics
```

### Create session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"scenario_slug": "subsidize-plf"}'
```

Returns `session_id` and the Policy Agent introduction.

### Submit a turn

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/turn \
  -H "Content-Type: application/json" \
  -d '{"message": "I believe subsidies could help small farms adopt welfare monitoring."}'
```

### Get recommendation (when deliberation is complete)

```bash
curl http://localhost:8000/api/v1/sessions/{session_id}/recommendation
```

### Export transcript

```bash
curl http://localhost:8000/api/v1/sessions/{session_id}/transcript
```

## Scenarios

| Slug | Question |
|------|----------|
| `subsidize-plf` | Should governments subsidize precision livestock farming technologies? |
| `mandatory-ai-welfare` | Should AI welfare monitoring be mandatory? |
| `ai-vs-human-inspection` | Can AI monitoring replace human inspections? |

## Architecture

- **Policy Agent** — neutral facilitator; routes deliberation via LangGraph
- **Economic Agent** — costs, adoption, livelihoods (evidence from Economics & Adoption category)
- **Environmental Agent** — sustainability, emissions, resource use
- **Shared retriever** — all agents use the same pgvector knowledge base

Documents live in `Futurekind Research/` (the spec refers to this as "Futurekind"). Category subfolders map to research domains.

## Project Layout

```
app/
├── main.py              # FastAPI entrypoint
├── agents/              # Policy, Economic, Environmental agents
├── graph/               # LangGraph deliberation workflow
├── ingestion/           # PDF load, chunk, embed pipeline
├── retrieval/           # Shared semantic search
├── services/            # Session persistence & deliberation orchestration
└── api/routes/          # REST endpoints
scripts/ingest.py        # Corpus ingestion CLI
supabase/migrations/     # Database schema
```

## Notes

- No authentication in MVP — sessions are anonymous
- Frontend integration is out of scope; API is designed for future `ai-deliberation-hub` wiring
- Empty `Futurekind Research/Policy & Governance/` folder is skipped during ingestion
