# Research -> Testbed: PIVOT CONFIRMATION — Tier 5 SPRINT is current direction

**From:** Research  **Date:** 2026-06-08 ~20:00 UTC
**Re:** SPEC went through 4 iterations rapidly today. Clear confirmation of current direction.

## Current SPEC (LOCKED; user-confirmed)

**notes/research_to_testbed_TIER5_SPRINT_SPEC_2026-06-08.md**

Single architectural pitch on Pythia:
- **Panel A:** Pythia-1.4B + Tier 5a substrate-KV (production; D2 already HP empirically)
- **Panel B:** Pythia-160M with layer 6 attention MODIFIED (substrate provides K/V via retrieval; Tier 5b PoC)

## RESCINDED (do not build)

- v1: 5-wow-moment side-by-side gpt-4o-mini demo
- v2: "tiny LLM vs frontier" context-window pitch
- v3: 3-mode toggle (Default / Cost-efficiency / Compliance)

User decision was: pick ONE architectural pitch (Tier 5 sprint on Pythia); drop multi-mode complexity.

## What this means for your in-flight work

- **Reuse:** all 8 substrate library modules + FastAPI skeleton + demo-mode toggle + Cloudflare tunnel + runner toolchain — ALL APPLY to Tier 5 sprint
- **Research VERIFY signoff** (3 MODIFY + 1 ADD + 2 v1.1 FLAGS) — still valid; apply before wiring to `/query`
- **DON'T build:** 3-mode toggle UI; OpenAI/Anthropic API integration as PRIMARY (still useful as side-by-side ablation against Tier 5a panel)
- **DO build:** Pythia-1.4B local serving (Tier 5a) + Pythia-160M layer 6 modification (Tier 5b PoC) + 200M-fact substrate KB

## Experiments in flight (Exp-Dev, parallel)

notes/research_to_exp_dev_TIER5_SPRINT_EXPERIMENTS_2026-06-08.md

T5a-S1/S2/S3/S4 (substrate-KV capacity + Llama family) + T5b-1/2/3/4 (substrate-attention-layer PoC) + KB-1/2/3/4/5 (Wikidata + ConceptNet + Wikipedia + arXiv + PubMed).

## Side note: sparse-value CLOSED empirically (C1 K=10 ratio 0.40)

Doesn't affect Testbed build. Substrate is dense by default (already what your library uses). Sparse-value was a hypothetical v2 optimization now ruled out empirically.

## Standing for your BUILD PLAN

If Tier 5 sprint changes your Week 1 priorities or risk register from prior BUILD PLAN, flag it. I'm standing for your response.

## Cross-references
- Current SPEC: notes/research_to_testbed_TIER5_SPRINT_SPEC_2026-06-08.md
- Library VERIFY signoff: notes/research_to_testbed_v1_demo_LIBRARY_VERIFY_RESPONSE_2026-06-08.md
- Experiments routed: notes/research_to_exp_dev_TIER5_SPRINT_EXPERIMENTS_2026-06-08.md
- Sparse-value CLOSED: notes/exp_dev_to_research_sparse_value_CLOSED_2026-06-08.md
