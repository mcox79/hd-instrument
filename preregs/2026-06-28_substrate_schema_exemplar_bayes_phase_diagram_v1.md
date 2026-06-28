# Prereg: substrate_schema_exemplar_bayes_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Stage 2 phase-diagram coverage MID -> HIGH
**Drill source:** Research directive 2026-06-28 — schema exemplar-Bayes (ANCHOR 3) is CHAIN-GRADE at ~75% completeness with phase coverage MID. vmPFC schema-retrieval analog. Promote to HIGH coverage via (n_exemplars, n_classes, N) phase diagram. Sibling structural template = sequence_binding_K_cliff_phase_diagram_v1.
**Stage:** Stage 2 (substrate higher-function characterization — schema Bayesian inference cliff)
**P_deflated:** 0.55 (existing chain-grade primitive; phase-diagram fill = new but well-bounded by Bayes/NN floor algebra)
**Phase-diagram axis:** (n_exemplars_per_class, n_classes, N_DIM) at fixed prior_strength=1.0

## SUBSTRATE-AS-CANONICAL prior work

- Existing chain-grade Stage 2 schema exemplar-Bayes primitive (per characteristics table — vmPFC schema analog, 75% completeness, MID phase coverage).
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1` (2026-06-28): sibling structural template (chunked-per-seed; K cliff sweep).
- `exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1` (2026-06-28): sibling pattern (3-arm bracket; cliff axis).
- `exp_substrate_ultrametric_clustering_phase_diagram_v1` (2026-06-28): sibling Stage 2 phase-diagram fill.

## HYPOTHESIS

Substrate **schema exemplar-Bayes**: for each class c in {1..C}, store K exemplars e_c_1..e_c_K (bipolar HDC vectors of dim N). Query q -> classified by posterior `p(c | q) ~ p(c) * sum_k exp(beta * cos(q, e_c_k))` (log-sum-exp aggregation across exemplars per class). vmPFC-style schema retrieval: posterior aggregates evidence across multiple stored instances per class.

Capacity bounded by:
- Class separability: as `n_classes` grows, expected per-class cosine to a random query shrinks ~1/sqrt(C); classes start to bleed at high C.
- Exemplar collision: as `n_exemplars * n_classes` exceeds substrate capacity, exemplars become non-orthogonal; Bayes posterior aggregation buys less.
- N dim sets capacity ceiling. For N=2048 bipolar codebook, capacity_bound ~ 0.15 * N = ~300 distinguishable codes.

**Sweep axes:**
- **n_exemplars_per_class in {1, 5, 10, 50, 100}** (5 points; 1 = degenerate NN; 100 = saturation)
- **n_classes in {2, 5, 10, 50}** (4 points; 2 = trivial; 50 = high-load)
- **N_DIM in {2048, 4096, 8192}** (3 points; capacity sweep)
- **prior_strength = 1.0 fixed** (uniform-ish; ablated separately if needed)
- **= 60 phase points per seed** (5 x 4 x 3)

## ARMS (3) — per phase-point

1. **ARM_SCHEMA_BAYES** — full Bayes posterior aggregation: `posterior(c | q) ~ p(c) * sum_k exp(beta * cos(q, e_c_k))` then argmax. **The mechanism.**
2. **ARM_NEAREST_EXEMPLAR** — argmax_c argmax_k cos(q, e_c_k); single nearest exemplar (no Bayesian aggregation). **Discriminator floor — proves Bayes aggregation > best-NN.**
3. **ARM_UNIFORM_RANDOM** — random class assignment. **Chance floor; rules out artifact (~1/C accuracy).**

**arms-must-differ at each phase point:** BAYES > NN by >= 0.15 at HARD_PASS bands. If BAYES == NN at ALL points (within tolerance 0.02), META_RULE flag = "mechanism not firing" (Bayes degenerated to NN — bug).

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = classification accuracy in [0,1])

Phase-diagram headline: **bayes_advantage_per_(n_exemplars, n_classes, N)** = ARM_BAYES_acc - ARM_NN_acc.

- **HARD_PASS** (chain-grade phase-diagram HIGH coverage confirmation):
  - For >= 30 of 60 phase points, ARM_BAYES - ARM_NN >= 0.15 (Bayes provides aggregation lift)
  - AT LEAST ONE phase point with high-exemplar-low-class (n_ex=50, n_classes=2, N=8192) shows ARM_BAYES >= 0.95 (mechanism saturates well)
  - AT LEAST ONE phase point shows ARM_BAYES < 0.40 (capacity cliff observable)
  - arms-must-differ: avg(ARM_BAYES - ARM_NN) across all 60 points >= 0.10
  - ARM_UNIFORM_RANDOM ~ 1/C at each point (sanity)
  - Capacity scaling: ARM_BAYES top-half mean accuracy at N=8192 > ARM_BAYES top-half mean accuracy at N=2048 by >= 0.05

- **MIDDLE_BAND**:
  - ARM_BAYES - ARM_NN >= 0.15 in 15-29 phase points (regime-narrow Bayes lift)
  - OR avg(ARM_BAYES - ARM_NN) in [0.05, 0.10] (modest aggregation effect)
  - OR no N-scaling

- **HARD_FAIL**:
  - ARM_BAYES accuracy >= 0.95 at ALL 60 points (by-construction saturation — sweep missed regime)
  - OR avg(ARM_BAYES - ARM_NN) < 0.05 (Bayes posterior not load-bearing over NN)
  - OR ARM_BAYES <= ARM_NN at HIGH-class-load sweet-spot (n_ex>=10, n_classes>=10, N>=8192) within tolerance 0.02 (mechanism not firing — Bayes degenerated to NN at the regime where Bayesian aggregation should clearly help). NOTE: at n_classes=2, BAYES<=NN is EXPECTED (NN argmax over many noisy exemplars beats Bayes-averaged prototype) and is NOT pathology.
  - OR ARM_UNIFORM_RANDOM > 0.20 above 1/C floor at ANY point (random arm bug)

**HEADLINE per (n_exemplars, n_classes, N):** bayes_advantage value — this is the load-bearing phase-diagram output.

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (bipolar random HDC) for both BAYES and NN arms.
- Same class+exemplar codebook per seed.
- Same query set per seed.
- BAYES and NN consume IDENTICAL query encoding; only readout differs (Bayes posterior aggregation vs argmax NN).
- beta (Bayes temperature) computed from class capacity: `beta = log(n_classes) / 0.1` so log-sum-exp is well-conditioned.
- Q-discipline: ARM_BAYES = 1.000 at high-load points (n_ex=100, n_classes=50, N=2048) triggers leakage audit.

## CARDINALITY (META_RULE_H_ANCHOR)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms x 5 n_ex x 4 n_classes x 3 N x 20 queries = **3600 records per seed**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms x 6 corners x 5 queries = **90 records per seed**
- **EXPECTED_N_SEEDS** = 3 chunked siblings (seed 7, 13, 19)
- **EXPECTED_N_UNITS_AGGREGATE_FULL** = 3600 x 3 = **10800 records**

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == expected_n)` per sibling.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

Smoke 6 corners (analytic preview):

| corner                           | n_ex | n_cl | N    | expected_BAYES   | expected_NN     | expected_diff |
|----------------------------------|------|------|------|------------------|-----------------|----------------|
| low-load saturate                | 50   | 2    | 8192 | HIGH (>=0.95)    | HIGH (>=0.85)   | SMALL (0.05-0.15) |
| mid-load Bayes-lift              | 10   | 10   | 4096 | MID (0.50-0.80)  | LOW (0.20-0.50) | LARGE (>=0.20) |
| degenerate (1 ex/class = NN)     | 1    | 5    | 4096 | MED (0.40-0.70)  | MED (same)      | NULL (~0)      |
| high-load capacity cliff         | 100  | 50   | 2048 | LOW (<0.40)      | LOW (<0.30)     | SMALL (~0.05) |
| sweet-spot Bayes-lift            | 50   | 10   | 4096 | HIGH (>=0.85)    | MID (0.50-0.80) | LARGE (>=0.20) |
| trivial 2-class                  | 5    | 2    | 8192 | HIGH (>=0.95)    | HIGH (>=0.90)   | SMALL (<=0.10) |

Smoke gate (BLOCK full dispatch if not met):
- 6 corners all RUN (no silent except)
- >= 2 corners with ARM_BAYES - ARM_NN >= 0.15 (mid-load + sweet-spot)
- >= 1 corner BAYES == NN within 0.02 (the K=1 degenerate; mechanism sanity)
- >= 1 corner saturates (low-load: BAYES >= 0.90)
- >= 1 corner low (high-load: BAYES < 0.50)
- ARM_UNIFORM_RANDOM at ~ 1/n_classes (within +/- 0.15) at every corner
- cardinality_ok (observed_n == 90)
- arms_differ verified (BAYES vs NN per-corner diffs > 0 except for K=1 degenerate)

If discriminator does NOT fire at smoke (e.g. BAYES ~ NN everywhere; or BAYES saturates everywhere), HARD_FAIL prior to full dispatch.

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. META_RULE_X main-guard. PROT-021 N+anchor stamp on every partial.

## HARDWARE / DISPATCH

- **CPU-only cell** (no torch; numpy + scipy.special.logsumexp). All ops are O(C * K * N) matrix multiplies — well within numpy CPU performance for N <= 8192.
- Target queue: **local_cpu_queue** (Research directive). Fallback: remote_cpu_queue if local zombie blocks dispatch.
- per-seed full estimate: ~10-20 min (60 pts x ~10s/pt avg; lots of small ops).
- timeout_s = 2700 (45min; 2x safety margin).

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_7.py`
- `exp_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_13.py`
- `exp_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_19.py`

Shared core: `experiments/_substrate_schema_exemplar_bayes_phase_diagram_v1_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor + N stamping).

Aggregation post-hoc: combine 3 sibling metrics.json -> phase-map matrix; verdict computed per-sibling AND combined.

## SUBSTRATE PREREQS (chain-grade primitives cited)

- Bipolar random HDC codebook (chain-grade per `exp_substrate_sequence_binding_v1`)
- Cosine similarity readout (chain-grade ubiquitous)
- Log-sum-exp Bayesian aggregation (substrate-native; no exotic ops)
- Class membership encoded via stored exemplar set (vmPFC schema analog)

## HDLAB_QUEUE CONTRACT (Skunkworks META RULE)

`# PRESERVE_ENV_VARS: HDLAB_QUEUE` header in cell files.
NO gpu_mandate_check that blocks CPU dispatch. This is a CPU-only cell.

## PRE-REG FIELDS

- expected_n_units_full = 3600 (per seed; 60 pts x 3 arms x 20 queries)
- expected_n_units_smoke = 90 (6 corners x 3 arms x 5 queries)
- HARD_FAIL_CARDINALITY_BREACH (asserted in metrics.json `cardinality_ok` field)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR (asserted via all_saturated / avg_bayes_advantage_too_low)
- HARD_FAIL_ARMS_IDENTICAL (asserted via avg_bayes_minus_nn < 0.05)
- discriminator_survives_scale (smoke gate gating full dispatch)
- CARDINALITY_OK
- META_RULE_AM_regime_flip (BAYES <= NN at low-load corner)
- §13 patterns (3-arm bracket; cliff axis; arms-must-differ)

## PHASE-DIAGRAM DECISION TABLE

| Smoke + Full outcome                         | Phase-diagram verdict                                              |
|----------------------------------------------|--------------------------------------------------------------------|
| HARD_PASS — Bayes lift in 30+ pts + capacity scaling | Schema exemplar-Bayes phase coverage MID -> HIGH; chain-grade phase-fill done |
| MIDDLE_BAND — Bayes lift in 15-29 pts                | Regime-narrow Bayes lift; partial fill                              |
| HARD_FAIL — no lift OR saturation OR mechanism off   | Mechanism not load-bearing here OR bracket wrong; v2 with tighter regime |

## NOTES

- This cell PROMOTES schema exemplar-Bayes phase coverage MID -> HIGH on the chain-grade primitive (75% completeness ANCHOR 3 per characteristics table).
- vmPFC schema analog: aggregates evidence across stored instances per class — vs single nearest exemplar.
- Per USER 2026-06-27 substrate-as-canonical: builds on existing chain-grade schema exemplar-Bayes atom.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring sequence_binding_K_cliff_phase_diagram_v1.
- 60-grid version (n_ex x n_classes x N at prior=1.0 fixed) per Research directive: 180-grid trimmed to 60 for tractable CPU compute.
