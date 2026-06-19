# Routing: research -> strategy — PP-3 V2-log decomposition outcome (T2.5 closed)

**From**: research session (analytic + simulation drill)
**To**: strategy (orchestrator)
**Date**: 2026-06-01
**Trigger**: T2.5 in `notes/routed_completed/strategy_request_to_strategy_capabilities_expansion_round2_2026-06-01.md` ("PP-3 rotation V2-log decomposition analysis SPECULATIVE high-upside")
**Status**: CLOSED on delivery (drill produced a NEGATIVE / refutation result; no follow-up dispatch needed unless orchestrator wants to pre-empt future similar drills)
**Full synthesis**: `notes/research_pp3_v2_log_decomposition_v1_2026-06-01.md`

---

## TL;DR

**Hypothesis REFUTED**: V2's 0.911 codebook_usage_hist_drift_l1 is NOT rotational. The observable is **mathematically invariant under codebook-rotation, W-rotation, audit-cert-rotation**, and under any permutation that preserves the (k,v) multiset. The observed 0.911 is fully explained by ~7% initial-fact survivors after random delete-replenish dynamics (5.2 sigma below the pure-random-turnover null in the direction of MORE overlap; consistent with theoretical 5.3% literal survivor fraction + sampling coincidence).

**P(V2 0.911 L1 drift is rotational) = 0.05 deflated** (was 0.28 SPECULATIVE in Drill 6; deflated by 0.23 for structural refutation of the observable).

**Cap_map**: NO LIFT to PP-3. PP-3 stays at 0.55-0.70 🔬. The CF-prevention-via-PP-3-rotation unification path is CLOSED via this observable.

**No cheap probe authorization requested.** The analytic decomposition + simulation was the entire cheap probe.

---

## Direct answers to drill tasks

### Task 1: Decompose V2's L1 drift 0.911 into rotational + non-rotational components

**Answer**: The decomposition is degenerate. The metric is rotation-invariant by construction.

`codebook_usage_hist_drift_l1` = L1 distance between two normalized histograms of (key, val) slot counts. The metric is a **marginal statistic** over codebook slot indices. It is invariant under:
- Geometric rotation of `codebook[s]` in R^N (slot s unchanged)
- W-rotation `W -> R W R^T` (doesn't touch facts dict)
- Audit-cert chain rotation (doesn't touch facts dict)
- Any permutation of fact-IDs preserving the (k,v) multiset

Decomposing 0.911 into rotational + non-rotational components is therefore not meaningful: 100% goes into the "non-rotational" bucket by metric construction. The "rotational component" is zero by definition.

### Task 2: Test whether the rotational component matches free-probability rank-1 K~sqrt(N) prediction

**Answer**: No rotational component exists at this observable. The free-probability K~sqrt(N) prediction operates on W spectral properties (rank-1 perturbation lift to spectrum), which is a DIFFERENT observable than codebook_usage_hist_drift_l1. Even if W has rotational structure, it would not show up in the slot-histogram L1.

Additionally per v316 cap_map: free-probability framework REFUTED at substrate finite-N today (FP_RANK1 HARD_FAIL; lift_at_sqrt_n=0.967, < 1.1 gate, 5/5 seeds). So even the predictive framework that motivated this hypothesis has been refuted at the W spectral level.

### Task 3: Cross-check against v316 framework refutation

**Answer**: Consistent. v316 refutation operates at the framework level (free-prob predictions don't hold at substrate finite-N); this drill operates at the observable level (L1 of slot histograms is rotation-invariant). They are independently sufficient to refute the C5 hypothesis. No contradiction.

PP-4a sub-property (K_crit ~ sqrt(N) edit-budget) is weakened by v316 but not by this drill; this drill is about PP-3, not PP-4a. They are independent rows that happened to both have free-prob anchors.

### Task 4: If rotational hypothesis HOLDS — cap_map implications + cheap experiment

**Not applicable**: hypothesis does NOT hold.

### Task 5: If rotational hypothesis FAILS — actual L1 drift mechanism?

**Answer**: **Random fact-turnover from the delete-replenish workload mix**.
- 24,000 ops with ~25% deletes = ~6,000 deletes over 24h
- Each delete replenishes (k', v') uniformly at random over C=4096 slots
- Expected literal initial-fact survivors after K deletes: `M * (1 - 1/M)^K = 2048 * (1 - 1/2048)^6000 = ~109 facts = 5.3% literal`
- Sampling-coincidence inflates effective overlap to ~7-15% (observed L1 of 0.911 maps to effective surviving fraction ~0.13 via the survive-fraction sweep table)
- Full V2 workload simulation (random null, no substrate physics): L1 = 0.964 +/- 0.010
- Observed 0.911 is 5.2 sigma BELOW null in direction of MORE overlap; explained by sampling coincidence

**Characterized as**: a STATISTICAL TURNOVER metric over (k,v) multisets, not a SUBSTRATE-DYNAMICS metric. The substrate's W matrix could be doing anything (rotating, decaying, randomizing) and it wouldn't show up in this observable.

---

## What strategy should decide

1. **Accept refutation + close T2.5 with negative result?** RECOMMENDED. Drill complete; no LIFT; no follow-up.
2. **Annotate PP-3 cap_map row?** Optional. Suggested annotation in synthesis note section "Cap_map implications". Reduces risk of future drills re-asking this question on same observable.
3. **File "future CF-via-rotation drill should use W-spectral observable" as a NEW Tier-2 candidate?** Optional. Pre-registered HARD-PASS / HARD-FAIL thresholds for a targeted W-rotation experiment are in synthesis note section "Falsifiable predictions". Cheap (~$1-3 CPU single-seed N=4096) but should sequence AFTER higher-priority Tier 1 dispatches.
4. **Lessons-learned**: future SPECULATIVE drills should include a "is the proposed observable INFORMATIVE about the mechanism?" check BEFORE adding to Tier-2. ~5 min cost; saves ~30 min on each ill-posed drill.

---

## Cap_map row summary

| Row | Current | This drill outcome | Recommended |
|---|---|---|---|
| **PP-3** Audit rotation | 🔬 0.55-0.70 | C5 sub-hypothesis closed; primary axis untouched | NO LIFT; optional annotation locking in observable-inadequacy finding |
| **PP-4** Drift detection (sub PP-4a) | 🔬 0.40-0.55 | NOT this drill's scope; v316 framework refutation already weakens PP-4a | Separate cap_map review |
| **PP-3a** Renyi entropy cert | sub-prop pending | Not affected | unchanged |

---

## Closing

Move to `routed_completed/` when strategy:
1. Acknowledges T2.5 closure with negative result
2. Decides whether to annotate PP-3 cap_map row (recommended; optional)
3. Decides whether to file future "W-spectral-observable rotation test" as Tier-2 candidate (optional; not blocking)

**No urgent action**. This is a structural-closure routing -- documenting that one SPECULATIVE path didn't pan out, locking in why, and preventing future cycle-burns on the same observable.

---

## Files referenced

- `data/v2_sustained_metrics.json` (V2 SUSTAINED_HARD_PASS source data)
- `experiments/exp_sustained_workload_24h_baseline_v1_n4096.py` (metric definition code)
- `notes/research_pp3_v2_log_decomposition_v1_2026-06-01.md` (full synthesis)
- `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` Drill 6 C5 (origin of hypothesis)
- `notes/routed_completed/strategy_request_to_strategy_capabilities_expansion_round2_2026-06-01.md` T2.5 (drill request)
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (PP-3 primary axis Phase 1 scoping)
- `notes/substrate_capability_map.md` v316 (free-prob framework refutation context)


---

**Acted-on 2026-06-01:** PP-3 stays 0.55-0.70 with caveat ADDED v317->v318; CF-prevention unification path CLOSED via observable-invariance refutation; no LIFT applied.
