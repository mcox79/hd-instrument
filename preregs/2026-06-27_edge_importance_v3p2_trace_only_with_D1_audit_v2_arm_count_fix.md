# Prereg: edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix

Date: 2026-06-27
Anchor: edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix
Cell: experiments/exp_edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; 2026-06-26)
  - experiments/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3
    (setup function only; coreness IGNORED per drill)

## Motivation

v3.2 v1 (exp_edge_importance_v3p2_trace_only_with_D1_audit_v1) HARD_FAILed
META_RULE_H cardinality_ok: expected 2 arm entries got 6. Forensics:

  data/exp_edge_importance_v3p2_trace_only_with_D1_audit_v1/metrics.json
  shows per_seed arms = [BASELINE_RANDOM_IMPORTANCE, TRACE_ONLY,
  ULTRAMETRIC_ONLY, TRACE_X_CORENESS x 3] (6 arms total).

But the v1 cell source code declares `ARM_NAMES = ["ARM_BASELINE_RANDOM_
IMPORTANCE", "ARM_TRACE_ONLY"]` and `run_seed` only iterates those 2 arms.

Root cause: the output dir
`data/exp_edge_importance_v3p2_trace_only_with_D1_audit_v1/` held STALE
PARTIALS from an earlier v3-lineage run (6-arm lambda sweep). The v3.2
v1 cell's resumable_seeds() loaded those partials because run_config
(N, M, alpha, run_mode) matched -- but the body's arm count didn't,
which META_RULE_H caught downstream.

## Fix mechanism (v2)

Two-part fix:

1. **NEW anchor name** = `edge_importance_v3p2_trace_only_with_D1_audit
   _v2_arm_count_fix` -> new output dir
   `data/exp_edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count
   _fix/` -> no collision with v1's stale partials.

2. **Defensive partial-cleanup at startup**: before resumable_seeds()
   runs, the cell scans existing partials in the v2 output dir; any
   partial whose body.arms has != 2 entries is deleted. (At first run
   this is a no-op; if v2 is re-run after a future bug, the cleanup
   catches recurrence.)

3. **Per drill recommendation**: ULTRAMETRIC composition dropped
   PERMANENTLY (no LAMBDA_LIST in module scope, no ULTRA_ONLY arm, no
   TRACE_X_CORENESS arm). v2 enforces exactly 2 arms via
   `_selftest_arm_count_exactly_2()` (META_RULE_K).

4. **Module-level selftest** `_selftest_anchor_name_differs_from_v1()`
   prevents future regressions to v1's anchor name.

## Mechanism (TRACE-only; identical to v1 in concept)

```
importance_score[atom] = retrieval_trace_score[atom]

retrieval_trace_score[atom] = per-atom cleanup-argmax hit counter
                              during composite-query operation
                              (brain STC analog)
```

## Arms (EXACTLY 2; enforced by selftest)

- ARM_BASELINE_RANDOM_IMPORTANCE -- random importance (control rail)
- ARM_TRACE_ONLY                 -- importance = retrieval_trace_score
                                    (the mechanism; primary verdict)

## Pre-reg bands (load-bearing; verbatim v1; from drill)

### HARD_PASS (all hold across 3 seeds)
- TRACE D1_partition_AUC mean >= 0.65 across 3 seeds
- TRACE D1_AUC cv <= 0.05 across 3 seeds (stability)
- TRACE D1_AUC - RAND D1_AUC >= 0.05 (lift over random baseline)
- mechanism fires (n_downscaled > 0 in TRACE arm)
- cor(importance, |W|) < 0.30 (USER fairness gate)

### MIDDLE_BAND
- TRACE D1_AUC >= 0.55 AND cv <= 0.10 AND mechanism fired

### HARD_FAIL (any one trips)
- Both arms within 0.05 of each other on D1_AUC (saturation)
- cor(importance, |W|) >= 0.30 (fairness regression)
- n_downscaled == 0 in TRACE arm (mechanism inert)
- H_n_edges < 50 (workload did not populate H)
- TRACE D1_AUC < 0.55 (mechanism does NOT rank above unretrieved)
- any caught exception (META_RULE_J)
- META_RULE_H cardinality_ok breach (per-seed arm count != 2)
- STALE_PARTIAL detected at v2 startup (v1-bug-recurrence sentinel)

## Regime (inherits v3.2 v1)

- N = 512, M_OLD = 600, M_RECENT = 400, alpha = 1.953
- J_composite = 3000, arity = 3, USE_FRAC = 0.40, N_USE = 240
- DOWNSCALE_SCALE = 0.20, N_PRUNE_FRAC = 0.30
- SEEDS = [7, 17, 23], N_QUERIES = 200 per subset per arm

## Discriminator-must-survive-scale

Smoke runs at FULL-N (N=512, M_OLD=600, M_RECENT=400); only
J_composite -> 1500 (vs 3000 full), SEEDS=[7], N_QUERIES=100.

Smoke must produce trace_total > 0 AND H_n_edges >= 50 AND mean D1_AUC
strictly above 0.5 baseline (META_RULE_K).

## Substrate-only-decode gate

n_llm_calls = 0 by structural-guarantee. Decode is sign(W @ key) cosine
cleanup against value matrix.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`.

## New disciplines applied

- META_RULE_H cardinality_ok: per-seed expected arm count = EXACTLY 2.
- META_RULE_J no-silent-except: setup + each arm wrapped; exception
  RECORDED + HARD_FAIL.
- META_RULE_K smoke fires discriminator: smoke must produce
  trace_total > 0 AND H_n_edges >= 50 AND mean D1_AUC > 0.5.
- META_RULE_L band-floor strictly-above-floor.
- v2-specific defensive partial-cleanup: scan + delete partials with
  != 2 arms before resumable_seeds().
- PROT-020: numpy-only -> remote_cpu_queue.

## Honest scope

This cell ships the SAME mechanism as v1 (TRACE-only); the only changes
are operational (anchor name, partial cleanup, selftest discipline) to
prevent the v1 stale-partial bug recurrence. If v3-lineage 6-arm cell
re-runs later under THIS v2 anchor name (shouldn't, but defensive),
the partial-cleanup deletes stale partials before they corrupt v2's
metrics.

## Runtime estimate

Smoke (1 seed, J=1500): ~60s setup + 2 arms ~ 10s -> ~70s wall.
Full (3 seeds, J=3000): 3 * (~120s setup + 2 arms ~ 20s) = ~420s.

timeout_s = ceil(1.5 * 420) = 630s -> use 900s (15min) for safety.

## ASCII-only; no unicode; no emojis; no em-dashes.
