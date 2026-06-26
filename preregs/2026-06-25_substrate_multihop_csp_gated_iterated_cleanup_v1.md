# Pre-registration: substrate_multihop_csp_gated_iterated_cleanup_v1

**Date:** 2026-06-25
**Anchor:** substrate_multihop_csp_gated_iterated_cleanup_v1
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [7, 17, 23], **max_depth:** 10

## Why this cell exists

Research drill 2026-06-25 (`notes/research_drill_all_open_load_bearing_items_2026-06-25.md`)
identifies Barrier 1 (multi-hop beyond 2 hops) as REFUTED 3-for-3:
- consolidation v1/v2/v3 HARD_FAIL (lookup pollution)
- pointer_chain v1/v2 HARD_FAIL (cleanup error compounds geometrically)
- WM-scaffolded v1 HARD_FAIL (clean intermediate but no metacognitive gating)

CSP-gated iterated-cleanup is identified as the only NOVEL angle remaining.
Brain analog: PFC working memory + ACC conflict detection (CSP) + hippocampal
lookup + iterated cleanup with confidence threshold. Substrate has all three
chain-grade primitives:
- CSP from `csp_first_ship_v1` (Hopfield convergence confidence)
- iterated cleanup from `iterated_cleanup_cue_clamped_v1`
- WM from `working_memory_hrr_slots_PRODUCTION_v1` HARD_PASS K=32 sigma=1.0
... never before composed for multi-hop.

## Mechanism

For each k-hop query:
1. Initialize WM slot 0 with query subject E[s_0].
2. For hop i in 1..k:
   a. Read slot i-1 (clean intermediate from prior hop).
   b. Bind with relation R[p_i]; lookup via W; score against E codebook.
   c. Compute CSP confidence = (top1 - top2) cosine separation.
   d. If conf < CSP_THRESHOLD: ITERATE cleanup up to N_ITER=3 times. Each
      iteration: mix-toward-winner + small bipolar-quantized noise + re-project
      through W. This is the brain's theta-gamma oscillatory cleanup analog.
   e. If still below threshold: REFUSE (abort chain; counts as miss).
   f. Else: write cleaned codebook atom E[next_idx] to next WM slot.
3. Return final slot content.

## Scientific question

Does CSP-gated iterated-cleanup multi-hop close the substrate's depth-5 and
depth-10 retrieval ceiling that 3 prior attempts (consolidation, pointer-chain,
WM-scaffold) failed to break?

## Pre-registered bands

**HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL:**
- BASELINE in [0.62, 0.68] (sanity rail reproduces pointer_chain v2)
- ARM_CSP_GATED_ITER_2HOP >= 0.80
- ARM_CSP_GATED_ITER_5HOP >= 0.50 (vs pointer_v2: 0.122; WM-scaffold v1: 0.122)
- ARM_CSP_GATED_ITER_10HOP >= 0.20 (vs pointer_v2: 0.035)
- refuse_rate at depth 5 in (0.10, 0.90)
  (CSP gate ACTUALLY filtering; not too permissive, not refusing everything)
- cv <= 0.07 across seeds (all CSP arms)

**HARD_PASS_PARTIAL_BARRIER_1_LIFT:**
- ARM_CSP_GATED_ITER_5HOP >= 0.30
  (lift over both pointer_v2 AND WM-scaffold v1 which both sat at ~0.12)

**MIDDLE_BAND:**
- ARM_CSP_GATED_ITER_5HOP in [0.20, 0.30]

**HARD_FAIL_CSP_DOESNT_HELP:**
- ARM_CSP_GATED_ITER_5HOP < 0.20
  (4th multi-hop attempt also failed; Barrier 1 ceiling more permanent;
   substrate's ~0.12 depth-5 floor is intrinsic)

**RAIL_SANITY_BREACH:**
- BASELINE out of [0.62, 0.68] on majority of seeds
  (interpretation halted)

## Calibration rationale

- 0.80 / 0.50 / 0.20 targets at 2/5/10-hop mirror brain literature for
  transitive-inference accuracy (Eichenbaum 2018; Olsen/Buzsaki 2021 theta-
  gamma cleanup).
- CSP_THRESHOLD = 0.05 is a calibrated separation floor (top1 must be
  measurably above top2 in cosine space); too tight refuses everything; too
  loose passes noise. 0.05 is a 5% margin which is well above noise floor at
  N=8192.
- N_ITER = 3 matches brain's gamma-cycle count per theta-cycle (literature:
  ~3-4 gamma cycles per theta cycle).
- refuse_rate band (0.10, 0.90) ensures CSP gate is ACTUALLY discriminating.
  If refuse=0, gate is permissive (cleanup never triggered); if refuse=1, gate
  blocks everything. Either way the mechanism is not the source of lift.
- cv <= 0.07 because seed-stability is required for the mechanism claim.

## Q-discipline (BIAS-Q: suspect 1.000 results)

If any CSP arm scores >= 0.995, treat as suspect saturation; verify queries
are NOT in train W. The chain set + W are built from each other intentionally,
but the held-out chains' final-hop targets aren't being re-read from W
directly — the substrate must compose hop-by-hop. At depth 10 with V=200, 0.20
top1 is well above chance (1/200 = 0.005).

## Capacity-feasibility analysis

- W stores CSP_N_CHAINS * max_depth = 200 * 10 = 2000 (s,p,o) bindings in W
  at N=8192. Crosstalk floor sqrt(2000/8192) = 0.49.
- CSP confidence band relies on (top1 - top2) > 0.05 cosine; codebook
  crosstalk at V=200 N=8192 is sqrt(8192/200) = 6.4. Margin OK.
- N_ITER * depth_max = 3 * 10 = 30 max cleanup iterations per chain;
  ITER_NOISE_FRAC = 0.05 jitter per iteration; total noise budget ~ 1.5 per
  chain (manageable at N=8192).

Capacity feasible.

## Q-discipline cross-arm verification

Per Fix #28 (Skunkworks correction 2026-06-22): verdict_msg includes per-arm
per-depth top1 + refuse_rate + cv. Do NOT propagate "CSP solved it" from
verdict_msg framing; read metrics.json per-arm. If CSP_5HOP = 0.50 but
refuse=0.95, gate refused 95% of chains and "0.50 of the 5% that answered"
is NOT chain-grade — read refuse_rate.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; PROT-018 does not apply.

## Timeout estimate

Smoke ~ 60-120s estimated at N=2048, 1 seed, max_depth=5, 50 chains.
FULL: N=8192, 3 seeds, max_depth=10, 200 chains.
Scaling: matmul-bound + per-hop iterated cleanup (up to N_ITER=3 extra
matmuls per hop); scaling_exp = 2.0 (W is N x N).
formula: ceil(1.5 * 90 * (8192/2048)^2 * (3/1) * 1.3 iter_overhead)
       = ceil(1.5 * 90 * 16 * 3 * 1.3) = 8424s
budget timeout_s = 9000 (2.5 h).
timeout_s = 9000

## Provenance rail

ARM_BASELINE_HRR_2HOP must reproduce pointer_chain v2 BASELINE within +/- 0.05
of 0.65 (sanity rail [0.62, 0.68]). If baseline breaches band, verdict is
RAIL_SANITY_BREACH (cell not interpretable).

## Cross-cell apples-to-apples

Seeds [7, 17, 23] match pointer_chain v2 + WM-scaffold v1 for direct
apples-to-apples comparison. Per-arm reference values in verdict_msg:
- pointer_v2_5hop = 0.122 (the prior HARD_FAIL)
- WM_scaffold_5hop = 0.122 (the second prior HARD_FAIL)
- target: CSP_GATED_5HOP >= 0.30 for HARD_PASS_PARTIAL
       OR CSP_GATED_5HOP >= 0.50 for HARD_PASS_CHAIN_GRADE
