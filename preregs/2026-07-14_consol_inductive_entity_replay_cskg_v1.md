# Pre-registration: consol_inductive_entity_replay_cskg_v1

**Cell:** `experiments/exp_consol_inductive_entity_replay_cskg_v1.py`
**Date:** 2026-07-14
**Author:** exp_dev
**Upgrades:** `exp_consol_interleaved_replay_v1` (commit a6d93fbae, BELIEVED construction-proof)

## Question

Does INTERLEAVED-replay consolidation manufacture INDUCTIVE (novel-ENTITY) inference structure on REAL reduced-CSKG,
beating a COMPUTE-MATCHED task-blocked CONTINUAL learner AND a FAIR FREQUENCY baseline? Glass-box, no LLM.

## Two changes from the construction-proof cell (both VET-flagged bounds removed)

1. **ARENA = REAL reduced-CSKG k-core** (NOT a planted synthetic). k_core=30 -> N=2335 nodes, 151070 edges, 20
   relations (MEASURED@ sizing probe 2026-07-14; matches the "~2869/20" reduced core other real-data cells use).
2. **SPLIT = INDUCTIVE held-out-ENTITY** (NOT novel (head,rel) pairs). Hold out 15% of head-appearing entities; a
   held-out entity appears ONLY as a HEAD in edges (h_held, r, t_seen) whose TAIL is a SEEN entity; its edges are
   NEVER in train; its query tail (a SEEN, frequency-having entity) is predicted from its OWN support edges via the
   frozen scaffold. Predicting a SEEN tail keeps the FREQUENCY baseline a FAIR, informative, beatable BAR (the VET
   named frequency as the bar).

## Mechanism under test = the batch SCHEDULE producing the frozen scaffold (X entity codes, D relation displacements)

All arms fit the SAME additive/TransE model, SAME CE self-adversarial loss, SAME TOTAL GRADIENT-STEP BUDGET; only
the schedule differs:
- **INTERLEAVED** (mechanism): i.i.d. minibatch SGD over ALL train edges, P_max=20 passes (replay/consolidation).
- **CONTINUAL** (compute-matched head-to-head): RELATION-BUCKET-blocked (relation-incremental continual, a standard
  CL-KGE protocol), P_max passes PER bucket in order, NO replay. Each edge trained P_max times in BOTH arms
  (compute-matched; step mismatch gated <= 2% at FULL). Shared ENTITY codes are contested across relation-buckets
  (entities appear in many relations, esp. on cross-cutting CSKG edges) -> sequential blocking forgets early-relation
  structure. The VET predicts compute-matched continual forgets WORSE -> a beat cannot be a compute artifact.
- **SHUFFLE** (must-fail): interleaved schedule on structure-destroyed train edges (tails randomized) -> flat lift.

The INDUCTIVE readout (identical across the 3 scaffold arms) is ZERO-training ANCHOR-COMPOSE: E_derived[h_held] =
mean_i(X[t_i] - D[r_i]) over support edges (TransE head estimate; degree-invariant bundle), scored by the REAL
`additive_direct_scores` (score(c) = -||E_derived[h] + D[r_q] - X[c]||), filtered-MRR ranked vs ALL candidates.

## Reference arms

- **SCRAMBLE** (must-fail): anchor-compose on the INTERLEAVED scaffold with support relation ids scrambled -> isolates
  whether relation operators carry the signal vs an anchor-identity/degree confound.
- **RANDOM** (chance floor): random-init X + random D + same readout.
- **ORACLE** (info-ceiling / positive control): transductive interleaved fit with held-out entities FOLDED IN (codes
  learned). If ORACLE does not fire, arena not answerable -> gated INCONCLUSIVE (not a substrate negative).
- **POP_RELFREQ** (fair frequency bar): rank the gold SEEN tail by per-relation tail frequency (VET-named bar).

## Metric + info-ceiling discipline

Primary metric = **FILTERED MRR** rank-vs-ALL (KGE standard, degree-unbiased, no sampled-negative pool). The
held-out-ENTITY arena has an info-ceiling; the ANCHOR bands are FRACTIONS of the MEASURED oracle headroom
H = ORACLE_mrr - RANDOM_mrr, computed in-run (compute-info-ceiling-before-iterating discipline).

## Pre-registered bands (picked BEFORE the FULL; ceiling-relative, resolved to absolute MRR from MEASURED H)

- **ORACLE-FIRES (arena answerable):** ORACLE_mrr >= 3.0x RANDOM_mrr AND (ORACLE_mrr - RANDOM_mrr) >= 0.003.
- **HARD_PASS_INDUCTIVE_REPLAY_BEATS_CONTINUAL_AND_FREQ:** INTERLEAVED beats CONTINUAL by >= max(0.10*H, 0.003) MRR
  AND beats POP_RELFREQ by >= max(0.10*H, 0.003) AND recovers >= 0.30*H over RANDOM AND ORACLE fires AND must-fails
  fire (SHUFFLE and SCRAMBLE within 0.25*H of RANDOM) AND sub-ceiling (INTERLEAVED_mrr < ORACLE_mrr) AND
  compute-matched AND not broken AND holds on a majority of seeds (>=3/5).
- **REFUTE_REPLAY_NO_INDUCTIVE_ADVANTAGE:** ORACLE fires AND (INTERLEAVED - CONTINUAL <= 0.001 OR
  INTERLEAVED - POP_RELFREQ <= 0.001). Replay does NOT beat compute-matched continual OR does NOT beat frequency on
  real+inductive. A VALUABLE, drill-worthy negative (would trigger a 2x drill on WHY real+inductive breaks it).
- **MIDDLE_BAND_PARTIAL_INDUCTIVE_ADVANTAGE:** ORACLE fires, beats both by > 0.001 but below the HARD_PASS margins.
- **INCONCLUSIVE:** ORACLE underfit / too few held-out queries / broken control.

Supporting signature (reported, not a separate gate): DOSE-RESPONSE (INTERLEAVED mrr(P_max) - mrr(P=1) >= 0.10*H).

## Band values (all HYPOTHESIZED@ this prereg unless tagged; NOT tuned on real data)

- ORACLE_FIRE_RATIO=3.0, ORACLE_FIRE_ABS=0.003, MIN_SIG_MRR=0.003, HP_CEIL_FRAC=0.30, BEAT_CONT_FRAC=0.10,
  BEAT_POP_FRAC=0.10, DOSE_FRAC=0.10, FLAT_FRAC=0.25, REFUTE_EPS=0.001, MIN_HELDOUT=20, step_match_tol(FULL)=0.02.

## Fairness + weak-point localization (first-class per USER 2026-07-10)

- **Fair frequency bar:** POP_RELFREQ over a SEEN, frequency-having gold tail (head-holdout keeps it informative,
  unlike tail-holdout where POP is a structural zero). guard_baseline_valid asserts POP > chance floor.
- **Info-ceiling computed in-run:** ORACLE is the transductive ceiling; bands are fractions of the MEASURED H.
- **Must-fails fire:** SHUFFLE (structure-destroyed) + SCRAMBLE (relation-scrambled) + RANDOM below INTERLEAVED.
- **Compute-match:** per-arm gradient-step counts logged; compute_matched gate <= 2% mismatch at FULL.
- **Metric can move:** ORACLE fires by a large margin (MEASURED@ memsmoke: 23.9x, H=0.064).
- **Weak-point localization:** support-degree histogram + per-seed votes + full hits@{1,3,10,100}+MRR spectrum per
  arm; the SCRAMBLE-controlled gate localizes whether the inductive signal is relational or anchor/degree-confounded.

## Discriminator-survives-scale (Option C preview + analytical B)

MEASURED@ memsmoke (real CSKG, P_max=4, seed 7, nq=500): INTERLEAVED=0.0569 beats compute-matched CONTINUAL=0.0273
(+0.0297), ORACLE=0.0665 fires 23.9x (H=0.064), SHUFFLE=0.0017 flat, but POP_RELFREQ=0.0730 > INTERLEAVED
(under-trained). MEASURED@ dose probe (real CSKG, P_max sweep, seed 7, nq=2000): INTERLEAVED plateaus at P=20-40
(mrr ~0.062-0.064) then OVERFITS (P=80 -> 0.059); POP_RELFREQ=0.0603. => P_max=20 is ADEQUATE + FAIR (not
under-trained; more passes overfit). At the plateau INTERLEAVED (~0.062) only marginally exceeds POP (~0.060), so the
likely FULL outcome is MIDDLE_BAND (beats compute-matched continual clearly; matches frequency) or REFUTE if the
beats-POP margin dips <= 0.001 across seeds. Both are honest, valuable outcomes.

Analytical (B): a random-init scaffold cannot compose (RANDOM at the 1/N floor) and relation-incremental blocking
leaves early-relation entity codes stale as shared codes drift -> the INTERLEAVED > {CONTINUAL, SHUFFLE, RANDOM}
ordering persists at any N; the ORACLE-fires control proves the metric can move at scale.

## Self-test (MEASURED@ data/exp_consol_inductive_entity_replay_cskg_v1_selftest/metrics.json)

Planted TransE arena (copied from the VET'd inductive-entity cell): SELFTEST_PASS. INTERLEAVED=0.231 beats
CONTINUAL=0.179 (beat_cont=+0.052, forgetting fires), beats RANDOM by +0.213, beats POP by +0.016; SHUFFLE/SCRAMBLE
below INTERLEAVED; ORACLE fires; compute-matched; 5 validity-preflight checks declared (real_code_path,
substrate_signature, metric_moves, negative_control_margin, guard_baseline_valid). Exercises the REAL readout/eval
substrate primitives (additive_direct_scores, filtered_hits_from_scores, pop_hits, build_ids, _to_int_edges); the
REAL CSKG loader build_cskg_core_triples is exercised by the local MEMSMOKE gate.

## Compute architecture

class (c) MIXED: split + support/query partition + POP + rel_tail_freq = sequential-CPU graph ops (no matmul); the
additive fits = minibatch CE-self-adversarial SGD; E_derived = a single vectorized index_add_ bundle (no training);
readout = query-chunked batched matmul. Storage SHARDED (each entity its own code). device=auto (remote_cpu forces
cpu). Reduced core streamed ONCE (k-core seed-independent at max_nodes=0), re-split per seed.

## SCHEMA-VET fields

- cell_chunked: false (5 seeds in one cell; per-seed try/except with failure_class; cardinality gate on n_seeds)
- start_marker_written: true; crash_diagnostic_present: true; heartbeat_present: true
- defensive_error_checking: passed_all_4_patterns
- arms_differ_verified: true (>=5 distinct sigs asserted per seed)
- final_metrics_atomicity: tmp_replace
- crlb_n/a: relative between-arm MRR gap, ceiling-relative bands (no absolute noise-floor target)
- calibration_check: adaptive_with_discriminator_gate (bands are fractions of MEASURED H; discriminator-fires verified)
- deterministic_seeding: true (PROT-023 static scan clean; integer seeds only)
- progress_logging: line_buffered_stdout (+ per-seed/per-arm flush prints); FULL timeout_s >= 1800
- baseline_in_band: ORACLE fires; RANDOM/POP near floor; INTERLEAVED strictly between (self-test asserts)

## Routing

- self_test + one MEMSMOKE run LOCAL (both PASS). FULL (5 seeds) -> **remote_cpu_queue**.
- Expected FULL runtime ~15-25 min (streaming 161s + ~5x memsmoke seed cost); timeout 3600s.
