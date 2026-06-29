# Pre-registration: substrate_pc_cleanup_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive (Research, 2026-06-28) — THIRD systematic COMPONENT-SUBSTITUTION phase diagram. Sibling cells `substrate_pc_encoder_family_phase_diagram_v1` (encoder OUTER axis, PC primitive) and `substrate_seqbind_encoder_family_sweep_v1` (encoder OUTER axis, sequence-binding primitive) already in flight. This cell sweeps **CLEANUP FAMILY** as the OUTER axis on the **pattern completion** primitive, holding encoder fixed at `binary_bipolar` (PC v2.2 default).

## Anchor

`substrate_pc_cleanup_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_pc_cleanup_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct invocation, then `local_cpu_queue` for traceability)
- **Full queue:** **remote_cpu_queue** (cpu_runner_0 idle per USER; cell is light — only 4 cleanup families x 80 inner pts. Modern Hopfield + classical Hopfield + iterative cosine + soft-energy attractor are all matmul + softmax. binary_bipolar at N=8192 is the largest matmul. Estimated <15 min/seed CPU.)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via SendMessage post-smoke).

## Why this cell exists (the gap)

Substrate has ~30 levers across ~9 categories. Encoder is the most load-bearing; cleanup-attractor mechanism is the 2nd-most-load-bearing. Substrate inherits **modern-Hopfield softmax cleanup** with `beta=8.0` as the fixed default in ALL pattern-completion chain-grade work to date (PC v1/v2/v2.1/v2.2; cleanup-deeper-chains; modern-hopfield-prototype-attractor). The cleanup family choice has NEVER been independently audited as "best" for PC vs alternatives.

**Skunkworks earlier session note (Research context):** "Modern Hopfield wins at N drop" was an informal finding — modern Hopfield outperformed alternatives when N was small. This cell verifies systematically across the full PC corruption-cliff regime at multiple N.

**Cross-domain prior:** Classical Hopfield (sign(W q) with W = sum_i x_i x_i^T) is the historical Hebbian baseline. Iterative-cosine (no softmax; pick argmax cosine, replace with that codeword) is the simplest non-Hebbian cleanup. Soft-energy-attractor (gradient on continuous energy landscape with damping) is a smoother variant. All four families differ in: (a) update rule (Hebbian outer-product vs softmax-mix vs argmax-snap vs gradient), (b) capacity (classical ~0.14N; modern exponential), (c) basin shape (sharp vs smooth), (d) iteration dynamics (one-shot vs convergent).

## Cleanup families (the OUTER axis)

Four families, each with same input/output shape `(M, N)` but distinct mechanism:

| Family | Update rule | Capacity (approx) | Iteration |
|--------|-------------|-------------------|-----------|
| `modern_hopfield` | `Q_{t+1} = sign(softmax(beta * Q_t @ X.T) @ X)` (PC v2.2 default; POSITIVE CONTROL) | exponential in N | T iters |
| `classical_hopfield` | `Q_{t+1} = sign(Q_t @ W)` where `W = X.T @ X / M` (Hebbian outer product) | ~0.14*N | T iters async-sequential bits replaced with batched sign() per step |
| `iterative_cosine` | `Q_{t+1} = X[argmax(Q_t @ X.T)]` (snap to nearest codeword; no softmax mixing) | M (perfect within basin) | T iters |
| `soft_energy_attractor` | `Q_{t+1} = sign(Q_t + alpha * (softmax(beta * Q_t @ X.T) @ X - Q_t))` (gradient-on-mixed-target; alpha=0.5) | comparable to modern_hopfield | T iters |

Encoder is FIXED `binary_bipolar` across all 4 cleanup arms. Corruption model is bit-flip fraction `c`. Score is `Q @ X.T` (real, identical across all 4 cleanup arms).

`beta=8.0` (same as encoder-family cell; matches PC v2.2 default).
`alpha=0.5` for soft_energy_attractor (mixing rate).

**Why this is apples-to-apples:** corruption_frac `c` identical; encoder + codebook identical per seed; score function identical; M_items identical; N_dim identical. ONLY the cleanup mechanism's update rule differs.

**Selftest validation:** for each cleanup family at N=512, M=20, c=0.10, T=1 starting from corrupted query: at least 50% recovery to source. If any family fails this sanity, the cell HARD_FAILs at selftest before any phase points run. PLUS: at c=0.0 (no corruption), T=1 must recover 100% across all 4 (trivial identity check — cleanup mustn't break clean inputs).

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| cleanup_family (OUTER) | {modern_hopfield, classical_hopfield, iterative_cosine, soft_energy_attractor} | 4 |
| N (inner) | {2048, 8192} | 2 |
| corruption_frac (inner) | {0.20, 0.35, 0.45, 0.475, 0.50} | 5 |
| cleanup_iters (inner) | {1, 5} | 2 |

`M_items=300`, `beta=8.0`, `alpha=0.5` (soft_energy_attractor only), `encoder=binary_bipolar`.

**Cardinality FULL per seed:** `4 * 2 * 5 * 2 = 80` phase points per seed.
**Cardinality SMOKE per seed:** `4 * 1 * 3 * 1 = 12` corner points per seed (N=2048; corruption ∈ {0.20, 0.45, 0.50}; iters=1).

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files; matches encoder-family cell convention).

Total grid: 80 pts x 3 seeds = 240 phase points FULL (parallel to encoder-family cell scale).

## Hypothesis

**H1 (PRIMARY): Cleanup families WILL differ in cliff location AND/OR slope.**
- Prediction per family (HYPOTHESIZED@):
  - `modern_hopfield`: cliff at ~0.486 (N=8192), matches PC v2.2 (POSITIVE CONTROL — must reproduce)
  - `classical_hopfield`: cliff shifts LEFT (lower corruption tolerance). Classical Hopfield capacity ~0.14N means M=300 at N=2048 is at capacity (300/2048=0.146); spurious minima dominate; predicted cliff ~0.30-0.40 at N=8192 (where 300/8192=0.037 is well below capacity, so classical should improve)
  - `iterative_cosine`: cliff at ~similar to modern_hopfield in 1-step (both snap to nearest); but T=5 may show LESS improvement than modern (no softmax-averaging across multiple candidates). Predicted cliff ~0.46-0.49 at N=8192 across T.
  - `soft_energy_attractor`: cliff similar to modern_hopfield with potentially SMOOTHER transition (less abrupt cliff due to alpha-damping); predicted cliff ~0.46-0.48 at N=8192.

**H2 (N-effect — Skunkworks "Modern Hopfield wins at N drop"):** At N=2048 (smaller), modern_hopfield WIDENS its advantage over classical_hopfield because classical is at capacity (M=300, M/N=0.146 > 0.14). At N=8192, classical_hopfield CATCHES UP because M/N=0.037 << 0.14. Iterative_cosine and soft_energy_attractor relatively N-invariant.

**H3 (positive-control): `modern_hopfield` at (N=8192, c=0.475, T=5) reproduces PC v2.2 cited HP-recall.** If this control fails, the cleanup-comparison harness is broken; cell aborts with CONTROL_FAIL.

**H4 (null): All 4 cleanup families identical within +/- 0.05 top1 at EVERY (N, c, T) phase point.** If H4 holds, cleanup choice doesn't matter for PC — would be a load-bearing **negative** finding (downstream cells free to pick any cleanup; cleanup is NOT a discriminating lever for PC). Less likely than encoder-family H4 since cleanup mechanism differences are larger than encoder mechanism differences a priori.

**H5 (dominance): One cleanup family strictly dominates all others at all phase points.** If H5 holds, would be the strongest finding — substrate should switch default. Modern Hopfield is the candidate per Skunkworks informal note.

## Discriminator: per (cleanup, regime) vs random-floor

For each (cleanup, N, c, T) phase point: ARM_MECHANISM (the cleanup's PC top1) vs ARM_RANDOM (fresh-random codebook entry instead of corrupted source). Random ~ 1/M = 0.0033 ~ FLOOR.

**Per-cleanup discriminating_fraction prediction (HYPOTHESIZED@):**
- modern_hopfield: ~0.40
- classical_hopfield: ~0.25 (predicted weaker at N=2048; equal at N=8192)
- iterative_cosine: ~0.35
- soft_energy_attractor: ~0.35

**Discriminating_fraction (overall) >= 0.30** = pre-reg PASS threshold (>= 24/80 pts per seed in HARD_PASS+MIDDLE_BAND across all cleanups).

## Pre-reg bands (per-point; LOCKED at module init)

| Tier | top1_mechanism | Discriminator (mech - random) |
|------|----------------|-------------------------------|
| SATURATED | >= 0.95 | record but down-weight (Skunkworks Q-rule) |
| HARD_PASS | [0.80, 0.95) | >= 0.50 |
| MIDDLE_BAND | [0.50, 0.80) | >= 0.30 |
| HARD_FAIL | (0.10, 0.50) | mechanism breaking |
| FLOOR | <= 0.10 | substrate at chance |

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_CLEANUP_DISCRIMINATION**: cardinality_ok + arms_differ AND (per-cleanup hashes differ pairwise: at least 2 of the 6 cleanup-pair-hash comparisons must differ) AND >= 24/80 points in HARD_PASS+MIDDLE_BAND AND positive control reproduces (modern_hopfield @ N=8192, c=0.475, T=5: top1 >= 0.50) AND at least one cleanup shows interior cliff
- **MIDDLE_BAND_CLEANUP_DIFFERS_BUT_LOW_DISC**: arms_differ + cleanup-pair hashes differ but disc_pts < 24
- **MIDDLE_BAND_CLEANUP_DIFFERS_BUT_NO_CLIFF**: cleanup-pairs differ but no interior cliff at any cleanup
- **MIDDLE_BAND_NULL_CLEANUP_INVARIANCE**: arms_differ but ALL cleanup-pair hashes IDENTICAL (H4 confirmed — cleanups don't matter for PC; cell still useful as honest-negative; routes to Research as "cleanup NOT a discriminating lever for PC")
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 80
- **HARD_FAIL_ARMS_IDENTICAL**: substrate and random hashes match for any cleanup (mechanism not working)
- **HARD_FAIL_CONTROL_FAIL**: modern_hopfield positive control doesn't reproduce PC v2.2 (test rig broken; halt before any framing claims)

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 12/12 corner points + arms_differ + 4 distinct cleanup hashes (META_RULE_AF) + positive control (modern_hopfield @ N=2048, c=0.20, T=1) shows top1 >= 0.80 + cliff observable at c=0.45 (at least 1 cleanup has top1 in [0.10, 0.95])
- **HARD_FAIL_SMOKE_CLEANUP_COLLAPSE**: 2+ cleanups produce identical hashes at smoke (mechanism bug)
- **HARD_FAIL_SMOKE_CONTROL_FAIL**: positive control fails at smoke
- **HARD_FAIL_SMOKE_NO_DISCRIMINATION**: zero cells in HARD_PASS+MIDDLE_BAND tiers at smoke
- **HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE** (USER 2026-06-26): smoke at N=2048 shows zero cleanup cliff-edge values in [0.10, 0.95] for c=0.45 — abort FULL

## Calibration selftest (cleanup mechanism sanity)

For each cleanup ∈ {modern_hopfield, classical_hopfield, iterative_cosine, soft_energy_attractor} at N=512, M=20, seed:
- At c=0.0 (no corruption), T=1: top1 == 1.0 (cleanup doesn't break clean input; identity check)
- At c=0.10, T=1: top1 >= 0.5 (easy regime; all cleanups must recover most items)

If ANY cleanup fails calibration, selftest exit 1 with verdict_msg naming the failing (cleanup, c). This catches broken cleanup implementations at selftest time.

## CRLB / noise-floor prediction (META_RULE_AG)

For binary_bipolar encoder, noise floor for M_items random patterns:

```python
noise = sqrt(2 * log(M) / N)
cliff_1step = 0.5 * (1 - noise)
# N=2048 M=300 cliff ~ 0.464; N=8192 M=300 cliff ~ 0.482
```

CRLB applies to 1-step matched-filter retrieval. Modern Hopfield 1-step is exactly this. Classical Hopfield 1-step is matched-filter on covariance, NOT identical to CRLB (capacity-limited). Iterative cosine 1-step matches CRLB exactly (argmax over inner products). Soft-energy at T=1 with alpha=0.5 is a partial-step toward modern Hopfield's softmax-target.

Per-cleanup cliff prediction stamps `crlb_1step_cliff_prediction` (identity across all 4 — same encoder + M; difference appears in T>1 iteration).

## Arms per point (META_RULE_AF)

Each (cleanup, N, c, T) point logs TWO arm results:
1. `ARM_MECHANISM` — cleanup's pattern completion top1
2. `ARM_RANDOM_FLOOR` — fresh-random codebook entry instead of corrupted source, same cleanup pipeline; floor ~1/M

**arms_differ_sha256** per cleanup: SHA-256(json(mech.recall_per_point)) != SHA-256(json(random.recall_per_point)). All 4 cleanup arms must differ from their random.

**cleanup_pair_hashes** (META_RULE_AF extension): SHA-256(json(top1_per_point_for_cleanup_X)) for each cleanup. All 4 hashes computed; for chain-grade discrimination claim, at least 2 of the 6 pairs must differ. If ALL 4 identical, that's the H4 NULL finding.

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 12 (4 cleanups x 1 N x 3 corruption x 1 iters x 1 seed)
FULL : EXPECTED_N_UNITS = 80 (4 cleanups x 2 N x 5 corruption x 2 iters x 1 seed)
```

HARD_FAIL if observed != expected.

## Compute routing (Fix #24 note)

This cell is CPU-routable; CPU is sufficient. Cell uses `binary_bipolar` (float32) only — no complex64 — so GPU advantage is modest. Per USER context: cpu_runner_0 is idle and this is a "modest light cell."

- `import torch` at TOP of file (PROT-020 routing-gate)
- `DEVICE = torch.device("cuda")` preferred if available; CPU fallback ALLOWED for both smoke and full
- Codebook materialized once per (N, seed); cleanup is batched matmul throughout
- Per-point peak_mem_mb logged
- No GPU mandate; cell is CPU-natural

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_pc_cleanup_family_phase_diagram_v1_seed_{7,13,19}.py`.
Shared core: `experiments/_substrate_pc_cleanup_family_phase_diagram_v1_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py`.

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker: STARTED metrics written before any heavy work
2. crash-diag: outer try -> import-crash sentinel with full traceback
3. per-unit checkpoint: write_partial_key per seed
4. heartbeat: per-phase-point flush print

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (mechanism vs random; per-cleanup)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 cleanup arms produce distinct hashes (else cleanup substitution didn't happen)
- META_RULE_AG: per-cleanup per-point CRLB / overlap-floor pre-validation in Python
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_H: cardinality_ok mandatory (80 full, 12 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- META_RULE_M-S (USER 2026-06-24): production-scale calibration; verify-referent; 1.000 results suspect
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at N=2048 cliff-edge — abort if smoke shows no cliff
- BAND-FLOOR-IS-MIDDLE-BAND: clearing 24-MB threshold AND positive control reproducing AND >= 2 cleanup-pair-hashes differing — all three required for HARD_PASS
- Honest-downward classification per cleanup
- Substrate-as-canonical query-first: PC v1/v2/v2.1/v2.2 chain (commit `2daf9b55`) reviewed; encoder-family cell in flight; this cell SUBSTITUTES the cleanup, not the encoder

## Positive control

`modern_hopfield` at (N=8192, c=0.475, T=5) must reproduce PC v2.2 corruption-cliff measured value top1 >= 0.50 (PC v2.2 evidence: top1=0.55-0.65 at this point at seed 7, MEASURED@ commit 2daf9b55). If control fails: cell HARD_FAILs with verdict CONTROL_FAIL.

Smoke-variant positive control: `modern_hopfield` at (N=2048, c=0.20, T=1) must show top1 >= 0.80.

## Composition edges (substrate atomization context)

- This cell uses the existing FIXED encoder (binary_bipolar dense) and SUBSTITUTES the cleanup mechanism. SHAPE_MATCH: each cleanup's input shape (M, N) and output shape (M, N) identical across all 4 arms.
- Cleanup is the COMPONENT being swept; encoder is the COMPOSED-WITH-it primitive (unchanged across arms).
- Downstream atomization: HARD_PASS_CLEANUP_DISCRIMINATION promotes the winning cleanup for `pattern_completion` ROLE; informs downstream cells' default-cleanup choice.

## ETA

Per-point on CPU (N=8192, M=300, modern_hopfield T=5): ~3-6s. 80 pts/seed * ~4s = ~5-8 min science + 30 s init = ~6-10 min/seed FULL on CPU.

Per-point on CPU (smoke; N=2048, M=300): ~0.5-1s. 12 pts/seed * 0.7s = ~10s science + 10s init = ~20-30s/seed SMOKE on CPU.

Timeouts:
- SMOKE: 600 s (10 min margin per seed; budget 20-30s expected)
- FULL: 1800 s (30 min margin per seed; budget 6-10 min expected)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit (no LLM calls; pure substrate mechanism).

## Smoke gate (MUST pass before FULL dispatch)

1. 12 corner points all ran (no silent except)
2. cardinality_ok: observed_n_units == 12
3. arms_differ_sha256.differ == True for ALL 4 cleanups
4. cleanup_pair_hashes: 4 distinct cleanup mechanism hashes
5. positive_control: modern_hopfield @ N=2048, c=0.20, T=1 shows top1 >= 0.80
6. cliff observable: at least 1 cleanup shows top1 in [0.10, 0.95] at c=0.45
7. discriminator_pre_check: at least 1 point per cleanup in HARD_PASS/MIDDLE_BAND/HARD_FAIL transition band

If gates 1-6 fail, FULL dispatch is HARD-blocked. Gate 7 is informational.

## Cleanup-family routing tier classifications

Per-cleanup downstream verdict (informational; cell aggregator stamps these):
- DOMINANT_CLEANUP: top1_mean > 0.10 above all other cleanups (strong substitution case)
- COMPETITIVE_CLEANUP: top1_mean within +/- 0.05 of best
- DOMINATED_CLEANUP: top1_mean > 0.10 below best (downstream should NOT default to this cleanup for PC)

## Outputs

`data/exp_substrate_pc_cleanup_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` with:
- per_seed phase_map (list of dicts; one per phase point)
- per_cleanup_summary (4 entries; tier classification + top1_mean + cliff_locator + N-effect_indicator)
- cleanup_pair_distinctness (6 pair-comparisons)
- positive_control_result (top1 at modern_hopfield @ N=8192, c=0.475, T=5)
- crlb_predictions_1step (per N)
- arms_differ_sha256 (per cleanup)
- tier_counts per cleanup + overall
- skunkworks_n_drop_check: comparison of (modern_hopfield top1 at N=2048 vs N=8192) vs (classical_hopfield top1 at N=2048 vs N=8192). If modern_hopfield delta-N > classical delta-N, Skunkworks "Modern Hopfield wins at N drop" partially confirmed.

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_CLEANUP_DISCRIMINATION: SUBSTRATE_CLEANUP_FAMILY_DISCRIMINATING_FOR_PC + WINNING_CLEANUP_FOR_PC
- if MIDDLE_BAND_NULL_CLEANUP_INVARIANCE: CLEANUP_NOT_DISCRIMINATING_LEVER_FOR_PC
- if Skunkworks N-drop hypothesis confirmed at chain-grade: MODERN_HOPFIELD_DOMINANCE_GAINS_AT_LOW_N atom
- if HARD_FAIL: NEEDS-RERUN with smoke-gate-specified fix
