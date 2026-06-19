"""Substrate self-index pilot (Research authorized 2026-06-11; 2-3 day build).

Goal: substrate stores its own architectural knowledge (math operations + concepts +
cross-corpus USES links). Comparative validation against LLMs (Claude/GPT) on
pre-registered structural queries.

Day 1 deliverables (this module):
- schema.py    : Atom + Relation dataclasses; Tier, Corpus, RelationType enums
- encode.py    : Atom encoder (bge-large text vector + FHRR tier/corpus binding)
- store.py     : In-memory + JSON-persisted atom store + typed-edge relation store
- ingest.py    : Load atoms + relations from JSON input
- retrieve.py  : Query interface (semantic similarity + relation lookup + hybrid)
- cli.py       : Operator CLI (ingest, query, stats)

Day 2-3 deliverables (later modules):
- validate.py  : Comparative-vs-LLM harness for the 10 pre-registered queries

Cross-references:
- Research authorization: notes/research_to_testbed_SUBSTRATE_SELF_INDEX_PILOT_2026-06-11.md
- Existing substrate primitives: backend/substrate/*.py + backend/kb/*
- Encoder: backend/llm/bge_encoder.py
"""
