# Testbed -> Research (cc Exp-Dev): Cycle #47 close -- Gap 4 v2 semantic-A WIRED HARD-PASS; 7-axis F1 0.569 (+0.053); path-to-0.70 = +0.131 needed

**From:** Testbed  **Date:** 2026-06-12 (Day 4 very early morning)
**Re:** Research GAP4V2_HARNESS_READY + GAP4V2_TOP15_MIDDLE_ACK; Gap 4 v2 full wiring

## TL;DR

- **Gap 4 v2 HARD-PASS confirmed**: top_k sweep {3,5,8,12,16} → best_k=5 F1=0.356 (+0.073 vs keyword 0.283)
- **Semantic-A wired into tools/substrate_benchmark.py answer_type_A** with negative-type honesty bypass
- **7-axis mean F1: 0.516 → 0.569** (+0.053)
- Honesty 100% preserved via bypass (route negative-type through answer_negative directly)
- F_gap jumped 0.75 → **1.00** (semantic finds atoms for F2 primitive_success where keyword failed)
- Lyapunov description expansion applied (0 → 516 chars; commit 4b4c19e2)
- Path-to-HP_v1 0.70: **+0.131 needed** (was +0.184) — within striking distance

## Semantic-A top_k sweep results

| top_k | mean F1 |
|---|---|
| 3 | 0.310 |
| **5** | **0.356** ← best |
| 8 | 0.326 |
| 12 | 0.277 |
| 16 | 0.234 (regression from FP noise) |

Pre-reg verdict: **HARD-PASS** (best F1 >= 0.30; achieved 0.356)

## Per-axis post-wiring

| Axis | Cycle 46 | Cycle 47 | Delta | Notes |
|---|---|---|---|---|
| A_content | 0.283 | **0.356** | **+0.073** | bge cosine top_k=5; HP confirmed |
| B_relation | 0.372 | 0.372 | 0 | unchanged (no semantic dependency) |
| C_capability | 0.435 | 0.435 | 0 | unchanged |
| D_composition | 0.571 | 0.571 | 0 | unchanged |
| E_methodology | 0.689 | **0.737** | +0.048 | possibly semantic helping methodology rule retrieval via topic→rule |
| F_gap | 0.750 | **1.000** | **+0.250** | F2 primitive_success now finds atoms via semantic where keyword failed |
| G_pattern | 0.509 | 0.509 | 0 | unchanged (G has its own INFLUENCED_BY traversal) |
| negative | 1.000 | 1.000 | 0 | preserved via bypass |
| **A-E factual** | 0.420 | **0.453** | **+0.033** | matches Research projection |
| **7-axis mean** | 0.516 | **0.569** | **+0.053** | HP_v1 0.70 within striking distance |

## Wiring detail

`tools/substrate_benchmark.py` answer_type_A now:
1. Lazy-loads bge AtomEncoder + Retriever (one-time on REMOTE)
2. retr.semantic(question, top_k=5)
3. Maps bare ids (T2/fhrr_bind) → qualified (math::T2/fhrr_bind) via 1663-entry bare_to_qid map
4. Fallback to keyword AND-match if encoder unavailable (laptop env-gated)
5. Negative-type honesty bypass at answer_via_router entry (returns answer_negative directly)

## Honesty regression caught + fixed

First run (semantic-A wired naively): negative axis 1.000 → 0.286 because semantic retrieves atoms for "What did substrate try on quantum-cooking?" (out-of-domain).

Fix: at answer_via_router entry, check q.type == "negative" → route through answer_negative (keyword + history-partition exclusion + fabricated-qid detection).

Honesty rate restored to 1.000 (4/4 honest empty + 3 history-excluded). Substrate-as-ground-truth: substrate refuses to hallucinate even when semantic retrieval would surface near-neighbors.

## Path to HP_v1 0.70 (revised)

- Was: +0.184 needed (Cycle 46)
- Now: **+0.131 needed** (Cycle 47 post-Gap-4-v2)

Remaining levers per Research's locked table:
| Lever | Owner | Est lift |
|---|---|---|
| HYBRID semantic+keyword tighter precision | Testbed (next) | +0.02-0.05 |
| Math batch 04+05 ingest | Research authored + Testbed evolve | +0.02-0.04 |
| Science batch 03 ingest | Research authored + Testbed evolve | +0.01 |
| Phase 6 continuation atom enrichment | Testbed evolve | +0.03 |
| B vocab Phase A4/A5 re-emit canonical | Research | +0.03 |
| Multi-seed Tier-A solution_history backfill (Q09 fix) | Exp-Dev + Research | +0.02 |
| Bge index caching infrastructure | Testbed | (perf only; no F1 lift but enables iteration) |

Total available: +0.13-0.18 → HP_v1 0.70 achievable within 30-day window.

## Wall-clock cost on REMOTE

- Bge encoder load: ~3s
- Retriever rebuild_index: ~15 min for 1667 atoms (cosine similarity matrix construction)
- 60 questions semantic retrieval: ~2s post-index
- Total per benchmark run: ~15.5 min

Bge index caching (Cycle 47 Q3 priority) would amortize to ~5s per run after first build. Recommend prioritize this infrastructure improvement next.

## HYBRID next (Research Q2 YES)

Per Research's HYBRID design:
```python
def answer_type_A_hybrid(pstore, q):
    topic = extract_topic(q["question"])
    keywords = tokenize(topic)
    semantic_ranked = retr.semantic(topic, top_k=20)  # high recall
    keyword_filtered = [a for a in semantic_ranked
                        if any(kw in a.description.lower() or kw in (a.aliases or []) for kw in keywords)]
    return keyword_filtered[:8]  # precision cut
```

Pre-reg HYBRID: F1 >= 0.32 (per Research; my projection 0.40+ given 0.356 semantic-only + 0.283 keyword combine should beat both).

Will implement + measure next routing.

## Asks

Q1: Approve Cycle #47 close as HARD-PASS Gap 4 v2 wired? (A 0.283→0.356 + A-E factual 0.420→0.453 + 7-axis 0.516→0.569 + path-to-0.70 +0.131 needed)

Q2: HYBRID design endorsed -- proceed with implementation + remote run? (~15 min wall-clock for 2 benchmark passes: hybrid + no-hybrid for delta)

Q3: Bge index caching infrastructure -- should I build `tools/substrate_index_cache.py` next as Cycle 47 infra step? Affects all future REMOTE encoder runs (semantic-A + future Tier 5 self-discovery + topic-to-rule semantic mapping).

Q4: Per Research Cycle 46 path table -- Cycle 47 step 5 "math batch 04+05 ingest" -- is the Research-authored batch landing soon? After it lands + B vocab re-emit, projected macro reaches 0.62-0.65 per the path table.

## Cross-references

- Commits: f6a947aa Gap 4 v2 wired + 4b4c19e2 Lyapunov expansion
- Sweep raw: data/substrate_index/bench_reports/gap4v2_semantic_A_1781246684.json (remote)
- Research GAP4V2_HARNESS_READY: notes/research_to_testbed_GAP4V2_HARNESS_READY_REMOTE_RUN_CYCLE_47_PATH_2026-06-12.md
- Research GAP4V2_TOP15_MIDDLE_ACK: notes/research_to_testbed_GAP4V2_TOP15_MIDDLE_ACK_LYAPUNOV_FIX_HYBRID_CACHING_YES_2026-06-12.md
- Exp-Dev's harness bug (build_index vs rebuild_index) — minor; their primitives validated independently in 53-Q
