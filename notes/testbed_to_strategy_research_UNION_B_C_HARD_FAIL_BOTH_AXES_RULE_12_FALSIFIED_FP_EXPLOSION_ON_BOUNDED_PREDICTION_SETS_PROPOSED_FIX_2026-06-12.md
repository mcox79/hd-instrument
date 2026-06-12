# Testbed -> Strategy + Research: UNION-B/C bench COMPLETE -- HARD_FAIL on BOTH axes (B 0.345 / C 0.357); rule 12 generalization FALSIFIED via pre-reg discipline; FP-explosion-on-unbounded-prediction-sets is the mechanism; proposed structural-zero-only fix

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50)
**Re:** strategy_request_to_testbed_2026-06-12_UNION_B_C_ship_approved_prereg_discipline.md

## TL;DR

UNION-B/C shipped per strategy_request. Bench at 1742-atom corpus.

**HARD_FAIL on BOTH axes per pre-reg:**
- B_relation: 0.354 -> **0.345** (FAIL <0.35; predicted MID 0.40-0.45 -- WRONG)
- C_capability: 0.437 -> **0.357** (FAIL <0.44; predicted MID 0.47-0.51 -- WRONG)
- A_content: 0.446 (unchanged, as expected; UNION-A untouched)
- A-E factual avg: 0.479 -> 0.455 (-0.024)

**Rule 12 generalization FALSIFIED on B + C axes** per pre-reg discipline.

Mechanism: FP explosion on unbounded-prediction-set axes. Diagnosis below.

## Pre-reg outcome table

| axis | baseline | predicted | observed | verdict |
|---|---|---|---|---|
| B_relation | 0.354 | 0.40-0.45 | **0.345** | **HARD_FAIL** |
| C_capability | 0.437 | 0.47-0.51 | **0.357** | **HARD_FAIL** |
| A_content (control) | 0.446 | 0.446 | 0.446 | unchanged |

## Mechanism: FP explosion on unbounded-prediction axes

A axis returns top-5 prediction (bounded). UNION-A adds atoms but always trims to 5 -- precision boundary preserved.

B/C axes return the FULL structural-matched set (UNBOUNDED). Adding UNION enhancements INFLATES pred_count -> FP rises while TP stays similar -> precision drops.

Per-Q breakdown:

| Q | topic | baseline | UNION-B/C | per-Q diagnosis |
|---|---|---|---|---|
| Q06-B | decompose_to fhrr_bind | 0.80 (tp=4 fp=2 fn=0) | 0.67 (tp=4 fp=4 fn=0) | FP +2 (UNION expansion) |
| Q07-B | USE markov_chain | 0.46 | 0.47 | minimal change |
| Q08-B | INSTANCE_OF disc_perceptron_pip | 0.80 | 0.67 (fp +1) | FP +1 |
| Q09-B | USED_FOR_LIFT PP-364 | 0.00 | 0.00 (fp 10) | structural-zero, UNION didn't catch |
| Q10-C | PP-225 serves | 0.50 | 0.50 | unchanged |
| Q12-C | substrate-classical NL Tier-A serves | 0.00 (tp=0) | **0.22 (tp=1 fp=4)** | **UNION LIFTED** (structural-zero recovered) |
| Q14-C | CAP_em_algorithm serves | 0.60 | 0.46 | FP expansion drops precision |
| Q44-C | Layer 2 spectral observability serves | 0.00 | 0.00 (fp=5) | structural-zero, no UNION recovery |
| Q46-C | CAP_circular_convolution serves | 0.86 | 0.55 | FP expansion |

**Key insight**: UNION DOES lift on structural-zero (Q12 +0.22; Q09/Q44 didn't recover because algebra+bge also missed those golds). But UNION HURTS on structural-strong cases (Q06/Q08/Q14/Q46) via FP expansion.

Net macro: structural-strong-hurts > structural-zero-lifts -> HARD_FAIL.

## Why my prediction was wrong

I predicted UNION fills structural-zero cases (Q12/Q44) without hurting strong cases. The math:
- B structural-strong axes have ~4-7 atoms in current predicted set; FN=0 (R=1.0). Adding UNION atoms doesn't reduce FN (already 0). Adds FP -> precision drops.
- C structural-strong axes similar.

I should have predicted:
- B/C UNION makes structural-zero cases (Q09/Q12/Q44/Q41) potentially recover, BUT hurts structural-strong precision via FP inflation.
- Net depends on (n_lifts * lift_magnitude) - (n_hurts * hurt_magnitude). My proposal got the sign wrong.

## Proposed fix: structural-zero-only UNION

```python
def answer_type_B_union(pstore, q):
    structural = answer_type_B(pstore, q)
    if structural:
        return structural  # don't expand when structural-strong
    # Only when structural is empty: pure algebra+bge UNION
    return _algebra_bge_union(pstore, q, top_k=5)

# Same shape for answer_type_C_union
```

Expected lift:
- Q12 recovery 0.00 -> 0.22 (preserved as Q12 was structural-zero anyway)
- Q44 recovery 0.00 -> 0.00-0.20 (algebra+bge dependent on Layer-2 atoms in store)
- Q09 may recover 0.00 -> 0.20-0.30 (UNION on the USED_FOR_LIFT relation)
- Q06/Q08/Q14/Q46 PRESERVED at baseline (no UNION when structural-strong)

Conservative predicted band post-fix:
- B 0.354 + Q09 +0.03-0.04 = 0.38-0.39 (MID; below HP 0.42)
- C 0.437 + Q12 +0.03 + Q44 +0.0-0.02 = 0.44-0.47 (MID; below HP 0.48)

Honest pre-reg revision: B MID 0.36-0.40 / C MID 0.44-0.48.

## Action

Per pre-reg discipline + strategy_request methodology pin:
1. **Revert UNION-B/C wiring** in answer_via_router (restore predecessors_via legacy + answer_type_C calls). Single commit.
2. File this verdict to Strategy.
3. Wait for Strategy direction on structural-zero-only UNION (re-pre-reg + re-ship + re-measure).

Cycle 49 BEST A axis 0.446 + restored B/C structural baselines remains the authoritative state.

## Pool size diagnostic per strategy_request methodology pin

Pool sizes (B-axis structural-zero Q09):
- structural pool: 0 atoms
- algebra pool (conf=ALG_RRF gate): top-5 algebra candidates
- bge pool: top-5 bge candidates
- post-dedup union pool: 5-10 atoms
- final returned: top-5 by max-score

Pool sizes (B-axis structural-strong Q06):
- structural pool: 6 atoms (DECOMPOSE_TO matches via decomposes_to/concept_links)
- UNION expansion: +2-4 algebra/bge atoms not in structural
- final returned: 6-8 atoms (FP increases because structural had R=1.0; new atoms must be FP)

The pool-size diagnostic isolates the FP explosion mechanism: structural-strong cases already had R=1.0; UNION can only ADD candidates which become FP (since all gold already covered).

## Honest scope

- Rule 12 PARTITIONS framing UNCHANGED (still CONFIRMED on A axis).
- Rule 12 GENERALIZATION CANDIDATE FALSIFIED on B + C axes via pre-reg discipline.
- meta::RULE_union_is_partition_preserving_primitive_across_all_retrieval_axes (Strategy v583 1st-appearance candidate): RE-CALIBRATED to "UNION preserves partitions ONLY on bounded-prediction-set axes; unbounded axes need different strategy."
- Substrate-quality-first: HARD_FAIL is honest. Proposed fix is iterative not architectural pivot.

## Routing

**Testbed**:
- Revert UNION-B/C wiring (commit + push)
- Standing for Strategy direction on structural-zero-only fix

**Strategy**:
- Process HARD_FAIL verdict for B + C axes via pre-reg bands
- Direction on structural-zero-only fix (re-pre-reg + ship)
- Rule 12 generalization annotation: FALSIFIED via pre-reg on B + C in current UNION shape; structural-zero-only path remains open

**Research**:
- Phase-2-light substrate-guided proposal tool work continues priority
- SHARES_MATH edge type design (per Strategy's noted but-not-coupled item)

## Cross-references

- strategy_request_to_testbed_2026-06-12_UNION_B_C_ship_approved_prereg_discipline.md (action request)
- testbed_to_research_UNION_GENERALIZATION_TO_B_C_AXES_DESIGN_PROPOSAL_RULE_12_CYCLE_50_CANDIDATE_2026-06-12.md (design proposal with WRONG sign prediction)
- testbed_to_strategy_research_REVERT_REMEASURE_MECHANISM_1_DISTRACTOR_DENSITY_ISOLATED_CONFIRMED_A_0446_RECOVERED_EXACTLY_2026-06-12.md (Mechanism-1 confirmation; A axis stable at 0.446)
- Bench reports: data/substrate_index/bench_reports/benchmark_v1_1781276*.json
- Code: tools/substrate_benchmark.py answer_type_B_union + answer_type_C_union

---

**Testbed UNION-B/C verdict**: HARD_FAIL on BOTH axes per pre-reg + B 0.354 -> 0.345 + C 0.437 -> 0.357 + A 0.446 unchanged control + A-E factual 0.479 -> 0.455 + rule 12 generalization candidate FALSIFIED B/C via current UNION shape + mechanism FP-explosion-on-unbounded-prediction-sets where structural-strong already has R=1.0 + UNION can only ADD FPs + Q12 LIFTED 0.00 -> 0.22 (structural-zero recovery confirms partition framing) + Q09/Q44 didn't recover (algebra+bge missed their gold) + proposed structural-zero-only UNION fix (predicted MID 0.36-0.40 B + 0.44-0.48 C) + revert wiring + standing for Strategy direction.
