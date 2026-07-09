# Pre-reg: grounding_encoder_clean_codes_cheap_levers_v1 (Stage-1 no-retrain cheap-lever encoder fix)

Cell: `experiments/exp_grounding_encoder_clean_codes_cheap_levers_v1.py`
Anchor: `grounding_encoder_clean_codes_cheap_levers_v1`
Author: exp_dev. Filed BEFORE FULL dispatch. Bands picked before the FULL run.

## Question
Does any CHEAP NO-RETRAIN lever applied to the binding-structured encoder's FROZEN learned codes lift
role-recovery fidelity + multi-hop reach above the confirmed HARD_FAIL floor
(role-apply edge_recall = 0.2819, effective reach = 1)? This is Stage 1 of the drill's ablation ladder --
the near-zero-cost decisive test that resolves the S3 fork:
(a) codes are merely insufficiently SPARSE (cheap post-hoc fix), vs
(b) codes were never trained with a strong-enough structural signal (needs Stage-2 retrain).

## Levers (all NO-RETRAIN, applied to the SAME per-seed binding-encoder codes)
1. SPARSE: native-space k-WTA at active-fraction a, sweeping `SPARSITY_SWEEP=[0.02,0.05,0.10,0.20,0.35,0.50]`.
2. SPARSE_ORTHO: + Lowdin (symmetric) orthonormalized role basis (reduce cross-role unbind crosstalk).
3. RESONATOR: dense codes (a=1.0, the codes' fair-best point) + ortho roles + iterative soft-attractor
   cleanup (`hdlab.iterative_attractor.iterative_cleanup`, alpha=0, RES_MAX_STEPS=4, RES_TEMP=4.0).

Native-space k-WTA (not DG expansion) is the faithful no-retrain sparsity lever: HRR bind structure lives
in the native code space, so a fixed random expansion would break bind(role_r,z_i)~=z_j without a retrain.
DG-expansion + binding-consistency objective is DEFERRED to Stage-2 (gated on this cell's verdict).

## Discriminator (telemetry-sensitive; reach shuffle+collapse-gated)
- Role-recovery edge_recall + edge_precision of role-apply unbind on the LEARNED codes (score matrix ->
  size-aware crosstalk floor + top-k adjacency -> recall/precision vs true typed edges), AND
- Effective multi-hop REACH over the CODE-RECOVERED graph (grounded graph-smooth attribute propagated D
  steps; reach = farthest contiguous TRUE-distance bin with ordering-acc >= REACH_THRESH=0.55 and margin
  over shuffled >= MARGIN_FLOOR=0.05, non-collapsed). reach>=2 == typed binding chains past 1 hop on real
  codes. Reach machinery imported VERBATIM from the baseline cell -> bit-identical reach definition.

## Pre-registered bands
- Baseline reproduce contract (contrast floor): BASELINE_RAW recall in [0.20, 0.42] AND reach <= 1.
  Else BASELINE_REPRO_FAIL. (baseline_in_band: a floor to beat, NOT a saturated ceiling.)
- HARD_PASS: a lever point with edge_recall >= RECALL_HP_MIN=0.45 AND precision >= PRECISION_FLOOR=0.10
  AND eff_reach >= REACH_HP_MIN=2 AND (reach - baseline_reach) >= REACH_DELTA_HP=1.
- MIDDLE_BAND: best lever recall >= RECALL_MIDDLE_MIN=0.38 OR a recall-preserving lever extends reach>=2
  (sparsity partially helps; Stage-2 retrain indicated).
- HARD_FAIL_CHEAP_LEVERS_INSUFFICIENT: best lever recall < baseline + RECALL_HARDFAIL_DELTA=0.05 AND no
  recall-preserving lever extends reach past 1 (cheap levers null -> Stage-2 retrain NECESSARY; resolves
  the S3 fork toward (b)).
- Reach-extension is credited ONLY to lever points that PRESERVE recall (recall >= base_recall - 0.02): a
  reach win on codes WORSE than the raw baseline is reach-probe noise, not a chaining gain.

### Number provenance (MEASURED / HYPOTHESIZED / THEORETICAL / CITED)
- baseline role-apply edge_recall = 0.2819, reach = 1
  MEASURED@data/exp_grounding_binding_structured_encoder_multihop_v1/metrics.json:gates.recall_mean.BINDING_UNBIND
- baseline role-apply edge_precision = 0.1334 (sets PRECISION_FLOOR)
  MEASURED@data/exp_grounding_binding_structured_encoder_multihop_v1/metrics.json:gates.precision_mean.BINDING_UNBIND
- single-hop fidelity f>=0.85-0.90 needed for reliable reach>=2 (f^2 compounding)
  CITED@notes/research_encoder_clean_composable_relational_codes_2026-07-09.md:S2/predictions
- recovery-vs-sparsity is a sharp PHASE TRANSITION (Donoho-Tanner), not a gradual curve
  CITED@notes/research_encoder_clean_composable_relational_codes_2026-07-09.md:S1b
- crosstalk floor = c*sqrt(2 ln n / d) (codebook-size-aware VSA cleanup floor)
  THEORETICAL@extreme-value/Bonferroni crosstalk criterion (imported crosstalk_floor)
- RECALL_HP_MIN=0.45, REACH_HP_MIN=2 bands HYPOTHESIZED@this prereg (decisive jump above the 0.40 cosine
  arm + functional 2-hop chaining beating baseline reach=1)

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (3 FULL). Sweep coverage asserted WITHIN each seed
  (len(recall_by_a)==len(SPARSITY_SWEEP) for SPARSE and SPARSE_ORTHO); else SWEEP_CARDINALITY_BREACH.
- arms_differ_verified: true (recovered-edge-set hash; lever arms vs BASELINE_RAW). arms_differ_exempted: none.
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-clean).
- crlb_n/a: "reach ordering-acc chance floor = 0.5; discriminator is shuffle+collapse-gated reach + role-
  recovery edge_recall vs a reproduced baseline floor, not a closed-form estimator noise floor."
- discriminator_reachability: true (baseline reproduces the 0.28/reach-1 floor with headroom to 0.45/reach-2).
- baseline_in_band: true (BASELINE_RAW recall ~0.29 in [0.20,0.42], reach 1 <= 1; a floor to beat).
- calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run; over-
  smoothing collapse gate fires; crosstalk floor sqrt(2 ln n/d)-scaled).
- cell_chunked: false (<=3 seeds in-cell; per-seed checkpoint via write_partial; single anchor).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: true (per-sweep-point).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-arm/per-sweep flush prints + heartbeat).

## §15 composition/sweep gates
- sweep_alignment_verdict: ALIGNED (the swept param a is the ACTUAL active-fraction each recovery arm
  experiences; no partition indirection).
- discriminating_fraction: sweep spans a=0.02..0.50 straddling the native-k-WTA phase transition;
  smoke confirms a NON-FLAT recall curve (0.001 at a=0.02 -> 0.25 at a=0.50) => discriminator fires.
- composition_edges: encoder_code -> {kwta / ortho-role / iterative-cleanup} -> topk-floor-adjacency ->
  reach-propagation. SHAPE_MATCH at each edge (all operate on [n, code_dim] native codes; cleanup returns
  [n, code_dim] state; scores are cosine-scale so the SAME floor/topk applies).
- positive_control_arms: BASELINE_RAW reproduces the cited baseline atom (role-apply recovery, tol via the
  reproduce band [0.20,0.42]); lever_selftest reproduces PLANTED-structure recovery (recall_res>=0.5).
- functional_requirements: (1) lift role-recovery fidelity on frozen learned codes [levers]; (2) preserve
  precision / no spurious edges [size-aware floor + precision floor + F1]; (3) chain reach>=2 on real codes
  [reach machinery]; (4) reproduce the baseline floor [BASELINE_RAW control].

## Compute architecture
- class (b) sequential-CPU with justification: reuses the CG'd CPU-only teacher-free relational encoder +
  HRR FFT bind (numpy) VERBATIM; encoder training has sequential epoch dependency; recovery/reach are
  matmul-heavy but run through numpy BLAS (multithreaded). Baseline FULL landed in 47.6s on CPU; this cell
  trains ONE encoder per seed (vs baseline's 2) + ~13 no-retrain recovery arms + 1 resonator. Wall < 10 min
  expected. Porting to GPU would fork the proven baseline machinery for no material gain.
- storage strategy: SHARDED (each node its own code vector; recovery is per-edge; no bundling).

## SMOKE result (2 seeds, n=1525, MEASURED@data/exp_grounding_encoder_clean_codes_cheap_levers_v1_smoke/metrics.json)
- baseline_reproduces=True: BASELINE_RAW recall=0.294 prec=0.175 reach=1.0 (floor reproduced).
- Discriminator fires: sparsity sweep is a clean monotone phase curve; native k-WTA MONOTONICALLY HURTS
  (a=0.02 recall 0.001 -> a=0.50 recall 0.25, all BELOW the dense 0.294 baseline).
- SPARSE_ORTHO == SPARSE within noise (ortho adds nothing at code_dim>>n_rel_types; roles already near-orthogonal).
- RESONATOR (cleanup on dense) HURTS: recall 0.294 -> 0.106 (iterative attractor collapses the weak-but-
  correct top-k signal onto confident-wrong attractors).
- No lever preserves recall AND extends reach => verdict HARD_FAIL_CHEAP_LEVERS_INSUFFICIENT.
- Smoke strongly predicts the FULL verdict: cheap no-retrain levers do NOT crack the encoder wall ->
  Stage-2 (DG-expansion + binding-consistency retrain) is the necessary fix (fork resolved toward (b)).

## FULL profile
seeds=[7,13,17], n_nodes=5000, epochs=100, code_dim=256, feat_dim=8192, D=[1,2,3,4,5]. Confirms the
Stage-1 finding at canonical scale (bigger code_dim halves the crosstalk floor -> a fair last chance for a
lever to cross the phase boundary). Both outcomes gold.
