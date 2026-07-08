# Pre-reg: encoder_twoband_single_vector_am_fm_v1

Date: 2026-07-08
Cell: `experiments/exp_encoder_twoband_single_vector_am_fm_v1.py`
Anchor: `encoder_twoband_single_vector_am_fm_v1`
Trigger: the two-head cell (`exp_encoder_twohead_decoupled_store_retrieval_v1`) proved a shared trunk feeding
TWO separate full-N heads (2N budget) achieves both high superposition and high pointwise. The strict-tradeoff
frontier (`exp_encoder_distill_anchor_sweep_vicreg_decorr_v1`) MEASURED that NO single N-dim code serving BOTH
readouts through the SAME dimensions can do both (per-dimension conflict). Certified law:
`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval`.

Prior-work check: substrate concept-query "two-band single vector encoder bundling superposition fine-detail
pointwise partition dimensions conditional readout" returned only char-trigram lexical coincidences
(`conditional_reaction`/`condition`/`partition` at cosine 0.34-0.38, all wordnet/verbnet dictionary words, NOT a
prior arc cell -- the substrate encoder is char-trigram and semantically blind). No existing `two_band`/`am_fm`
cell in experiments/. Genuinely NOVEL (a distinct workaround from the two-head sibling and the single-code
frontier; see the WHY-THIS-IS-DISTINCT scour in the cell docstring vs frontier / two-head / R5-serial /
sparsified-dense-retrofit).

## Question
The single-code frontier forces ALL N dims to serve BOTH readouts (per-dim conflict -> provably cannot do both).
The two-head sibling spends 2N (two full-N vectors). Can ONE N-dim vector do both by PARTITIONING ITS OWN
DIMENSIONS into two DISJOINT internal sub-bands read CONDITIONALLY per task -- AM+FM on one wire -- so no
dimension serves two masters, at the frontier's N budget (HALF the two-head's 2N)?
  band_B (BUNDLING sub-band, first N_b dims): VICReg-decorrelated; superposition carrier; read via WTA block code.
  band_D (fine-DETAIL sub-band, last N_d dims): RKD BGE-distilled; pointwise carrier; read via dense argmax-cosine.

## Mechanism
Shared LINEAR trunk feats = x @ W_trunk (Din -> H=512). ONE output projection W_out (H -> N) emits ONE code z;
its columns are PARTITIONED into disjoint slices z_B = z[:, :N_b] (VICReg var-floor + off-diag covariance
decorrelation) and z_D = z[:, N_b:] (global/landmark RKD, match student pairwise-cosine to BGE teacher; Gram-trick
VICReg when B<=N, full cov when B>N). No dimension is shared between roles; the ONLY shared parameter is the trunk
(the interference surface). L = mu*L_var(z_B) + nu*L_cov(z_B) + lambda_d*L_rkd(z_D); mu=nu=lambda_d=1.0,
gamma_var=1.0, lr=1e-3. band_frac_B (= N_b / N) is the split ratio; HEADLINE gate reads frac 0.5 (N_b=2048 at
N=4096); FULL sweeps {0.375, 0.5, 0.625} (diagnostic, non-gating).

## Arms (7)
twoband_shared [HEADLINE] (shared trunk, ONE W_out, band_B VICReg + band_D RKD, ONE vector N budget);
twoband_split_trunk [ENRICH] (separate trunk per band, still ONE concatenated N-dim vector -- isolates whether
TRUNK-sharing not partition is the cost); twohead_2N [CEILING] (TWO separate full-N vectors, 2N budget = the
sibling architecture; double-budget ceiling); singlecode_native [FRONTIER] (one N code, VICReg only, dual
readout); singlecode_distill [FRONTIER] (one N code, RKD only, dual readout); teacher_bge [REF] (raw unit BGE);
native_untrained [REF] (random W + WTA superposition ceiling).

## Metrics (uniform per arm; band_B superposition axis + band_D pointwise axis + two CROSS-READ axes)
- SP_B = superposition recall@J on band_B WTA block code (3.125% sparsity per band).
- SC_D = single-concept pointwise recall@alpha on band_D DENSE code (noisy BGE query encoded through the band,
  argmax-cosine over the dict).
- SP_D = CROSS: superposition recall@J on band_D WTA (WRONG band for superposition; should FAIL -- band_D is
  BGE-anchored/crowded).
- SC_B = CROSS: pointwise recall@alpha on band_B DENSE (WRONG band for pointwise; should be lower for a
  VICReg-decorrelated band).
- achieves_both = SP_B@J_OP(5) >= SP_HI AND SC_D@alpha_OP(1.2) >= SC_HI.
- split_real (anti-cosmetic) = (SP_B - SP_D >= CROSS_SP_GAP) AND (SC_D - SC_B >= CROSS_SC_GAP): reading the WRONG
  band for a task must fail -> the two bands carry DIFFERENT content, not the same thing duplicated.

## Pre-reg bands (envelope-fail; HEADLINE = twoband_shared at band_frac_B=0.5; strictly-above-floor per META_RULE_L)
SP_HI=0.83 (below the MEASURED N_b=2048 feasibility ceiling 0.876, headroom), SC_HI=0.90 (below teacher ~1.0),
MIDDLE_TOL=0.05, CROSS_SP_GAP=0.20, CROSS_SC_GAP=0.10.
- `HARD_PASS_TWOBAND_SINGLE_VECTOR_ACHIEVES_BOTH` = twoband_shared achieves_both AND split_real: ONE N-dim
  vector, partitioned, delivers BOTH high superposition (band_B SP_wta>=0.83, clearing the single-code frontier)
  AND high pointwise (band_D SC_dense>=0.90), AND the cross-read confirms the bands are genuinely specialized.
- `HARD_FAIL_COSMETIC_SPLIT_BOTH_BANDS_SAME` = achieves_both numerically BUT cross-read gaps too small (the
  split is cosmetic; both bands carry the same content).
- `MIDDLE_ONE_BAND_HITS` = exactly one band hits its target, the other within MIDDLE_TOL of target.
- `HARD_FAIL_ONE_BAND_FAR_MISS` = one band hits, the other misses by > MIDDLE_TOL.
- `HARD_FAIL_NO_GAIN_OVER_SINGLE_CODE` = twoband_shared joint <= best single-code frontier arm's joint (the
  partition bought nothing over a single code).
- `HARD_FAIL_SHARED_VECTOR_INTERFERES_NEITHER_BAND` = neither band hits (the shared vector/trunk forces
  interference so the partition starves both).
Enrichment (reported, not gating): twoband_split_trunk + twohead_2N joints (N-vs-2N budget ceilings the two-band
approaches); band_frac_B in {0.375, 0.5, 0.625} sweep (FULL only) locating the split where BOTH bands clear.

## Compute architecture
Class (a) batched-GPU. Training is matmul-heavy (per-iter RKD pairwise BxB, VICReg covariance over a minibatch,
trunk+out forwards); 5 trained arms (twoband arms x 3 band-fracs at FULL) x 5 seeds x hundreds of iters. Storage:
no_composition / no_store (encoder-geometry cell; the "dictionary" is the per-concept code, evaluated by
argmax-cosine cleanup, not a bundled associative store). FULL routes to GPU (overnight_queue): N=4096, V=40000,
B=8192 > N gives a full-rank covariance estimate; cell auto-selects cuda. SMOKE is CPU-local at PRODUCTION N=4096
(band dims = the REAL operating dimension -> the superposition discriminator is dimension-dependent so smoke runs
at full N per DISCRIMINATOR-MUST-SURVIVE-SCALE option A) with reduced V/iters/B and a single band_frac=0.5.

SMOKE SCOPE LIMITATION (declared honestly): the split_real cross-read discriminator (SP_B - SP_D) is V/crowding
dependent -- at smoke V=1500 the superposition task is easy for ALL bands (even band_D superposition stays high),
so the cross gap is SMALL and split_real may not clear at smoke; the split discriminator fires at FULL V=40000.
This is quantified by the MEASURED feasibility probe: at V=4000, band_D-read-for-superposition = 0.324 (fails)
vs band_B = 0.909, a 0.585 gap >> CROSS_SP_GAP=0.20 (analytical justification B). Smoke's load-bearing job is to
fire the achieves_both discriminator (SP_B>=0.83 AND SC_D>=0.90) + arms-differ + trunk-interference mechanics; the
split-at-scale test is the intended smoke->FULL handoff, not a masked saturation.

## SCHEMA-VET / cell-template fields
```json
{
  "cardinality_ok": true,
  "expected_n_units_formula": "n_seeds (each seed = all-arm, all-band-frac measurement)",
  "arms_differ_verified": true,
  "arms_differ_exempted": [],
  "arms_differ_note": "arm-name+n_b init salt added so objective-sharing arms (twoband_split_trunk and singlecode_native both VICReg) do NOT draw bit-identical; MEASURED distinct band_B hashes at self-test + smoke.",
  "baseline_in_band": "singlecode_distill band_B SP_wta@J5 in (0.05,0.95); crowded RKD single code (MEASURED smoke below).",
  "final_metrics_atomicity": "tmp_replace",
  "crlb_n/a": "recall/accuracy over argmax cleanup + geometry cosines; no closed-form noise floor. Feasibility calibrated by the MEASURED feasibility probe (band_B SP@5=0.876 at N_b=2048 clears SP_HI=0.83; band_D SC=0.998 clears SC_HI=0.90) at this exact regime.",
  "discriminator_reachability": true,
  "calibration_check": "default_ok_for_this_regime",
  "cell_chunked": false,
  "cell_chunked_justification": "5 trained arms x band-fracs x seeds in ONE cell with per-seed partial checkpoint+resume (atomic .tmp+os.replace); each seed light; runner-death loses only the in-progress seed and resumes from partial.",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": "_heartbeat.jsonl per-seed + print_flush cadence <60s (per-iter every iters//5, per-arm SP/SC line, per-seed [seed-done]); FULL est <45min.",
  "defensive_error_checking": "passed_all_4_patterns (start_marker, crash_metrics CELL_CRASHED+traceback, no bare/BaseException except, per-seed partial atomic write)",
  "progress_logging": "print_flush_true",
  "progress_cadence_expected_s": 60,
  "sweep_alignment_verdict": "ALIGNED (band_frac_B sweep is diagnostic-only; the HEADLINE gate reads a single pre-declared frac 0.5. Each swept frac trains a fresh (arm, n_b) code that DIRECTLY experiences that N_b as its band-B dimension -- effective param == nominal param, no partition/routing indirection).",
  "discriminating_fraction": "achieves_both discriminator: singlecode_distill (frontier) misses band_B SP while twoband_shared clears it -> the arms straddle the SP_HI=0.83 band. split_real cross-read discriminator fires at FULL V=40000 (declared smoke-scope limitation; feasibility probe gap 0.585 at V=4000).",
  "positive_control_arms": "native_untrained reproduces the zero-train WTA superposition ceiling (~0.93); teacher_bge reproduces BGE pointwise (SC ~1.0); twohead_2N reproduces the sibling two-head architecture as the 2N ceiling. Regime-extension: same BGE cache + same WTA/superposition harness as the two-head + anchor-sweep cells (SHAPE_MATCH, not synthetic-to-narrative drift).",
  "telemetry_sensitivity": "self-test asserts (1) store axis: twoband_shared band_B SP_B@J5 differs across seeds 7 vs 13 (not analytically pinned); (2) pointwise axis on TWO non-fragile sub-axes -- NOISE-axis: headline SC_D drops 1.0 -> ~0.465 at NOISE_PROBE_ALPHA=4.0 (strong data-response, no discretization-tie risk), SEED-axis: continuous sep_D_dense geometry differs across seeds (avoids the count/nq recall ties that make single-point comparisons fragile). MEASURED PASS.",
  "functional_requirements": "FR1 high superposition capacity (band_B, VICReg decorrelation -> WTA block code); FR2 high single-concept pointwise fidelity (band_D, RKD BGE-distillation -> dense readout); FR3 both from ONE partitioned N-dim vector at N budget (the interference + partition test); FR4 the split is REAL not cosmetic (cross-read guard). Each FR maps to an existing chain-grade primitive (VICReg decorrelation certified; RKD distillation; WTA superposition harness from the anchor-sweep/two-head cells)."
}
```

## Self-test + smoke (MEASURED)
- `--self-test` PASS (8 witnesses): valid_enc (teacher band_B J1=1.000), telemetry-sensitivity (store SP moves
  across seeds; pointwise SC_D moves on noise-axis 1.0 -> 0.465 AND continuous sep_D_dense moves across seeds),
  arms_differ (7 distinct band_B hashes), both_bands_train, superpos_specializes (twoband_shared SP_B 0.949 >
  SP_D 0.889 -- band_B beats band_D on superposition), pointwise_specializes (SC_D 1.0 >= SC_B 0.97 -- band_D
  beats band_B on pointwise), sc_noise (teacher SC degrades with noise). MEASURED@self-test stdout 2026-07-08.
- SMOKE (N=4096, H=512, V=1500, B=768, 120 iters, band_frac 0.5, seeds 7/13/19; CPU, 698s): verdict
  `HARD_FAIL_COSMETIC_SPLIT_BOTH_BANDS_SAME`. MEASURED@data/exp_encoder_twoband_single_vector_am_fm_v1/metrics.json:
  - twoband_shared [HEADLINE]: SP_B@5 = 0.961 (cv 0.023), SC_D@1.2 = 1.000 -> achieves_both = True (joint 1.111).
  - CROSS-READ (the gating axis): SP_D@5 = 0.896 -> cross_sp_gap = +0.066 (< CROSS_SP_GAP 0.20);
    SC_B@1.2 = 0.985 -> cross_sc_gap = +0.015 (< CROSS_SC_GAP 0.10) -> split_real = False -> COSMETIC verdict.
  - CEILINGS: twoband_split_trunk SP_B 0.963 / SC_D 1.0 (both); twohead_2N (2N budget) SP_B 0.984 / SC_D 0.999
    (both), SP_D 0.969. FRONTIER: singlecode_native SP_B 0.993 / SP_D 0.993 and singlecode_distill 0.932 / 0.932
    -- ONE code so their cross gaps are EXACTLY 0 by construction. best_frontier_joint 1.111.
  - GENUINE-vs-DESIGN (honest): the two-band cross gaps are directionally CORRECT on BOTH axes (band_B > band_D
    on superposition +0.066; band_D >= band_B on pointwise +0.015) -- NOT the zero-gap identity the single-code
    arms show -- but small in MAGNITUDE. This is the DECLARED low-V smoke-scope limitation: at V=1500 both
    superposition@J5 and pointwise@alpha1.2 among only 1500 concepts SATURATE, so even the WRONG band scores high.
    The SP cross-axis is feasibility-probe-backed to fire at FULL V=40000 (band_D superposition 0.324 vs band_B
    0.909 = 0.585 gap at V=4000). The SC (pointwise) cross-axis is UNPROVEN (needs band_B's decorrelated pointwise
    to degrade at V=40000; the sibling two-head cell flagged this exact question as open). So: NOT a genuine "one
    vector cannot hold two separate bands" collapse (bands ARE directionally specialized, not identical); the
    residual risk is a DESIGN lever (no explicit cross-band anti-redundancy / orthogonality pressure). Routed to
    skunkworks to adjudicate declared-artifact-vs-redesign BEFORE any FULL or drill.

## FULL dispatch (GPU overnight_queue; NOT shipped -- skunkworks adjudication first per coordinator)
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_twoband_single_vector_am_fm_v1 experiments/exp_encoder_twoband_single_vector_am_fm_v1.py preregs/encoder_twoband_single_vector_am_fm_v1.md 3600`
(runner invokes with `--run-mode full`; cell auto-selects cuda when available. Post-dispatch: verify landed
metrics.json run_mode==full + size per section 16 RUN_MODE VERIFICATION.)

ASCII-only. No unicode. No emojis. No em dashes.
