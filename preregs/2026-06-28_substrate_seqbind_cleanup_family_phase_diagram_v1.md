# Pre-registration: substrate_seqbind_cleanup_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive (Research, 2026-06-28) -- FOURTH systematic COMPONENT-SUBSTITUTION phase diagram in the substrate program. Sister cells already landed:
- `substrate_pc_encoder_family_phase_diagram_v1` (encoder OUTER axis, PC primitive) -- HARD_PASS
- `substrate_seqbind_encoder_family_sweep_v1` (encoder OUTER axis, seqbind primitive) -- LANDED
- `substrate_pc_cleanup_family_phase_diagram_v1` (cleanup OUTER axis, PC primitive) -- FULL 3-seed MIDDLE_BAND convergent

USER lesson from PC cleanup-family: substrate handles cleanup family-invariant at PC scale (all 4 cleanups produced near-identical top1 at scale; classical_hopfield was the only mild outlier). **Different primitive may show different cleanup family dependencies.** This cell tests that hypothesis on the chain-grade `sequence_binding` K-cliff primitive.

## Anchor

`substrate_seqbind_cleanup_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_seqbind_cleanup_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct invocation, then `local_cpu_queue` for traceability)
- **Full queue:** **remote_cpu_queue** (cpu_runner_0 IDLE per USER; cell is NumPy-light -- FFT + matmul, no GPU advantage)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes via hd_metrics_sync push -> Orchestrator queue_add (Director-mediated).

## Why this cell exists (the gap)

Substrate's `sequence_binding` chain-grade primitive (HRR-style FFT-circular-convolution + bipolar codebook + iterative_cosine cleanup) inherits **iterative_cosine top1 readout** as the unaudited cleanup default at every chain-grade evidence point (sequence_binding 586 + multi-hop chains + role-binding cells). The cleanup choice has NEVER been independently audited as "best" for SEQBIND.

**PC cleanup-family result (sister cell):** substrate handles cleanup family-invariant at PC scale. Convergent MIDDLE_BAND.

**Hypothesis here:** SEQBIND may show DIFFERENT cleanup dependency than PC because:
- SEQBIND's cleanup operates on the unbind OUTPUT (noisy + crosstalk from K-1 other bound items)
- PC's cleanup operates on a directly corrupted codeword (bit-flip noise)
- Crosstalk noise has DIFFERENT distribution than bit-flip noise (continuous-Gaussian-like vs binary)
- Modern_hopfield's softmax-mixing might handle Gaussian crosstalk BETTER than iterative_cosine's pure-argmax-snap (which is greedy under contested argmax)
- OR: K-cliff is so steep that ALL cleanups fall together (substrate cleanup-family-invariant for SEQBIND too)

## Cleanup families (the OUTER axis)

Substituted at the READOUT step (after FFT-unbind). The unbind step itself is identical across all 4 cleanups (FFT-circular-convolution + complex-conjugate; seqbind v2 idiom). Only the codeword-snap step varies.

| Family | Update rule | Capacity | T (iters) |
|--------|-------------|----------|-----------|
| `modern_hopfield` | `Q_t+1 = sign(softmax(beta * Q_t @ X.T) @ X)` | exponential | 1 |
| `classical_hopfield` | `Q_t+1 = sign(Q_t @ W)` where `W = X.T @ X / V_items` (Hebbian; zero diag) | ~0.14 * N | 1 |
| `iterative_cosine` | `Q_t+1 = X[argmax(Q_t @ X.T)]` (snap to nearest; SEQBIND v2 default; POSITIVE CONTROL) | V_items | 1 |
| `soft_energy_attractor` | `Q_t+1 = sign(Q_t + alpha * (softmax(beta * Q_t @ X.T) @ X - Q_t))` (alpha=0.5) | comparable to modern | 1 |

**Encoder FIXED** (bipolar +/-1 codebook; NO L2 normalization; seqbind v2 idiom). Bind/unbind FIXED (FFT-circular-convolution). Score function = `cleaned_vector @ items_book.T` (identical across all 4 cleanup arms).

`beta=8.0` (matches PC cleanup-family cell + seqbind v2). `alpha=0.5` (soft_energy_attractor mixing rate). `CLEANUP_ITERS=1` (matches seqbind v2 idiom).

**Apples-to-apples:** corruption (tag_noise) identical per seed; positions + items + Q_noise identical; bundle S identical; only the FINAL cleanup mechanism varies.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| cleanup_family (OUTER) | {modern_hopfield, classical_hopfield, iterative_cosine, soft_energy_attractor} | 4 |
| K (inner; bundle size) | {20, 100, 500} | 3 |
| N (inner; dim) | {1024, 4096, 8192} | 3 |

Fixed: `Q_level=2` -> `tag_density_effective=0.2`; `V_items=V_pos=1000`; `n_queries_full=100`; `n_queries_smoke=4`; `beta=8.0`; `alpha=0.5`; `cleanup_iters=1`.

**Cardinality FULL per seed:** `4 * 3 * 3 = 36` phase points.
**Cardinality SMOKE per seed:** `4 * 1 * 2 = 8` corner points (K=20; N in {4096, 8192}).

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files).

Total grid: 36 pts x 3 seeds = 108 phase points FULL.

## Hypothesis

**H1 (PRIMARY): Cleanup families WILL differ at the K-cliff regime for SEQBIND.** Predictions:
- `iterative_cosine` (POSITIVE CONTROL): K-cliff at K_cliff_pred(N) ~ N / (2 log V_items). N=1024 -> ~74; N=4096 -> ~297; N=8192 -> ~594. At K=20: SAT for all N. At K=100: cliff at N=1024, SAT at N>=4096. At K=500: FLOOR at N=1024, cliff at N=4096, SAT at N=8192.
- `modern_hopfield`: similar at low contestation (K=20); MAY OUTPERFORM iterative_cosine at K=100-500 where unbind output is noisy and softmax-mixing averages across plausible candidates rather than greedy snap.
- `classical_hopfield`: capacity-bound. At V_items=1000, N=1024 -> V/N=0.98 >> 0.14 (over capacity; spurious minima dominate). At N=4096 -> 0.24 (still over). At N=8192 -> 0.12 (approaching capacity). Predicted DOMINATED at low N; CATCHES UP at N=8192.
- `soft_energy_attractor`: similar to modern_hopfield with smoother basin (alpha-damping).

**H2 (modern WINS at K cliff):** modern_hopfield > iterative_cosine at contested K (K=100, N=1024 OR K=500, N=4096). Specifically because softmax-mixing handles unbind crosstalk better than pure argmax-snap.

**H3 (positive control):** `iterative_cosine` at (K=20, N=8192, Q=2) must reproduce seqbind v2 chain-grade evidence: SUBSTRATE_top1 >= 0.50. If control fails, cleanup-discrimination harness is broken; cell HARD_FAILs with CONTROL_FAIL.

**H4 (null -- substrate cleanup-family-invariant for SEQBIND too):** All 4 cleanups produce top1 within +/- 0.05 at every (K, N). If H4 holds, mirrors PC cleanup-family result and would confirm substrate's cleanup-mechanism-invariance is GENERAL (not PC-specific).

**H5 (dominance):** One cleanup strictly dominates. Would promote that cleanup as new default and trigger atomization of `WINNING_CLEANUP_FOR_SEQBIND`.

## Discriminator: 3 arms (SUBSTRATE / RANDOM / SHUFFLE)

Each (cleanup, K, N) phase point runs:
1. **ARM_SUBSTRATE**: bind K (pos, item) pairs into bundle S; unbind correct query positions; cleanup; top1 readout
2. **ARM_RANDOM**: random unit vector through SAME cleanup pipeline (no bundle)
3. **ARM_SHUFFLE**: same bundle S; unbind SHUFFLED (wrong) query positions; cleanup; top1 readout

`arms_diff = SUBSTRATE_top1 - max(RANDOM, SHUFFLE)`.

## Pre-reg bands (per-point; LOCKED)

| Tier | SUBSTRATE_top1 | arms_diff | Comment |
|------|----------------|-----------|---------|
| SATURATED | >= 0.90 | record but down-weight | substrate solves easily |
| HARD_PASS | > 0.70 | >= 0.30 | clear discrimination |
| MIDDLE_BAND | [0.30, 0.70] | >= 0.15 | cliff / partial |
| TRANSITION | (0.10, 0.30) U (0.70, 0.90) | -- | gap between bands |
| FLOOR | <= 0.10 | -- | substrate at chance |

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_CLEANUP_DISCRIMINATION_SEQBIND**: cardinality_ok (36/36) + arms_differ for ALL 4 cleanups + n_pairs_differ >= 2/6 + n_discriminating >= 12/36 + avg_arms_diff >= 0.15 + positive_control PASS + interior K-cliff observable for at least 1 cleanup
- **MIDDLE_BAND_CLEANUP_DIFFERS_BUT_NO_K_CLIFF**: cleanups distinguish but no interior K-cliff
- **MIDDLE_BAND_CLEANUP_DIFFERS_PARTIAL**: arms_differ + pairs_differ >= 2 but n_disc < 12 or avg_diff < 0.15
- **MIDDLE_BAND_NULL_CLEANUP_INVARIANCE**: all 4 cleanup pair hashes identical (H4 confirmed -- SUBSTRATE cleanup-family-invariant for SEQBIND too)
- **MIDDLE_BAND_SPARSE**: low disc, low pairs_differ
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 36
- **HARD_FAIL_ARMS_IDENTICAL**: mech and random hashes match for any cleanup
- **HARD_FAIL_CONTROL_FAIL**: iterative_cosine positive control doesn't reproduce seqbind v2

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 8/8 corner points + arms_differ for all 4 cleanups + 6 distinct cleanup-pair hashes + positive_control PASS + at least 1 cliff-edge point per cleanup
- **HARD_FAIL_SMOKE_CARDINALITY_BREACH**: not 8/8
- **HARD_FAIL_SMOKE_CLEANUP_COLLAPSE**: 2+ cleanups identical hashes
- **HARD_FAIL_SMOKE_CONTROL_FAIL**: positive control fails
- **HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE** (USER 2026-06-26): smoke at chosen N shows no cliff-edge per cleanup -- abort FULL

## Calibration selftest (cleanup mechanism sanity)

For each cleanup at N=512, V_items=20:
- **Identity:** feed exact codeword 0 -> top1 == 0 (cleanup mustn't break clean)
- **Recovery:** feed codeword 0 + small Gaussian noise -> top1 == 0

Then: contested-input test. mix = 0.4*X[0] + 0.35*X[1] + 0.30*X[2] + noise; all 4 cleanups should produce DISTINCT cleaned bipolar outputs (SHA-256 hashes differ).

## Theoretical K-cliff prediction (META_RULE_AG)

For random bipolar bundle of K bound pairs, unbind produces signal ~ 1 codeword + crosstalk noise std ~ sqrt(K-1)/sqrt(N). Argmax-cleanup succeeds when signal_mag > sqrt(2 log V_items) * noise_std:

```python
K_cliff_approx = N / (2 * log(V_items))
# N=1024, V=1000 -> K_cliff ~ 74
# N=4096, V=1000 -> K_cliff ~ 297
# N=8192, V=1000 -> K_cliff ~ 594
```

This is for iterative_cosine (1-step argmax = matched filter). Other cleanups may shift cliff +/- by their basin-shaping properties.

## Arms per point (META_RULE_AF)

Each (cleanup, K, N) point logs THREE arm results:
1. `SUBSTRATE_top1_recall` -- correct query, correct unbind, cleanup, top1
2. `RANDOM_top1_recall` -- random unit vector, cleanup, top1 (~1/V_items)
3. `SHUFFLE_top1_recall` -- same bundle, shuffled (wrong) query positions, cleanup, top1

**arms_differ_per_cleanup**: SHA-256 hash of mechanism output bytes per cleanup; must differ from random hash for each cleanup.

**cleanup_pair_distinctness**: 6 pair-wise SHA-256 comparisons; chain-grade HP requires >= 2 differ.

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 8 (4 cleanups x 1 K x 2 N)
FULL : EXPECTED_N_UNITS = 36 (4 cleanups x 3 K x 3 N)
```

HARD_FAIL if observed != expected.

## Compute routing (Fix #24 N/A)

NumPy-only cell (FFT + matmul); no GPU advantage. CPU-natural.

- No `import torch` at top of file required (NumPy-only path); torch optional for backend label
- All compute via numpy (matches seqbind v2 idiom)
- No GPU mandate

Routes to `remote_cpu_queue` post-smoke (cpu_runner_0 IDLE per USER).

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_seqbind_cleanup_family_phase_diagram_v1_seed_{7,13,19}.py`.
Shared core: `experiments/_substrate_seqbind_cleanup_family_phase_diagram_v1_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py`.

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker: STARTED metrics before heavy work
2. crash-diag: outer try -> import-crash sentinel with full traceback
3. per-unit checkpoint: write_partial_key per seed
4. heartbeat: per-phase-point flush print

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (mechanism vs random; per-cleanup)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 cleanup arms produce distinct hashes (else cleanup substitution didn't happen)
- META_RULE_AG: per-cleanup CRLB / K-cliff pre-validation in Python
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_AP (recency-decode floor / Pareto gate): bands set so RANDOM arm cannot accidentally clear MB threshold; RANDOM ~ 1/V_items = 0.001 << BAND_FLOOR = 0.10. avg_arms_diff floor 0.15 prevents Pareto-tied bands from passing HP.
- META_RULE_H: cardinality_ok mandatory (36 full, 8 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at chosen N shows cliff-edge per cleanup -- abort if not
- Honest-downward classification per cleanup
- Substrate-as-canonical query-first: seqbind v2 chain (commit lineage) reviewed; encoder-family seqbind cell in flight; PC cleanup-family LANDED MB convergent; this cell SUBSTITUTES cleanup ON SEQBIND not encoder

## Positive control

`iterative_cosine` (SEQBIND v2 default) at (K=20, N=8192, Q=2) must reproduce SEQBIND chain-grade evidence: SUBSTRATE_top1 >= 0.50 at this point. If control fails: cell HARD_FAILs with verdict CONTROL_FAIL.

Smoke-variant: same point, top1 floor 0.40 (4-query coarse).

## Composition edges (substrate atomization context)

- This cell uses FIXED bind/unbind (FFT-circular-convolution) + FIXED encoder (bipolar) and SUBSTITUTES cleanup at READOUT.
- SHAPE_MATCH: each cleanup's input (Q, N) and output cleaned (Q, N); top1 idx (Q,). Identical across arms.
- Downstream atomization: HARD_PASS_CLEANUP_DISCRIMINATION_SEQBIND promotes winning cleanup for `sequence_binding` ROLE; informs role-binding + multi-hop chain cells' default-cleanup choice.

## ETA

Per-point (CPU): K=500 N=8192 with 100 queries ~ 5-10s (V_items=1000 dot products per query). 36 pts/seed * ~3s avg = ~2-4 min science + 30s init = ~3-5 min/seed FULL.
Smoke per-point at K=20 N=8192 with 4 queries ~ 0.5-1s. 8 pts/seed * 0.7s = ~6s science + 5s init = ~15s/seed SMOKE.

Timeouts:
- SMOKE: 180 s (1 min margin)
- FULL: 1800 s (30 min margin per seed; budget 3-5 min)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit (pure substrate; no LLM calls).

## Smoke gate (MUST pass before FULL dispatch)

1. 8 corner points all ran (no silent except)
2. cardinality_ok: observed_n_units == 8
3. arms_differ_sha256.differ == True for ALL 4 cleanups
4. cleanup_pair_hashes: 4 distinct cleanup mechanism hashes (6 pairs all differ)
5. positive_control: iterative_cosine @ K=20, N=8192, Q=2 shows top1 >= 0.40
6. cliff observable: at least 1 cleanup shows top1 in (FLOOR=0.10, SAT=0.90) per cleanup

If gates 1-6 fail, FULL dispatch is HARD-blocked.

## Cleanup-family routing tier classifications

- DOMINANT_CLEANUP: top1_mean > 0.10 above all other cleanups
- COMPETITIVE_CLEANUP: top1_mean within +/- 0.05 of best
- DOMINATED_CLEANUP: top1_mean > 0.10 below best

## Outputs

`data/exp_substrate_seqbind_cleanup_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` with:
- per_seed phase_map (one dict per phase point; SUBSTRATE / RANDOM / SHUFFLE recalls + tier)
- per_cleanup_summary (4 entries; top1_mean + tier_counts + K_cliff per N)
- cleanup_pair_distinctness (6 pair-comparisons)
- positive_control_result (iterative_cosine @ K=20, N=8192, Q=2)
- kanerva_K_cliff_predictions (per N)
- arms_differ_per_cleanup (SHA-256 mech vs random per cleanup)
- tier_counts overall

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_CLEANUP_DISCRIMINATION_SEQBIND: SUBSTRATE_CLEANUP_FAMILY_DISCRIMINATING_FOR_SEQBIND + WINNING_CLEANUP_FOR_SEQBIND
- if MIDDLE_BAND_NULL_CLEANUP_INVARIANCE: CLEANUP_NOT_DISCRIMINATING_LEVER_FOR_SEQBIND (mirrors PC cleanup-family; would establish substrate's cleanup-mechanism-invariance as GENERAL not PC-specific)
- if Modern dominant at K-cliff: MODERN_HOPFIELD_DOMINATES_SEQBIND_AT_K_CLIFF atom (substrate's cleanup default should change for SEQBIND)
