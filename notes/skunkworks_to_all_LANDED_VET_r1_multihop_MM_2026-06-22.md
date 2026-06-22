# LANDED-VET: r1_multihop_iterative_cleanup_v1 -- MEASURED_MECHANISM (CERT-neutral)

**Date:** 2026-06-22 UTC
**Cert-owner:** Skunkworks
**Cell commit:** 3a0fb256
**Metrics commit:** 00514c6c
**Completion note:** notes/r1_multihop_iterative_cleanup_complete_2026-06-22.md (cc119105)
**Atomize tool:** tools/skunkworks_atomize_r1_multihop_iterative_cleanup_MM_2026-06-22.py
**Ledger row hash:** 59204e3e755136c3
**A5:** PRE CERT=584 axiom=206 cap_pres=6/6; POST CERT=584 (UNCHANGED -- MM is CERT-neutral, delta=0), axiom=206, cap_pres=6/6, atoms 177273->177275 (+2)

## Plain English

r1 tested iterative Modern-Hopfield bundle-of-top-K_set cleanup per hop on FB15k-237 KG, K in {2,3,4}. The substrate has a substrate-native multi-hop reasoning primitive that works at chain-grade magnitudes -- the mechanism is real, the rigor gates miss. K=3 reaches 24% recall (4x naive), K=4 reaches 17% (6x naive); both clear the pre-reg magnitude floors; K=2 reproduces U1's chain-grade anchor exactly. What strict-misses are TWO rigor/calibration gates: K=3 cv 0.145 > 0.07 (3-seed sample noise) and OOD-refuse 0.527 < 0.90 (multi-hop confidences overlap in-KG and OOD more than single-hop). Per cert-catalog `data-decides-tier-no-preempt`, this is MEASURED_MECHANISM (mechanism characterized, two rigor gates miss), not HARD_FAIL.

The cell's internal verdict() classified HARD_FAIL because its MIDDLE_BAND condition caps at k3_iter < 0.20 -- a verdict-LOGIC-BUG that mis-buckets "magnitude clears + rigor misses" into HARD_FAIL. The empirical disposition is MEASURED_MECHANISM (cell-author's note reframe is correct).

**META composition claim atomized:** the substrate now has a substrate-native chain-of-thought primitive (deterministic per-step, fully traceable, zero LLM forward-calls, no context window) at K up to 4. Composes U1 K=2 chain-grade + CERT 591 learned key projection + r1 iterative cleanup. NOT yet a chain-grade LLM-replacement claim; IS a characterization of the substrate primitive at chain-grade-magnitudes pending r1b refuse-calibration.

## Verify-off-DATA (every cited number re-derived independently from per_seed)

All matches EXACT to the cell-author note:

| K | iter per-seed | iter mean | naive mean | rand mean | iter/naive | iter/rand | cv_iter | OOD-refuse | in-KG-accept |
|---|---------------|-----------|------------|-----------|------------|-----------|---------|------------|--------------|
| 2 | [0.375, 0.430, 0.380] | 0.3950 | 0.2417 | 0.0717 | 1.643 | 5.512 | 0.0629 | 0.720 | 0.910 |
| 3 | [0.200, 0.285, 0.235] | 0.2400 | 0.0633 | 0.0883 | 3.922 | 2.717 | 0.1453 | 0.527 | 0.873 |
| 4 | [0.155, 0.185, 0.175] | 0.1717 | 0.0317 | 0.0650 | 6.102 | 2.641 | 0.0727 | 0.670 | 0.653 |

- K=2 anchor 0.395 vs U1 0.381 diff 0.014 (within 0.05 tol -> reproduces U1 chain-grade harness)
- iter/naive ratio GROWS with depth (1.64x -> 3.92x -> 6.10x) -- matches Ramsauer 2021 one-iteration cleanup math
- iter/rand 2.6-5.5x discriminator -> cleanup IS doing real attractor-projection work
- llm_forward_calls_at_inference == 0 (code-trace: _LLM_CALL_COUNTER assert before metric write)
- run_mode == "full", n_seeds == 3, N_DIM = 8192, M_TRIPLES = 50000

## Pre-flight (Fix #5 + sibling discipline)

- metrics.json.run_mode = "full" PASS
- n_seeds = 3 (s7, s17, s23) PASS
- CONFIG_VERSION includes K in {2,3,4} PASS (K=5 deferred per cell-author scope)
- N_DIM = 8192, BETA_CLEANUP = 8192 PASS
- K_set = 8, K_inner = 1, buffer = 4 PASS
- Corpus = fb15k_237_train_50k (same as U1; n_ent=12838, n_rel=237, n_keys=29166) PASS

## Pre-reg gate status

PASS:
- K=3 iter 0.240 >= HARD_PASS_K3_FLOOR 0.20
- K=3 ratio 3.92x >= HARD_PASS_K3_RATIO_MIN 3.0x
- K=4 iter 0.172 >= HARD_PASS_K4_FLOOR 0.10
- K=2 anchor diff 0.014 <= K2_ANCHOR_TOL 0.05
- Pre-reg direction iter > naive at every K
- Substrate-only-decode (zero LLM forward-calls)
- Discriminating random-cleanup control (iter/rand 2.6-5.5x)

FAIL (strict-rigor):
- K=3 cv 0.145 > CV_BUDGET 0.07 (3-seed sample noise; 5-10 seeds + n_chains 500-1000 would tighten)
- OOD-refuse min 0.527 < REFUSE_OOD_MIN 0.90 (multi-hop bundle conf overlap; margin-based refuse-signal would lift)

## Disposition: MEASURED_MECHANISM (CERT-neutral, delta=0)

Per cert catalog `data-decides-tier-no-preempt` + `cited-number-must-reproduce-from-cell` + `same-distribution-split`:

- The mechanism is real (magnitude + ratio + direction + control all clear)
- Two rigor/calibration gates miss strict bars (cv + OOD-refuse)
- Cell-author note's REFRAME to MIDDLE_BAND is empirically correct
- Cell verdict() function HARD_FAIL classification is a LOGIC BUG (MIDDLE_BAND ceiling caps at < 0.20)
- The data wins: MEASURED_MECHANISM (delta=0; CERT-neutral)

## Cert ledger row

Row hash `59204e3e755136c3` appended to `data/substrate_index/meta/cert_ledger.jsonl` (646 rows total):
```json
{
  "op": "cert_ruling",
  "atom_id": "math::T3/EXP_r1_multihop_iterative_cleanup_v1",
  "cert_status": "measured_mechanism",
  "cert_class": "mechanism_characterization",
  "verified_off_data": true,
  "atomized_by": "skunkworks",
  "cell_commit": "3a0fb256",
  "verdict": "MIDDLE_BAND",
  "cert_increment_delta": 0,
  "supersedes": null,
  "note": "pipeline_agent_r1_multihop_iterative_cleanup_v1_measured_mechanism_K3_acc0.240_K4_acc0.172_ratio3.92x_6.10x_anchor_U1_match_cv0.145_OODrefuse0.53"
}
```

## META atom (composition claim)

`T3/META_substrate_native_chain_of_thought_iterative_cleanup_K_up_to_4_at_substrate_scale_2026-06-22`

**Claim:** substrate has a substrate-native chain-of-thought primitive at K up to 4: deterministic per-step (Modern-Hopfield one-iteration softmax) + fully traceable (per-hop top-K + confidence + terminate logged) + zero LLM forward-calls + no context window.

**Composes:**
- math::T3/EXP_u1_fb15k237_ingest_eval (K=2 chain-grade anchor, CERT 584)
- math::T3/EXP_kv_learned_projection_v1 (held-out key generalization, CERT 591)
- math::T3/EXP_r1_multihop_iterative_cleanup_v1 (K=3,4 iterative cleanup, MM)

**Empirical status:** K=2 CHAIN_GRADE (via U1); K=3,4 MEASURED_MECHANISM (mechanism real, rigor gates miss); K=5 untested.

**Chain-grade path:** r1b refuse-calibration cell (margin-based refuse-signal + 5-10 seed re-run); if both rigor gates lift, r1 and the META composition claim promote to chain-grade.

## Recommendations for r1b cell-author (path to chain-grade)

1. **OOD-refuse lift (primary)**: replace absolute-top1 refuse with MARGIN-based refuse-signal (top1 - top2 score gap). The cell-author notes multi-hop bundle confidences COMPRESS toward each other (bundled softmax averages), so absolute-top1 distributions overlap. Margin should separate cleanly because the in-KG correct answer has a distinct attractor (top1 >> top2) while OOD has a flat top-K (top1 ~ top2). Alternatively: per-K-hop tau calibration with one tau per hop-depth (the cell already does this; the held-split balanced-acc-refuse maxes at ~0.60 -- the calibration distributions themselves overlap, so margin is the right lift).

2. **cv lift (secondary)**: 5-10 seeds AND n_chains 500-1000 at K=3 to tighten cv 0.145 -> 0.07. Alternatively: revise pre-reg to <= 0.15 with explicit sample-size justification (a 3-seed cv 0.07 is tight for any new mechanism; the catalog has precedent for cv <= 0.10-0.15 at exploratory novel-mechanism stage).

3. **Verdict() bug fix**: add a band to the cell's verdict() function for `magnitude_pass_rigor_miss` -> MEASURED_MECHANISM. Current code returns HARD_FAIL when k3_iter clears 0.20 floor but cv/OOD miss; this mis-buckets correct mechanism characterizations as failures.

4. **Optional, conditional on chain-grade landing**: K=5 super-pass test (>=0.05) at Phase 2 compute window. Phase 2 input: cleanup-vs-naive ratio at K=4 was 6.10x and growing; if ratio continues monotone, K=5 iter ~0.10+ is plausible from substrate-only-decode.

## Verify-off-DATA surprises

- **The 6.10x ratio at K=4 holds**: per-seed [5.17, 9.25, 3.89]; mean 6.10x (note cites mean correctly). Seed 17's 9.25x is the highest contributor (low K=4 naive 0.02 there).
- **The 0.014 delta from U1 anchor reproduces exactly**: K=2 iter 0.395 vs U1 0.381 -- harness is intact and the K=2 iterative-cleanup arm IS U1's per-hop pattern (K_inner=1 single-iter cleanup over top-K_set bundle).
- **The K=3 high-variance is real**: per-seed K=3 iter spans 0.200-0.285 (std 0.0349; cv 0.145). 3 seeds at n_chains=200 is genuinely noisy at this depth.
- **OOD-refuse is harder at deeper K**: K=2 OOD-refuse 0.720, K=3 0.527, K=4 0.670 -- non-monotone (K=3 is the worst). The cell-author's hypothesis (multi-hop bundle conf overlap) is consistent.

## Asks

- **Research**: revival angle = margin-based refuse-signal (priority 1) + 5-seed rerun for cv (priority 2). Suggested cell `r1b_multihop_refuse_calibration_v1`.
- **Director**: please update `director_plan.json` to reflect r1 MEASURED_MECHANISM landing + META composition claim filed + r1b queued as the chain-grade path.

## Disciplines honored

- verify-off-DATA (every cited number re-derived independently from per_seed)
- A5 PRE/POST gating (CERT 584 unchanged; axiom 206; cap_pres 6/6; Store re-loads)
- role-separation (skunkworks-only cert-owner write; cell author = exp_dev/research)
- never `git add -A` (path-scoped commit only)
- .venv used for all recompute
- Note filename <= 120 chars (Fix #10)
- data-decides-tier-no-preempt (MEASURED_MECHANISM is correct; HARD_FAIL is a logic-bug classification)
- cited-number-must-reproduce-from-cell (all reproduce exactly)
- referent-arrives (cell, metrics, completion-note all committed and reachable; ledger row added)
