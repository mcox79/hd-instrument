# exp_dev PRE-DISPATCH HOLD: n6_optimal_V_C_sweep_v1 -- routes back to research

**Filed-by:** exp_dev (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** Orchestrator request to author + dispatch `n6_optimal_V_C_sweep_v1` to overnight_queue (GPU) per research drill 1 handoff anchor 2.
**Verdict:** HOLD (Fix #26 pre-dispatch verify-the-referent gate triggered HOLD recommendation).
**Routing:** back to Research (sibling drill) before dispatch.

## What the Fix #26 gate found

`python tools/predispatch_check.py n6_optimal_V_C_sweep_v1` -> PROCEED (no prior n6 landings)
`python tools/predispatch_check.py vc_4096` -> HOLD
`python tools/predispatch_check.py frontier` -> HOLD

Two prior HARD_FAILs on the SAME MECHANISM in the last 4 days:

| Landing | Date | wall_s | sub_bpc at V_C=4096 | verdict |
|---|---|---|---|---|
| `exp_n5_vc_4096_frontier_v1` | 2026-06-22 | 5530s | 5.68-5.80 | HARD_FAIL anchor mismatch |
| `exp_n5_vc_4096_frontier_v2_anchor_fix` | 2026-06-23 | 809s | (aborted) | HARD_FAIL_HARNESS_DRIFT |

Combined ~6300 wall-seconds (~1.75 hr) of compute already burned. Recommendation = HOLD.

## Empirical failure modes (from metrics.json)

**v1 measured V_C=4096 at N=16384 across 3 seeds (per_unit detail in `data/exp_n5_vc_4096_frontier_v1/metrics.json`):**

- substrate_bpc = 5.77 / 5.80 / 5.68 (seeds 7/17/23) -- WORSE than V_C=1024 anchor 5.08 by ~0.65 bits
- ceiling_bpc = 2.69 / 2.78 / 2.62 -- ROSE from V_C=1024's 2.05 (research-drill PREDICTED ceiling would DROP to ~1.5)
- codebook_utilization = 0.67 / 0.69 / 0.72 -- DEAD CONCEPT collapse (V_C=4096 has ~30% of bins unused)
- substrate_concept_top1 = 0.30 / 0.32 / 0.33 -- recall dropped from V_C=1024's 0.49 (transition noise dominates)

**v2 anchor pre-gate even FAILED on V_C=1024 reproduction:**

- V_C=1024 / N=16384 anchor pre-gate band = [4.939, 4.979] (N2 4.959 +/- 0.02)
- Measured: 4.991 / 5.011 / 5.063 -- ALL three seeds drifted ABOVE band
- v2 aborted before running V_C=4096 arms -- harness itself is not bit-reproducing N2 anymore

**Diagnosis:** the substrate's K-means + count-prop + Jelinek-Mercer pipeline cannot push V_C beyond ~1024 without (a) ceiling rising faster than transition-noise drops (Skunkworks tradeoff sign-inverted in real-text regime), AND (b) dead-concept collapse on text8's heavy-tail token distribution. V_C=8192 is predicted WORSE not better on this mechanism.

## Why the research drill missed this

The drill 1 research note Section 2 / Section 7 says "V_C=4096 untested. needs cell." -- **substrate-mine missed `n5_vc_4096_frontier_v1` 2026-06-22 and `n5_vc_4096_frontier_v2_anchor_fix` 2026-06-23.** Both cells landed in the same week as the drill. Honest "substrate-mine FULL Store before extrapolating" discipline would have caught this; the drill's `cap_map` reading is stale.

This is the cert-owner-correctly-overrides-Director / by-construction-saturation pattern in reverse: **the research drill's premise that V_C-sweep is an untested lever is empirically falsified.** Per Fix #28 default-classify-down + under-claim-by-default discipline, exp_dev cannot ship a third HARD_FAIL on this mechanism without an explicit structural change to the harness.

## What WOULD address the failure modes (research drill recommendations)

The drill-1 research note Section 6 says "Going to Shannon-floor ... DOES require W2 + cross-sentence context." The empirical V_C=4096 failure is consistent with **single-layer Kmeans-VQ saturating at V_C ~ 1024** for text8's heavy-tail distribution. To unlock V_C=4096+, the structural lever is NOT a simple sweep but one of:

1. **Codebook training algorithm change.** K-means with k_active=98 sparse-bipolar projection can't allocate 4096 distinct concepts on text8's frequency distribution (top-100 tokens dominate >60% of mass). Alternatives: balanced-VQ (Roy et al), product-VQ (Jegou), hierarchical-VQ (Vasuki), or VQ-VAE-style commitment loss with a forced uniformity prior. Each is a 2-3 day cell.
2. **Pre-frequency-binning.** Bin tokens by frequency band first (top-1k / 1k-10k / 10k+); allocate V_C=1024 codebook per band; V_C_total=3072. Avoids head-tail competition. Quick (~1 day).
3. **Drop V_C=4096 lever; pivot to context-depth (n5 trigram) which research-drill explicitly recommends as PRIMARY anchor.** n5_trigram_concept_lm_v1 is Tier-A and untested; routes around the V_C-ceiling problem entirely.

The handoff lists n5_trigram_concept_lm_v1 as ANCHOR 1 (top priority) and routes to local_cpu_queue (laptop-feasible). Per substrate-mine + Fix #26, **the correct next dispatch is ANCHOR 1 not ANCHOR 2.**

## Recommended routing

1. **Skip Anchor 2 (n6_optimal_V_C_sweep_v1) as written** -- proposed mechanism is empirically falsified at V_C >= 4096; V_C=8192 will be strictly worse.
2. **Dispatch Anchor 1 (n5_trigram_concept_lm_v1) instead** as orthogonal lever (HRR-bound trigram context). This is what the drill calls "the structural fix" and lists Tier-A.
3. **Route back to Research** for a refreshed drill that incorporates the two V_C=4096 HARD_FAILs and decides whether to retire the V_C-sweep lever or design a structurally different VQ training algorithm (option 1 or 2 above).

## What I will NOT do

- Will NOT push a third HARD_FAIL of the K-means + count-prop pipeline at V_C=4096 or V_C=8192. No structural delta in the proposed cell vs the two failed cells -- only the sweep granularity changes.
- Will NOT route to overnight_queue without GPU-utilization fix designed (Fix #24); the V_C=8192 arm is matmul-heavy but the K-means clustering step is the wall-time dominator (km_wall_s=629-923s per arm on CPU; that step is not trivially GPU-portable without rewriting the pipeline). Routing-to-GPU without re-architecting wastes the queue slot.
- Will NOT bypass the Fix #26 HOLD recommendation without an explicit structural delta + research re-scour ack.

## State

- No dispatch fired this cycle.
- No path-scoped commits.
- This routing note is uncommitted (annotation only; not needed for remote dispatch).
- Pause flag: clear (verified `data/orchestrator_paused.flag` does not exist).
- Returning HOLD + routing-to-research as the verdict.

-- exp_dev (Opus 4.7-1M)
