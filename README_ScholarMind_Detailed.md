# 🧠 ScholarMind — AI Research Intelligence Hub

ScholarMind is an AI-powered research assistant that helps users search academic papers, summarize the state of research, surface open research gaps, remember past interests, and export useful outputs.

It is designed as a portfolio-ready product project that demonstrates:
- Product thinking
- End-to-end shipping ability
- Applied AI workflow design
- API integration
- Memory and personalization
- Practical debugging and iteration

---

## What the app does

### Current features

- Search papers from **arXiv** and **Semantic Scholar**
- Merge results into one normalized table
- Summarize research papers with **Groq Llama 3.3**
- Generate **3 research gaps** from paper abstracts
- Save user search memory in **Supabase Postgres**
- Show past interests in a sidebar
- Visualize publication trends by year
- Export search results as **CSV**
- Export citations as **BibTeX**

### What makes it interesting

- It combines retrieval, summarization, memory, and visualization
- It uses a real database instead of temporary in-memory history
- It handles free-tier limitations like rate limits gracefully
- It is deployable as a public Streamlit project
- It shows real product iteration (bug fixes, dedup, retry logic)

---

## Product goal

The goal of ScholarMind is to reduce the friction of early-stage literature review.

Typical academic search is fragmented:
- one site for search,
- another for summaries,
- another for notes,
- and no memory of what the user explored before.

ScholarMind solves that by combining discovery, understanding, and memory into one workflow.

---

## Target users

- Students starting literature reviews
- Researchers scanning new areas quickly
- PMs exploring technical domains
- Analysts tracking AI and emerging technologies
- Curious professionals trying to learn faster

---

## Core problem

Academic discovery is often:
- repetitive,
- hard to synthesize,
- difficult to personalize,
- and easy to forget.

Users often search the same themes repeatedly and still struggle to answer:
- What are the important papers?
- What is the field currently focused on?
- What is still unsolved?
- What did I already explore last week?

---

## Solution overview

ScholarMind combines:

- **Search** → fetch papers from academic sources
- **Reasoning** → summarize findings and detect gaps
- **Memory** → save and recall prior search interests
- **Visualization** → show publication trends
- **Export** → help users take results into their own workflow

---

## Tech stack

| Layer | Tool | Role |
|-------|------|------|
| Frontend | Streamlit | Web app UI and orchestration |
| Search source 1 | arXiv Python client | Paper retrieval from arXiv |
| Search source 2 | Semantic Scholar REST API | Paper retrieval (unauthenticated, with retry) |
| Summarization | Groq (llama-3.3-70b-versatile) | Summary and research-gap generation |
| Memory DB | Supabase Postgres | Persistent memory store |
| Vector extension | pgvector | Prepared for future semantic memory |
| Data handling | pandas | Result normalization and deduplication |
| Charting | Plotly Express | Publication trend visualization |
| Config | python-dotenv | Environment variable management |
| Deployment | Streamlit Community Cloud | Free public hosting via GitHub |

---

## Architecture

```
User
  │
  ▼
Streamlit App (app.py)
  │
  ├── agents/search.py
  │     ├── arXiv API
  │     └── Semantic Scholar API (with retry + backoff)
  │
  ├── agents/summarize.py
  │     └── Groq Llama 3.3 (summary + research gaps)
  │
  ├── agents/memory.py
  │     └── Supabase Postgres
  │           └── research_memory table (upsert + dedup)
  │
  └── utils/export.py
        ├── CSV download
        └── BibTeX download
```

### How it works

1. The user enters a topic in the Streamlit UI
2. The app calls arXiv and Semantic Scholar in parallel
3. Results are normalized into a shared schema
4. Duplicate papers are removed by title
5. Groq LLM generates a multi-paper summary
6. Groq LLM generates 3 research gaps
7. The query and summary are saved to Supabase memory
8. Prior searches appear in the sidebar automatically
9. Users can export results as CSV or BibTeX

---

## Final project structure

```
scholarmind/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── agents/
│   ├── search.py
│   ├── memory.py
│   └── summarize.py
└── utils/
    └── export.py
```

---

## What we built step by step

This section documents the real build journey including fixes and improvements made while shipping the app.

### Step 1 — Create the project scaffold

We started with a simple multi-file Streamlit app structure:

- `app.py` for UI and orchestration
- `agents/search.py` for academic paper retrieval
- `agents/summarize.py` for summaries and research gaps
- `agents/memory.py` for memory storage and retrieval
- `utils/export.py` for CSV and BibTeX export

---

### Step 2 — Build paper search

We added two academic paper sources: arXiv and Semantic Scholar.

Then we normalized both sources into a shared schema with fields:
- `title`, `authors`, `abstract`, `year`, `url`, `source`

Finally, we merged both sources into one dataframe and removed duplicates using lowercase titles.

---

### Step 3 — Add LLM summarization and research gaps

We added Groq Llama 3.3 as the summarization engine.

The app sends top paper titles and abstracts to the model and generates:
- a plain-language research summary,
- and a short list of research gaps.

This gave the app its "AI Intelligence Hub" behavior instead of just showing a list of papers.

---

### Step 4 — Add memory with Supabase

We added persistent memory using Supabase Postgres.

The memory layer saves:
- the user query,
- a normalized version of the query,
- and a summary snippet.

This allowed the app to show prior interests in the sidebar and made the product feel more personalized.

---

### Step 5 — Fix memory display bugs

Early on, memory rows were returned as dictionaries but the UI treated them like strings.

That caused errors like slicing a dict with `mem[:100]`.

We fixed that by reading the `content` field safely:

```python
content = mem.get("content", "")
if content:
    st.caption(content[:120] + "...")
```

---

### Step 6 — Fix import and module issues

During development we ran into import problems in `summarize.py`.

We resolved them by:
- rewriting the file cleanly,
- clearing stale `__pycache__`,
- and validating the import directly before restarting Streamlit.

---

### Step 7 — Handle Streamlit rerun behavior properly

Initially memory saving used `st.rerun()` after inserts.

That caused duplicate saves and reset the visible results.

We replaced that pattern with `st.session_state` so the app could:
- keep search results visible,
- avoid unnecessary reruns,
- and save memory only once per unique query.

---

### Step 8 — Make memory dedup smarter

The first memory implementation stored only a large `content` field, which made duplicate prevention weak.

We improved the design by adding:
- `query` column for the original search text
- `normalized_query` column for lowercase/trimmed version

Then we created a unique index on `(user_id, normalized_query)`.

This let us use `upsert` so repeated searches like `LLM`, `llm`, or extra-spaced versions map to the same memory record.

---

### Step 9 — Improve Semantic Scholar reliability

Semantic Scholar worked but rate limits became a real issue without an API key.

So we updated the search logic to:
- keep the result limit low (2 papers),
- use only required fields,
- wait 2.5 seconds between requests,
- retry on `429` with exponential backoff,
- and fail gracefully instead of breaking the app.

---

### Step 10 — Add charts and exports

To make the app more useful and portfolio-ready, we added:
- publication trend visualization by year,
- CSV export,
- BibTeX export.

---

### Step 11 — Connect the full experience

Once the parts worked independently, we connected them into one flow:

1. Search topic
2. Retrieve papers
3. Summarize findings
4. Detect gaps
5. Save memory
6. Display prior interests
7. Export outputs

---

## Local setup

### 1) Clone the repo

```bash
git clone https://github.com/your-username/scholarmind.git
cd scholarmind
```

### 2) Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=optional_kept_for_status_label
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
```

Notes:
- `GROQ_API_KEY` is required for summaries and research gaps
- `SUPABASE_URL` and `SUPABASE_KEY` are required for memory
- Semantic Scholar works without an API key but applies strict rate limits
- The app handles Semantic Scholar rate limits with retries and backoff

---

## Supabase setup

### 1) Create a new Supabase project

Create a free project at supabase.com.

### 2) Run this SQL in the Supabase SQL Editor

```sql
create table public.research_memory (
  id uuid not null default gen_random_uuid (),
  user_id text not null,
  content text null,
  embedding extensions.vector null,
  created_at timestamp with time zone null default now(),
  query text null,
  normalized_query text null,
  constraint research_memory_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists research_memory_embedding_idx
on public.research_memory
using ivfflat (embedding extensions.vector_cosine_ops)
with (lists = '100') TABLESPACE pg_default;

create unique index IF not exists research_memory_user_query_uidx
on public.research_memory
using btree (user_id, normalized_query) TABLESPACE pg_default;
```

### 3) Why this schema

- `content` stores the readable memory snippet
- `query` stores the original user search text
- `normalized_query` enables dedup across different capitalizations
- `embedding` is included for future vector-memory expansion
- the unique index prevents duplicate rows for the same normalized query and user

---

## Run locally

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

---

## Current user flow

1. Open the app
2. Enter a research topic
3. Click **Search Papers**
4. View state of research, research gaps, publication trends, and search results
5. Check the sidebar for saved past interests
6. Export results if needed

---

## Troubleshooting

### Semantic Scholar rate limit hit

You may see messages like:

```
Semantic Scholar rate limit hit. Retrying in 3.2s...
```

This is expected on the unauthenticated free path.

What to do:
- avoid rapid repeated searches,
- wait a few seconds between queries,
- rely on arXiv results when Semantic Scholar is temporarily limited.

### Memory not showing

Check:
- `.env` contains valid Supabase credentials
- the `research_memory` table exists in Supabase
- rows are being inserted (check the Supabase Table Editor)
- `SUPABASE_KEY` is a server-side service role key

### Results disappear after search

This used to happen when `st.rerun()` was used in the wrong place.

The current implementation uses `st.session_state` to keep results stable across reruns.

### Duplicate memories

If duplicates still appear:
- confirm `normalized_query` column exists
- confirm the unique index was created
- confirm `memory.py` uses `upsert` with `on_conflict="user_id,normalized_query"`

---

## Limitations

- Semantic Scholar free usage can be rate-limited
- Authentication is not yet implemented
- Memory currently stores text-based records only, not full vector retrieval
- The sidebar shows recent interests, not relevance-ranked memory yet
- Research gap quality depends on model output and source paper quality

---

## Roadmap

- Add user authentication via Supabase Auth
- Add saved-paper collections per user
- Enable semantic memory recall using embeddings
- Rank memories by relevance instead of recency
- Add PDF upload and summarization
- Add follow-up chat on top of search results
- Add daily digest or topic alert feature

---

## Why this project is portfolio-worthy

ScholarMind demonstrates:
- clear problem framing,
- practical MVP scoping,
- real tradeoff decisions,
- multi-API orchestration,
- state management in Streamlit,
- persistence with Supabase,
- debugging and iteration under real constraints,
- and user-facing product polish.

It is not just an AI demo.
It is a productized research workflow built and debugged end to end.

---

## Deployment

This app is deployed on **Streamlit Community Cloud**.

### Steps

1. Push the code to a public GitHub repository
2. Sign in to Streamlit Community Cloud at share.streamlit.io
3. Connect your GitHub account
4. Select your repo, branch, and `app.py`
5. Add secrets in the deployment settings
6. Click Deploy
7. Test the public URL

### Secrets for deployment

Add these in the Streamlit Cloud secrets editor:

```toml
GROQ_API_KEY = "your_groq_key"
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
GEMINI_API_KEY = "optional"
```

---

## Author

Built by Siddhant Jain as a portfolio project to demonstrate AI product development, research tooling, and practical full-stack iteration.

---

## License

MIT License
