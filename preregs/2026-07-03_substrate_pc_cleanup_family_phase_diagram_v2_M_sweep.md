# Pre-registration: substrate_pc_cleanup_family_phase_diagram_v2_M_sweep

**Date:** 2026-07-03
**Author:** exp_dev (Opus 4.7, agent-spawn)
**Trigger:** USER-directed Stage 1 physics-law arc (post substrate-mine 2026-07-03). v1 (2026-06-28) established the cleanup-family phase diagram at FIXED `M=300`. v2 adds `M` as a swept OUTER-INNER axis to characterize how each cleanup mechanism scales with codebook size — candidate `PHYSICS_LAW_cleanup_mechanism_M_scaling` analog to existing `SCALE_FREE` and `TOPOLOGY_FREE` CG_META laws.

## Prior-work check (substrate concept-query)

Query: "cleanup mechanism codebook size M sweep phase diagram scaling law"
Top hit at cosine=0.3916: `Codebook size scaling law` in `notes/research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md` — ENCODER-side VQ codebook (semantic clustering), NOT cleanup-side matched-filter capacity. Different concept sharing "codebook" word. This cell is genuinely novel — no prior cleanup-M-sweep phase diagram in substrate.
Second hit at cosine=0.2842: `MEASURED_MECHANISM_phase_diagram_capacity_codebook_separated_envelope_v1` — sibling capacity envelope work; distinct axis (envelope shape not M scaling per cleanup).

## Prior atomized capacity framework (composing on, not creating anew)

Cited substrate atoms this cell extends:
- `T2/amit_gutfreund_sompolinsky_capacity` — classical Hopfield alpha_c = 0.138·N (AGS 1985)
- `T2/modern_hopfield_ramsauer` — modern Hopfield exponential capacity ~ exp(N/2) (Ramsauer 2020)
- `T2/sparse_hopfield_hu_santos` — sparse Hopfield extension
- `T3/capacity_composition_multiplicative` — capacity under composition

Prior substrate experiments as sanity anchors:
- `EXP_m2_capacity` (2026-05-16): FHRR bind/cleanup, k=100 recall 87.3% at N~1024
- `EXP_capacity_scaling_law_cpu_v1` (2026-06-07): pinv-based recall confirms linear-N capacity

Director-provided theoretical framework (`feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03`): cite exact formulas per mechanism, not abstractions.

## Anchor

`substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s{11,17,23}` (3 sibling files; chunked-per-seed per USER 2026-06-28). Seeds 11/17/23 chosen distinct from v1 seeds (7/13/19) so a v1+v2 meta-analysis wouldn't share sub-seed state.

Shared core: `experiments/_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_core.py`.

## Routing

- **Smoke queue:** local (`.venv/Scripts/python.exe` direct invocation; USER-LOCKED 2026-07-01 SMOKE-only on laptop)
- **Full queue:** `overnight_queue` (GPU-preferred). GPU batching mandatory per USER 2026-07-02. FULL grid = 288 phase points/seed x 3 seeds = 864 points. On CPU at N=8192 M=3200 iters=5 estimated ~15-30s/point → ~2-3h/seed unacceptable. On CUDA torch matmul ~50ms/point → ~15 min/seed. **Route to overnight_queue for GPU.**
- **Push constraint:** exp_dev harness-DENIED push. Post-smoke Director spawns `hdi_orchestrator` for SSH+push+queue_add remote dispatch.

## Why this cell exists (the gap)

v1 (2026-06-28) established cleanup-family discrimination at FIXED M=300. USER-directed 2026-07-03 substrate-mine identified open Stage 1 phase-diagram gap: **M is a natural physics axis** (codebook capacity / interference at retrieval). Existing chain-grade physics laws (SCALE_FREE in N; TOPOLOGY_FREE in encoder) are AXIS-of-substrate laws. Adding a THIRD axis (M) tests whether cleanup mechanism robustness is likewise scale-free with respect to codebook size, OR whether classical-vs-modern Hopfield's *capacity* difference (0.14N ceiling for classical) creates a fundamentally different M-scaling curve.

**Theoretical prediction (THEORETICAL@ sqrt(2 log M / N) CRLB):**
- Modern_hopfield / iterative_cosine / soft_energy_attractor: matched-filter noise floor `sqrt(2 log M / N)`; cliff position drifts smoothly LEFT as M grows (log(M) growth); **SMOOTH monotonic curve** predicted.
- Classical_hopfield: Hebbian capacity ~0.14N; below ceiling, works; above ceiling, spurious minima dominate → **DISCONTINUOUS phase transition** at M ≈ 0.14 N (M ≈ 287 at N=2048; M ≈ 1147 at N=8192).

**Physics-law claim (HARD_PASS_CG_META tier eligibility):** cleanup mechanism performance follows a SMOOTH, MONOTONIC function of M across all (N, c, iters) for the 3 non-Hebbian cleanups — proving M-axis is analogous to N-axis (SCALE_FREE). Classical Hopfield's capacity-bounded regime becomes a documented MEASURED_BOUND (not a physics-law violation; it's a known Hebbian property).

## Compute architecture

Class: **(a) batched-GPU** for FULL dispatch (M-sweep phase points are independent; matmul-heavy → GPU-natural). SMOKE runs local CPU (24 pts, ~30-60s wall).

Storage strategy: **no_storage** — cleanup mechanism reads a codebook X and cleans a corrupted query. No PartitionedStore, no chain composition. Cell is pure primitive-benchmark.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| cleanup_family (OUTER) | {modern_hopfield, classical_hopfield, iterative_cosine, soft_energy_attractor} | 4 |
| **M** (NEW inner outer) | {100, 200, 400, 800, 1600, 3200} | 6 |
| N (inner) | {2048, 8192} | 2 |
| corruption_frac (inner) | {0.20, 0.45, 0.475} | 3 |
| cleanup_iters (inner) | {1, 5} | 2 |

M-sweep values log-scale (×2). c values BRACKET CRLB cliff at both N (easy 0.20 for positive control; cliff-adjacent 0.45 for M-discrimination at N=2048; near-cliff 0.475 for M-discrimination at N=8192).

**Cardinality FULL per seed:** `4 × 6 × 2 × 3 × 2 = 288` phase points per seed.
**Cardinality SMOKE per seed:** `4 × 3 × 1 × 2 × 1 = 24` corner points (M ∈ {100, 800, 3200}, N=2048, c ∈ {0.20, 0.45}, iters=1).

Seeds: 11, 17, 23 (chunked; 3 sibling files). Total FULL grid: 288 × 3 = 864 phase points.

## Hypothesis

**H1 (PRIMARY, physics-law eligible): 3 non-Hebbian cleanups exhibit SMOOTH monotonic top1(M) at fixed (N, c, iters).** Cliff location drifts LEFT with log(M) as CRLB predicts. No abrupt phase transitions. 3-seed replication required.

**H2 (COMPLEMENTARY, measured bound): Classical Hopfield exhibits DISCONTINUOUS phase transition at M ≈ 0.14 N.** Capacity-bounded regime; not a law violation (Hebbian property well-established); documents crossover M for classical vs modern.

**H3 (crossover): At some M in the sweep, the ranking of cleanups changes.** E.g., iterative_cosine may dominate at low M (small basins are easy); modern_hopfield may dominate at high M (softmax mixing helps when candidates crowd).

**H4 (null, unlikely): All 4 cleanups scale identically with M.** Would surprise; classical's capacity ceiling is well-established.

**H5 (positive control): modern_hopfield @ N=8192, M=100, c=0.20, T=5 must reproduce top1 >= 0.90.** Small-M easy-regime; must nail. Smoke variant: modern_hopfield @ N=2048, M=100, c=0.20, T=1 → top1 >= 0.85.

## Sharp theoretical predictions per mechanism (Director lit-drill 2026-07-03)

Cite exact formulas per `feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03`. Do not abstract; the specific numbers are the falsifiable content.

| Mechanism | M_crit at N=2048 | M_crit at N=8192 | Curve shape (low c) |
|---|---|---|---|
| modern_hopfield | > 10^6 (Ramsauer exp(N/2)) | > 10^6 | FLAT top1 ≈ 1.0 across whole sweep at easy c |
| classical_hopfield | ≈ 286 (AGS alpha_c=0.138·N) | ≈ 1147 | SHARP cliff between M=200 and M=400 (N=2048) at cliff-adjacent c |
| iterative_cosine | ≈ 134.30 (Plate N/(2 ln N)) | ≈ 455.85 | gentle roll-off at cliff-adjacent c; Plate applies to random-query recall (ARM_RANDOM), not corrupted-source ARM_MECHANISM; per-arm distinct behavior expected |
| soft_energy_attractor | tracks modern_hopfield | tracks modern_hopfield | flat at low c; damped update behavior at high c untested |

M_crit_locator(mechanism, N) function encodes these in `_v2_core.py:M_crit_locator`.

## 6 falsifiable HARD_PASS_CG_META criteria (all in metrics.json cg_meta_predictions)

**P1_ordering_high_M** — at M=3200, N=8192, c=0.475 (near cliff for N=8192), T=5:
`top1(modern_hopfield) - top1(classical_hopfield) >= 0.40`
Citation: `T2/modern_hopfield_ramsauer` vs `T2/amit_gutfreund_sompolinsky_capacity`.
HARD-FAIL if reversed; MIDDLE_BAND if gap 0.10-0.40; HARD_PASS if >= 0.40.

**P2_AGS_cliff_classical** — classical_hopfield at N=2048, c=0.20, T=1: monotone drop crossing 0.50 between M=200 and M=400 (AGS alpha_c=0.138 → M_crit=286 sits between).
Citation: `T2/amit_gutfreund_sompolinsky_capacity`.
NOTE: at easy c=0.20 argmax matched-filter dominates crosstalk; MEASURED cliff empirically emerges at CLIFF-ADJACENT c=0.45 (SMOKE observed classical M=100→0.960 M=3200→0.129 at c=0.45 N=2048). P2 as stated at c=0.20 may show None (all M saturate); FULL includes measurement at c=0.45 through the P6 capacity-relative gate.

**P3_Plate_iterative_cosine** — Plate bound N/(2 ln N)=134 at N=2048 for RANDOM-query recall regime; at cliff-adjacent corruption where signal ~ noise, iterative_cosine's basin behavior approaches Plate. Falsifiable form: at N=2048 c=0.45 T=1, `top1(M=100) - top1(M=400) >= 0.15` (Plate onset).
Citation: `Plate 1995 N/(2 ln N)`.

**P4_scale_invariance_modern** — `top1(modern_hopfield, N=2048, M) ~ top1(modern_hopfield, N=8192, 4·M)` within +/- 0.05 across M grid (Ramsauer exponential capacity → no N-dependence in accessible M range).
Citation: `T2/modern_hopfield_ramsauer`.

**P5_META_RULE_W_capacity_sweep_exemption** — declared. Alpha M/N spans [0.012, 1.56] intentionally crossing [0.03, 0.20] safe band; crosstalk wall is INFORMATIVE per the physics claim. Metrics field records the exemption with rationale.
Meta-rule reference: `capacity_cell_gate_must_be_capacity_relative_not_fixed_M` (2026-06-20).

**P6_capacity_relative_classical** — classical gates evaluated on `M / M_crit(classical, N)` ratio, not fixed M. Expected: at ratio < 0.7 top1 >= 0.80 at easy c; at ratio > 1.5 top1 <= 0.50 at cliff-adjacent c. Metrics per-point `m_over_m_crit` field enables this.
Meta-rule reference: `capacity_cell_gate_must_be_capacity_relative_not_fixed_M`.

## Pre-reg bands (per-point; LOCKED at module init)

| Tier | top1_mechanism | Discriminator (mech - random) |
|------|----------------|-------------------------------|
| SATURATED | >= 0.95 | record but down-weight |
| HARD_PASS | [0.80, 0.95) | >= 0.50 |
| MIDDLE_BAND | [0.50, 0.80) | >= 0.30 |
| HARD_FAIL | (0.10, 0.50) | mechanism breaking |
| FLOOR | <= 0.10 | substrate at chance |

## Physics-law tier (HARD_PASS_CG_META eligibility criterion)

For each of the 3 non-Hebbian cleanups {modern_hopfield, iterative_cosine, soft_energy_attractor} at each (N, c, iters) combination:

1. **Monotonicity:** `top1(M)` monotone non-increasing as M grows (small increases allowed only within 3-seed noise; monotone check on 3-seed mean with 1-seed exception allowance if 2-seed monotone).
2. **Smoothness:** no adjacent-M jump larger than max(0.15, 2 × 3-seed stddev at either endpoint).
3. **Scale-free character:** cliff position (smallest M where top1 < 0.50 at c=0.50, iters=1) shifts LEFT with N as expected from `sqrt(2 log M / N)` — cliff at N=8192 is right of cliff at N=2048.
4. **3-seed replication:** all 3 seeds satisfy 1+2+3 independently; framing reports 3-seed agreement.

If all 3 non-Hebbian cleanups satisfy 1-4 across all (N, c, iters): **physics-law CG_META tier eligible** for a `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` atom (chain-grade only after Skunkworks landed-VET).

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_M_SCALING_LAW**: cardinality_ok + arms_differ + 4-cleanup-distinct + positive_control_pass + all 3 non-Hebbian cleanups satisfy monotonicity+smoothness+scale-free criterion (physics-law-eligible; Skunkworks re-tiers to CG_META if 3-seed agreement)
- **HARD_PASS_M_CROSSOVER**: non-monotone-between-cleanups (curves cross between mechanisms; regime crossover measured; measured-bound tier)
- **MIDDLE_BAND_CLASSICAL_CAPACITY_CONFIRMED**: non-Hebbian smooth-monotone but classical shows expected phase transition at M ~ 0.14N (measured bound for classical; law confirmed for 3 non-Hebbian)
- **MIDDLE_BAND_NOISY_M_SCALING**: monotonicity fails on 1-2 mechanisms due to 3-seed noise; measured bound recorded
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 288
- **HARD_FAIL_ARMS_IDENTICAL**: any cleanup's mech==random hash
- **HARD_FAIL_CONTROL_FAIL**: modern_hopfield @ small-M easy regime doesn't reproduce
- **HARD_FAIL_NAN_OR_NON_MONOTONIC_COLLAPSE**: mechanism collapse at some M without theoretical explanation

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 24/24 corner points + arms_differ + 4-distinct-cleanups + positive_control (modern_hopfield @ N=2048, M=100, c=0.20, T=1 → top1 >= 0.85) + M-monotonicity observable (at c=0.50, top1 at M=100 > top1 at M=3200 for at least 2 of the 3 non-Hebbian cleanups)
- **HARD_FAIL_SMOKE_CLEANUP_COLLAPSE**: 2+ cleanups produce identical hashes
- **HARD_FAIL_SMOKE_CONTROL_FAIL**: positive control fails
- **HARD_FAIL_SMOKE_NO_M_DISCRIMINATION**: at c=0.50, top1 identical (within 0.05) across all 3 M values for ALL 4 cleanups → M-axis not discriminating; abort FULL
- **HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE**: all 24 pts saturate at 1.0 or floor at 0.0 → smoke regime doesn't exercise cliff; re-spec

## Selftest (cleanup mechanism sanity + M-cardinality + CRLB)

Inherits v1 selftest logic. Additionally:
1. Cardinality math: FULL_N = 288, SMOKE_N = 24
2. CRLB shift with M: `crlb_cliff(N=2048, M=100)` > `crlb_cliff(N=2048, M=3200)` (cliff must shift LEFT with M)
3. Identity check at c=0.0 (all 4 cleanups preserve clean input) — for all M ∈ smoke set
4. Easy-regime c=0.10 recovery >= 0.5 for all 4 cleanups at M=20 N=512

## META_RULE_W (alpha-gate) capacity-sweep exemption

Alpha_c = 0.138 (AGS) is the classical Hopfield storage threshold; the [0.03, 0.20] safe band from META_RULE_W (2026-06-27) is a discipline to avoid unintentional crosstalk saturation in capacity-neutral cells. **This cell is INTENTIONALLY a capacity sweep** — its PURPOSE is to probe across alpha={M/N} spanning [0.012 (M=100/N=8192), 1.56 (M=3200/N=2048)]. The crosstalk wall for classical is the physics being measured, not a design flaw. Skunkworks: honor the exemption declared in metrics `cg_meta_predictions.P5_META_RULE_W_capacity_sweep_exemption`.

## CRLB / capacity-feasibility (META_RULE_AG)

```python
noise = sqrt(2 * log(M) / N)
cliff_1step = 0.5 * (1 - noise)
```

MEASURED shifts across the sweep (THEORETICAL@ above formula):

| N | M=100 | M=400 | M=1600 | M=3200 |
|---|-------|-------|--------|--------|
| 2048 | 0.466 | 0.446 | 0.432 | 0.425 |
| 8192 | 0.483 | 0.472 | 0.464 | 0.460 |

Classical Hopfield capacity `M_cap ≈ 0.14 N`:
- N=2048: cap ≈ 287 → classical fails at M ∈ {400, 800, 1600, 3200}
- N=8192: cap ≈ 1147 → classical fails at M ∈ {1600, 3200}

**Discriminator reachability:** HARD_PASS band (top1 >= 0.80) is achievable for the 3 non-Hebbian cleanups at c=0.20 across all M values (well below cliff). At c=0.50 (at cliff), we EXPECT top1 to fall into HARD_FAIL/MIDDLE_BAND band — this is the physics measurement, not a design flaw.

**discriminating_fraction prediction:** modern_hopfield ~0.42, iterative_cosine ~0.38, soft_energy ~0.38, classical ~0.28 (classical FLOOR at high M drags mean down). Overall discriminating_fraction ~ 36/288 = 0.125 — this is per-cleanup-per-N-per-c-per-iter fraction; overall gate is n_disc >= 60/288 (0.21 fraction) for FULL HARD_PASS.

Overall discriminator-fires-at-smoke gate: at c=0.50 (cliff-adjacent), NON-Hebbian cleanups should show top1 DIFFERENTIATION between M=100 (near saturation) and M=3200 (near cliff) of at least 0.20 for at least 2 of the 3 non-Hebbian cleanups.

## Arms per point (META_RULE_AF)

Each (cleanup, M, N, c, T) point logs TWO arm results:
1. `ARM_MECHANISM` — cleanup's PC top1 on corrupted source
2. `ARM_RANDOM_FLOOR` — fresh-random codebook entry instead of corrupted source; floor ~1/M

**arms_differ_sha256** per cleanup: SHA-256 of packed mech vs random output-bytes across all M/N/c/T for that cleanup. All 4 cleanups must have mech-hash != random-hash.

**cleanup_pair_hashes** (META_RULE_AF extension): SHA-256 per cleanup across sweep; at least 4 distinct hashes required for the sweep to be meaningful.

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 24 (4 x 3 x 1 x 2 x 1)
FULL : EXPECTED_N_UNITS = 288 (4 x 6 x 2 x 3 x 2)
```

`cardinality_ok: True` required for any non-HARD_FAIL verdict.

## SCHEMA-VET pre-dispatch checklist

- `cardinality_ok`: True (verified at smoke)
- `arms_differ_verified`: True (SHA-256 check at smoke)
- `crlb_floor_computed`: MEASURED@ per (N, M) via `crlb_1step_cliff_prediction`
- `crlb_formula_reference`: `sqrt(2 log M / N)` THEORETICAL matched-filter CRLB
- `discriminator_reachability`: True — HARD_PASS band achievable at low c / low M
- `discriminating_fraction`: predicted ~0.21 overall; >= 0.10 required at smoke
- `baseline_in_band`: N/A — RANDOM_FLOOR arm expected at 1/M (near 0); this is a floor not a discriminator baseline
- `sweep_alignment_verdict`: ALIGNED — M appears in both codebook construction AND softmax normalization (effective and nominal M identical)
- `bracket_includes_discriminating_band`: 6 M values, 3 c values → per-point predictions span [0.05, 0.99]; ~40% predicted in [0.30, 0.70] discriminating band
- `composition_edges`: N/A (single-primitive cell, no composition)
- `positive_control_arms`: modern_hopfield @ small-M easy regime (see H5)
- `functional_requirements`: (a) codebook lookup at capacity, (b) noise-tolerance under corruption, (c) monotone scaling with M
- `cell_chunked`: True (3 sibling files)
- `start_marker_written`: True
- `crash_diagnostic_present`: True (outer try + write_import_crash_sentinel)
- `heartbeat_present`: True (per-phase-point flush print; also `_heartbeat.jsonl` optional via CellHeartbeat if wall > 15min)
- `defensive_error_checking`: passed_all_4_patterns
- `final_metrics_atomicity`: `tmp_replace` (via _seed_checkpoint.write_metrics)
- `progress_logging`: `print_flush_true` (per-phase-point flush)
- `progress_cadence_expected_s`: 60 (heartbeat approx per phase point)

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s{11,17,23}.py`.
Shared core: `experiments/_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py`.

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker
2. crash-diag import-crash sentinel with traceback
3. per-unit checkpoint via write_partial_key
4. heartbeat: per-phase-point flush print

## ETA

Per-point on CUDA (torch): ~10-100 ms depending on (N, M). Full seed = 288 pts × ~50 ms avg = ~15 s science + 30 s init = ~1 min/seed on GPU. **BUT** modern Hopfield at M=3200, N=8192, T=5: full matmul (M, N)*(N, M)=M^2 = ~10M elements per iter × 5 iters × 2 arms = 100M elements. On CPU ~30s/point; on GPU ~100ms. Full-seed CPU estimated ~2-3 h; GPU ~1-3 min.

Smoke on CPU (24 pts, N=2048, M<=3200, iters=1): ~1-2s per point → total ~30-60s + ~10s init.

Timeouts:
- SMOKE: 300 s
- FULL: 1800 s (30 min GPU margin; expected 1-15 min; classical at large M may be slow due to N×N W matmul)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit.

## Outputs

`data/exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s{11,17,23}/metrics.json` with:
- `phase_map`: 288 dicts (one per phase point) with `cleanup_family, N, M_items, corruption_frac, cleanup_iters, top1_mechanism, top1_random, discriminator, mech_output_hash, rnd_output_hash, verdict_tier_per_point, crlb_1step_cliff_prediction`
- `per_cleanup_M_summary`: per-cleanup per-M mean top1; monotonicity flag per (N, c, iters) sweep
- `physics_law_check`: dict with `{monotonic_pass_per_cleanup, smoothness_pass_per_cleanup, scale_free_shift_pass_per_cleanup, cg_meta_tier_eligible}`
- `crossover_analysis`: per (N, c, iters), which cleanup ranks best at each M
- `classical_capacity_crossover`: measured M value where classical drops below 0.50 at c=0.20 iters=1
- `crlb_predictions`: per (N, M) 1-step cliff
- `positive_control_result`
- `arms_differ_per_cleanup`
- `cardinality_ok`, `expected_n_units`, `observed_n_units`

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_M_SCALING_LAW: `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` atom (CG_META tier if 3-seed agreement)
- if MIDDLE_BAND_CLASSICAL_CAPACITY_CONFIRMED: `MEASURED_BOUND_classical_Hopfield_capacity_ceiling_0.14N` atom
- if HARD_PASS_M_CROSSOVER: `MEASURED_CROSSOVER_cleanup_ranking_by_M` atom with per-regime winner
