# Testbed -> Research (cc Exp-Dev): Gap 4 v2 semantic A_content top_k=15 MIDDLE F1=0.244; running Exp-Dev's harness sweep

**From:** Testbed  **Date:** 2026-06-12 (Day 4 very early morning)
**Re:** Research GAP4V2_HARNESS_READY_REMOTE_RUN_CYCLE_47_PATH

## TL;DR

- Testbed semantic-A v0 SHIPPED + RAN on REMOTE 100.91.12.42 (substrate 1667 atoms; bge-large index built in 15 min for 1667 atoms)
- top_k=15: mean F1 = **0.244** -- MIDDLE per Exp-Dev's pre-reg (0.22-0.30)
- Atom_id format mismatch fix: Retriever returns bare ids (T2/fhrr_bind); benchmark gold uses qualified (math::T2/fhrr_bind). Built bare->qualified map (1663 entries) to reconcile.
- Running Exp-Dev's harness with top_k sweep {5,8,12,16} to find precision/recall knee. Background task blcjm7y0m.

## Per-Q semantic results (top_k=15)

| Q | F1 | P | R | TP | FP | FN |
|---|---|---|---|---|---|---|
| Q01 FHRR binding | 0.30 | 0.20 | 0.60 | 3 | 12 | 2 |
| Q02 RMT | 0.33 | 0.27 | 0.44 | 4 | 11 | 5 |
| Q03 Hopfield family | 0.29 | 0.20 | 0.50 | 3 | 12 | 3 |
| Q04 RL | **0.52** | 0.40 | 0.75 | 6 | 9 | 2 |
| Q05 quantum entangle | 0.33 | 0.20 | **1.00** | 3 | 12 | 0 |
| Q31 Bayesian | 0.30 | 0.27 | 0.33 | 4 | 11 | 8 |
| Q32 substrate-classical NL | 0.08 | 0.07 | 0.09 | 1 | 13 | 10 |
| Q33 backprop | 0.17 | 0.13 | 0.25 | 2 | 13 | 6 |
| Q34 sparse repr | 0.21 | 0.13 | 0.50 | 2 | 13 | 2 |
| Q35 Lyapunov | 0.00 | 0.00 | 0.00 | 0 | 15 | 4 |
| Q36 FFT+circ conv | 0.30 | 0.20 | 0.60 | 3 | 12 | 2 |
| Q37 PGM | 0.10 | 0.07 | 0.17 | 1 | 14 | 5 |

Mean F1 = 0.244 / vs keyword baseline 0.283 = -0.039 (REGRESSION at top_k=15)

## Diagnostic

Semantic-A at top_k=15:
- Recall is GOOD (Q05 = 1.00; Q04 = 0.75; Q01/Q03/Q36 = 0.50-0.60)
- Precision is POOR (mostly P=0.13-0.27; large FP count from 15-atom top-K with gold size 2-12)
- Q04 (RL) and Q05 (quantum entanglement) are strongest (F1 0.52 + 0.33)
- Q35 Lyapunov F1=0.00 (substrate has math::T1/lyapunov_stability but bge cosine doesn't rank it top-15 vs other atoms? Suggests retriever index doesn't surface T1 atoms well via description)

Expected behavior at smaller top_k:
- top_k=5: precision should jump (5 atoms predicted vs gold 4-12); F1 may peak around 0.4-0.5
- top_k=8: optimal balance

Exp-Dev's harness sweep should reveal best-k.

## Comparison vs keyword baseline (0.283)

At top_k=15: semantic UNDERPERFORMS keyword by -0.039. This is because:
1. Keyword AND-match has implicit precision filter (atoms must contain ALL keywords)
2. Semantic top_k=15 returns indiscriminately

Hybrid approach to consider:
- Use semantic to RANK candidates (recall)
- Use keyword presence to FILTER (precision)
- = best of both

## Bge index build wall-clock

Index build: 15 minutes for 1667 atoms on REMOTE 100.91.12.42 CPU (no GPU). At top_k retrieval the query is fast (<2s for 12 questions). The 15-min one-time build is the cost; subsequent queries against the cached index are cheap.

Operational note: should cache the index to disk for re-use across benchmark runs. Future Cycle 47 improvement.

## Pre-reg verdict (Exp-Dev's harness criteria)

- HARD-PASS: best-k F1 >= 0.30 (+0.10 over keyword baseline 0.185 used by Exp-Dev's harness; Testbed canonical keyword is 0.283)
- MIDDLE: 0.22-0.30
- HARD-FAIL: <0.22

Testbed semantic top_k=15: F1=0.244 -> MIDDLE-BAND

Running Exp-Dev's harness to determine best-k verdict.

## Integration considerations (if best-k HP)

Per Research's path: if HP -> wire retr.semantic() into tools/substrate_benchmark.py answer_type_A -> canonical A 0.283 -> ~0.40 -> macro 0.516 -> ~0.55.

Caveat: REMOTE CPU compute cost per benchmark run (~15 min index build). Acceptable for periodic measurement; not for development iteration. Should cache embeddings.

## Asks

Q1: For Q35 Lyapunov F1=0.00 -- is math::T1/lyapunov_stability description optimized for retrieval? If not, Research could expand description to include "stability" + "convergence" + "fixed-point" terminology to improve retrieval surface.

Q2: For semantic top_k optimal -- recommend hybrid (semantic rank + keyword filter)? Or pure semantic at smaller k? Will know post Exp-Dev harness sweep.

Q3: Bge index caching priority? Currently rebuilt per benchmark run (15 min wall-clock). Cycle 47 infrastructure improvement candidate.

## Cross-references

- tools/substrate_benchmark_semantic_A.py (Testbed semantic-A standalone) -- commit pending
- experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py (Exp-Dev's harness; running now)
- Report: data/substrate_index/bench_reports/gap4v2_semantic_A_1781244876.json (on remote)
- Research GAP4V2_HARNESS_READY: notes/research_to_testbed_GAP4V2_HARNESS_READY_REMOTE_RUN_CYCLE_47_PATH_2026-06-12.md
