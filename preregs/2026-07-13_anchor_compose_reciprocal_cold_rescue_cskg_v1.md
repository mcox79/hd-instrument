# Pre-registration: ANCHOR_COMPOSE reciprocal cold-rescue (CSKG v1)

- **Cell:** `experiments/exp_anchor_compose_reciprocal_cold_rescue_cskg_v1.py`
- **Anchor name:** `anchor_compose_reciprocal_cold_rescue_cskg_v1`
- **Shared-dep edit:** `experiments/_kge_anchor1_fit.py` gains a backward-compatible `return_inverse=False` kwarg
  (2-tuple return bit-identical for every prior caller; verified X + D_forward bit-identical between the 2-tuple and
  3-tuple calls at seed=7). When `return_inverse=True` (requires `reciprocal=True`) it ALSO returns the trained
  inverse-relation block `D[n_rel:2*n_rel]`.
- **Filed:** 2026-07-13 by exp_dev. **Queue:** overnight_queue (GPU). **Timeout:** 16200 s.
- **Trigger:** wave-2 substrate-realizable lever (Lever 1, `P_deflated=0.35`) from
  `notes/research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md` (HEADLINE 1). ORTHOGONAL
  to the in-flight SIC-peel/hard-neg magnitude cell (that targets adequate-support entities; this targets COLD/
  low-support entities).
- **Prior-work check (substrate-KB concept-query):** NONE at cosine>0.30 (top hit 0.2881 = a generic
  decomposition/bundling note, not this reciprocal cold-rescue arc). Genuinely novel.

## Hypothesis

The confirmed ANCHOR_COMPOSE composer bundles ONLY a held-out entity's TAIL-support edges `(seen_head, r, held_ent)`.
Edges where the held-out entity is the HEAD of a triple to a KNOWN tail `(held_ent, r, seen_tail)` are silently
dropped (CODE-VERIFIED: `build_heldout_entity_split_ac`'s `h_hold and not t_hold` branch is never collected). The
COLD bucket (entities whose single tail-edge is reserved as the query, leaving 0 tail-support) currently scores
`anchor_mrr=0.000041` -- BELOW its own `random_mrr=0.000524` and far below `oracle_mrr=0.650751`
(MEASURED@data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json:anchor_mrr_by_support_degree, CITED via the
research note Part A). No cleanup/weighting/decorrelation lever can move COLD because there is nothing to aggregate.
Bundling the dropped HEAD edges via the ALREADY-TRAINED inverse relation (`X[seen_tail] + D_inverse[r]`; the reciprocal
inverse block is already fit because `fit_kge_anchor1` runs with `reciprocal=True`) is a ZERO-new-training,
same-primitive change that ADDS a usable support edge for exactly this population.

**Brain-analog (CITED@Kosko 1988, Bidirectional Associative Memories):** one learned association supports recall in
EITHER direction from the same symmetric (Hebbian) plasticity. Ties to the relational-capability program spine
(CITED@project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md).

## Arms (9; SHARDED per-entity codes; all scored PAIRED on the SAME held-out QUERY edges + candidate pool)

The QUERY set and the shared additive/rotate/oracle fits are BIT-IDENTICAL to the confirmed v1: head edges go ONLY to
a NEW head-support pool, never to train or query. The tail-side split RNG streams are preserved.

- `ANCHOR_COMPOSE` -- TAIL-ONLY flat additive mean == confirmed v1 baseline (Gate-D reproduce; the COLD floor).
- `ANCHOR_RECIP` -- MECHANISM: tail-support + head-support (via trained inverse `D_inverse`) bidirectional mean.
- `ANCHOR_RECIP_SCRAMBLE` -- must-fail for the reciprocal lever: head estimates use PERMUTED inverse-relation ids
  (`X[seen_tail] + D_inverse[perm[r]]`); tail-support identical. Isolates whether the COLD lift is RELATIONAL.
- `ADDITIVE_TRANSE` -- memorize control (same additive fit; held-out code random-init).
- `ONESHOT_ROTATE` -- 2nd memorize control (rotation fit).
- `RANDOM_CODES` -- null (the bar COLD currently sits BELOW).
- `ANCHOR_SCRAMBLE` -- v1 must-fail: TAIL-support forward relation ids scrambled.
- `ORACLE_ADDITIVE` -- positive control / ceiling (held-out folded in -> codes learned). COLD oracle ~0.65 (fork
  MEASURED) proves COLD is answerable-in-principle when a code exists.
- `BASELINE_POP` -- frequency incumbent (fit-independence sanity; held-out tails have train-freq 0 -> ~floor).

## Primary metric

Filtered MRR rank-vs-ALL (degree-unbiased, KGE standard). Legacy hits@10 reported, not gated. Primary question = the
COLD bucket, stratified by ORIGINAL TAIL-support degree (COLD = 0 tail-support, directly comparable to the ladder).

## Pre-registered bands (picked BEFORE the run)

Symbols: all HYPOTHESIZED unless MEASURED@/CITED@.

- **GATE-D REPRODUCE:** `|ANCHOR_all - 0.1282| <= 0.03`
  (MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE at the
  matched k=24/ep=500/k_core=12/support_frac=0.5 regime). Off-tolerance -> `INCONCLUSIVE_BASELINE_NOT_REPRODUCED`.
- **ORACLE-FIRES (overall):** `ORACLE_mrr >= 3x RANDOM_mrr` AND `ORACLE_mrr - RANDOM_mrr >= 0.003`.
- **CONSTRUCTION-FIRED:** `>= 8` COLD queries whose entity gained `>= 1` reciprocal HEAD-support edge. Else COLD band
  = `INCONCLUSIVE_COLD_NO_RECIP_SUPPORT` (a graph-sparsity finding: CSKG COLD entities lack usable edges in either
  direction; redirect to multi-hop/textual fallback, NOT a mechanism HARD_FAIL).
- **COLD HARD-PASS (`HARD_PASS_RECIPROCAL_COLD_RESCUE`):** COLD-bucket `ANCHOR_RECIP mrr >= 0.02` absolute
  (a ~40-500x rescue off the ~0.00004-0.0005 floor) AND `(RECIP - ANCHOR)_cold >= 0.01` AND COLD scramble controlled
  (`(RECIP - RECIP_SCRAMBLE)_cold >= 0.5 * (RECIP - RANDOM)_cold` AND `|RECIP_SCRAMBLE_cold - RANDOM_cold| <= 0.005`)
  AND NO-REGRESSION holds AND ORACLE fires AND Gate-D holds AND v1 tail-scramble controlled.
- **COLD HARD-FAIL (`HARD_FAIL_COLD_NO_RECIPROCAL_TRANSFER`):** COLD-bucket `ANCHOR_RECIP mrr < 0.0002` WITH
  construction fired = genuine negative (localize to multi-hop/textual fallback).
- **COLD MIDDLE (`MIDDLE_BAND_PARTIAL_COLD_RESCUE`):** COLD lift present but `< 0.02` -> sub-stratify by
  reciprocal-edge count (1 vs 2+); if lift scales with reciprocal-edge-count, the lever works but COLD is thin on
  reciprocal edges too.
- **REGRESSION/CONFOUND (`MIDDLE_BAND_COLD_RESCUE_WITH_REGRESSION_OR_CONFOUND`):** COLD HP met but the no-regression
  guard OR the tail-scramble control fails.
- **NO-REGRESSION guard:** overall AND every adequate bucket (`d2_3`/`d4_7`/`d8plus`)
  `ANCHOR_RECIP mrr >= ANCHOR mrr - 0.005` (adding head estimates must not degrade already-working populations).
- **SECONDARY (reported, not gating):** overall `(RECIP - ANCHOR)_mrr` gain (`>= 0.005` = a good secondary; small
  because COLD is a minority bucket -- the PER-BUCKET COLD rescue is the primary signal).

## Four validity-preflight checks (declared in self-test)

1. `positive_control_passes` -- ORACLE recovers planted held-out tails + clears RANDOM by the fire gate.
2. `metric_moves` -- COLD-bucket MRR MOVES across [RANDOM, ANCHOR(tail-only), ANCHOR_RECIP, ORACLE].
3. `negative_control_margin` -- RANDOM + ANCHOR_RECIP_SCRAMBLE below ANCHOR_RECIP on COLD, deterministic >= 2.
4. `full_gates_exercised` -- `aggregate_and_verdict` runs on the planted per-seed, firing every fail-closed gate.

## Adversarial self-test discriminator (MEASURED, this cell, self_test)

Planted TransE-consistent arena with COLD-head-only entities. **SELFTEST_PASS (87.2 s, single-thread CPU).**

- COLD-bucket MRR: ANCHOR(tail-only)=0.00525, `ANCHOR_RECIP=0.11355`, RECIP_SCRAMBLE=0.02586, RANDOM=0.012
  (MEASURED@data/exp_anchor_compose_reciprocal_cold_rescue_cskg_v1_selftest/metrics.json:mechanism_selftest.cold_bucket_mrr).
  Reciprocal head-bundling lifts COLD ~21x over the tail-only baseline; the relation-scramble collapses to ~random.
- ORACLE=0.91957 fires (ratio + abs); POP=0.00642 at floor; 9 distinct arm signatures; n_cold_with_recip=14.
- The self-test aggregate verdict is `INCONCLUSIVE_BASELINE_NOT_REPRODUCED` -- CORRECT and EXPECTED: the planted
  arena's ANCHOR (0.290) is not the CSKG 0.1282 target, so the Gate-D fail-closed gate correctly fires at self-test
  scale (proving it is exercised). SELFTEST_PASS is gated on the discriminator checks, all of which fire.

## Compute architecture

class (c) MIXED. 3 fits (additive+reciprocal-inverse, rotate, additive-oracle) = minibatch SGD (batched,
self-adversarial, neg-chunked) == the confirmed v1 fit cost (MEASURED@v1 FULL elapsed_s=12073 for
k=24/ep=500/3 seeds/3 fits). The tail + bidirectional recip E_derived constructions = vectorized index_add segment
ops (no training, seconds). Readouts = query-chunked batched matmul. Storage SHARDED. device=auto (cuda on the GPU
host; overnight_queue). FULL fits are fit-checkpointed (ckpt_every=20) so a timeout resumes each fit from its last
epoch. Memory footprint is identical to v1's GPU-proven FULL (same N, k, n_neg, neg_chunk; one extra cheap index_add
bundle + cheap readouts) -> no new OOM risk; an optional memsmoke is available but analytically covered by v1 parity.

## SCHEMA-VET fields

- `arms_differ_verified: true` (self-test: 9 arms -> 9 distinct sigs; FULL asserts >= 6).
- `final_metrics_atomicity: tmp_replace` (via `_seed_checkpoint.write_metrics` + `os.replace`).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException / no bare except; grep-verified).
- `crlb_n/a`: primary metric is filtered MRR with a ceiling-aware ORACLE fire gate; the COLD band is a low ABSOLUTE
  bar (0.02) off a MEASURED ~0.00004 floor, with the COLD oracle (~0.65 fork) proving reachability-in-principle.
- `baseline_in_band: true` (ORACLE must fire; RANDOM/POP near 1/N floor; Gate-D reproduces ANCHOR within 0.03).
- `discriminator_survives_scale`: self-test fires the reciprocal COLD discriminator on the planted arena (option A);
  the CONSTRUCTION-FIRED gate guards against a vacuous COLD band on CSKG; analytical (B) -- a per-entity table cannot
  encode an unseen entity, so the memorize null persists at any N.
- `HP_SCOPE`: COLD-rescue HP gates apply to `ANCHOR_RECIP` only. ORACLE = positive control; RANDOM/ANCHOR_SCRAMBLE/
  ANCHOR_RECIP_SCRAMBLE = must-not-clear-bar; ADDITIVE_TRANSE/ONESHOT_ROTATE = memorize head-to-heads;
  ANCHOR_COMPOSE = tail-only baseline (Gate-D); POP = fit-independence sanity.
- `cardinality_ok: true` -- `EXPECTED_N_UNITS = n_seeds (3)`; each seed asserted to produce all 9 arms + >= 6 sigs.
- `per_unit_failure_class: true` (no bare except; per-seed `failure_class` recorded; `HARD_FAIL_CARDINALITY_BREACH`).
- `calibration_check: adaptive_with_discriminator_gate` -- HELDOUT_ENTITY_FRAC/SUPPORT_FRAC + COLD band absolutes
  pre-registered, NOT tuned on real data; COLD stratifier uses ORIGINAL TAIL-support degree.
- `cell_chunked: false` (single-cell multi-seed with fit-checkpoint durability, matching v1).
- `start_marker_written: true`; `crash_diagnostic_present: true`; `heartbeat_present: true`;
  `defensive_error_checking: passed_all_4_patterns`.
- `run_mode_verification`: FULL expected `run_mode=full`, size > 5 KB (per-seed data), elapsed > 1 s.
- `progress_logging: print_flush_true` (line-buffered stdout + per-seed/per-arm flush prints; timeout_s >= 1800).

## §15 composition/sweep gates

- `sweep_alignment_verdict: ALIGNED` (no nominal-vs-effective parameter sweep; single regime).
- `discriminating_fraction: n/a` (not a sweep; the COLD bucket is the discriminating stratum by construction, and the
  self-test confirms it is answerable-via-reciprocal at self-test scale).
- `composition_edges`: fit(additive, reciprocal=True) -> `D_inverse` block -> head-edge estimate `X[t]+D_inverse[r]`
  -> bidirectional additive bundle -> additive readout. All SHAPE_MATCH (same additive geometry throughout).
- `positive_control_arms`: `ANCHOR_COMPOSE` reproduces v1's 0.1282 (Gate-D, tolerance 0.03, matched regime);
  `ORACLE_ADDITIVE` reproduces the transductive ceiling and fires.
- `functional_requirements`: (1) represent a COLD held-out entity from its OWN edges with zero training -> reciprocal
  head-bundle via the already-trained inverse operator; (2) prove the lift is relational -> ANCHOR_RECIP_SCRAMBLE
  must-fail; (3) prove no harm to working populations -> no-regression guard; (4) prove answerability -> ORACLE fire.

## Falsifiable prediction

Reciprocal head-bundling moves the CSKG COLD bucket from ~random to `>= 0.02` MRR (HARD-PASS), with the relation
scramble flat, and no regression on adequate buckets. If COLD stays `< 0.0002` despite construction firing (HARD-FAIL),
CSKG COLD entities are single-edge-in-any-direction (a genuine graph-sparsity floor) -> redirect to multi-hop/textual
fallback. If lift is present but `< 0.02` (MIDDLE), COLD is thin on reciprocal edges too (sub-stratified diagnostic).
