# Pre-registration: reader DECISIVE-WIN multi-hop chaining (threshold-crossing, ambition-first)

- Anchor: `grounding_multihop_decisive_win_v1`
- Cell: `experiments/exp_grounding_multihop_decisive_win_v1.py`
- Date: 2026-07-09
- Track: Stage-5 reader / grounding multi-hop chaining WIN-engineering (successor to Stage-4
  `grounding_multihop_perhop_cleanup_gate_v1`, MIDDLE_BAND).
- Source drill: `notes/research_reader_decisive_multihop_win_engineering_2026-07-09.md`
- Framing: WIN-designed (ambition-first), NOT floor-clearing. The brain is an existence proof, not a
  ceiling; this cell throws dimension / cleanup-architecture / redundancy a ~20W brain cannot. Claims stay
  honest: real correlated ConceptNet learned codes; hit@K fidelity; NO language understanding claimed.
- Prior-work check (substrate KB, cosine): top hits `capability_implication_modern_hopfield_upgrade_path_
  2026-06-04` (cos 0.319), `research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_
  2026-06-12` (0.318, Ramsauer/sparse-Hopfield), `research_drill_substrate_training_n_threshold_3x` (0.312).
  The dense/modern-Hopfield exponential-capacity CLEANUP lever is a KNOWN substrate upgrade path (partial
  rediscovery). NOVEL here: its composition with the path-as-single-bound-object chaining primitive on REAL
  correlated multi-hop ConceptNet chains + the capacity-threshold-crossing diagnosis. Reported as such.

## Question

Stage-4's per-hop cleanup added a flat per-hop boost but did NOT change the decay SLOPE (PLAIN slope
-0.1289 vs NO_CLEANUP -0.1283, MEASURED@data/exp_grounding_multihop_perhop_cleanup_gate_v1/metrics.json:
gates.decay_slope). That is the signature of operating ABOVE the capacity-correction threshold, where
error-correction only adds a constant offset and cannot flatten the exponential collapse (THEORETICAL,
three converging literatures per source drill). Does throwing resource the brain cannot afford
(exponential-capacity dense-Hopfield cleanup + a path-as-object chaining primitive whose noise is
linear-in-length + 8x retrieval dimension + K=5 voted redundancy) CROSS below the threshold so multi-hop
chaining SNAPS to working?

## Arms (7; PAIRED: identical planted chains + identical seeds per model-seed; codes differ BY DESIGN --
code dimension / cleanup architecture IS the lever). Each single-lever arm changes exactly ONE thing from
PLAIN_CLEANUP; the COMBINED arms stack levers.

- `NO_CLEANUP` (MUST-FAIL control): raw HRR accumulation, global readout, dim=base. Anti-saturation gate:
  MUST collapse at reach>=2 (SMOKE MEASURED @2=0.038 <= 0.40 abs AND <= 0.5x@1=0.444 -> collapses=True).
- `PLAIN_CLEANUP` (CALIBRATION ANCHOR / marginal reference): top-1 argmax snap, dim=base. At FULL must
  reproduce Stage-4 fid2 (0.106 MEASURED@stage4 metrics gates.fid_mean.PLAIN_CLEANUP.2) within CALIB_TOL=0.06.
- `DENSE_HOPFIELD`: per-hop cleanup readout = dense/modern-Hopfield softmax attractor pass to convergence
  (beta=25, n_iter=3), dim=base. Lever = CLEANUP ARCHITECTURE (exponential vs linear capacity). CITED@
  arXiv:2503.00241 / notes/capability_implication_modern_hopfield_upgrade_path_2026-06-04.
- `N_SCALE`: PLAIN snap at 8x retrieval dimension (dim=8*base). Lever = RESOURCE-THROW / threshold-cross.
- `PATH_AS_OBJECT`: compose the whole path (no intermediate commit -> DEFER), decode ONCE via a dense
  attractor pass, dim = MAX_REACH*base (linear-in-length budget). Lever = CHAINING PRIMITIVE.
- `COMBINED_WIN`: path-object composition + dense attractor readout at 8x dim. Levers stacked.
- `COMBINED_WIN_VOTED`: COMBINED_WIN + K=5 independent random sub-codebook projections, score-ensembled
  (soft majority vote). Full resource stack. CITED@repetition-code majority-vote theory.

`arms_differ_verified: true` (smoke: no <2-distinct warning; WIN arms asserted distinct from NO_CLEANUP by
hash at run time -> RuntimeError if identical). `arms_differ_exempted: []`.

## HONEST-RISK arm: D_f/N crosstalk pre-diagnostic (load-bearing)

(a) THEORETICAL closed-form crosstalk-load ratio `n_nodes/code_dim` vs resonator stability threshold ~0.056
(CITED@arXiv:1906.11684) and classical Hopfield alpha_c ~0.138. Reports above/below threshold + the
code_dim needed to cross by the naive full-codebook bound. NOTE (honest): the naive full-codebook ratio is
PESSIMISTIC (effective per-hop competition << full codebook because the BIND directs to a small candidate
region); reported plainly, not over-interpreted.
(b) MEASURED empirical incidental-vs-aliasing decomposition at hop-2 (conditioned on hop-1 correct): of the
hop-2 misses, `aliasing_frac` = fraction that retrieve a genuine graph-neighbour of the true midpoint
(SEMANTIC ALIASING -> resource cannot escape; ceiling is representation quality = CRITICAL redirect finding)
vs an unrelated node (INCIDENTAL crosstalk -> resource-throw escapes). `aliasing_frac>=0.50` = aliasing;
`<=0.30` = incidental; between = MIXED. This decides whether the WIN is reachable at all.

## Discriminator bands (author-picked BEFORE running FULL; both bands)

WIN gate (HP_SCOPE below). WIN reported per-arm; verdict HARD_PASS_WIN if ANY WIN-eligible arm meets ALL:
- `reach2 >= 0.60` (WIN_REACH2) -- usable, not merely detectable. (Stage-4 missed a 0.212 floor.)
- `reach3 >= 0.35` (WIN_REACH3) -- material chainable signal.
- `gain2 = arm@2 - NO_CLEANUP@2 >= 0.30` absolute (WIN_GAIN2) -- decisive multiple of Stage-4's 0.10 bar.
- `slope_flatten = 1 - |slope_arm|/|slope_NO_CLEANUP| >= 0.40` (WIN_SLOPE_FLATTEN) -- direct evidence of
  crossing the correction threshold (Stage-4's slope was UNCHANGED).

HARD_FAIL_CEILING_FUNDAMENTAL if ALL MAXIMAL arms {N_SCALE, COMBINED_WIN, COMBINED_WIN_VOTED} have
`reach2 < 0.15` (FAIL_REACH2) AND `slope_flatten < 0.10` (FAIL_SLOPE_FLATTEN) -- no crossing even at max
resource -> the correlated-codebook capacity ceiling is representation-fundamental (semantic-aliasing);
redirect roadmap to hierarchical chunking / landmark-hub. This is GOLD, not a loss.

MIDDLE_BAND_PARTIAL_CROSSING otherwise (partial crossing; some arm above FAIL but none meets WIN).

Gating preconditions (else INCONCLUSIVE): `hop1_ok` (NO_CLEANUP@1 >= 0.30) AND `baseline_collapses`
(NO_CLEANUP@2 <= 0.40 AND <= 0.5x@1). At FULL, `HARD_FAIL_HARNESS_DRIFT_CALIBRATION` if PLAIN@2 deviates
from Stage-4's 0.106 by > 0.06.

Prediction sub-verdicts (for research; reported, not gated): P1 N_SCALE gain2 >= 2x PLAIN gain2 (super-linear
threshold signature); P2 DENSE@2 - PLAIN@2 >= 0.15; P3 PATH@2 >= 0.50; P4 VOTED@2 - COMBINED@2 >= 0.10.

## SMOKE RESULT (provisional, VERDICT ONLY -- mechanism-story HELD until landed-VET)

MEASURED@data/exp_grounding_multihop_decisive_win_v1_smoke/metrics.json (2 seeds, n=1525, dim_base=128,
dim_scale=1024, cpu, 19.9s): verdict MIDDLE_BAND_PARTIAL_CROSSING. NO_CLEANUP@2=0.038 collapses=True
(must-fail fires; NOT saturation-vacuous). best_win=N_SCALE @2=0.272 (gain2~0.234). No arm crosses
reach2>=0.60 (EXPECTED at smoke's small dim per analytical justification B). aliasing_frac=0.332 -> MIXED
(leans incidental; ~2/3 of hop-2 errors are unrelated nodes -> resource-throw has room to escape; provisional
small-scale). P1=True (N_SCALE super-linear vs PLAIN), P2/P3/P4=False at smoke dim.

## SCHEMA-VET fields

- `cardinality_ok: true`. EXPECTED_N_UNITS = n_seeds (FULL=3). Each seed asserts all 7 arms x 4 depths
  present (ARM_DEPTH_CARDINALITY_BREACH else). < expected seeds -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- `final_metrics_atomicity: tmp_replace` (via `_seed_checkpoint.write_metrics` + os.replace; crash path atomic).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException, no bare except; grep-clean MEASURED).
- `crlb`: hit@K chance floor = K/n_nodes ~0.002 at n=5000,K=10; WIN floor 0.60 >> chance and reachable in
  principle (crosstalk floor sqrt(2 ln n / d) drops with thrown dim d). `discriminator_reachability: true`.
  `crlb_n/a` for the recovery gain (empirical baseline-collapse gate, not a closed-form estimator).
- `baseline_in_band: true` (NO_CLEANUP@1=0.444 in (0.05,0.95); @2 collapses; MEASURED smoke).
- `calibration_check: adaptive_with_discriminator_gate` (baseline-collapse recomputed empirically per run;
  PLAIN calibration anchor vs Stage-4 0.106 at FULL; paired per-chain hits -> all deltas paired).
- `HP_SCOPE`: WIN gate eligible = {DENSE_HOPFIELD, N_SCALE, PATH_AS_OBJECT, COMBINED_WIN, COMBINED_WIN_VOTED}
  (any lever may cross; attribution arms name WHICH). EXCLUDED: NO_CLEANUP (must-fail control), PLAIN_CLEANUP
  (calibration/marginal reference). Ceiling-fundamental judged on MAXIMAL = {N_SCALE, COMBINED_WIN,
  COMBINED_WIN_VOTED}.
- Gate A `sweep_alignment_verdict: ALIGNED` (sweep axis = hop depth d in 1..4; every arm decodes at each
  depth d against the FULL codebook; effective competitor set is the same n_nodes for all arms; the dimension
  differs by arm BY DESIGN as the lever, not a hidden misalignment).
- Gate B `discriminating_fraction`: n/a as a saturation bracket -- this is an arm-comparison discriminator, not
  a sweep-point accuracy bracket. The anti-saturation guard is the must-fail control failing at smoke scale
  (MEASURED NO_CLEANUP@2=0.038). discriminating axis (depth) spans collapse (@2..4) not saturation.
- Gate C `composition_edges`: bind(role, code) -> [C,d] matches dense/plain/vote readout input [C,d]
  (SHAPE_MATCH); dense attractor q [C,d] -> argmax snap -> Z[est] [C,d] carry (SHAPE_MATCH); path defer carry
  = raw pred [C,d] (SHAPE_MATCH); vote sub-projection [C,sub] internal, aggregated score [C,n] (SHAPE_MATCH).
  No SHAPE_MISMATCH_no_adapter.
- Gate D `positive_control_arms`: PLAIN_CLEANUP reproduces Stage-4 primitive at test regime; cited prior metric
  0.106 (fid2 FULL), tolerance 0.06, if outside -> HARD_FAIL_HARNESS_DRIFT_CALIBRATION. Regime-extension:
  SAME encoder/graph/loader imported VERBATIM from the Stage-4 cell (no regime drift).
- Gate E `functional_requirements`: (1) single-hop retrieval on correlated codes -> BIND + InfoNCE encoder
  (reused). (2) multi-hop carry without crosstalk compounding -> per-hop cleanup (snap / dense attractor /
  defer). (3) exponential-capacity cleanup -> dense/modern-Hopfield. (4) linear-in-length noise -> path-object
  compose-once. (5) incidental-noise suppression -> voted redundancy. (6) escape-vs-ceiling discriminator ->
  aliasing decomposition.
- `cell_chunked: false` (multi-seed loop within one cell WITH per-seed try/except failure-class + write_partial
  per seed; seed loss is isolated, not chunked-file). `start_marker_written: true`. `crash_diagnostic_present:
  true`. `heartbeat_present: true` (emit_heartbeat during encoder training). `defensive_error_checking:
  passed_all_4_patterns`.
- `progress_logging: print_flush_true` (line-buffered stdout + per-epoch/per-arm/per-seed flush prints +
  heartbeat). Required as FULL timeout_s >= 1800.

## Compute architecture

- Class: `(a) batched-GPU`. Substrate primitives (bind = elementwise FFT-mul, cleanup = matmul + softmax/argmax,
  dense-Hopfield iterate = matmul, sub-projection vote = matmul) are matmul-heavy and device-aware torch (cuda
  if available). Per-hop is a genuine sequential dependency (hop N carry depends on hop N-1 snap) but that is
  the mechanism under test, and each hop's per-chain work IS batched over all C chains at once. Encoder train
  is batched GD on GPU.
- Storage strategy: `sharded` (each node its own code vector; retrieval = matmul vs the [n,d] codebook; no
  bundled superposition). Compositional cell -> sharded default honored.
- Wall-time: Stage-4 FULL ran 17.5s on cuda; this cell trains 3 encoders/seed + 7 arms + vote, MEASURED smoke
  19.9s on CPU at reduced scale. FULL on GPU expected << timeout. Timeout 1800s with wide headroom.

## Dispatch

- Target queue: `overnight_queue` (GPU; gpu_runner_0). Heavier than Stage-4 (3 encoders/seed, dim up to 2048,
  dense iterate, K=5 vote) -> GPU, off the busy cpu_runner_0. Timeout 1800s.
- Numbers tagged: MEASURED@ (smoke/stage4 disk), THEORETICAL@ (crosstalk floor, chance), CITED@ (Hopfield /
  resonator / repetition-code literature). No untagged quantitative claims.
