# Pre-registration: substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research handoff 2026-06-28 — v2.1 landed MEASURED_MECHANISM (commit `2daf9b55`; Skunkworks audit). 3 seeds x 72 = 216 phase points: 36 SAT + 0 HP + 6 MB + 24 FLOOR + 6 FAIL per seed. Cliff razor-sharp at corruption=0.48-0.50 across all N. Skunkworks recommended PROMOTION PATH: denser corruption grid in [0.46, 0.50] @ 0.005 step to populate cliff region with enough MIDDLE_BAND points to clear the >=22 MB chain-grade promotion threshold.

## Anchor

`substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}` (3 sibling files; chunked per USER 2026-06-28).

## Routing

- **Smoke queue:** local_cpu_queue (laptop is CPU-only; torch.cuda.is_available()=False; smoke uses CPU fallback)
- **Full queue:** local_cpu_queue (per USER dispatch instructions; HDLAB_QUEUE=local_cpu_queue env var allows CPU FULL run; bypasses GPU mandate for this promotion path)
- **Reason for CPU route:** v2.1 already executed FULL grid on CPU successfully; 180 pts x 1 seed each is tractable on CPU (~30-45 min per seed estimated; M_ITEMS=500, N up to 16384, 3 cleanup iters)
- **Push constraint:** harness-DENIED push from exp_dev for remote queues; local_cpu_queue does NOT require push

## Why v2.2 exists (v2.1 root cause)

v2.1 result: `data/exp_substrate_pattern_completion_corruption_cliff_v2_narrow_regime_seed_{7,13,19}/metrics.json`
- corruption_frac sweep = {0.40, 0.43, 0.46, 0.48, 0.50, 0.52} (6 points)
- Per-seed result: 36 SAT (corruption in {0.40, 0.43}) + 6 MB (corruption near 0.46) + 6 FAIL (corruption=0.48 intermediate band) + 24 FLOOR (corruption in {0.50, 0.52})
- Cliff razor-sharp at corruption=0.48-0.50 — transitions happen within 0.02 of corruption space
- Skunkworks-audited as MEASURED_MECHANISM: cell ran clean, but only 6 MB / 72 below 22 MB chain-grade threshold

ROOT CAUSE: corruption grid too sparse around the cliff. 6 of 6 points fall OUTSIDE the cliff transition zone (3 sat, 1 MB, 1 fail, 1 floor per N) — most of the dynamic range is wasted on already-saturated or already-floored regimes.

v2.2 fix: dense grid in [0.46, 0.50] @ 0.005 step (9 points) plus shoulders {0.43, 0.44, 0.45} (3 below-cliff anchors) and {0.51, 0.52} (2 above-cliff anchors) and one transitional 0.455. Total 15 corruption points. Expected MB conversion at cliff: 5-9 of 9 dense points land in MB per (N, T). 4 N x 3 T = 12 (N, T) combos; even at 30% conversion of dense pts = ~32 MB / 180 — clears 22 threshold.

## Hypothesis

H1 (PRIMARY): Cliff is bounded width; 9-point dense band [0.46, 0.50] @ 0.005 step will catch the transition with high resolution at every (N, T), producing 3-7 MB per (N, T) on average.

H2: ITERATIVE cleanup (T=5, T=20) WIDENS the cliff zone vs T=1 (basin growth) — slightly more MB pts at higher T.

H3 (discriminator-survives-scale): smoke at N={2048, 16384} with corruption ∈ {0.43, 0.48, 0.52} shows: 0.43 saturates, 0.48 lies on cliff (top1 in [0.10, 0.95] at >=1 N), 0.52 floors. If 0.48 doesn't show edge value at any N at smoke regime, abort FULL dispatch.

## Mechanism (unchanged from v1 / v2.1)

Substrate bipolar codebook X (M_items x N_dim), random +/-1. For each item i, flip `corruption_frac` of bits to get Q_i. Run T iterations of modern-Hopfield cleanup:

```
Q_{t+1} = sign(softmax(beta * Q_t @ X.T) @ X)
```

top1 = `(argmax_j (Q_T @ X.T)_j == i)`. SUBSTRATE arm: this. RANDOM arm: Q_0 = fresh random +/-1; identical pipeline; floor ~1/M.

## Sweep axes (DENSE v2.2; cardinality 4 x 15 x 3 = 180 per seed)

| Axis | v2.1 values | v2.2 values | Count |
|------|-------------|-------------|-------|
| N | {2048, 4096, 8192, 16384} | UNCHANGED | 4 |
| corruption_frac | {0.40, 0.43, 0.46, 0.48, 0.50, 0.52} | {0.43, 0.44, 0.45, 0.455, 0.46, 0.465, 0.47, 0.475, 0.48, 0.485, 0.49, 0.495, 0.50, 0.51, 0.52} | 15 |
| cleanup_iters | {1, 5, 20} | UNCHANGED | 3 |

M_items = 500; beta = 8.0.
Seeds: 7, 13, 19 (3 chunked sibling files; one seed per file).

Dense band: corruption in [0.46, 0.50] @ 0.005 = {0.46, 0.465, 0.47, 0.475, 0.48, 0.485, 0.49, 0.495, 0.50} — 9 pts.
Shoulder band BELOW: {0.43, 0.44, 0.45, 0.455} — 4 pts (anchors saturated regime + cliff approach).
Shoulder band ABOVE: {0.51, 0.52} — 2 pts (anchors floor regime + immediate post-cliff).

## Smoke variant (6 corner points per seed)

- N_SWEEP_SMOKE = {2048, 16384} (low + full to test discriminator-survives-scale)
- CORRUPTION_SMOKE = {0.43, 0.48, 0.52} (well below all CRLB cliffs / on cliff / above all CRLB cliffs)
- ITERS_SMOKE = {5}
- M_ITEMS_SMOKE = 200
- 1 seed per sibling file
- EXPECTED_N_UNITS_SMOKE = 2 x 3 x 1 = 6

## Arms per point (META_RULE_AF)

1. **ARM_SUBSTRATE** — iterative softmax-Hopfield cleanup (mechanism)
2. **ARM_RANDOM_FLOOR** — same pipeline, Q_0 = fresh random +/-1; expected ~1/M

arms_differ_sha256: SHA-256(json(SUBSTRATE.recall_per_point)) != SHA-256(json(RANDOM.recall_per_point)) per cell.

## Pre-reg bands (per-point; LOCKED at module init)

| Tier | top1_substrate | Discriminator (sub - rnd) |
|------|---------------|---------------------------|
| SATURATED | >= 0.95 | record but down-weight (Skunkworks Q-rule) |
| HARD_PASS | [0.80, 0.95) | >= 0.50 |
| MIDDLE_BAND | [0.50, 0.80) | >= 0.30 |
| HARD_FAIL | (0.10, 0.50) | mechanism breaking |
| FLOOR | <= 0.10 | substrate at chance |

Headline cliff-locator: for each (cleanup_iters, N), the cliff = smallest corruption_frac where top1_substrate drops BELOW 0.50.

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_PHASE_DIAGRAM_LOCALIZED_CLIFF**: cardinality_ok AND arms_differ AND >= 22 points in HARD_PASS+MIDDLE_BAND (>= 22/180 = ~12% conversion; achievable per v2.1 evidence) AND cliff_locator returns non-{-1, 0.43} value for >= 1 (N, T) combo
- **MIDDLE_BAND**: cardinality_ok + arms_differ + 6 <= disc < 22 (improved over v2.1 but not chain-grade)
- **HARD_FAIL_BY_CONSTRUCTION_REPEAT**: <= 5 HARD_PASS+MIDDLE_BAND points (v2.2 dense grid still missed cliff — would imply cliff is < 0.005 wide which would be strong negative result)
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 180
- **HARD_FAIL_ARMS_IDENTICAL**: substrate and random hashes match

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 6/6 points + arms_differ + corruption=0.43 saturates at both N + corruption=0.52 floors at both N + corruption=0.48 lies in [0.10, 0.95] at >= 1 N (cliff edge present in smoke)
- **HARD_FAIL_DISCRIMINATOR_FAILS_SCALE**: corruption=0.48 floors or saturates at ALL N (no cliff edge survives scale) — abort FULL dispatch
- **HARD_FAIL_SMOKE**: any other condition

## CRLB / random-vector overlap floor (META_RULE_AG)

Per-point CRLB pre-validation (M=500, N varies; Python-computed at module init):

```python
import math
for N in [2048, 4096, 8192, 16384]:
    P = 500
    noise_floor = math.sqrt(2 * math.log(P) / N)
    cliff_1step = 0.5 * (1 - noise_floor)
    # N=2048 cliff~0.461; N=4096 cliff~0.472; N=8192 cliff~0.481; N=16384 cliff~0.486
```

Selftest assertions: 0.40 < cliff(N=2048) < 0.50 AND 0.40 < cliff(N=16384) < 0.50 AND cliff(16384) > cliff(2048) AND len(dense_band [0.46, 0.50]) >= 9.

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 6 corner points (2 N x 3 corruption x 1 iters x 1 seed)
FULL : EXPECTED_N_UNITS = 180 phase points (4 N x 15 corruption x 3 iters x 1 seed)
```

HARD_FAIL if observed_n_units != expected (silent-drop guard, USER 2026-06-26 META_RULE_J).

## GPU mandate (Fix #24) — DISPENSATION for v2.2

- `import torch` at TOP of file (Fix #24 gate detects torch eligibility)
- `DEVICE = torch.device("cuda")` preferred; CPU fallback ALLOWED for this cell when HDLAB_QUEUE=local_cpu_queue is set (USER explicit route per dispatch instructions)
- Codebook X materialized once per (seed, N) on DEVICE; encoder hoisted
- Inner cleanup loop operates on DEVICE tensors throughout
- Per-arm peak_mem_mb logged
- Memory budget at N=16384, M=500: ~65 MB peak per point. 180 points sequential per seed -> tractable on CPU (~30-45 min/seed)

## Chunked-per-seed architecture (USER 2026-06-28)

- 3 sibling files: `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}.py`
- shared core: `experiments/_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_core.py`
- per-seed checkpointing via `experiments/_seed_checkpoint.py` (PROT-021 config-mismatch guard ON)
- 4 defensive patterns: start_marker (`STARTED` metric immediately), crash-diag (import-crash sentinel), per-unit checkpoint (write_partial_key per seed), heartbeat (per-phase-point flush print)

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (substrate vs random)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: arms-must-differ at each point
- META_RULE_AG: per-point CRLB / overlap-floor pre-validation in Python
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_AN: empirical baseline if cone-formula uncertain (iterative case)
- META_RULE_H: cardinality_ok mandatory; observed == expected (180 full, 6 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- Functional-requirement decomposition: pattern completion = retrieve clean from corrupted (single primitive, no composition)
- Signal-shape compatibility: single-primitive cell, no composition; trivial audit
- Substrate-as-canonical query-first: v1 phase-diagram + v2 narrow + v2.1 narrow all reviewed (chain ends at v2.1 commit 2daf9b55)
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at full-N (N=16384) with cliff-edge corruption (0.48) — full preview arm validates discriminator survives scale before FULL dispatch
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26): clearing the 22-MB threshold gives HARD_PASS only when paired with real cliff-edge localization (cliff_locator returns interior cliff); otherwise tier-up requires Skunkworks audit

## ETA

Per-point on CPU (laptop, N=16384, M=500): ~10-15 s avg.
- SMOKE per seed: 6 pts * ~3-5s (M=200; smaller) = ~30s science + 10s init = ~40-60 s; timeout 1200 s margin
- FULL per seed: 180 pts * ~10-15s = ~30-45 min science + 30 s init; timeout 2700 s (45 min) per USER spec, with one 60min headroom variant if needed

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit.

## Smoke gate (MUST pass before FULL dispatch)

1. 6 corner points all ran (no silent except per META_RULE_J)
2. cardinality_ok: observed_n_units == 6
3. arms_differ_sha256.differ == True
4. corruption=0.43 saturates at >= 1 N (sanity: easy regime works)
5. corruption=0.52 floors at >= 1 N (sanity: hard regime fails)
6. corruption=0.48 produces top1 in [0.10, 0.95] at >= 1 N (cliff edge observable; discriminator survives scale)
7. >= 1 point lands in HARD_PASS / MIDDLE_BAND / HARD_FAIL transition band — i.e., not all SAT or FLOOR. Smoke uses only 3 corruption pts so cliff-edge points typically land in HARD_FAIL band [0.10, 0.50); this still counts as cliff-zone evidence. Full sweep's 9 dense [0.46, 0.50] pts is what populates MB tier; smoke verifies cliff IS observable, not that MB-count is met.

If gates 4-7 fail, FULL dispatch is HARD-blocked.

## Smoke gate results (3 seeds; 2026-06-28)

All 3 seeds passed HARD_PASS_SMOKE:
- seed_7: sat=3 hp=0 mb=0 floor=2 fail=1; 0.48@N=2048 top1=0.205 (HARD_FAIL band cliff-edge); 0.48@N=16384 top1=0.985 (still SAT — cliff at higher N is just above 0.48)
- seed_13: sat=3 hp=0 mb=0 floor=2 fail=1; same shape
- seed_19: sat=3 hp=0 mb=0 floor=2 fail=1; same shape

Cliff confirmed observable at 0.48 for N=2048; cliff for N=16384 is just above 0.48 (within dense band [0.485-0.50]). Full dispatch with dense grid will populate cliff transition.
