# Pre-registration: substrate_schema_family_phase_diagram_v1

**Date:** 2026-06-29
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive 2026-06-28+29 — systematic phase-diagram coverage across substrate COMPONENTS. FIFTH cell in component-substitution series (after pc_encoder_family, seqbind_encoder_family, ...). Substitutes SCHEMA MECHANISM FAMILY rather than encoder or config parameter.

## Anchor

`substrate_schema_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_schema_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local CPU (`.venv/Scripts/python.exe` direct + local_cpu_queue traceability)
- **Full queue:** **remote_cpu_queue** (NumPy-light; 4 families x 12 inner pts x 1 seed each x 20 queries; ~10-25 min/seed at N=4096; CPU-bound; no GPU benefit per pure numpy matmul shape)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via SendMessage post-smoke commit + push by hd_metrics_sync).

## Why this cell exists (the gap)

Substrate schema retrieval (vmPFC analog) has been characterized through v1-v4 config-parameter sweeps:
- v1 phase_diagram (60 pts; alpha implicit via n_ex x n_classes): MIDDLE_BAND
- v3 capacity_stress (alpha 0.006 to 19.5; prior=1.0): 5/5 MB; CLIFF NOT observable; GRACEFUL DEGRADATION across 4 decades
- v4 capacity_stress (3-arm: BAYES_GRACEFUL / HARD_MAX / REFERENCE): SUSTAINED-FLOOR discovery — HARD_MAX centroid argmax DOMINATES at high alpha (HM=0.80 vs GR=0.20 at FLOOR alpha=19.5 on smoke n_q=5).

ALL prior sweeps held the MECHANISM CLASS FIXED (exemplar-Bayes with prior=1.0). v4's HARD_MAX was a 1-off discriminator arm, not a systematic family substitution. We have never done head-to-head between EXEMPLAR_BAYES / PROTOTYPE_BASED / HYBRID / BAYESIAN_WITH_PRIORS on a shared inner grid. This v1 fills that gap.

The lever: at fixed (alpha, n_schemas), swap only the READOUT mechanism. Same encoder, same exemplars, same query set. Pure family substitution.

## Schema families (the OUTER axis)

Four families, each consuming identical (queries (Q,N), exemplars (C,K,N)):

| Family | Readout | Source |
|--------|---------|--------|
| `FAMILY_EXEMPLAR_BAYES` | argmax_c [ log_prior(c) + LSE_k(beta*cos(q, e_c_k)) ]; prior_strength=1.0 | v3 default |
| `FAMILY_PROTOTYPE_BASED` | argmax_c cos(q, centroid_c); centroid = normalized mean exemplar | v4 HARD_MAX discovery |
| `FAMILY_HYBRID` | argmax_c [ 0.5 * log_posterior_bayes(c) + 0.5 * beta * cos(q, centroid_c) ] | mixture of above two |
| `FAMILY_BAYESIAN_WITH_PRIORS` | EXEMPLAR_BAYES with prior_strength = log(n_classes) | strong prior variant |

All 4 use the same beta = log(n_classes) / 0.1 for LSE temperature where applicable.

**Why this is apples-to-apples:** same encoder (bipolar HDC), same exemplar build (prototype + noise 0.30), same queries (held-out at 0.30 noise), same N=4096, same alpha grid. Only the readout function differs.

**Selftest validation:** for each family, verify produces top1 in [0, 1.0] for a single corner (alpha=0.1, n_schemas=50); >= 2 of 4 families must produce distinguishable top1 (differ by >= 0.01); positive control EXEMPLAR_BAYES top1 >= 0.20.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| family (OUTER) | {EXEMPLAR_BAYES, PROTOTYPE_BASED, HYBRID, BAYESIAN_WITH_PRIORS} | 4 |
| alpha = K_total/N (inner) | {0.01, 0.1, 1.0, 10.0} | 4 |
| n_schemas (inner) | {10, 50, 200} | 3 |
| N_DIM | 4096 fixed | 1 |

**Cardinality FULL per seed:** 4 * 4 * 3 = **48 phase points per seed**.
**Cardinality SMOKE per seed:** **6 corners** (covering each family + alpha range).

n_exemplars_per_class derived per-pt: `n_ex = round(alpha * N / n_schemas)`, min 1.

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files).

## Hypothesis

**H1 (PRIMARY): The 4 families WILL differ in cliff location AND/OR floor retention.**
- `EXEMPLAR_BAYES`: graceful across alpha decades; floor ~0.20-0.40 at alpha=10 (v3 finding).
- `PROTOTYPE_BASED`: stronger at FLOOR (alpha=10 high); centroid averaging suppresses exemplar noise (v4 finding); but possibly WEAKER at SATURATION where individual exemplars retain useful detail.
- `HYBRID`: should track best-of-two across regimes; if so, candidate substrate default for vmPFC retrieval.
- `BAYESIAN_WITH_PRIORS`: stronger prior shrinks to chance at FLOOR (helpful at high class load); may track or beat EXEMPLAR_BAYES at sweet-spot.

**H2 (regime-mapping): Different families WIN in different regimes.**
- If H2 holds: substrate doesn't have ONE best schema family; family choice depends on alpha + n_schemas. Downstream cells should pick per-regime.

**H3 (positive control): `EXEMPLAR_BAYES` at (alpha=0.1, n_schemas=50, N=4096) reproduces sweet-spot top1 >= 0.50.** Mid-load Bayes-lift regime; v1 phase_diagram showed this regime is informative.

**H4 (null): All 4 families identical within +/- 0.05 top1 at EVERY (alpha, n_schemas) phase point.** If H4 holds, schema family doesn't matter — load-bearing **negative** finding (default doesn't need re-evaluation).

**H5 (dominance): One family strictly dominates all others across all 12 inner pts.** If H5 holds, strongest finding — substrate should switch default. Most likely candidate is HYBRID (combines smoothing + noise-suppression).

## Discriminator: per (family, alpha, n_schemas) tier

For each inner phase point per family, classify into:

| Tier | top1_mean | lift_over_chance |
|------|-----------|------------------|
| SATURATED | >= 0.95 | (DOWN-WEIGHTED per Skunkworks Q-rule) |
| HARD_PASS | >= 0.50 | >= 5x chance |
| MIDDLE_BAND | [0.30, 0.50) | (mech alive but below HP) |
| HARD_FAIL | (0.10, 0.30) | mechanism breaking |
| FLOOR | <= 0.10 | substrate at chance |

**Discriminating_fraction (overall) >= 0.30** = pre-reg PASS threshold = (>= 14/48 inner pts in HARD_PASS + MIDDLE_BAND tiers across all families).

## Pre-reg bands (LOCKED at module init)

### HARD_PASS (chain-grade family-discrimination)
- cardinality_ok (observed_n == expected_n: 48 FULL or 6 SMOKE)
- discriminating_fraction >= 0.30 (>= 14/48 pts in HP+MB)
- family_pair_distinctness: at least 2 of 6 family pairs produce distinct per-point top1 hashes (META_RULE_AF — substitution actually happened)
- positive_control_pass: EXEMPLAR_BAYES @ alpha=0.1, n_schemas=50: top1 >= 0.50
- NOT all_saturated; NOT arms_identical; NOT random_arm_pathology

### MIDDLE_BAND (family differs but low discrimination)
- arms_differ (family_pair_distinctness >= 1) AND discriminating_fraction in [0.10, 0.30)
- OR positive_control_pass + family_pair_distinctness >= 2 but disc_frac < 0.30

### MIDDLE_BAND_NULL_FAMILY_INVARIANCE (H4 negative)
- discriminating_fraction OK but family_pair_distinctness == 0 (all 4 families identical hashes — schema family is NOT a discriminating lever)

### HARD_FAIL
- HARD_FAIL_CARDINALITY_BREACH: observed != expected
- HARD_FAIL_ALL_SATURATED: all 48 points top1 >= 0.95 (sweep missed regime — by-construction-sat)
- HARD_FAIL_ARMS_IDENTICAL: family_pair_distinctness == 0 AND run_mode == "full" (no families differ — bug)
- HARD_FAIL_CONTROL_FAIL: EXEMPLAR_BAYES @ pos-ctrl pt top1 < 0.50 (test rig broken)
- HARD_FAIL_RANDOM_ARM_PATHOLOGY: random arm > +/- 0.30 of chance at >= 2 points

## Smoke gate (MUST pass before FULL dispatch)

1. 6 corner points all RAN (no silent except per META_RULE_J)
2. cardinality_ok: observed_n == 6
3. discriminator fires: at least 2 of 4 families produce distinguishable top1 at smoke
4. positive_control informational: EXEMPLAR_BAYES @ alpha=0.1, n_schemas=50: top1 >= 0.20 (mechanism alive at smoke n_q=5)
5. random arm sanity: rand_top1 within +/- 0.35 of chance at each corner (loose at n_q=5)
6. at least 1 corner shows top1 < 0.40 (cliff observable at smoke; if FLOOR everywhere = honest negative)
7. at least 1 corner shows top1 >= 0.50 (mechanism not all-floor)

If gates 1-5 fail, FULL dispatch is HARD-blocked. Gates 6-7 informational; if both fail at smoke, full grid may not span regimes — cell still ships but expects MIDDLE_BAND verdict.

## Calibration / smoke corners (DISCRIMINATOR-SURVIVES-SCALE)

| corner | family | alpha | n_schemas | n_ex | expected_top1 | expected_chance | expected_lift |
|--------|--------|-------|-----------|------|---------------|-----------------|----------------|
| 1 | EXEMPLAR_BAYES | 0.1 | 50 | 8 | MID (0.4-0.8) | 0.02 | 20-40x |
| 2 | EXEMPLAR_BAYES | 10.0 | 200 | 205 | LOW (0.1-0.4) | 0.005 | 20-80x |
| 3 | PROTOTYPE_BASED | 0.1 | 50 | 8 | MID-HI (0.5-0.9) | 0.02 | 25-45x |
| 4 | PROTOTYPE_BASED | 10.0 | 200 | 205 | HI (>= 0.50) per v4 | 0.005 | 100x+ |
| 5 | HYBRID | 1.0 | 50 | 82 | MID-HI (0.5-0.9) | 0.02 | 25-45x |
| 6 | BAYESIAN_WITH_PRIORS | 0.01 | 10 | 4 | HI (>= 0.80) | 0.10 | 8-10x |

Honest expectations: PROTOTYPE_BASED @ FLOOR is the key v4-confirm; if it doesn't hold ~0.50+ at corner 4, the v4 finding was selftest-only artifact. EXEMPLAR_BAYES @ corner 2 should be LOWER than PROTOTYPE @ corner 4 (the v4 inversion).

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_FULL per seed = 48 (4 families x 4 alphas x 3 n_schemas)
- EXPECTED_N_UNITS_SMOKE per seed = 6 (6 corners)
- EXPECTED_N_SEEDS = 3 (seed 7, 13, 19)
- EXPECTED_N_UNITS_AGGREGATE_FULL = 48 * 3 = 144

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == expected_n)` per sibling. HARD_FAIL if observed != expected (META_RULE_H_ANCHOR, USER 2026-06-26 META_RULE_J).

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26)

Smoke at N=4096 (same as full N). 6 corners chosen to span SAT / sweet / FLOOR regimes. If smoke saturates (all corners >= 0.95) or all-floors (all corners <= 0.10), the discriminator doesn't survive scale and full dispatch is HARD-blocked.

Per v4 selftest finding: PROTOTYPE_BASED @ (alpha=10, n_schemas=200) showed top1=0.80 at n_q=5. If this collapses to ~0 at n_q=20 (full), the v4 finding was n_q-artifact. The smoke corner 4 prediction (HI >= 0.50) is held loose to accommodate cv at small n_q.

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (bipolar random HDC; NOISE_SCALE=0.30) per family
- Same exemplar codebook per seed per inner config (built once, shared across families)
- Same query set per (seed, inner config) (built once, all 4 families consume identically)
- All 4 readouts compute over IDENTICAL exemplars+queries
- family_pair_hashes via SHA-256(json(rounded(top1_per_inner_pt))) — at least 2 of 6 pairs differ to claim discrimination

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. META_RULE_X main-guard. PROT-021 N+anchor stamp on every partial.

## SUBSTRATE PREREQS (chain-grade primitives cited)

- Bipolar random HDC codebook (chain-grade per `exp_substrate_sequence_binding_v1`)
- Cosine similarity readout (chain-grade ubiquitous)
- Log-sum-exp Bayesian aggregation (substrate-native; per v3 5/5 MB)
- Centroid argmax (substrate-native; per v4 HARD_MAX)
- Class membership encoded via stored exemplar set (vmPFC schema analog; v1 chain-grade)

## ETA

Per-point on CPU at N=4096, n_q=20: ~0.5-3s (matmul scales with K_total = alpha * N).
- At alpha=10, n_schemas=200: K_total = 2000 exemplars, matmul (20, 4096) @ (8.2M, 4096) ~ 1-2s
- 48 pts/seed * ~1.5s avg = ~75s science + 10s init = ~90-120s/seed FULL on CPU

Smoke: 6 pts/seed * 1s = ~10s science + 5s init = ~15-30s/seed SMOKE on CPU.

Timeouts:
- SMOKE: 180 s (3 min hard cap, harness default)
- FULL: 1800 s (30 min margin; budget ~2 min expected; 15x safety)

per-experiment timeout formula:
  full_timeout_s = ceil(1.5 * smoke_wall_s * (48/6)**1.0 * (1/1))
  smoke_wall ~ 30s -> full_timeout = ceil(1.5 * 30 * 8) = 360s; we use 1800 for substantial margin

## HDLAB_QUEUE CONTRACT

`# PRESERVE_ENV_VARS: HDLAB_QUEUE` header in cell files. CPU-only cell; no gpu_mandate_check.

## Composition edges (substrate atomization context)

- Existing CHAIN-GRADE primitive: bipolar exemplar codebook + cosine readout (composed)
- COMPONENT being swept: the AGGREGATION READOUT over per-class exemplars
- Downstream atomization candidate: WINNING_SCHEMA_FAMILY_PER_REGIME (if H2) or DOMINANT_SCHEMA_FAMILY (if H5) or SCHEMA_FAMILY_NOT_DISCRIMINATING (if H4)

## Pre-reg fields summary

- expected_n_units_full = 48 (per seed)
- expected_n_units_smoke = 6 (per seed)
- HARD_FAIL_CARDINALITY_BREACH (asserted in metrics.json `cardinality_ok`)
- HARD_FAIL_ALL_SATURATED (asserted via aggregate `all_saturated`)
- HARD_FAIL_ARMS_IDENTICAL (asserted via `arms_identical`)
- HARD_FAIL_CONTROL_FAIL (asserted via `positive_control_pass`)
- HARD_FAIL_RANDOM_ARM_PATHOLOGY (asserted via `random_arm_pathology`)
- discriminator_survives_scale (smoke gate gating full dispatch)
- CARDINALITY_OK
- §13 patterns (multi-arm bracket; component substitution; arms-must-differ via family hashes)

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (per-family top1 hashes)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 family arms produce distinct hashes (else component substitution didn't happen — bug); at least 2 of 6 pairs must differ
- META_RULE_AH: every quoted number tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@
- META_RULE_H: cardinality_ok mandatory (48 full, 6 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- META_RULE_M-S (USER 2026-06-24 production-scale calibration): verify-referent on per-family-discriminator; basis-vs-use-case (labels at readout, NOT in basis); anisotropy-hurts-retrieval; suspect 1.000 results (sat flag mandatory)
- Functional-requirement decomposition: schema retrieval = pick correct class given query (single primitive; family is the substituted COMPONENT)
- Substrate-as-canonical query-first: v1/v3/v4 chain reviewed; this v1 substitutes family rather than parameters
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at full N=4096 with same query depth structure
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26): clearing 14-pt discriminator AND positive control AND >= 2 pairs differ — all three required for HARD_PASS; otherwise MIDDLE_BAND
- Honest-downward (USER 2026-06-26): if all families cluster within +/- 0.05, that's H4 NULL (honest negative) — file as MIDDLE_BAND_NULL_FAMILY_INVARIANCE not HARD_FAIL

## Notes

- Builds on v1 (60 pts; phase_diagram), v3 (alpha-sweep 5/5 MB), v4 (HARD_MAX discovery) chain.
- Per USER 2026-06-28 systematic phase-diagram coverage across COMPONENTS: this is the 5th cell after pc_encoder_family, seqbind_encoder_family (and 2 others per Research arc).
- Per USER 2026-06-27 substrate-as-canonical query-first: existing schema atom chain (v1/v3/v4) reviewed; this cell pivots from config-sweep to family-sweep.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring exemplar_bayes phase_diagram_v1 pattern.
