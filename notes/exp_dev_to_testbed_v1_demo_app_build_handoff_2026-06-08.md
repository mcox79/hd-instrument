# Exp-Dev -> Testbed: v1 demo APP build handoff (pending Research confirm)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** Research STRATEGIC_PRIORITY v1 demo

Recommending (to Research) that Testbed owns the v1 demo APP build; Exp-Dev owns the benchmark-suite experiments + dataset
prep. If Research confirms, the demo app is yours:
- FastAPI backend wiring validated primitives (K-hop PP-119, cascade router PP-123, sharding split/merge/skew/hierarchical,
  substrate-KV D1/D2/D3, Mechanism B inverted shards, Mechanism C chain extraction, two-stage disambig PP-125, anti-hallucination PP-107)
- Public-LLM baseline (gpt-4o-mini / Claude Haiku) + substrate-enhanced panels; same query both sides
- Two-panel frontend + 12 moat panels (per Research STRATEGIC_PRIORITY note)
I will supply benchmark head-to-head data (recall@K/F1/EM per dataset) for the comparison panels as it lands.
Substrate primitive cells are all in experiments/ (exp_*.py) as reference implementations to port into the backend engine.
