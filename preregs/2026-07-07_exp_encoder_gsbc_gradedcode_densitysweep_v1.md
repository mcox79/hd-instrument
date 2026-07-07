# Pre-registration: exp_encoder_gsbc_gradedcode_densitysweep_v1

Date: 2026-07-07. Owner: exp_dev. Arc: encoder retrieval density-axis CHARACTERIZATION
(finer-resolution continuation of landed exp_encoder_gsbc_gradedcode_marginpush_v1).

## One-line
Locate the ACTUAL retrieval peak on the GSBC density axis (m*, activefrac = m/128) and
characterize plateau-vs-spike shape + map the cliff, by infilling the coarse 3-point
{3,5,8} marginpush grid to 8 points {3,4,5,6,7,8,10,12}. This is a PARAMETER CHANGE on
the density dial (GRADED_M_SWEEP), NOT new machinery: m is a first-class arg of
v11._train_student_v11 / _gsbc_code_from_z (reused VERBATIM from the landed HARD_PASS
code path).

## Motivation (MEASURED off-disk, landed marginpush 3-point grid)
We have only 3 density points and do NOT know where the retrieval max is:
- m=3: cross-seed graded ret_agree10 min 0.2568 (seed13) / 0.3116-0.3681 -> below/at bar
  MEASURED@data/exp_encoder_gsbc_gradedcode_marginpush_v1_seed13/metrics.json (landed)
- m=5: shipped (denser lifts ret; the 970K Marchenko-Pastur forecast named density as THE
  lever) MEASURED@data/exp_encoder_gsbc_gradedcode_marginpush_v1_seed{7,13,19}
- m=8: cliff-onset (cv-explosion across seeds = the density cliff signal)
The peak lies somewhere in [5,8] and the cliff far side is unmapped. Infill {4,6,7}
brackets the peak; {10,12} maps degradation past the cliff.

## Prior-work check (USER-locked concept-query, filesystem-verify Fix#28)
substrate_query.sh "encoder retrieval density sweep graded block code peak plateau cliff"
-> top-5 hits ALL cosine <= 0.2373 (generic wordnet 'retrieval'/'code' + retrieval-aug lit
chunks); NONE at cosine > 0.30. This is a CONTINUATION of the landed marginpush/gradedcode
density-dial arc (same lever, finer resolution), NOT a novel rediscovery -- confirmed on disk.

## Design
- Density grid (GRADED_M_SWEEP): m in {3,4,5,6,7,8,10,12}; activefrac = m/128 =
  {0.0234,0.0313,0.0391,0.0469,0.0547,0.0625,0.0781,0.0938}. blk_l=128, kb=32 FIXED
  (kb*blk_l = N_DIM = 4096; m changes only survivors-per-block, not geometry). 9 trained
  students/seed (1 hard-STE baseline + 8 graded m). m=3 retained as landed-baseline +
  Gate-D regime-reproducer + shuffled-GRADED control anchor.
- Seeds: 7,13,19 (the marginpush comparability triple) for direct cross-seed comparison.
  Trimmed from the 5-seed marginpush set (dropped 23,29) to fit the ~1hr GPU window; 3
  seeds keep the cross-seed MIN + cv (the cliff = cv-explosion) meaningful per m.
- Per-m emitted curve: graded ret_agree10, hi80 cosine_to_gold, composed_roundtrip@J10,
  isolated@J5, calib_err, spearman, joint_ok, near-dup concentration -> full per-m table
  in seed_ship_row so the peak + plateau/spike + cliff are readable and VET computes the
  cross-seed FIXED-m min WITHOUT cherry-picking m per seed.

## Nature of this cell: CHARACTERIZATION, not pass/fail ship
This maps m*(177K) + the boundary; the ship gate is inherited from marginpush (reported per
FIXED m* by VET) but the PRIMARY deliverable is the SHAPE of the curve. Registered "clean
result" vs "ragged":
- CLEAN (expected if density is a well-behaved dial): a single resolved interior peak OR a
  monotone-rising-then-plateau, with the cliff (joint-gate break or ret collapse) at a
  RESOLVED single m; cross-seed cv stays low (< ~0.15) on the plateau and JUMPS at the
  cliff m (reproducing the m=8 cv-explosion signal at higher resolution).
- RAGGED / inconclusive: multi-modal or non-monotone curve with no resolved peak, OR cv
  high across ALL m (no localizable cliff) -> density is not a clean single-axis dial at
  this corpus; report honestly, do not fit a spurious peak.
Ship-band inheritance (for VET's FIXED-m* ship call): HARD-PASS at a FIXED m* iff EVERY
seed graded ret_agree10 >= 0.30 WITH the joint gate each seed (hi80 cos >= 0.80 AND
composed_rt@J10 >= 0.95); MIDDLE if best fixed m* in [0.28,0.30) with joint; margin bought
by wrecking algebra/calibration = FALSE PASS.

## Firing controls
shuffled-key leak <= 0.05 BOTH algebras (SMOKE: HARD 0.000 / GRADED 0.000); RANDOM-code
keyed roundtrip >= 0.98 BOTH algebras (SMOKE: 1.000 / 1.000 -- bind/unbind lossless
independent of the density param); arms-differ sha256 over float32 codes of HARD + 8
graded-m + CHARPOS + 2 RANDOMs all distinct (SMOKE: no META_RULE_AF violation).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = 8 + 3*len(GRADED_M_SWEEP) = 32 (DERIVED from grid,
  not hardcoded); verdict counts len(per_unit); SMOKE emitted 32/32.
- arms_differ_verified: True (float32 code sha256; graded fractional; smoke clean).
- final_metrics_atomicity: tmp_replace (inherited from core).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare) -- grep-gated clean.
- crlb_floor_computed: 0.901 (THEORETICAL r_max block channel, inherited); discriminator
  reachability: True (0.30 characterization bar far below MEASURED@ landed v12 denser 0.6027).
- baseline_in_band: CHARPOS ret_agree10 = 0.11 in (0.05,0.95) (SMOKE).
- HP_SCOPE: {GRADED_m*: [ret_agree10, cosine_to_gold, composed_roundtrip]}; HARD_STE +
  CHARPOS + RANDOM_* integrity-only.
- calibration_check: default_ok_for_this_regime (identical hyperparameters to landed
  v11/v1/marginpush; ONLY the density grid changed; no new eval machinery).
- sweep_alignment_verdict: ALIGNED (m is the exact param the graded code experiences; no
  nominal-vs-effective gap). effective density = m/blk_l per arm.
- discriminating_fraction: ~1.0 (landed m3 0.257-0.368; denser forecast higher, v12
  denser 0.6027; all 8 grid points forecast in the discriminating band or above).
- positive_control_arms: GRADED_m3 reproduces the landed marginpush m=3 code path at the
  test regime (Gate D); REGIME_REPRO_WARN (not hard-fail) if |m3_here - landed| > 0.06.
- cell_chunked: True (single-seed-per-cell; sibling _dense wrappers seed_{7,13,19}).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True (inherited core).
- progress_logging: print_flush_true (timeout_s >= 1800 -> mandatory; line_buffered + flush).
- defensive_error_checking: passed_all_4_patterns (inherited core; per-unit failure-class).

## Compute architecture
Class (c) mixed: GPU-batched substrate primitives + student training (matmul-heavy; device
auto -> cuda on the GPU box) + a bounded CPU-side per-item near-dup tagging pass on ~17790
held names (seconds). Storage: no composition-store (retrieval-fidelity eval); no
bundled-vs-sharded axis. GPU dispatch to overnight_queue. 9 students/seed vs 4 in
marginpush (~2.1x arm+eval work); landed marginpush FULL = 460-575s/seed for 4 students ->
projected ~1000s/seed for 9 students; 3 seeds ~ 50min sequential (fits ~1hr GPU window);
timeout 3600s/seed (generous ceiling).

## DISCRIMINATOR-SURVIVES-SCALE (option B analytical + prior-landed)
The trained ret-agreement MARGIN + the DENSITY CLIFF are FULL-only phenomena. SMOKE
(V=3000/200-steps/width-256, max_block 727) does not crystallize the trained margin and is
too small to exercise the cliff -- the smoke curve rises monotone m3=0.465 -> m12=0.716
with NO cliff, which is EXPECTED and is precisely why FULL on the 177K-name corpus is
required to locate the real peak + cliff. Smoke validates machinery (all 9 arms train,
codes differ, algebra pos-ctrl BOTH, shuffled leak 0) + fires the near-dup discriminator.
Margin survives scale: MEASURED@ landed v12 denser 0.6027; landed marginpush m=3 0.2568-0.3681.

## Smoke result (seed7_dense, local CPU, 2026-07-07)
HARD_PASS machinery: 9 arms trained with distinct codes; cardinality 32/32; RANDOM_HARD /
RANDOM_GRADED keyed 1.000/1.000; shuffled leak HARD 0.000 / GRADED 0.000; CHARPOS
ret_agree10 0.11 in-band; near-dup discriminator fired (partition + projected finite all m).
Directional-only (SMOKE, not predictive): ret rises m3=0.465,m4=0.518,m5=0.571,m6=0.603,
m7=0.615,m8=0.633,m10=0.683,m12=0.716. REGIME_REPRO_WARN (m3 0.465 vs landed 0.311, dev
0.153) EXPECTED = smoke small-vocab/200-steps, neardup=0.91 small-vocab artifact. FULL on
17790 diverse held names + full training gives the real peak/plateau/cliff.
Formula self-test: PASS (anneal + graded density-sweep invariants m in [3,4,5,6,7,8,10,12]
+ hard one-per-block + BOTH-algebra roundtrip + shuffled-leak + near-dup/polysemy + concen-
tration + projected-if-dedup + verdict bands HP/MB/HF/integrity/smoke), 0.68s, exit 0.

## Seeds / dispatch
Seeds 7,13,19 (comparability). Chunked single-seed-per-cell (_dense wrappers). FULL ->
overnight_queue (GPU). HELD (reuse committed 177899-name teacher cache; NO re-encode).
timeout 3600s/seed. Post-ship verify referent landed (exit 5 = ship FAIL). Output isolated
under data/exp_encoder_gsbc_gradedcode_marginpush_v1_seed{7,13,19}_dense/ -- landed 3-point
marginpush metrics NOT clobbered.

## On landing
VET: (1) locate m* (the interior peak or plateau-onset) from the cross-seed per-m curve;
(2) characterize plateau-vs-spike (is the peak a broad plateau or a sharp single-m spike?);
(3) map the cliff (which m does the joint gate break / ret collapse / cv explode?); (4) at
the resolved m*, does cross-seed min graded ret_agree10 clear 0.30 with the joint gate?
