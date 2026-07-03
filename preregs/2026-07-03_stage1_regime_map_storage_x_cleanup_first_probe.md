# Pre-registration: Stage 1 REGIME MAP — STORAGE x CLEANUP_MECHANISM cross-term probe (first of arc)

Date: 2026-07-03
Author: hdi_exp_dev (agent-spawn, Opus 4.7)
Anchor: `stage1_regime_map_storage_x_cleanup_v1`
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER strategic direction 2026-07-03).
Arc note: `notes/project_stage1_regime_map_of_CG_META_axes_USER_2026-07-03.md` (Director-filed).

## Purpose (intuitive)

I am mapping the regime boundaries of the 5 established Stage 1 CG_META axes. Today's
physics-law composition Option Y (`stage1_physics_law_joint_composition_factorial_v1`,
seed 11 smoke, 2026-07-03) revealed that the CLEANUP_MECHANISM M-scaling axis produced
`max_mechanism_variation_at_cliff = 0.000` at SHARDED storage — all 3 non-Hebbian
mechanisms (modern_hopfield / iterative_cosine / soft_energy_attractor) achieved
identical accuracy in the SHARDED FHRR-chain composition regime. This directly targets
the question: **is CLEANUP_MECHANISM axis universally regime-narrow (holds only in
bipolar-codebook cleanup regime), or does its degeneracy at SHARDED reflect a specific
storage-strategy interaction?**

Option Y-2 pairwise probe: measure the STORAGE x CLEANUP_MECHANISM cross-term. If
BUNDLED (below-capacity storage regime) recovers mechanism-axis variance while SHARDED
does not, we have discovered that CLEANUP_MECHANISM is CONDITIONALLY meaningful only
at BUNDLED storage in FHRR chain-composition. If BUNDLED also collapses mechanism
variance, we have a CG_META finding: CLEANUP_MECHANISM_M_scaling is fundamentally
regime-exclusive to the bipolar-codebook cleanup regime; it does NOT extend to FHRR
under any storage strategy.

## Cited source atoms (exact names per META_RULE_AC + Director MM_STANDARD)

- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` — Stage 1
  CG_META axis; established 2026-07-02.
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` — SHARDED-vs-BUNDLED
  chain-depth physics law; established 2026-07-02.
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` — bipolar-codebook regime
  M-sweep 2026-07-03; source of the 3 non-Hebbian mechanisms being tested here.
- `feedback_chain_grade_primitives_not_trivially_composable_2026-06-28.md` — cross-
  regime SHAPE_DRIFT audit discipline.
- Stage-1 physics-law composition Option Y result (seed 11 smoke,
  `data/exp_stage1_physics_law_joint_composition_factorial_v1_s11_smoke/metrics.json`)
  MEASURED@`bundle_pc_result.storage_gap_sharded_minus_bundled = 1.0`
  MEASURED@`max_mechanism_variation_at_cliff = 0.0`.

## Compute architecture

- Class: `(a) batched-GPU` — reuses batched-GPU primitives from
  `_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when
  available; CPU fallback for local smoke).
- Storage strategy: `mixed` — cell IS testing SHARDED vs BUNDLED as the discriminator
  arm (case (b) of the storage-default rule); explicitly compositional (chain L=2).
- Progress logging: `print_flush_true` (per-phase-point print with flush=True).

## Design

### Sweep axes

- STORAGE ∈ {SHARDED, BUNDLED} — Option Y-2 change from Option Y (which was
  SHARDED-only).
- CLEANUP_MECHANISM ∈ {modern_hopfield, iterative_cosine, soft_energy_attractor} — 3
  non-Hebbian (drops classical/Hebbian).
- M ∈ {200, 800, 3200} — M-scaling axis.
- N ∈ {2048, 8192} — SCALE_FREE axis.
- corruption ∈ {0.20, 0.45} — cleanup-regime probe.
- Fixed: F=1 (drops TOPOLOGY axis for pairwise probe; add later if warranted).
- Fixed: L=2 (drops ALGEBRA axis for pairwise probe).

### Cardinality

- FULL: 2 × 3 × 3 × 2 × 2 = **72 phase points per seed** × 3 seeds = 216.
  - `EXPECTED_N_UNITS_FULL = 72`
- SMOKE: 2 × 3 × 1 × 1 × 1 = **6 phase points × 1 seed** (M=200, N=2048, corr=0.20).
  - `EXPECTED_N_UNITS_SMOKE = 6`
  - Rationale for M=200 in smoke: at N=2048, Plate 1995 bundle bound = 0.14*N = 287;
    M=200 sits just below the bound so BUNDLED should be discriminable (not floor,
    not ceiling); SHARDED is expected near-ceiling (established 2026-07-02 that
    SHARDED extends 13.9x beyond bundle bound).

### Reuse (Principle 11)

- Primitives (cphasor_torch, cnorm_torch, phase_corrupt, build_rules, run_chain,
  CLEANUP_REGISTRY, CLEANUP_MECHANISMS, BETA, ALPHA_SOFT) imported from
  `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py`.
- New file: `experiments/_stage1_regime_map_storage_x_cleanup_v1_core.py` — defines
  the sweep, verdict logic, storage-cleanup cross-term ANOVA calculation.
- Seed wrappers: `experiments/exp_stage1_regime_map_storage_x_cleanup_v1_s{7,13,19}.py`.

## SMOKE HP criteria (SHIP FULL if all met)

1. selftest_ok (`selftest()` returns True; imported storage-gap gate at PC regime).
2. cardinality_ok (observed 6 = expected 6).
3. arms_differ_verified (3 distinct mechanism output-hash aggregates across SHARDED
   points).
4. positive_control at SHARDED-vs-BUNDLED storage-gap `>= 0.30` at M=200 N=2048
   corr=0.20 (per Plate 1995: M/N=0.098 just below 0.14 bound — SHARDED should hold,
   BUNDLED should degrade).
5. discriminator_fires_check: at BUNDLED smoke regime (M=200 N=2048 corr=0.20), at
   least ONE mechanism produces `acc >= 0.10` (BUNDLED is not universally floor) OR
   at least ONE produces `acc <= 0.90` (BUNDLED is not universally ceiling). If
   BUNDLED at M=200 N=2048 corr=0.20 is 0.0 for all 3 mechanisms, the smoke regime
   is too hard for BUNDLED — need to lower M or corruption in FULL grid (report to
   Director).
6. **KEY smoke discriminator (informational, not gating):** measure
   `mech_variance_at_BUNDLED_smoke = max(acc_bundled) - min(acc_bundled)` across
   3 mechanisms at (M=200, N=2048, corr=0.20). Report the value.
   - If `mech_variance_at_BUNDLED_smoke >= 0.05` → strong evidence BUNDLED reveals
     mechanism axis; recommend FULL dispatch.
   - If `mech_variance_at_BUNDLED_smoke == 0.0` AND BUNDLED is not floor/ceiling →
     preliminary evidence of universal CG_META finding (CLEANUP_MECHANISM
     regime-exclusive). FULL still warranted to confirm at wider grid.

## FULL HARD_PASS_CG_TIER criteria

1. cardinality_ok per seed (72 pts each).
2. arms_differ_verified across seeds.
3. positive_control storage-gap SHARDED-minus-BUNDLED `>= 0.30` at M > 0.14*N.
4. 3-seed CV `< 0.10` per phase point (accuracy stability across seeds).
5. **STORAGE x CLEANUP cross-term test (primary discriminator):**
   - Compute ANOVA-style 2-axis interaction deviation for STORAGE x
     CLEANUP_MECHANISM.
   - If `max_abs_deviation_STORAGE_x_CLEANUP >= 0.15` OR `mech_variance_at_BUNDLED
     >= 0.05` (in ANY M/N/corr slice) → **HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_
     STORAGE**: mechanism axis is meaningful at BUNDLED (below-capacity) storage but
     collapses at SHARDED.
   - If `max_abs_deviation_STORAGE_x_CLEANUP < 0.05` AND `mech_variance_at_BUNDLED
     < 0.05` across ALL slices → **HARD_PASS_MECHANISM_AXIS_UNIVERSALLY_DEGENERATE_
     IN_FHRR**: CG_META finding; CLEANUP_MECHANISM axis does not extend to FHRR
     under any storage strategy.
6. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- cardinality breach (any seed missing pts).
- PC storage-gap `< 0.20` at M > 0.14*N (SHARDED-BUNDLED distinction collapses;
  invalidates the storage-axis baseline for this arc).
- selftest fails.

## MIDDLE_BAND

- `0.05 <= max_abs_deviation_STORAGE_x_CLEANUP < 0.15` → crossover regime; not
  chain-grade CG; file as MM_TENTATIVE with cross-term inventory.

## SCHEMA-VET checklist (must all be True/present)

- `cardinality_ok`: True (72 FULL / 6 SMOKE)
- `arms_differ_verified`: True (3 distinct cleanup mechanisms; run-time hash check)
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end)
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException)
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; discriminator is
  cross-term interaction deviation not a CRLB-governed quantity. Positive-control
  reproduces the same primitives at the test regime (Gate D compliance)."
- `discriminator_reachability`: True (measured non-zero storage gap at SHARDED-vs-
  BUNDLED at M=200 N=2048 corr=0.20 expected from Plate 1995).
- `baseline_in_band`: designed True at BUNDLED smoke regime; SHARDED expected
  near-ceiling (already known 13.9x extension). Since SHARDED-vs-BUNDLED IS the
  discriminator, one arm near-ceiling is acceptable IF the OTHER is in-band.
- `HP_SCOPE`: {`SHARDED_arm`: [`arms_differ`, `cardinality_ok`],
  `BUNDLED_arm`: [`discriminator_fires`, `cross_term_deviation`],
  `positive_control_arm`: [`storage_gap_>=_0.30`]}
- `cell_chunked`: True (3 seed wrappers)
- `start_marker_written`: True (inherited from v1 factorial pattern)
- `crash_diagnostic_present`: True
- `heartbeat_present`: per-phase-point print with flush (long enough at FULL to be
  useful)
- `defensive_error_checking`: `passed_all_4_patterns`
- `sweep_alignment_verdict`: `ALIGNED` (STORAGE + CLEANUP + M + N + corr are the
  actual primitives that experience each swept value; no partition-routing
  intermediation).
- `discriminating_fraction`: 5/6 pts in discriminating band at BUNDLED smoke arm
  (predicted). SHARDED all 3 mech expected near-ceiling (1 pt each). BUNDLED all 3
  expected in [0.15, 0.85] band at M=200 N=2048 corr=0.20 (near Plate bound). Overall
  ≥ 50% of smoke pts in discriminating band.
- `composition_edges`: [`build_rules -> run_chain: SHAPE_MATCH`,
  `run_chain -> cleanup_argmax_idx: SHAPE_MATCH`, all inherited from v1 core].
- `positive_control_arms`: [{arm: `sharded_iterative_cosine_at_smoke_regime`,
  primitive: `run_chain(storage=SHARDED, mechanism=iterative_cosine)`,
  cited_prior_atom: `stage1_physics_law_joint_composition_factorial_v1_s11_smoke`,
  cited_prior_metric: 1.0 (at M=800 N=2048 corr=0.20 SHARDED),
  cited_prior_regime: {M: 800, N: 2048, corr: 0.20, F: 1, L: 2},
  test_regime: {M: 200, N: 2048, corr: 0.20, F: 1, L: 2},
  tolerance: 0.10, if_outside: `HARD_FAIL_INVOCATION_MISMATCH`,
  regime_extension_audit: `SHAPE_MATCH`: same primitives (imported from core)
  reduced M from 800 -> 200 (still well below the chain-fail cliff empirically)}].
- `functional_requirements`:
  - FR-1: chain-composition (rule storage + unbind + cleanup + readout)
    → `run_chain` primitive (imported).
  - FR-2: storage-strategy comparability (SHARDED vs BUNDLED at same phase point)
    → `build_rules` primitive returns both codebook forms (imported).
  - FR-3: mechanism-axis variance measurement across 3 cleanup families
    → `CLEANUP_REGISTRY` (imported).
  - FR-4: cross-term ANOVA deviation calculation
    → new logic in this cell's `aggregate_and_verdict`.
- `progress_logging`: `print_flush_true` (per-phase-point + per-seed).
- `calibration_check`: `default_ok_for_this_regime` — BETA=8.0 ALPHA=0.5 inherited
  from v1 core where they passed the SHARDED positive-control at M=800 N=2048
  corr=0.05 (`acc >= 0.80`).

## Reachability of criteria

- SMOKE wall: ~7-15s (6 pts × ~1s/pt from v1 evidence at M=800 N=2048). Reduced M=200
  should be faster.
- FULL wall estimate: 72 pts × ~1s each × 3 seeds = ~4 min per seed on GPU; ~15 min
  per seed on CPU. Comfortably fits `remote_cpu_queue` timeout (default 3600s).

## Substrate-KB concept-query result

Query: "STORAGE SHARDED BUNDLED CLEANUP_MECHANISM cross-term FHRR regime mechanism
variance modern hopfield iterative cosine soft energy attractor". Top-5 cosines
0.284-0.292; **all below 0.30 threshold** → this cell is genuinely novel; no prior
arc cell covers this specific storage-x-cleanup cross-term probe. Prior-work check
result: `NONE at cosine>0.30`.
