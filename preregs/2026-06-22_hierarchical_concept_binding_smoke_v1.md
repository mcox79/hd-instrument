# Pre-registration: hierarchical_concept_binding_smoke_v1

**Date:** 2026-06-22
**Anchor:** hierarchical_concept_binding_smoke_v1
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** 3 (7, 17, 23), **depth:** 4, **branching:** 2, **n_roots:** 30 (full) / 15 (smoke)

## Scientific question
Does nested HRR binding (parent_vec -> child_vec via shared per-level role-bind) enable the
substrate to (a) encode 4-level hierarchical ontologies with reasoning-down-the-chain retrieval
("is labrador a mammal?") and (b) deliver a capacity multiplier vs flat random-vector encoding
under fixed noise (sigma=1.0)?

## Pre-registered bands

**HARD-PASS** (substrate-only enabler; chain-grade-eligible at full-grid, MEASURED_MECHANISM at smoke):
- HP1: ARM_NESTED_BIND hierarchy_retrieval_accuracy >= 0.85 at ALL parent-recovery levels (per-level mean across 3 seeds, levels 1..3 in 0-indexed = "all 4 levels" in 1-indexed counting since recovering parent at level k uses entities at level k)
- HP2: capacity_at_sigma1_NESTED >= 2.0 x capacity_at_sigma1_FLAT (mean across seeds)

**MIDDLE:** hierarchy works at shallow levels but degrades with depth, OR partial multiplier
(>1x but <2x); characterize depth limit.

**HARD-FAIL:** HF1: deepest-level (level=3) nested-bind retrieval mean < 0.50 (deep retrieval broken),
OR HF2: nested_cap_mean <= flat_cap_mean AND NOT both arms saturated at M-grid cap (no
multiplier benefit; only counts when discriminator is informative).

**METRIC-CEILING GUARD (by-construction-saturation per cert-architecture):** if BOTH arms hit
the largest M in CAP_M_GRID (recall stays >= 0.80 at smoke's M=800), HF2 is DEMOTED to
MIDDLE_BAND (METRIC_CEILING). Production cell must extend M-grid to discriminate.

## Calibration rationale
- HP1 0.85 floor: substrate-native HRR bind/unbind at N=4096 has 1/sqrt(N) compounded-noise floor
  ~0.4 cos per layer; cleanup against a sibling-codebook of size 30..240 should drive recall@1
  near 1.0 if mechanism is sound. 0.85 is the substrate-standard "clearly works" bar (matches
  comparator_resonator HP1 0.75 with margin for hierarchy depth).
- HP2 2x: a "capacity multiplier" claim requires non-trivial separation; 2x is the minimum that
  is interpretable as structural (not noise). Literature on HRR cleanup capacity is ~N/log(M)
  for unique-atom flat encoding; if nesting yields any benefit from role-sharing the multiplier
  should be visibly > 2x at modest N. If it is below 2x, the mechanism is not delivering its
  promised structural benefit.
- HF1 0.50: above-chance at depth=3 (which is "level 4" in 1-indexed counting). Chance for a
  parent codebook of size 120 is ~1/120 = 0.008; the 0.50 floor demands the mechanism is doing
  meaningful work (not just chance).
- HF2: if nesting cannot match flat capacity it is strictly worse than the baseline (one of the
  cleanest negative-result signals in this whole arc).

## N-suffix section
Anchor has NO _n<N> suffix (smoke does not pin N to PROT-018 the way a production _n4096 anchor
would). N_DIM=4096 is fixed in the script; this is a smoke, not a production-grade _n4096 anchor.
If the smoke clears, a follow-up production anchor `hierarchical_concept_binding_v1_n4096` will
be pre-registered separately with full seeds=5, n_roots=60, branching=3.

## Timeout estimate
Smoke wall estimate at smoke config (N_DIM=4096, n_roots=15, total_entities=225, 3 seeds,
capacity-grid 5 points):
- Per-seed: ~30s arm-build, ~10s metric-A, ~120s metric-B (capacity sweep dominates), ~15s metric-C
  -> ~180s/seed
- 3 seeds: ~540s = 9 minutes
- Smoke total estimate: 540s; with 1.5x safety = 810s ~ 14 min. Smoke queue cap is 180s by
  default, so smoke gate uses HDLAB_SMOKE_TIMEOUT_S override of 600s.

formula: ceil(1.5 * 540 * (4096/4096)^1.0 * (3/3)) = 810
timeout_s = 1800 (local_cpu_queue runner cap; smoke completes well under)

# Routing
queue: local_cpu_queue
smoke-only this round; production follow-up gated on smoke verdict.
