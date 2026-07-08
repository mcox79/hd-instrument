# Pre-reg: encoder_phase_traversal_graded_sparse_rescue_v1

Date: 2026-07-08
Cell: `experiments/exp_encoder_phase_traversal_graded_sparse_rescue_v1.py`
Anchor: `encoder_phase_traversal_graded_sparse_rescue_v1`
Trigger: 5x-drill of the v1 phase-traversal genuine-negative
(`encoder_phase_traversal_spread_condense_v1`, smoke HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB,
structural_gain -0.348). Skunkworks confirmed the wall is SPECIFIC to the HARD sign+top-k code,
NOT fundamental: v1's own phase_traversal_DENSE arm condensed to SC 0.993 (near-oracle), so the
condenser is valid; the entire loss is the discontinuity of the sign+top-k quantization (a noisy
query, sign-quantized, maps inconsistently through the nonlinearity). This drill tests the
skunkworks-named rescue lever: a GRADED / soft-sparse store code that degrades gracefully under
noise.

Prior-work check (MANDATORY substrate-KB concept-query, MEASURED): `bash tools/substrate_query.sh
"graded soft sparse store code magnitude top-k decorrelation superposition condensation"` -> top
hits are generic WordNet/concept atoms (CN_correlation cosine 0.3877, condensation 0.3828,
magnitude_relation 0.3818); NO prior arc EXPERIMENT cell at cosine > 0.30 (as expected: the
substrate KB has no ingested concept for this). `topk_mag` grep: the identifier is coded-but-unused
in the v1 cell and appears only in unrelated cells (moe_hebbian, qe1_annealing = the beta-knob
negative). No prior cell SWEEPS graded-ness for condensation. Genuinely novel drill continuing the
phase-traversal arc, not a rediscovery.

## Question
Does a GRADED / soft-sparse store code preserve enough decorrelation for high superposition SP AND
condense (or read) gracefully for high pointwise SC -- getting BOTH from ONE code, rescuing the
hard sign+top-k negative? THE TENSION TO RESOLVE EMPIRICALLY (do NOT assume either way): high SP
comes from HARD WTA decorrelation (the sign code is maximally spread); a graded code concentrates
energy on a few large coords -> it may condense/read GRACEFULLY (magnitude survives noise better
than a sign flip) but LOSE the decorrelation that gives SP.

## Mechanism -- MAGNITUDE-GRADED TOP-K, swept by gradedness exponent gamma
Store code: `code_i = sign(z_i) * |z_i|^gamma` on the top-k magnitude support (k = N//32 = 3.125%),
0 elsewhere; z = x @ W_up (fixed random Din=1024 -> N=4096 native expansion; NOT a retrofit
sparsification of dense BGE).
  gamma=0.0 -> sign(z_i)  == the HARD sign+top-k code (v1's confirmed NEGATIVE; kept as the IN-SWEEP
               negative-control endpoint).
  gamma=1.0 -> z_i        == topk_mag (full magnitude retained within the support).
  0<gamma<1 -> partial magnitude gradedness (soft interpolation hard-WTA -> graded).
The top-k SUPPORT (sparsity k) is HELD FIXED across the sweep -> the ONLY variable is
magnitude-gradedness, cleanly ISOLATING the decorrelation-vs-condensability tension (a
temperature-softened WTA that also changed effective sparsity would confound the two). This IS a
temperature-softened interpolation from hard-WTA to graded, realized as a clean single-axis sweep.

Each gamma is judged against ITS OWN static readout (raw argmax on the same graded code, no
transform) -- structural_gain(gamma) = graded_g{gamma} condensed SC - static_g{gamma} SC. The
condenser is the same trained nonlinear RKD-distilled operator as v1 (gelu(s @ W1) @ W2, noise-aug),
retrieval-only, so SP is preserved by construction per gamma.

## Arms
- `graded_g{gamma}` [SWEEP; rescue candidates]: store graded code (gamma), read via trained noise-aug
  CONDENSER. gamma in {0.0, 0.25, 0.5, 0.75, 1.0} at FULL. gamma=0.00 is the HARD-WTA negative control.
- `static_g{gamma}` [own static ctrl per gamma]: store graded code (gamma), read via RAW argmax (NO
  transform). structural_gain is measured against THIS, not the hard code's static.
- `dense_condense` [v1 near-oracle reference]: condense off the non-sparsified dense z (v1 got 0.993).
- `oracle` [CEILING]: SP from a decorrelated store; SC from teacher dense (decoupled existence proof).

## Metrics (uniform per arm)
- SP = superposition recall@J on the arm's OWN graded store code (bundle J, argmax-cosine top-J).
  Measured PER gamma (graded codes have DIFFERENT SP than the hard code -- this is the tension).
- SC = single-concept pointwise recall@alpha (noisy BGE source -> expand -> graded-encode -> [condense]
  -> argmax-cosine over the arm's dict).
- structural_gain(gamma) = graded_g{gamma} condensed SC - static_g{gamma} SC (its OWN static readout).

## Pre-reg bands (envelope-fail; strictly-above-floor per META_RULE_L)
SP_HI=0.83, SC_HI=0.90, MIDDLE_TOL=0.05, STRUCT_MARGIN=0.15. REVIVAL CRITERION (skunkworks-specified,
VERBATIM): a graded/soft-sparse store code achieving SP_B >= 0.83 AND condensed SC >= 0.90 AND
structural_gain >= 0.15 over ITS OWN static readout, at production V.
- `HARD_PASS_GRADED_STATIC_ACHIEVES_BOTH_NO_CONDENSER_NEEDED` = some graded gamma's SP >= 0.83 AND its
  RAW static SC >= 0.90 (the graded sparse code alone serves both; condenser not even needed; the
  STRONGEST rescue -- the hard sign quantization was the entire problem; two-head not needed).
- `HARD_PASS_GRADED_CONDENSE_REVIVES_BOTH` = some graded gamma satisfies the verbatim revival criterion
  (SP >= 0.83 AND condensed SC >= 0.90 AND structural_gain >= 0.15).
- `HARD_FAIL_WALL_FUNDAMENTAL_TWO_HEAD_CONFIRMED` = NO graded gamma beats its own static
  (max structural_gain < 0.15) AND no graded static achieves both -> the condensation wall is
  FUNDAMENTAL, not a sign-discontinuity artifact; two-head decoupled-code is CONFIRMED the only
  solution. VALUABLE CLOSING RESULT (single-code phase-traversal exhausted; route to two-head).
- `HARD_FAIL_GRADED_LOSES_SUPERPOSITION` = a graded gamma beats its static (structural real) but that
  gamma's SP < 0.83 -> the named tension resolves in the LOSE-SP direction (condensability bought with
  magnitude costs the spread). Genuine tradeoff frontier; route to two-head.
- `MIDDLE_GRADED_NEAR_MISS` = graded condenser beats static AND keeps SP AND condensed SC within
  MIDDLE_TOL of SC_HI -> a weight/regime nudge away; report to Research.
- `HARD_FAIL_GRADED_CONDENSE_CANNOT_RECOVER` = graded beats static + keeps SP but condensed SC still
  below SC_HI - MIDDLE_TOL -> gradedness helps but is insufficient; route to two-head / escalate.
- Schema breaches (override): `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`,
  `HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF`, `HARD_FAIL_BASELINE_SATURATED_NO_TRADEOFF_META_RULE_AG`
  (baseline = static_g0.00 hard static; SC >= 0.95 => no tradeoff to solve).

## Compute architecture
Class (a) batched-GPU. Condenser training is matmul-heavy (per-iter store-code forward B x N @ N x H,
nonlinear, then B x B RKD pairwise); (n_gammas + 1 dense) = 6 trainable condensers x 5 seeds x 800
iters. Storage: no_composition/no_store (encoder-geometry cell; per-concept codes evaluated by
argmax-cosine cleanup). FULL routes to GPU (overnight_queue): N=4096, V=40000, B=8192 (B > N ->
full-rank RKD sample); cell auto-selects cuda. SMOKE is CPU-local at PRODUCTION N=4096 AND V=8000
with gammas {0.0,0.5,1.0} (DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C: smoke at full-N, scaled
preview V; the gamma frontier fires at production N and the fixed sparsity fraction).

## Functional Requirements
- FR1 high superposition recall -> decorrelated spread code. Measured SP@J PER gamma (drill tests
  whether gradedness KEEPS this).
- FR2 noisy pointwise discrimination -> semantic code via graded-static readout OR trained condenser.
  Measured SC@alpha.
- FR3 BOTH from ONE stored code -> the graded sparse code is condensable/readable (magnitude survives
  noise where sign flips), tested by the gamma sweep (new mechanism; no prior primitive maps it).

## SCHEMA-VET / cell-template fields
```json
{
  "cardinality_ok": true,
  "expected_n_units_formula": "n_seeds (each seed = all-gamma all-arm measurement) AND every seed carries all n_gammas graded+static arms (gamma-cardinality gate)",
  "arms_differ_verified": true,
  "arms_differ_exempted": [],
  "arms_differ_note": "each gamma's graded store + condensed code is a distinct draw; oracle/dense/static all distinct SC dicts. MEASURED no collisions at smoke.",
  "baseline_in_band": "static_g0.00 (hard static; the negative-control baseline) SC@alpha_OP < 0.95. MEASURED 0.887 at smoke V=8000 (in band, not saturated).",
  "final_metrics_atomicity": "tmp_replace",
  "crlb_n/a": "retrieval recall + geometry cosines; no closed-form noise floor. Feasibility calibrated by v1 + two-head MEASURED SP band 0.43-0.905 and SC band 0.655-1.0 at this exact regime, plus the in-sweep gamma=0 negative-control endpoint.",
  "discriminator_reachability": true,
  "calibration_check": "default_ok_for_this_regime (real BGE cache; J_OP/alpha_OP calibrated in the two-head cell; gamma grid brackets hard(0)->graded(1))",
  "cell_chunked": false,
  "cell_chunked_justification": "few-seed single cell with per-seed partial checkpoint+resume (atomic tmp+os.replace); runner-death loses only the in-progress seed. Pausable/restartable.",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": "print_flush cadence <60s (per-iter every iters//6 + per-gamma SP/SC line + per-seed [seed-done]).",
  "defensive_error_checking": "passed_all_4_patterns (start_marker, crash_metrics, no bare/BaseException except, per-seed partial atomic write)",
  "progress_logging": "print_flush_true",
  "progress_cadence_expected_s": 60,
  "sweep_alignment_verdict": "ALIGNED (swept axis = gamma; each gamma's graded code is the code the condenser AND static readout directly experience -- no partition/effective-param indirection; effective gamma == nominal gamma per primitive)",
  "discriminating_fraction": "MEASURED at smoke V=8000: gamma modulates SP (0.977->0.941), condSC (0.488->0.643), statSC (0.887->0.930), structural_gain (-0.398->-0.287) monotonically across the sweep -> the discriminator (gamma) is highly telemetry-sensitive; 3/3 sweep points produce distinct in-band metrics.",
  "positive_control_arms": "native-spread SP reproduces the WTA superposition ceiling (~0.94-0.98 at V=8000); oracle SC reproduces BGE clean pointwise 1.000; dense_condense reproduces v1's near-oracle 0.988. All MEASURED at smoke.",
  "telemetry_sensitivity": "self-test asserts store SP@J5 AND graded condensed SC@1.2 both MOVE across seeds 7 vs 13 (not analytically pinned), AND condensed SC differs from its OWN static SC (operator changes argmax), AND gamma CHANGES the store code (hard vs graded SP/hash differ). MEASURED PASS (8 witnesses).",
  "functional_requirements": "FR1 superposition (native-expansion graded code, SP@J per gamma), FR2 pointwise (graded-static readout OR RKD condenser), FR3 BOTH from one graded traversed/read code (this cell's new mechanism, flagged)."
}
```

## Self-test (MEASURED)
`--self-test` PASS (8 witnesses) MEASURED (SELFTEST_REGIME N=2048 V=700, gammas {0,0.5,1}): valid_enc
(oracle SC@0=1.000), sp_high (hard store SP@5=0.997 >= 0.83), sp_moves + sc_moves (telemetry-sensitive
across seeds 7/13), struct_changes (hard condensed SC 0.422 != hard static 0.872 -- operator changes
argmax), gamma_fires (hard SP 0.997 != graded SP 0.986; distinct codes), arms_differ (all 8 SC-dict
hashes distinct), trains (finite RKD loss), sc_noise. Tiny-V=700 selftest is NOT predictive of the
FULL-scale verdict direction (static near-saturated with few concepts); that is why SMOKE runs at
V=8000 and FULL at V=40000.

## Smoke (MEASURED)
SMOKE N=4096, V=8000, iters=250, B=1280, seeds 7/13/19; elapsed 1798s CPU. Verdict
`HARD_PASS_GRADED_STATIC_ACHIEVES_BOTH_NO_CONDENSER_NEEDED`. All schema gates pass (arms_differ True,
collisions [], baseline_in_band True [static_g0.00=0.887<0.95], cardinality 3/3 + all gammas present).
MEASURED@data/exp_encoder_phase_traversal_graded_sparse_rescue_v1/metrics.json (3-seed aggregate,
J_OP=5, alpha_OP=1.2):

| gamma | SP@5 | condSC@1.2 | statSC@1.2 | structural_gain | static_achieves_both |
|---|---|---|---|---|---|
| 0.00 (hard sign; v1 neg ctrl) | 0.977 | 0.488 | 0.887 | -0.398 | False (statSC<0.90) |
| 0.50 | 0.963 | 0.601 | 0.911 | -0.310 | True |
| 1.00 (topk_mag) | 0.941 | 0.643 | 0.930 | -0.287 | True |

Reference: dense_condense SC@1.2=0.988; oracle SP=0.977 SC@1.2=1.000; graded_g1.00 clean SC@0.0=1.000.
SP cv <0.008, condSC cv <0.033 across 3 seeds (tight).

READ (honest, Step-0):
1. The RESCUE, if any, is the graded STATIC readout, NOT the condenser. The trained condenser HURTS at
   every gamma (structural_gain negative everywhere), echoing v1's -0.348 -- but structural_gain IMPROVES
   monotonically with gamma (-0.398 hard -> -0.287 topk_mag), confirming the sign discontinuity is the
   worst-case and magnitude-gradedness reduces the condensation penalty. The condenser is perfect on
   CLEAN queries (SC@0=1.000) -> not under-capacity; its failure is noise-robustness, same info wall as v1.
2. The graded STATIC code (raw argmax on topk_mag) achieves BOTH at V=8000: gamma=1.0 SP=0.941 (>=0.83)
   AND statSC=0.930 (>=0.90); gamma=0.5 also (SP 0.963, statSC 0.911). The HARD code (gamma=0) does NOT
   (statSC 0.887 < 0.90). So retaining magnitude (topk_mag) lifts static pointwise +0.043 over the sign
   code while SP falls only 0.977->0.941 (the named tension is MILD at V=8000): one graded code reads out
   BOTH raw, no condenser.
3. The named tension IS visible (SP falls with gamma while pointwise rises) but SP stays well above 0.83
   even at topk_mag -- so at V=8000 gradedness does NOT yet cost enough SP to break the rescue.

## SCALE CAVEAT (load-bearing; DISCRIMINATOR-MUST-SURVIVE-SCALE)
The smoke HARD_PASS fires on the graded-static branch where statSC clears SC_HI=0.90 by only 0.01-0.03
at V=8000. This is a scaled preview, NOT the canonical answer. At production V=40000, crowding lowers
ALL static SC (v1 anchor-sweep MEASURED the decorrelated-vs-crowded SP gap grows with V: -0.561 at
V=4000 -> -0.662 at V=40000), and the graded code's LESS-decorrelated store may also drop SP toward the
0.83 floor. The FULL run at V=40000 is the honest discriminating test:
- If graded static holds SP>=0.83 AND statSC>=0.90 at V=40000 -> genuine single-graded-code rescue
  (topk_mag serves both directly; two-head not needed).
- If graded statSC drops below 0.90 (or SP below 0.83) at V=40000 -> verdict flips to a HARD_FAIL branch
  (wall fundamental / loses-superposition / cannot-recover), the VALUABLE CLOSING RESULT confirming
  two-head as the only single-store-code solution.
Either outcome is informative; do NOT read the smoke HARD_PASS as the final answer.

## Disposition -- SHIP FULL to GPU
Smoke PASSES all dispatch gates (cell runs, discriminator fires cleanly across the gamma sweep, baseline
in band, telemetry-sensitive, multi-seed consistent). Unlike v1 (which HARD_FAILed smoke and honestly
aborted), this drill's revival question is genuinely answered only at production V=40000. SHIP FULL to
overnight_queue (GPU). timeout 14400s (> 10800 floor; 6 condensers x 5 seeds; cell auto-selects cuda,
run_mode defaults full).

queue_add (GPU FULL; orchestrator ships + verifies referent -- exp_dev cannot push/SCP):
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_phase_traversal_graded_sparse_rescue_v1 experiments/exp_encoder_phase_traversal_graded_sparse_rescue_v1.py preregs/encoder_phase_traversal_graded_sparse_rescue_v1.md 14400`

ASCII-only. No unicode. No emojis. No em dashes.
