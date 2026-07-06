# PRE-REG: exp_reasoning_depth_exact_order_statistic_self_margin_v1

Author: exp_dev 2026-07-06. Cell: `experiments/exp_reasoning_depth_exact_order_statistic_self_margin_v1.py`.
Status: SELFTEST PASS + SMOKE HARD_PASS (local, N=8192). FULL staged (remote_cpu_queue).
Non-parked (zero cert_ledger referent). Monitor-not-control (NOT self-improvement).
Hand-off: `notes/exp_dev_handoff_research_reasoning_depth_self_margin_2026-07-06.md`;
research note `notes/research_reasoning_depth_self_margin_closed_form_2026-07-06.md`.

## Question under test
Does the substrate predict its OWN usable reasoning depth (the collision-bound ceiling) in
closed form, EXACTLY, via the capture partial-credit order statistic -- promoting the landed
reasoning-depth cell (`exp_reasoning_depth_keyslots_sharding_v1`, MIDDLE_BAND) the same way the
exact order-statistic prefactor promoted the RNS decode-margin and FHRR bundle-capacity cells
to HARD_PASS? The landed cell is MIDDLE_BAND because its own pre-registered predictor is
OCCUPANCY-BINARY (treats a key-slot collision as a GUARANTEED failure); the true dynamics are
graceful CAPTURE (a collided slot is a superposition of c objects; single-shot argmax still
recovers the true one with probability ~1/c). Re-deriving per-hop success as an exact
Poisson-occupancy-averaged capture order statistic (the SAME Gauss-Hermite machinery as the two
sibling CG cells) and composing across depth via the series-reliability law
`D* = ln(FLOOR)/ln(p_hop)` should convert the occupancy-binary predictor's systematic +102%
under-prediction into an unbiased self-prediction.

## Extends / reuses
- Measurement machinery reused VERBATIM from the landed `exp_reasoning_depth_keyslots_sharding_v1`
  (FactoredStore, ShardedStore, make_chains, walk_curve, argmax_clean, empirical_collision_frac,
  usable_depth). Single-shot argmax cleanup is FIXED (proven MAP-optimal by
  `exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1`; the iterative-cleanup lever is
  CLOSED and NOT reopened here).
- Order-statistic template: `exp_rns_subblock_margin_exact_prefactor_v2` (HARD_PASS) +
  `exp_fhrr_bundle_capacity_exact_margin_v1` (HARD_PASS) -- 64-pt numpy Gauss-Hermite, no scipy.
- This is the SAME "elevated-mean signal vs zero-mean competitors" order-statistic family, one
  level UP the composition stack (per-hop decode margin -> multi-hop chain survival), plus one
  new ingredient: c-1 co-colliding objects at the SAME elevated mean (the capture term).

## Arms (per (N, seed, N_TEST); paired by identical chains where compared)
5 MEASUREMENT arms span 5 collision/fill levels + 1 broken-structure control (arm set identical
to the landed cell):
- baseline    P_REL=8,  S=1 (K=2048, highest fill).
- keyslots_2x P_REL=16, S=1 (K=4096).   keyslots_4x P_REL=32, S=1 (K=8192).
- shard_2     P_REL=8,  S=2 (eff 4096). shard_4     P_REL=8,  S=4 (eff 8192).
- control     P_REL=32, S=1, objects shuffled -> structure destroyed -> usable ~ 0.  [DISCRIMINATOR-FIRES CTL]
Per non-control arm, per op-point: measured usable_depth (fresh) [MECHANISM]; D*_exact (capture
order statistic) [PREDICTION, the new discriminator]; D*_loose (occupancy-binary
ln(0.5)/ln(1-collision_frac)) [CONTROL/BASELINE, retained, ~2x off].

## The exact formula (parameter-free)
- P_capture(c, mu, D) = E_z[ Phi(z)^(c-1) * Phi(mu+z)^D ], z ~ N(0,1), 64-pt Gauss-Hermite.
  THEORETICAL@order-statistic (Hajek ECE361 L8 / Proakis Ch.4 family); capture effect CITED@
  Roberts 1975 / Arnbak & Van Blitterswijk 1987 IEEE JSAC.
- mu = signal/noise = N/sqrt(M) ~ sqrt(N) ~ 90-128 (SATURATED: distractor factor Phi(mu+z)^D == 1
  to ~1000 decimals -> P_capture reduces EXACTLY to E_z[Phi(z)^(c-1)] = 1/c, the parameter-free
  capture-partial-credit probability). THEORETICAL@substrate physics (bipolar Hebbian factored
  store: signal = self inner-product N; crosstalk variance ~ M edges). D = V_CODE-1 = 511.
- p_hop = E_{c=1+Poisson(fill)}[ P_capture(c, mu, D) ], fill = -ln(1-collision_frac).
- D*_exact = ln(FLOOR=0.5)/ln(p_hop). The loose control uses p_clean = 1-collision_frac instead.
- HONESTY NOTE (for VET): in THIS high-SNR substrate regime the exact order statistic numerically
  coincides with the drill's crude symmetric 1/c capture -- because the distractor competition is
  saturated (>90 sigma), NOT because the two models are the same. The order-statistic derivation
  makes the capture probability parameter-free + rigorous (not asserted) and correctly folds in
  the crosstalk-distractor tail (negligible here, load-bearing at lower SNR). The tightening over
  the LOOSE control is the CAPTURE (partial-credit) physics -- the occupancy-binary model's error
  is treating capture-able collisions as fatal. This is the honest, distinct scientific content.

## Off-disk cheap decisive test (ALREADY RUN; zero new trials; MEASURED@author + in-cell retrospective)
Recomputed vs `data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json:extra.per_op` (in-cell
`_retrospective_offdisk`, gated in --self-test):
- occupancy-binary (loose control): measured/pred mean-ratio 2.00x (systematically >1) [BIASED]
- capture order statistic (exact):   measured/pred mean-ratio 0.99x (scattered around 1)  [UNBIASED]
- n=24 non-censored landed op-points. MEASURED@in-cell selftest RETRO exact=0.993 loose=1.998.
The exact model REMOVES the loose model's systematic +102% under-prediction.

## HP_SCOPE (per-arm gate scope)
- 5 MEASUREMENT arms (baseline, keyslots_*, shard_*): the ratio-error gates (exact vs loose).
- control (shuffled): ONLY the discriminator-fires gate (usable <= HP_CTL_USABLE_MAX=1); NEVER a
  ratio gate (structure destroyed -> no meaningful depth to predict).

## Bands (envelope-fail-bands; aggregate over non-censored, non-control op-points)
Ratio = measured/prediction. Ratio-error(r) = max(r, 1/r) (multiplicative, >=1). Op-point =
(N, N_TEST, arm) aggregated over seeds. CENSORED (measured usable >= D_MAX-0.5) op-points are
EXCLUDED from the ratio gates (reported separately). All bands are DEFLATED above the off-disk
retrospective / smoke MEASURED values (leaves margin for fresh-seed + integer-granularity noise).
- HARD_PASS (promotes reasoning-depth self-prediction to a CG-candidate):
  - exact per-op ratio-error <= HP_RATIO_MAX (1.5x) at ALL non-censored op-points, AND
  - exact aggregate mean-ratio in [HP_BIAS_LO, HP_BIAS_HI] = [0.80, 1.25] (UNBIASED), AND
  - loose control stays biased: loose aggregate mean-ratio >= HP_LOOSE_BIAS_MIN (1.70x) AND loose
    under-predicts at >= HP_LOOSE_DIR_FRAC (0.80) of op-points, AND
  - aggregate relative improvement loose_gm_ratioerr / exact_gm_ratioerr >= REL_IMPROVE_MIN (1.5x), AND
  - cross-seed stability: aggregate CV of per-seed exact ratio-error <= HP_CV_MAX (0.15), AND
  - discriminator-fires: shuffled control usable <= HP_CTL_USABLE_MAX (1) AND base d1 >= 0.80.
- HARD_FAIL (honest ACCEPT-boundary -- reasoning-depth resists exact closed-form self-prediction):
  - exact aggregate mean-ratio OUTSIDE [HF_BIAS_LO, HF_BIAS_HI] = [0.60, 1.70] (exact biased too), OR
  - exact per-op ratio-error > HF_RATIO_MAX (2.0x) at ANY non-censored op-point, OR
  - exact cross-seed CV > HF_CV_MAX (0.25).
- HARD_FAIL_CTL: shuffled control usable > 1. HARD_FAIL_ARMS: baseline bit-identical to an arm (AF).
- DISCRIMINATOR_DID_NOT_FIRE (-> MIDDLE_BAND): loose aggregate mean-ratio < NOFIRE_LOOSE_MIN (1.40x)
  -- the occupancy-binary baseline is not actually loose here; contrast vacuous (respec, NOT a refutation).
- MIDDLE_BAND: exact tightens vs loose but misses a HARD_PASS sub-gate (per-op<=1.5x / CV<=0.15 / bias band).

## SCHEMA-VET mandatory fields
- cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x N x N_TEST. smoke 3x1x1=3; full 5x2x3=30.
  Verdict emits HARD_FAIL_CARDINALITY_BREACH if len(units) != expected. Non-censored-op floor:
  MIN_NONCENSORED smoke>=3 / full>=15 (else MIDDLE_BAND, regime-too-easy).
- arms_differ_verified (AF): true (smoke arms_all_distinct=True; baseline differs from all arms;
  base_differs_from_others gated -> HARD_FAIL_ARMS if violated). exact-pred vs loose-pred are
  distinct closed forms (D*_exact >= D*_loose pointwise, asserted in formula selftest).
- final_metrics_atomicity: tmp_replace (os.replace of metrics.json.tmp).
- except SystemExit: raise BEFORE except Exception (no BaseException; grep-clean, verified).
- crlb/discriminator_reachability: prediction-match test. mu >= MU_SATURATED_MIN=40 on the
  measurement grids {8192,16384} (asserted in formula selftest) -> distractor factor provably ~1,
  exact reduces to parameter-free capture. discriminator_reachability=true: exact per-op
  ratio-error MEASURED off-disk in [0.84,1.23] (all < 1.5x) while loose stays [1.46,2.80]; HP reachable.
- baseline_in_band (AG): prediction-match, not a difficulty baseline. Shuffled control is a
  declared must-collapse CTL (usable ~ 0), exempt. The loose occupancy-binary arm is a live
  CONTROL/BASELINE (~2x off); the exact arm is the MECHANISM. The exact-vs-loose discriminator does
  NOT saturate at scale (the loose bias is a fixed ~2x multiplicative offset, N-independent).
- discriminator survives scale: the exact prediction is a DETERMINISTIC closed form; only measured
  usable_depth carries seed noise. The 2.00x->0.99x closure is already verified against the LANDED
  8192+16384 surface (option B) and re-fires fresh at smoke N=8192 (option A/C preview:
  max_op_err=1.108, cv=0.048). FULL adds N=16384 + N_TEST {24,40}.
- calibration_check: default_ok_for_this_regime -- the exact formula is parameter-free (mu from
  N,M physics; D=V_CODE-1 fixed; 64-pt GH matches the sibling CG cells). NOT tuned-for-PASS.
- sweep_alignment_verdict: ALIGNED (each arm's store literally experiences its declared collision
  fill; the exact predictor consumes each arm's own MEASURED collision_frac_emp).
- discriminating_fraction: >= 0.30 -- MEASURED off-disk exact ratio-error in [0.84,1.23], loose in
  [1.46,2.80]; the discriminating quantity (is-the-2x-bias-removed) is populated at every op-point.
- composition_edges: SHAPE_MATCH (single primitive: factored Hebbian retrieve -> argmax cleanup ->
  carry; the prediction is a downstream closed form, not a composed primitive).
- positive_control_arms (Gate D): the measurement machinery IS the landed reasoning cell's, reused
  VERBATIM; the fresh baseline reproduces the collision-bound depth curve (d1>=0.80, graceful
  decay) at the SAME regime (V=512/V_CHAIN=256/P=8). MEASURED smoke base d1 0.812-0.906 in band.
  regime_extension_audit: SHAPE_MATCH (identical scaffold). In-cell off-disk retrospective
  reproduces the landed loose-2.00x / exact-0.99x split (optional; skipped gracefully if landed
  metrics absent on remote -- they are NOT git-committed, so remote relies on the FRESH re-measurement).
- functional_requirements: (1) store N chains recallably [factored Hebbian store]; (2) walk a chain
  regeneratively [argmax cleanup + clean-codeword carry]; (3) predict per-hop success [capture order
  statistic]; (4) compose across depth [series-reliability D*=ln(0.5)/ln(p_hop)].
- progress_logging: line_buffered_stdout + print(flush=True) on every progress line (timeout_s>=1800).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true. cell_chunked: false
  (per-seed checkpoint via resumable_seeds -> a timeout resumes at seed granularity).
- defensive_error_checking: passed_all_4_patterns.
- run_mode: defaults to full (bare/runner HDLAB_RUN_MODE=full); --smoke / --self-test flip. Cell
  asserts written run_mode == mode (§16 RUN_MODE verification via the runner + author post-ship check).

## Compute architecture
SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 -- genuine chained-retrieval dependency
exemption) + the cell IS the substrate cleanup primitive being validated. Storage = MIXED
(bundled-Hebbian per shard; sharding is a swept fill axis per META_STORAGE_STRATEGY exemption (b)).
Factored store (no NxN materialization), M-chunked numpy matmul. The prediction arm is numpy
Gauss-Hermite quadrature (deterministic; no GPU, no scipy, no torch, no LLM). Self-contained
(synthetic chains; no pool/re-encode/cert_ledger dependency -> clean remote gate, NON-PARKED).

## SMOKE RESULT (local, N=8192, N_TEST=32, seeds 7/13/19, D_MAX=18)
HARD_PASS (clears even the FULL-canonical bars). MEASURED@data/exp_reasoning_depth_exact_order_statistic_self_margin_v1_smoke/metrics.json:
- EXACT mean_ratio=1.029 (UNBIASED, in [0.80,1.25]); max per-op ratio-error=1.108x (< 1.5x CG bar).
- LOOSE mean_ratio=2.031 (BIASED; under-predicts at 100% of op-points); exact gm_err=1.076 vs
  loose gm_err=2.014 -> rel_improve=1.87x (>= 1.5x).
- cross_seed_cv=0.048 (<< 0.15); ctl_usable_max=0 (shuffled control at chance -> discriminator
  fires); base_d1_min=0.812 (single-hop store works); arms_distinct=True.
- 4 non-censored + 1 censored op-point (keyslots_4x censored at NT=32; un-censored at NT=24/40 in FULL).
Per-seed exact/loose ratios: baseline 1.06/2.18, 1.07/2.20, 1.04/2.14; shard_4 1.00C/1.72C, 0.94/1.54, 0.78/1.56.

## FULL grid (staged; remote_cpu_queue -- SMOKE-only-local rule; exp_dev CANNOT push -> Orchestrator dispatches)
N in {8192,16384} (N-independence confirm); N_TEST in {24,32,40} (NT=40 un-censors the 4x arms for
more non-censored op-points; NT=24 gives the highest-depth baseline op-points); seeds {7,13,19,23,29}
(fresh; RNS v2 / FHRR v1 CG precedent; distinct from landed {7,17,23,31,41} -> independent
re-measurement). EXPECTED_N_UNITS=30. run_mode=full.
timeout: landed twin took 2430s (486s/seed, 5 seeds) on laptop; remote CPU may be slower; per-seed
checkpointed so a timeout resumes. recommend --timeout 9000 (2.5h).
