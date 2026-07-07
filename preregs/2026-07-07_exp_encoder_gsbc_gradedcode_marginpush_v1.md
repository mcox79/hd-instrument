# Pre-registration: exp_encoder_gsbc_gradedcode_marginpush_v1

Date: 2026-07-07. Owner: exp_dev. Arc: encoder retrieval margin-push (continuation
of landed exp_encoder_gsbc_gradedcode_retrieval_v1).

## One-line
Lift graded-GSBC retrieval agreement (ret_agree10) to per-seed-robust past the 0.30
ingest bar via the GSBC DENSITY DIAL (top-m survivors per block), and persist
per-item near-dup-tagged retrieval logging to answer the dedup question.

## Situation (MEASURED off-disk, landed v1)
- seed7  graded ret_agree10 = 0.3116  HARD_PASS
  MEASURED@data/exp_encoder_gsbc_gradedcode_retrieval_v1_seed7/metrics.json:ship.graded_ret_agree10
- seed13 graded ret_agree10 = 0.2568  MIDDLE_BAND (BELOW 0.30 bar)
  MEASURED@data/exp_encoder_gsbc_gradedcode_retrieval_v1_seed13/metrics.json:ship.graded_ret_agree10
- seed19 graded ret_agree10 = 0.3681  HARD_PASS
  MEASURED@data/exp_encoder_gsbc_gradedcode_retrieval_v1_seed19/metrics.json:ship.graded_ret_agree10
- mean=0.3122 (clears 0.30 by +0.012); min=0.2568 (below bar). Mechanism robust
  (graded beats hard-block on all seeds), absolute per-seed margin not cleared.

## Prior-work check (USER-locked concept-query, filesystem-verify Fix#28)
substrate_query.sh "GSBC graded code density dial top-m survivors per block sparsity
retrieval agreement margin per-seed robustness near-duplicate concentration" ->
top-5 hits ALL cosine <= 0.2656 (Hersche block-sparse lit-scan chunk + failure-mode
catalog); NONE at cosine > 0.30. This cell is a MARGIN-PUSH CONTINUATION of the
landed v1 arc (same density-dial lever), NOT a novel rediscovery -- confirmed on disk.

## Levers (combined in one cell)
1. DENSITY DIAL SWEEP: graded m in {3 (landed baseline), 5, 8}; density = m/blk_l =
   {0.0234, 0.0391, 0.0625}. blk_l=128, kb=32 FIXED (kb*blk_l = N_DIM = 4096; m
   changes only survivors, not geometry). REUSES v11._train_student_v11 +
   _gsbc_code_from_z VERBATIM (landed HARD_PASS code path); m is a first-class
   parameter of both -> NO monkeypatch. Named by the 970K Marchenko-Pastur forecast
   as THE lever + the one Donoho-Tanner cliff risk. v12 GSBC_EXPAND2X (denser) hit
   ret_agree10=0.6027 seed7 (MEASURED@data/exp_encoder_v12_gsbc_gwta_expansion_v1_seed7)
   -> denser lifts retrieval well past 0.30; discriminator has headroom.
2. PER-ITEM NEAR-DUP-TAGGED RETRIEVAL LOGGING: per-held-item ret_agree10 (self-masked
   top-10 overlap /10) tagged by (a) name-level near-dup (char-4gram Jaccard >= 0.60,
   first-token-blocked = Test-0 methodology, a LOWER BOUND) and (b) surface-form
   polysemy (normalized-name collision). Emits concentration summary: miss-rate + mean
   ret_agree10 in near-dup pool vs clean remainder + projected_ret_agree10_if_dedup.
   NOTE: this held set = 177899 concept NAMES (ConceptNet + math/science), a DIFFERENT
   corpus than the 970K dogfood chunk pool in Test-0; these are the name-level analogs.

## PRE-REGISTERED BANDS (both, before running)
Ship gate is CROSS-SEED at a FIXED m*, assembled by landed-VET across all seed metrics
(each per-seed cell emits the full per-m table + seed_ship_row so VET computes the
cross-seed FIXED-m min WITHOUT cherry-picking m per seed).
- HARD-PASS (ship bar): at a single FIXED density m*, EVERY seed graded ret_agree10
  >= 0.30 WHILE the JOINT gate holds each seed (graded cosine_to_gold(hi80) >= 0.80
  AND composed_roundtrip@J10 >= 0.95). SECONDARY: at fixed m*, mean >= 0.33 AND min
  >= 0.28 with joint gate. (Margin bought by wrecking algebra/calibration = FALSE PASS.)
- HARD-FAIL: no fixed m* (incl denser m=5,8) lifts the cross-seed min above the landed
  min (0.2568) with joint gate -> graded-code density approach hit a retrieval-agreement
  CEILING; retrieval needs a different mechanism. Report honestly; do NOT force a pass.
- MIDDLE: cross-seed min at best fixed m* in [0.28,0.30) with joint gate, OR a denser m
  clears margin but breaks joint gate (density cliff manifests as algebra/calibration cost).
Per-seed cell verdict is INFORMATIONAL (did density dial help AT THIS SEED).

## Firing controls (both modes)
shuffled-key leak <= 0.05 BOTH algebras; RANDOM-code keyed roundtrip >= 0.98 BOTH
algebras (bind/unbind lossless independent of training); arms-differ (sha256 over
float32 codes of HARD + 3 graded-m + CHARPOS + 2 RANDOMs, all distinct).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = 17 (5 semantic + 12 keyed); verdict counts per_unit.
- arms_differ_verified: True (float32 code sha256; graded fractional, not int8).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException / bare) -- grep-gated clean.
- crlb_floor_computed: 0.901 (THEORETICAL, r_max block channel); discriminator_reachability:
  True (0.30 bar far below MEASURED@ landed v12 denser 0.6027).
- baseline_in_band: CHARPOS ret_agree10 in (0.05,0.95).
- HP_SCOPE: {GRADED_m*: [ret_agree10, cosine_to_gold, composed_roundtrip]}; HARD_STE +
  CHARPOS + RANDOM_* integrity-only.
- calibration_check: default_ok_for_this_regime (identical hyperparameters to landed
  v11/v1; only m swept + eval adds per-item near-dup logging).
- sweep_alignment_verdict: ALIGNED (m is the exact parameter the graded code
  experiences; no nominal-vs-effective gap). effective density = m/blk_l per arm.
- discriminating_fraction: m-sweep predicted >= 0.30 of points in the discriminating
  band [0.30,0.70] -- landed m=3 at 0.257-0.368; denser m=5,8 forecast higher (v12
  denser 0.6027); all 3 points forecast in-band -> discriminating_fraction ~ 1.0.
- positive_control_arms: GRADED_m3 reproduces the landed v1 m=3 code path at the test
  regime (Gate D). REGIME_REPRO_WARN flagged (not hard-fail) if |m3_here - landed| >
  0.06 for seeds 7/13/19. RANDOM_HARD/RANDOM_GRADED keyed reproduce lossless algebra.
- cell_chunked: True (single-seed-per-cell; sibling wrappers seed_{7,13,19,23,29}).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: print_flush_true (timeout_s >= 1800 -> mandatory; satisfied).
- defensive_error_checking: passed_all_4_patterns.

## Compute architecture
Class (c) mixed: GPU-batched substrate primitives + student training (matmul-heavy;
device auto -> cuda on GPU box) + a bounded CPU-side per-item near-dup tagging pass
(first-token-blocked char-4gram Jaccard on ~17790 held names, seconds). Storage: no
composition-store (retrieval-fidelity eval); no bundled-vs-sharded axis. GPU dispatch
to overnight_queue.

## DISCRIMINATOR-SURVIVES-SCALE (option B analytical + prior-landed)
Trained ret-agreement MARGIN is FULL-only (smoke V=3000/200-steps/width-256 does not
crystallize; same precedent as v1/v11/v12). Smoke validates machinery (all 4 arms
train, codes differ, algebra pos-ctrl BOTH algebras, shuffled leak) + fires the NEW
per-item near-dup discriminator (partition + projected finite). Margin survives scale:
MEASURED@ landed v12 denser 0.6027; landed v1 m=3 already 0.2568-0.3681.

## Smoke result (seed7, local CPU, 2026-07-07)
HARD_PASS machinery: 4 arms trained with distinct codes; RANDOM_HARD/RANDOM_GRADED
keyed 1.000; shuffled leak HARD 0.000 / GRADED 0.000; cardinality 17/17; CHARPOS
ret_agree10 0.11 in-band; near-dup discriminator fired (partition + projected finite
all m). Directional (SMOKE-ONLY, not predictive): m3=0.465 m5=0.571 m8=0.633 (density
dial moves ret_agree10 up, consistent with v12). REGIME_REPRO_WARN expected (smoke
tiny cache / 200 steps). neardup=0.91 is a smoke small-vocab artifact (max_block 727
of 800); FULL 17790 diverse names give the real measurement.

## Seeds / dispatch
Seeds 7,13,19 (comparability) + 23,29 (per-seed-robustness power) = 5. Chunked
single-seed-per-cell. FULL -> overnight_queue (GPU). HELD (reuse committed 177899
teacher cache; no re-encode). timeout 3600s/seed. Post-ship verify (exit 5 = ship FAIL).

## On landing
XHIGH skunkworks VET: (1) at a FIXED m*, does cross-seed min graded ret_agree10 clear
0.30 with joint gate each seed? (2) is the retrieval miss concentrated in the dedupable
(near-dup / polysemy) pool -> does projected_ret_agree10_if_dedup lift the margin?
