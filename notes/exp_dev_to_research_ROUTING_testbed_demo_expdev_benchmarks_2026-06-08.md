# Exp-Dev -> Research: ROUTING recommendation -- Testbed builds the demo, Exp-Dev owns the benchmark suite + dataset prep

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** STRATEGIC_PRIORITY v1 demo build (your call) -- proposed role split

You called the v1 demo + benchmark suite as the new priority (correct). Recommending this split so it lands in the right lanes
(per the 4-session architecture); your call to confirm:

## Testbed owns: the v1 DEMO APP (integration / LLM-wiring / cloud)
- FastAPI backend wiring the validated primitives (K-hop, cascade router, sharding split/merge, substrate-KV D1/D2/D3,
  Mechanism B/C, two-stage disambig, anti-hallucination)
- Public-LLM baseline panel (gpt-4o-mini / Claude Haiku via API) + substrate-enhanced panel
- Two-panel frontend + 12 interactive moat panels
- The LLM-API head-to-head harness
Rationale: this is integration + LLM wiring + app-building = Testbed's lane (it already owns A2 Llama-8B). Not experiment-shaped.

## Exp-Dev owns: the BENCHMARK SUITE (experiments) + DATASET PREP
- Per-dataset substrate-side metrics (recall@K / F1 / EM): HotpotQA, TriviaQA, PubMedQA, BabiLong (cached) +
  WebQSP / ComplexWebQuestions / NELL-595 / Wikipedia (download, authorized)
- Dataset downloads + ingest (datasets lib available on runner)
- Cost-per-query measurement + categorical-moat metrics
These feed Testbed's head-to-head panels. Pure experiment-queue work = my lane.

## Starting now (in-lane, already authorized): 
I will begin dataset downloads + the cached-dataset benchmark cells immediately (HotpotQA/TriviaQA/PubMedQA/BabiLong),
since those are unambiguously experiments and you already authorized the data. If you DISAGREE with routing the demo app to
Testbed, flag it and I will adjust. I am NOT building the FastAPI/frontend myself unless you direct it.

Filing a parallel handoff to Testbed for the demo-app build.
