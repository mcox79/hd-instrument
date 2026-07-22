# Pre-reg: reader_perception_meaning_grounding_sharded_v1

Date: 2026-07-22
Author: exp_dev (cell author)
Cell: `experiments/exp_reader_perception_meaning_grounding_sharded_v1.py`
Local-only viability probe. No push, no remote-persist, no atom banking.

## Question (single-variable viability probe, not a build)

Does replacing the ADDITIVE-superposition bind store with a per-class SHARDED store recover the
perception-meaning GROUNDING LIFT that was lost to store crosstalk in atom 29438?

## Baseline to beat (CITED, disk-verified)

`data/exp_reader_perception_meaning_grounding_v1/metrics.json` (atom 29438),
verdict AWARE_USES_CONTENT_BUT_NO_GROUNDING_LIFT:
- olivetti(40-class, chance=0.025): ADDITIVE i2w BLIND(raw)=0.3167 AWARE(hog)=0.2317 -> aware-blind=-0.085
- perception is REAL: hog shuffle-sensitivity=0.188 vs raw=-0.030; scr_collapse(hog)=0.193
- digits(secondary): i2w blind=0.746 aware=0.754

## Single variable

STORE STRUCTURE only:
- `additive` = M = sum_i bind(word_c(i), code_i) into ONE vector; ground q = M * code_x argmax'd over
  the word codebook (VERBATIM GRD.build_store / GRD.i2w_heldout / GRD.w2i_heldout = the 29438 arm).
- `sharded` = per-class partition M_c = sum_{i in c} bind(word_c, code_i); ground
  pred = argmax_c cosine(word_c, M_c * code_x) (drops off-diagonal c!=w crosstalk terms). An
  inspectable per-class partition of the SAME bind/unbind VSA primitives -- glass-box, NOT a neural
  module.

Encoder front-ends (rung1_raw content-blind, rung3_hog content-aware), data (olivetti PRIMARY 40-class,
digits SECONDARY), split, referent words, retrieval task = REUSED VERBATIM from GRD. The 2x2 is
{additive, sharded} x {raw, hog}; aware-over-blind is measured under EACH store.

## Pre-registered bands (probe verdict on PRIMARY olivetti)

- POSITIVE CONTROL (Gate D, reproduce prior at FULL 40-class): additive aware_over_blind in
  [-0.135, -0.035] (cited -0.085 +/- 0.05) AND additive raw/hog absolute i2w within 0.06 of 0.317/0.232.
  Else RAIL_FAIL_ADDITIVE_NOT_REPRODUCED (store-comparison rail broken). NOTE: this check is a FULL-
  config property; the smoke config (8-class, N=3000) intentionally does NOT reproduce it -> smoke
  verdict RAIL_FAIL is expected and is NOT a gate failure.
- HARD-PASS SHARDED_RECOVERS_GROUNDING_LIFT: sharded aware_over_blind >= +0.05 AND controls robust
  (sharded hog shuffle-sensitivity >= 0.15, sharded hog scramble-collapse >= 0.10, sharded raw
  shuffle-invariant <= 0.12). => additive crosstalk WAS the limit; sharding is the fix.
- HARD-FAIL SHARDING_NO_LIFT_CROSSTALK_NOT_THE_LIMIT: sharded aware_over_blind <= 0.0. => crosstalk
  NOT the limit; the encoder / perception step is implicated (honest refutation).
- MIDDLE_BAND_WEAK_PARTIAL_RECOVERY: 0.0 < sharded aware_over_blind < +0.05.
- SHARDED_SATURATED_INCONCLUSIVE: both sharded raw and hog i2w >= 0.95 (baseline out of band).

## Design-gate compliance

- REAL baseline: additive store = the exact 29438 arm (VERBATIM reuse), reproduced as positive control.
- CAN-FAIL: sharding may help raw as much as hog (both are per-class-shard scoring in code space),
  leaving aware-blind <= 0 -> HARD-FAIL. Genuinely discriminates the two hypotheses.
- ONE VARIABLE: store structure; everything else held identical between the two stores.
- Must-fail controls carried over per store: global-pixel-shuffle (content-shuffle sensitivity) +
  word-scramble (base-rate collapse).

## Compute architecture

Class: sequential-CPU (numpy). Justification: cell IS the substrate-store operation being validated;
per-class sharded scoring is a small argmax loop; encoding dominates and is shared across stores.
Full wall ~5 min (5 seeds x 2 arms x 2 stores x 2 datasets). Smoke wall ~10s. No GPU speedup relevant
at this scale (bind = elementwise mul, N=8192). progress_logging = print_flush_true.

Storage strategy: this cell EXPLICITLY compares bundled(additive) vs sharded storage as the two
discriminator arms (allowed per SHARDED-STORAGE-DEFAULT exemption (b): testing bundled-vs-sharded).

## Discriminator-survives-scale (option B analytical)

Additive cross-class crosstalk variance grows with the number of other-class binds ~ (n_classes-1)*
k_train; sharding removes exactly those terms. The sharded-vs-additive gap GROWS with n_classes, so
FULL 40-class olivetti is MORE discriminating than the 8-class smoke, not less. Smoke (8-class) already
shows recovery-delta +0.469 (additive aob=-0.219 -> sharded aob=+0.250). Direct code-level crosstalk
micro-proof in self_test: 16-class near-orthogonal case additive i2w=0.375 vs sharded=1.000.

## SCHEMA-VET fields

- arms_differ_verified: true (raw vs hog codes bit-differ; store-variable-fires micro-proof)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise before except Exception (no BaseException / no bare except)
- crlb_n/a: grounding = held-out retrieval vs chance + shuffle-sensitivity contrast + scramble
  collapse + store-structure differential; no scalar noise-floor cap
- baseline_in_band: additive raw i2w in (chance, 0.95); flag if any store saturates >= 0.95 at FULL
- deterministic_seeding: true (fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering)
- cardinality: EXPECTED_N_UNITS = 5 seeds x 2 arms x 2 stores x 2 conds = 40 grounding evaluations
- positive_control (Gate D): additive reproduces 29438 aob=-0.085 at FULL 40-class olivetti
- real_code_path: reuses GRD.encode_images/build_store/i2w_heldout + HG loaders VERBATIM

## Routing note

Cell imports GRD (exp_reader_perception_meaning_grounding_v1) + HG
(exp_reader_image_shape_recognition_hog_v1) which landed LOCALLY (atoms 29438/29431) and are NOT on
origin/main. A remote (remote_cpu_queue / overnight_queue) dispatch would GATE_FAIL on those imports
until orchestrator pushes them. This is a CPU-light probe (~5 min) run to completion locally instead.
