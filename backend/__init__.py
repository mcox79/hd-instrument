"""
v1 demo backend (FastAPI monolith).

Layout:
    backend/main.py             FastAPI app entry; mounts routes
    backend/landing.py          / landing HTML
    backend/decisive_test.py    /demo cheap-decisive-test page
    backend/playground.py       /playground interactive algebraic ops
    backend/benchmark.py        /benchmark 30-query head-to-head
    backend/routes/
        query_tier5a.py         /query/tier5a + audit_chain + baseline + counterfactual + AND/NOT/COUNT
    backend/llm/
        openai_client.py        gpt-4o-mini (used by /query/tier5a/baseline)
        anthropic_client.py     Claude Haiku
        pythia_client.py        Local Qwen-2.5-1.5B-Instruct (Tier 5a panel A)
    backend/kb/
        seed_facts.py           169 hand-crafted facts (Wikipedia/Wikidata ingest pending)
    backend/config.py           env vars + paths

Imports `substrate/` library (FHRR primitives + validated PP-* ports).
"""
