# Pre-reg: encoder_distill_anchor_sweep_vicreg_decorr_v1

Date: 2026-07-08
Cell: `experiments/exp_encoder_distill_anchor_sweep_vicreg_decorr_v1.py`
Anchor: `encoder_distill_anchor_sweep_vicreg_decorr_v1`
Trigger: Rank-1 candidate of `notes/research_encoder_objective_beyond_bge_distillation_2026-07-08.md`
(add VICReg decorrelation ON TOP OF the R1 global/landmark RKD distillation anchor), REFRAMED by the
teacher-cap-vs-student-underfit disambiguation VET (`exp_recall_ceiling_teacher_cap_vs_student_underfit_v1`,
commit cdfe7b465) and the certified law `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval`.

## Question
The disambiguation certified that a substrate-native decorrelating block code BEATS BGE on the load-bearing
superposition recall task (matching BGE geometry caps SP@J5 at ~0.34 while native reaches ~0.93; mechanism =
BGE teacher-crowding, median_NN cos 0.921, 62% of concepts >0.90), BUT decorrelation COSTS single-concept
pointwise fidelity (native ~0.56 vs teacher ~0.997 at FULL). So the honest target is NOT "decorrelation wins"
but an objective that gets BOTH high superposition recall AND retained pointwise fidelity. This cell makes the
BGE-distillation anchor weight a SWEPT LEVER and asks: can a SINGLE scalar-anchor arm get both, or is it a
strict tradeoff along the knob (=> structural decoupling needed)?

## Mechanism
Train a linear student W: Din(1024)->N per arm by gradient descent.
`L = lambda_d * L_rkd + mu * L_var + nu * L_cov`
- L_rkd: global/landmark relational-KD (match per-minibatch student pairwise-cosine matrix to BGE teacher's;
  dimension-agnostic). This is the R1 distillation anchor.
- L_var: VICReg variance-floor `(1/N) sum_j relu(gamma - sqrt(Var(z_j)+eps))`, gamma=1.0.
- L_cov: VICReg off-diagonal covariance decorrelation `(1/N) sum_{i!=j} Cov(z)_ij^2` (Gram-trick when B<=N).
lambda_d (BGE-anchor weight) is the swept lever: {1.0 vicreg-off, 1.0, 0.3, 0.1, 0.0}. mu=nu=1.0 fixed
(the open question is HOW MUCH ANCHOR, not how much decorrelation; nu flagged for a follow-up sweep).

## Arms (7)
distill_only (lambda_d=1.0, vicreg off), hybrid_d1.0/0.3/0.1 (vicreg on), native_trained (lambda_d=0),
native_untrained (random W + WTA; disambiguation zero-train positive control), teacher_bge (raw unit BGE).

## Three metrics per arm
(a) SUPERPOSITION recall@J [PRIMARY, WTA block code] -- reuse disambiguation `_superposition_recall`.
    The decorrelation lever acts through the top-K WTA sparsification; DENSE geometry of any linear BGE map
    is Johnson-Lindenstrauss-bounded to the crowded teacher geometry and CANNOT discriminate the lever
    (confirmed at self-test: dense SP is JL-flat ~0.45 across arms; WTA SP spreads 0.62-0.90). Dense SP kept
    as a secondary diagnostic only.
(b) SINGLE-CONCEPT pointwise fidelity -- SC recall@alpha=1.2 (noisy source encoded THROUGH the arm's WTA
    code; teacher uses identity BGE). The axis BGE wins; the real tradeoff.
(c) OFF-TARGET separation geometry -- mean pairwise cosine among DIFFERENT concepts (the whitening-revival
    mean_cos anisotropy diagnostic), vs BGE's OWN off-target mean cosine on the SAME concept set.

## Pre-reg bands (envelope-fail)
RECONCILED PRIMARY (VET update): SP_HI_THRESH=0.75 (high superposition), SC_HI_THRESH=0.90 (high pointwise).
- `SCALAR_KNOB_SUFFICES_BOTH_ACHIEVED`  = some single trained arm has WTA SP>=0.75 AND SC>=0.90.
- `STRICT_TRADEOFF_STRUCTURAL_DECOUPLING_NEEDED` = no single arm gets both, BUT the decoupled-oracle
  (decorrelated store code for superposition + BGE-anchored retrieval for pointwise) achieves both.
- `NO_ARM_OR_DECOUPLING_ACHIEVES_BOTH` = neither (unexpected; inspect before FULL).
GEOMETRY sub-verdict (the note's original Rank-1 bands, secondary): SP_MARGIN=0.05, SEP_MARGIN=0.03,
SC_TOL=0.05 -> GEOM_HARD_PASS / GEOM_MIDDLE / GEOM_HARD_FAIL.
Structural-decoupling preview: the decoupled-oracle is a ZERO-compute existence proof; a real trained
two-head arm (VICReg-cov on store head, RKD on retrieval head) is the concrete next cell if the oracle fires.

## Compute architecture
Class (a) batched-GPU. Training is matmul-heavy (per-iter RKD pairwise B x B + VICReg covariance via Gram/full
over a minibatch); 5 trained arms x 5 seeds x hundreds of iters. Storage strategy: no_composition/no_store
(encoder-geometry cell; per-concept codes evaluated by argmax-cosine cleanup, not a bundled associative store).
FULL routes to GPU (overnight_queue): N=4096, B=8192 > N gives a full-rank covariance estimate. SMOKE is
CPU-local at reduced N=2048/B=1024 (covariance is O(N^2 B)); the WTA decorrelation lever is a fixed
nonlinearity the disambiguation MEASURED at N=4096, so the discriminator survives to FULL by that cell's
V-scaling evidence (DISCRIMINATOR-MUST-SURVIVE-SCALE option B + smoke preview at N=2048).

## SCHEMA-VET / cell-template fields
```json
{
  "cardinality_ok": true,
  "expected_n_units_formula": "n_seeds (each seed = all-arm measurement)",
  "arms_differ_verified": true,
  "arms_differ_exempted": [],
  "baseline_in_band": "distill_only WTA SP@J5 in (0.05,0.95); MEASURED smoke 0.828",
  "final_metrics_atomicity": "tmp_replace",
  "crlb_n/a": "retrieval recall + geometry cosines; no closed-form noise floor. Feasibility calibrated by the disambiguation MEASURED SP band 0.34-0.93 and SC band 0.56-1.0 at this exact regime.",
  "discriminator_reachability": true,
  "calibration_check": "default_ok_for_this_regime",
  "cell_chunked": false,
  "cell_chunked_justification": "follows disambiguation template (multi-seed single-cell with per-seed partial checkpoint+resume; each seed fast; runner-death loses only in-progress seed, resumes from partial).",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": "print_flush cadence <60s (per-arm every iters//6 + per-seed [seed-done]); FULL ~13min < hang-watchdog window; follows disambiguation template.",
  "defensive_error_checking": "passed_all_4_patterns (start_marker, crash_metrics, no bare/BaseException except, per-seed partial atomic write)",
  "progress_logging": "print_flush_true",
  "progress_cadence_expected_s": 60,
  "sweep_alignment_verdict": "ALIGNED (lambda_d anchor weight is experienced directly by the RKD loss of each trained arm; no partition indirection)",
  "discriminating_fraction": "smoke MEASURED WTA SP spread 0.62-0.90 across arms + SC spread 0.61-1.0; both metrics in discriminating band for >30% of arms",
  "positive_control_arms": "native_untrained reproduces the disambiguation zero-train WTA code (SP@J5 MEASURED 0.905 smoke ~ 0.929 disambiguation); teacher_bge reproduces BGE dense (SP 0.43, SC 1.0)",
  "telemetry_sensitivity": "self-test asserts native_untrained WTA SP@J5 differs across seeds 7 vs 13 (0.913 != 0.851); not bit-identical/analytically-pinned"
}
```

## Self-test + smoke (MEASURED)
- `--self-test` PASS: valid_enc (teacher J1=1.0), telemetry-sensitivity (seed moves metric), arms_differ (7
  distinct dense hashes), wta_boosts (WTA SP 0.913 >> dense 0.480 -- lever fires, scale-robust),
  both_branches, sc_moves, sep_ok.
- SMOKE (N=2048, V=1500, B=1024, 80 iters, seeds 7/13/19; ~5.5 min CPU): verdict
  `STRICT_TRADEOFF_STRUCTURAL_DECOUPLING_NEEDED`. both_arms=[] (no scalar arm gets SP>=0.75 AND SC>=0.90).
  Decoupled-oracle achieves_both=True (store native_untrained WTA SP=0.905 + teacher retrieval SC=1.000).

## FULL dispatch (GPU, gated on Director go)
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_distill_anchor_sweep_vicreg_decorr_v1 experiments/exp_encoder_distill_anchor_sweep_vicreg_decorr_v1.py preregs/encoder_distill_anchor_sweep_vicreg_decorr_v1.md 3600`
(runner invokes with `--run-mode full`; cell auto-selects cuda when available.)

ASCII-only. No unicode. No emojis. No em dashes.
</content>
