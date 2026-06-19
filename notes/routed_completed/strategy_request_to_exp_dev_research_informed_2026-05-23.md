# Strategy → Experiment Dev: Research-informed priorities — P(q) distributional + coset-count sweep

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-23 ~09:50 EDT
**Topic**: Research delivered 2 substantive analyses; substrate-physics specific tests warranted
**cap_map state**: v149 (commit `855a837`)
**Trigger**: User signal "exp dev needs more strategy"; Research delivered order_param_2x_drill (09:40) + strategy_open_questions (09:41)

## Context

Research delivered TWO substantive analyses minutes ago:

1. **research_order_param_2x_drill_2026-05-23.md** (09:40): substrate has
   **non-self-averaging distributional order parameter P(q)** — 3 scalar
   candidates failed because they SAMPLE not MEASURE; P(q) is functional.
   P=0.45.

2. **research_strategy_open_questions_2026-05-23.md** (09:41): ~25% fraction
   = **Kerdock 4-coset codebook geometry** — RM(1,16) is 1 of 4 cosets =
   25% by construction. P=0.40. Substrate-novel if confirmed.

Both with cheap decisive tests. Filing focused Exp Dev priorities INFORMED
BY Research (supersedes cycle 169 P4 multi-component test).

## PRIORITY A — 50-seed P(q) distributional test (cheapest decisive)

**`wave14_pq_distributional_op_v1`** (~5-30 min):

Research's cheap decisive test for distributional order parameter framework:

```python
def test_distributional_OP(K_test=1000, N=65536, n_seeds=50):
    q_overlap_samples = []
    for seed in range(n_seeds):
        substrate = setup_substrate(N, K_test, seed=seed)
        q = run_q_overlap_diagnostic(substrate)
        q_overlap_samples.append(q)
    return mean, std, frac_above_threshold, skewness
```

**Verdict criteria** (Research-specified):
- **PQ_DIST_OP_PASS**: mean(P(q)) ≥ 0.85 AND std(P(q)) < 0.05 → substrate
  HAS distributional OP; cycle 168 ORDER_PARAM_NONE was tool-not-substrate issue
- **PQ_DIST_OP_FAIL**: mean(P(q)) < 0.85 → substrate genuinely lacks OP
- **PQ_DIST_OP_BIMODAL**: P(q) bimodal → hidden symmetry breaking (2 phases conditioned on seed)

**No new code needed** — reuse cycle 168 instrumentation, 50 seeds instead of single.

Substrate-physics implication if PASS: substrate has substrate-physics
QUANTITATIVE order parameter (distributional P(q)), recovering Gap 2
characterization that was refuted as scalar.

## PRIORITY B — Coset-count sweep (~25% fraction = RM(1,16) hypothesis)

**`wave14_coset_count_sweep_v1`** (~30-60 GPU-min):

Research's cheap decisive test for ~25% = Kerdock 4-coset geometry framework:

- Build substrate with 3-coset codebook (3 × 131,072 = 393,216 codewords)
- Build substrate with 5-coset codebook (5 × 131,072 = 655,360 codewords)
- Build substrate with linear-only RM(1,16) codebook (1 coset)
- Measure idempotence fraction at depth L=50 for each

**Verdict criteria** (Research-specified):
- **COSET_25_GEOMETRIC**: 3-coset gives ~33% idempotence + 5-coset gives ~20% +
  linear-only RM(1,16) gives substantially different fraction
- **COSET_25_DYNAMICAL**: idempotence fraction stays ~25% across coset counts
  (NOT geometric; dynamical phenomenon)
- **COSET_25_MIXED**: partial dependence

Substrate-physics implication: if PASS, the ~25% partial idempotence is
GEOMETRIC (Kerdock codebook structure), substrate-novel finding. If FAIL,
substrate has dynamical mechanism for ~25% fraction (open).

## PRIORITY C — Endpoint projection onto RM(1,16) subcode (~25% support test)

**`wave14_endpoint_RM1m_projection_v1`** (~15 GPU-min):

Research's prediction: ~25% of terminal endpoints fall inside RM(1,16) subcode
(Hamming radius d/2 = 2^15).

- For 1000 codewords, run forward chain to L=50; get endpoint
- Project each endpoint onto RM(1,16) subcode; compute Hamming distance
- Count fraction within d/2 = 2^15

**Verdict criteria**:
- **RM1M_25_PASS**: ~25% endpoints within d/2 → RM(1,16) hypothesis confirmed
- **RM1M_FAIL**: ≠ ~25% (e.g., <15% or >35%) → not RM(1,16)-driven

## PRIORITY D — P(q) discrete spike structure (~28-element connection)

**`wave14_pq_discrete_spikes_v1`** (~20 GPU-min):

Research predicts P(q) supported on ~28 discrete spikes (connection to cycle 137
ENDPOINT_COLLAPSED 28/100 distinct endpoints).

- Run 1000-seed q_overlap measurements
- Compute P(q) histogram
- Check for discrete-spike structure (28 peaks vs continuous distribution)

**Verdict criteria**:
- **PQ_DISCRETE_28**: ~28 spikes detected → connection to endpoint partition
- **PQ_CONTINUOUS**: smooth distribution → no discrete structure

## Pending (cycle 169 v149 priorities `3845507` deferred to substrate-novel-PRIORITY-set complete)

- Bet Z.5 Phase 1 (still pending; longest)
- Observability V2 Kovacs + avalanche
- N=1M stress test
- Bet A continual-edit 5-seed FULL
- K1000_eigenspectrum + K_resonance_wide_sweep pending pickup

## Priority ordering recommendation

1. **PRIORITY A** P(q) distributional (~5-30 min cheapest)
2. **PRIORITY C** Endpoint RM(1,16) projection (~15 min)
3. **PRIORITY D** P(q) discrete spikes (~20 min)
4. **PRIORITY B** Coset-count sweep (~30-60 min)
5. Observability V2 remaining (~6 min from cycle 169)
6. N=1M stress (cycle 169 P3)
7. Bet A 5-seed FULL (cycle 169 P5)
8. Bet Z.5 Phase 1 (cycle 169 P1; longest)

Total ~3-4 GPU-hours for substrate-physics characterization battery.

## Substrate-physics implications

**If PRIORITY A + C + D all PASS**: substrate-physics characterization gains
substantial theoretical anchor:
- Distributional P(q) order parameter (recovers Gap 2)
- ~25% Kerdock 4-coset geometric origin (RM(1,16) subcode)
- 28-element endpoint partition = P(q) discrete spike structure
- Substrate-physics v149 → v150 QUANTITATIVE substrate-physics with
  distributional OP + geometric origin

## Per [[feedback-no-papers-product-only]]

All Research-informed tests substrate-product oriented (substrate-physics
characterization with theoretical anchor strengthens substrate-product positioning).

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 60-120 min for Research-informed battery.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
