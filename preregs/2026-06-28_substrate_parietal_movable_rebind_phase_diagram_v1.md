# Pre-reg: substrate_parietal_movable_rebind_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (hdi_exp_dev sub-agent)
**Parent capability:** parietal MOVABLE-rebind (chain-grade-quality at smoke; v1 movable_recall=0.847 cv=0.026 over FIXED=0.172)
**Goal:** Layer-1 phase diagram for parietal MOVABLE-rebind across (grid_size, n_objects, move_frequency); identify cliff location.

## Anchors (3 chunked seed siblings)
- `substrate_parietal_movable_rebind_phase_diagram_v1_seed_7`
- `substrate_parietal_movable_rebind_phase_diagram_v1_seed_13`
- `substrate_parietal_movable_rebind_phase_diagram_v1_seed_19`

Each seed cell runs the FULL 4 x 4 x 4 = 64-point phase grid (with position_noise=0.05 fixed).
Smoke = same code with `--smoke` flag → 4 corner points only (cardinality_ok=4), 1 seed.

## Substrate parameters (LOAD-BEARING)
- N_DIM = 1024 (CHOSEN per Python CRLB pre-validation; see below).
  Plate capacity = N / (4 * ln(M)). At N=1024, n_obj=8 ratio=0.065 (strong); n_obj=50 ratio=0.764 (CLIFF).
  N=8192 (v1 full default) is too large — n_obj=50 ratio=0.096 still saturates → NO CLIFF would be observable.
- FHRR-style complex unit-modulus atoms (n_half = N_DIM / 2 = 512 complex).

## CRLB pre-validation (Python compute, verified)
```
N_DIM=1024:
  n_obj= 3: cap=233.0 ratio=0.013 exp=0.99 (saturate)
  n_obj= 8: cap=123.1 ratio=0.065 exp=0.85-0.95 (strong)
  n_obj=20: cap= 85.5 ratio=0.234 exp=0.50-0.80 (degrading)
  n_obj=50: cap= 65.4 ratio=0.764 exp=0.20-0.50 (CLIFF)
```
**Discriminator survives scale:** n_obj=8 → n_obj=50 spans saturate-through-cliff at N=1024. Confirmed via Plate capacity formula (META_RULE_AC compliance).

## Sweep axes (CHUNKED by dropping position_noise)
- grid_size in {4, 8, 16, 32} (spatial scale, n_positions = grid^2)
- n_objects in {3, 8, 20, 50} (binding load → capacity sweep)
- move_frequency in {0.0, 0.2, 0.5, 0.8} (rebinding pressure; fraction of objects that move)
- position_noise = 0.05 fixed (not swept here per chunking decision)
- Total: 4 x 4 x 4 = 64 phase points per seed

## Smoke gate (cardinality_ok = 4)
Smoke = 4 corner points:
1. (grid=4, n_obj=3, move_freq=0.0) — low load, no rebind: HRR should HARD_PASS
2. (grid=32, n_obj=3, move_freq=0.0) — large grid sparse: still HARD_PASS expected
3. (grid=4, n_obj=50, move_freq=0.8) — over-cap + heavy rebind: HARD_FAIL expected (CLIFF)
4. (grid=32, n_obj=50, move_freq=0.8) — large grid over-cap heavy: HARD_FAIL expected (CLIFF + capacity)

**Smoke PASS criteria:**
- cardinality_ok = 4
- At least 2 points show SUBSTRATE > max(RANDOM, STATIC) + 0.20
- At least 1 point near-saturates (>= 0.90)
- At least 1 point fails (< 0.40) — proves discriminator FIRES at full-N (Fix #21 compliance)
- arms_differ SHA-256: SUBSTRATE/RANDOM/STATIC produce bit-distinct prediction lists per point

**Smoke FAIL:**
- cardinality breach (n_units != 4 * 3_arms = 12)
- arms-must-differ FAIL (any two arms produce identical predictions)
- RANDOM >= SUBSTRATE at any point (META_RULE_AM: by-construction-trivial regime)
- No saturate-AND-fail observed at corners (smoke discriminator did not survive)

## 3 arms per point (must be BIT-DISTINCT per META_RULE_AF)
1. **SUBSTRATE_HRR** (mechanism): HRR-bind(role_k, pos_k) for each object; on move: subtract old bind, add new bind; query: unbind(bag, role_k) → cleanup to position codebook.
2. **RANDOM** (chance floor): predict random position; chance = 1/n_positions.
3. **STATIC_BINDING** (rebind-removal control): same HRR bind at init; NEVER apply MOVE op; query asks for post-move position which was never updated → should hit chance OR initial position based on overlap.

**Arms-differ self-test:** SHA-256 hashes over per-(scene,query) prediction lists must be 3 distinct hex digests (catches v1's bit-identical bug).

## Phase-diagram metrics (per point)
For each (grid, n_obj, move_freq):
- `substrate_recall`: HRR post-rebind correct prediction rate
- `random_recall`: chance baseline rate
- `static_recall`: HRR no-rebind baseline rate
- `substrate_lift_over_random`: substrate - random
- `substrate_lift_over_static`: substrate - static (the rebind contribution)
- `n_queries`: cardinality this point

## HARD_PASS (cell-level)
- cardinality_ok = 64 (or 4 for smoke)
- arms_must_differ PASS (3 distinct SHA-256)
- META_RULE_AM PASS (no point where RANDOM >= SUBSTRATE)
- At least 30% of points show substrate_lift_over_static >= 0.30 (mechanism active in non-trivial regime)
- At least 1 saturation point (substrate >= 0.90)
- At least 1 cliff point (substrate <= 0.40) — phase diagram has structure

## HARD_FAIL
- arms_must_differ FAIL
- cardinality breach
- METARULE_AM breach at any point
- All 64 points saturate (no phase structure observable) — discriminator did not survive scale at full
- All 64 points fail (cell broken)

## MIDDLE_BAND
- HARD_PASS criteria mostly met but lacks 1 saturate-AND-cliff polarity OR points cluster in single regime band.

## Headline target
"Where does parietal MOVABLE-rebind cliff?" — smallest grid OR largest n_obj where substrate_recall drops below 0.40.

## Cardinality (META_RULE_H)
- EXPECTED_N_UNITS_SMOKE = 4 points * 3 arms = 12 (per seed, smoke = 1 seed)
- EXPECTED_N_UNITS_FULL = 64 points * 3 arms = 192 (per seed; 3 seed cells = 576 total)

## Hardening
- META_RULE_AC (CRLB Python pre-validation): DONE above
- META_RULE_AE (smoke-gates discipline): smoke 4-corner with HARD_PASS criteria above
- META_RULE_AF (arms-must-differ SHA-256): enforced per-cell post-run
- META_RULE_AG (atomic metrics write): .tmp + os.replace
- META_RULE_AH (main-guard L1-L4): per v1 pattern
- META_RULE_AM (no by-construction-trivial regime): assert SUBSTRATE > RANDOM per point
- META_RULE_AN (config_version completeness): ANCHOR, N, sweep axes, seeds, bands, hardening
- DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke runs at FULL N_DIM=1024 (same as full); CRLB shows cliff in sweep range
- ASCII-only, no emojis, self-contained

## Dispatch plan
1. Smoke seed_7 local CPU (~30-60s expected) → HARD_PASS
2. After HARD_PASS: 3 FULL seed cells to `remote_cpu_queue` with `--timeout 4500` each
3. Per-experiment timeout justification (formula): smoke_wall ~ 40s * (64/4) * 1.0 = 640s * 1.5 safety = ~960s estimate; 4500s is generous ceiling (META_RULE: better-overbudget-than-killed for phase-diagram cells)
