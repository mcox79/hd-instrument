"""
v1 demo backend (FastAPI monolith).

Layout:
    backend/main.py             FastAPI app entry; mounts routes
    backend/routes/             HTTP route handlers
        query.py                POST /query (bare LLM + substrate-enhanced)
        add_fact.py             POST /add_fact
        delete_facts.py         POST /delete_facts (GDPR)
        scale_stats.py          GET /scale_stats
        audit_chain.py          GET /audit_chain/{query_id}
    backend/admin/              Administrative endpoints + control plane
        demo_mode.py            Experiment-pause toggle (per user mandate)
    backend/llm/                LLM client wrappers
        openai_client.py        gpt-4o-mini
        anthropic_client.py     Claude Haiku toggle
    backend/kb/                 Knowledge base ingestion
        wikipedia.py            5.84M article ingest (Week 2)
        corporate.py            Crunchbase + SEC EDGAR + News overlay (Week 2)
    backend/config.py           env vars + paths

Imports `substrate/` library (FHRR primitives + validated PP-* ports).
"""
