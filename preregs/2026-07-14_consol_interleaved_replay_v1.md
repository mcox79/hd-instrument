# Pre-registration: CONSOLIDATION (P1) interleaved-replay manufactures inference structure

- **anchor_name:** `consol_interleaved_replay_v1`
- **script:** `experiments/exp_consol_interleaved_replay_v1.py`
- **date:** 2026-07-14
- **queue (target):** `remote_cpu_queue` (CPU-only; small model; no GPU speedup at this scale)
- **seeds (FULL):** [7, 13, 19, 29, 37] (5 seeds)
- **pause_state:** NOT PAUSED

## Question
Does integrating the P1 "interleaved slow update" CLS primitive into the substrate's learned-code loop
(`hdlab/additive_map.py`) MANUFACTURE held-out relational-inference structure at substrate scale, BEATING continual
(task-blocked, non-replayed) learning? Claim B was CONFIRMED inline (4 CLS/Saxe signatures) but never integrated;
this is the integration + at-scale test.

## Design (one line)
Learn entity codes X and shared relation displacements D by SGD on a masked-attribute (relational) prediction task
over a scaled synthetic hierarchical concept-attribute KG, under three batch SCHEDULES (INTERLEAVED / CONTINUAL /
SHUFFLE), and measure held-out relational-inference lift + the 4 signatures. Held-out readout = the REAL additive
substrate primitive (`AdditiveKGMap.score_edges` -> `additive_direct_scores`, score = -||X_h + D_r - X_t||).

## Arms (identical model + matched compute budget; ONLY schedule/structure differs)
- **INTERLEAVED** (mechanism): i.i.d. minibatch SGD over ALL train edges, `P_max` passes (replay/consolidation).
- **CONTINUAL** (forgetting control): domain-blocked, `P_max/S` local passes per domain in order, NO replay (matched
  total gradient steps). Shared D is contested across sequentially presented domains -> early domains forgotten.
- **SHUFFLE** (structure-destroyed control): interleaved schedule but per-entity RANDOM tails -> siblings disagree,
  nothing to generalize; held-out lift must stay flat at POP.
- Non-arm references: **POP** (per-relation marginal-frequency baseline = fair floor), **ORACLE** (latent-type ->
  info-ceiling), **P=0** random-init readout (chance).

## The 4 signatures (gates)
1. **DOSE-RESPONSE**: INTERLEAVED held-out MRR(P_max) - MRR(P=1) >= `DOSE_MARGIN` (0.05); saturating rise.
2. **STAGING**: coarse/SUPER normalized-progress reaches half-asymptote at an EARLIER pass than fine/SUB
   (`_pass_to_half(super) < _pass_to_half(sub)`).
3. **BEAT-CONTINUAL**: INTERLEAVED - CONTINUAL MRR >= `BEAT_MARGIN` (0.05) AND CONTINUAL early-domain MRR forgotten
   (<= POP + `FORGET_EPS` 0.03).
4. **SHUFFLE-FLAT**: SHUFFLE MRR(P_max) - POP_shuf <= `FLAT_EPS` (0.03) AND |dose slope| small.

A signature "fires" on aggregate iff it fires on the seed-mean AND on a majority of seeds.

## Pre-registered bands (BOTH before running)
- **HARD_PASS**: INTERLEAVED beats CONTINUAL by >= 0.05 MRR AND beats POP by >= 0.05 MRR AND >= 3 of 4 signatures fire.
- **REFUTE**: (INTERLEAVED - CONTINUAL) < 0.02 OR (INTERLEAVED - POP) < 0.02 (no inference structure manufactured /
  replay does not beat continual at scale). Honest REFUTE is a valid, valuable outcome.
- **MIDDLE**: otherwise (beats continual but < 3 signatures, or margins between REFUTE and HARD_PASS bands).
- **HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF**: any arm's final code table bit-identical to another.
- **HARD_FAIL_CARDINALITY_BREACH_META_RULE_H**: fewer than 5 seeds complete.

Band-number provenance:
- `BEAT_MARGIN=0.05`, `POP_BEAT_MARGIN=0.05`, `DOSE_MARGIN=0.05`, `FLAT_EPS=0.03`, `FORGET_EPS=0.03`,
  `REFUTE_EPS=0.02`, `SIGS_FOR_HARD_PASS=3`  HYPOTHESIZED@this-prereg, calibrated + discriminator-verified at
  self-test (see below). Margins are BETWEEN-ARM gaps (relative), not absolute noise-floor targets -> `crlb_n/a`.

## Compute architecture
- Class: **(b) sequential-CPU with justification.** Model is tiny (N_total ~= 592 rows at FULL, k=32, ~3500 train
  edges, k_neg=16). SGD passes are inherently sequential (each pass depends on the last); negatives sampled
  vectorized (no per-edge Python loop). Per-phase-point wall << 10s; GPU offers no meaningful speedup at this scale
  and CPU keeps it portable to `remote_cpu_queue`.
- **Storage strategy:** SHARDED (each entity is its own X row; never bundled). The mechanism under test is the
  learning SCHEDULE, not a storage/composition op. `no_composition`.

## Fairness + weak-point localization (first-class per USER 2026-07-10)
- **Info-ceiling**: ORACLE (latent-type modal tail) computed per seed; headroom reported. Ceiling < 1 by label noise
  (`p_noise=0.10`) so achieved MRR is sub-ceiling and interpretable.
- **Fair baseline**: POP (per-relation marginal frequency) is the no-structure floor INTERLEAVED must beat.
- **Must-fail controls**: SHUFFLE (structure destroyed) must stay flat at POP; CONTINUAL early-domain must be
  forgotten below POP. Both are load-bearing.
- **Weak-point localization**: metrics split by relation LEVEL (super/sub) and by domain PRESENTATION ORDER
  (early/late), plus per-checkpoint trajectories and the CONTINUAL per-block forgetting curve -> pinpoints WHERE
  (which granularity / which domain / which pass) the mechanism breaks.

## SCHEMA-VET / validity-preflight (declared in self-test)
- `real_code_path`: `AdditiveKGMap`, `set_coords`, `score_edges`, `additive_direct_scores` all EXERCISED at self-test.
- `substrate_signature`: `AdditiveKGMap` bound against live `inspect.signature` (base kwargs `device` only; advisory
  WARN that `device` is optional/defaulted -> verify remote parity or drop; `additive_map.py` is a maintained live
  module, parity holds once pushed with the cell).
- `metric_moves`: INTERLEAVED held-out MRR trajectory must not be structurally frozen.
- `negative_control_margin`: SHUFFLE + CONTINUAL-early must sit below INTERLEAVED by margin (>= 2 repeats).
- `guard_baseline_valid`: POP floor validated above pure chance (not a structural-zero floor).
- `arms_differ_verified`: SHA-256 of the three arms' final X tables must be distinct (META_RULE_AF).
- `final_metrics_atomicity`: `tmp_replace` (write_metrics atomic tmp+os.replace).
- `cardinality_ok`: EXPECTED_N_UNITS = 5 seeds; verdict counts `len(per_seed)`.
- `start_marker_written`, `crash_diagnostic_present`, `heartbeat_present`: yes.
- `calibration_check`: `adaptive_with_discriminator_gate` (bands calibrated at self-test; discriminator-fires
  verified via `assert_discriminator_fires` on the CONTINUAL/POP null).
- Determinism: integer seeds only; `np.random.default_rng(int_seed)` + `torch.Generator().manual_seed(int_seed)`;
  no `hash()` / `list(set())` (PROT-023 static scan runs on ship).

## Self-test result (MEASURED, calibration evidence)
`experiments/exp_consol_interleaved_replay_v1.py --self-test` (arena S=2,C=2,M=8, N_ent=32, k=16, P_max=12):
- INTERLEAVED MRR = 0.885, CONTINUAL = 0.744, SHUFFLE = 0.577, POP = 0.571; beat_gap = 0.141 (>> 0.05).
- Ordering INTERLEAVED > CONTINUAL > SHUFFLE ~ POP holds; `assert_discriminator_fires` passed; 5 validity-preflight
  checks declared and passed. SELFTEST_PASS.
  MEASURED@data/exp_consol_interleaved_replay_v1_selftest/metrics.json:mechanism_selftest

## Near-full-scale smoke result (MEASURED; discriminator-survives-scale evidence)
`--memsmoke` (arena S=3,C=3,M=16, N_ent=432, k=24, P_max=12, seeds [7,13]), wall = 179s:
- AGGREGATE **HARD_PASS**: INTERLEAVED=0.925, CONTINUAL=0.496, SHUFFLE=0.430 ~ POP=0.425, CEIL=0.958.
  beat_gap=0.429 (>> 0.05), pop_gap=0.500 (>> 0.05), signatures 3/4 [dose=T(v2), staging=F(v1), beat=T(v2),
  shuffle=T(v2)], forgot_early_mean=0.413 (~POP), arms_differ=T.
- Effect STRENGTHENS with scale vs self-test (beat_gap 0.14 -> 0.43): more domains -> worse catastrophic forgetting
  in CONTINUAL. STAGING is the weakest signature (fired 1/2 seeds); the other 3 fire with large margins.
  MEASURED@data/exp_consol_interleaved_replay_v1/metrics.json:gates

## EXPECTED_N_UNITS
5 (one per seed).

## Timeout
FULL est. ~= 150s (single-thread self-test) + 5 seeds x ~40s ~= 350s. Timeout set to **1800s** (5x headroom for
remote CPU variance).
