# Pre-reg: substrate_parietal_movable_rebind_phase_diagram_v2

**Date:** 2026-06-28
**Author:** exp_dev (hdi_exp_dev sub-agent)
**Parent capability:** parietal MOVABLE-rebind (v1 smoke HARD_PASS, full FULL never landed; v1 BACKUP characterization: MM PARTIAL, cliff onset at n_obj=200 grid=32 N_DIM=1024 -> recall=0.25)
**Goal:** EXTEND v1 phase diagram past the v1 cliff into the failure-mode floor, AND characterize cliff-location-vs-substrate-dimensionality (N_DIM sweep).

## Why v2 (delta from v1)
- v1 mapped cliff onset (n_obj=200 at grid=32 N=1024) but did not characterize the floor (>=400 objects, sub-N substrates).
- v1 fixed N_DIM=1024. Real claim "where does parietal MOVABLE-rebind cliff?" requires sweeping the substrate-dimensional axis to map the (N_DIM, n_obj) cliff-curve.
- v1 used point-recall only. v2 adds Pareto-AUC discriminator (area under recall-vs-load curve) per chain-grade lessons.

## Anchors (3 chunked seed siblings)
- `substrate_parietal_movable_rebind_phase_diagram_v2_seed_7`
- `substrate_parietal_movable_rebind_phase_diagram_v2_seed_13`
- `substrate_parietal_movable_rebind_phase_diagram_v2_seed_19`

Each seed cell runs the FULL filtered phase grid; smoke = 4 corners (cardinality_ok=4).

## Substrate parameters (LOAD-BEARING)
- N_DIM in {512, 1024, 2048} (3 substrate-dim regimes spanning sub/equal/super v1)
- FHRR complex unit-modulus atoms (n_half = N_DIM // 2)
- position_noise = 0.05 fixed
- k_scales = 4 (Frady-Kanerva multi-scale fractional-power binding)

## CRLB pre-validation (Python compute, verified above)
Plate capacity formula: N_cap = N_DIM / (4 * ln(M_codebook)); M_codebook = max n_pos = 32*32 = 1024
```
N_DIM=512:  cap=18.5; n_obj= 50 ratio=2.71 expected=floor;  n_obj=400 ratio=21.7 expected=floor
N_DIM=1024: cap=36.9; n_obj= 50 ratio=1.35 expected=cliff;  n_obj=200 ratio= 5.4 expected=floor
N_DIM=2048: cap=73.9; n_obj= 50 ratio=0.68 expected=strong; n_obj=100 ratio= 1.4 expected=cliff
```
Plate is conservative; v1 empirics showed substrate beats Plate by ~2x at N=1024 grid=32 (saturate at n_obj=20-50 ratio<=0.23-0.76). v2 sweep range still spans saturate-through-floor across the (N_DIM, n_obj, grid) cross-product.

**Discriminator survives scale (Fix #21 / smoke discipline):** smoke runs the same 4-N_DIM-spanning corners as full; v1 anchor point (1024, 32, 200, 0.5) -> 0.25 recall is reproduced as smoke corner 3.

## Sweep axes
- N_DIM in {512, 1024, 2048}
- grid_size in {16, 32}  (n_positions = grid^2 in {256, 1024}; drop tiny grids so big n_obj fits)
- n_objects in {50, 100, 200, 400}
- move_frequency in {0.0, 0.2, 0.5, 0.8}

**Filter:** skip points where n_obj > n_pos (clipping creates duplicate effective configs).
- grid=16 (n_pos=256): n_obj in {50,100,200} -> 3 admissible
- grid=32 (n_pos=1024): n_obj in {50,100,200,400} -> 4 admissible
- Per N_DIM: (3+4) * 4 mf = 28 points
- Total per seed: 3 N_DIM * 28 = 84 points

EXPECTED_N_UNITS_FULL = 84 phase-cells per seed
EXPECTED_N_UNITS_SMOKE = 4 (corners)
META_RULE_H cardinality_ok: HARD_FAIL if observed != expected.

## Smoke gate (cardinality_ok=4)
Smoke = 4 corner points designed to span saturate / cliff / floor at FULL N_DIM range:
1. (N_DIM=2048, grid=16, n_obj=50, mf=0.5) -- expected saturate (>=0.90)
2. (N_DIM=1024, grid=16, n_obj=50, mf=0.5) -- expected mid-recall (0.40-0.80)
3. (N_DIM=1024, grid=32, n_obj=200, mf=0.5) -- v1-anchored cliff (~0.25)
4. (N_DIM=512,  grid=32, n_obj=400, mf=0.5) -- expected floor (<=0.10)

**Smoke PASS criteria:**
- cardinality_ok = 4
- arms_differ SHA-256: 3 distinct hex digests
- META_RULE_AM: every point has substrate_recall >= random_recall + 0.02
- At least 2 points have substrate - max(random, static) >= 0.20 (strong discriminator)
- At least 1 point saturates (recall >= 0.90)
- At least 1 point floors (recall <= 0.10) -- proves discriminator fires at full-N

**Smoke FAIL:**
- cardinality breach
- arms-must-differ FAIL
- METARULE_AM breach at any point
- ALL_SATURATE or ALL_FLOOR (discriminator did not survive scale)

## 3 arms per point (BIT-DISTINCT per META_RULE_AF)
1. **SUBSTRATE_HRR** (mechanism): HRR-bind(role_k, pos_k) for each object; on move: subtract old bind, add new bind; query: unbind(bag, role_k) -> cleanup to position codebook.
2. **RANDOM** (chance floor): predict random position from [0, n_pos); chance = 1/n_pos.
3. **STATIC_BINDING** (rebind-removal control): same HRR bind at init; NEVER apply MOVE op; query asks for post-move position which was never updated.

**Arms-differ self-test:** SHA-256 hashes over per-(scene,query) prediction lists must be 3 distinct hex digests.

## Phase-diagram metrics (per point)
For each (n_dim, grid, n_obj, move_freq):
- `substrate_recall`, `random_recall`, `static_recall`
- `substrate_lift_over_random`, `substrate_lift_over_static`
- `n_queries`

## Aggregate metrics (per seed)
- `pareto_auc.auc_substrate` / `auc_static` / `auc_random` (area under recall-vs-n_obj curve, normalized n_obj range, averaged over (n_dim, grid, mf) buckets)
- `pareto_auc.pareto_lift_subst_static` (>= 0.20 to HARD_PASS)
- `cliff_curve_first_failure_n_obj`: dict keyed "N=<n_dim>_grid=<grid>" -> smallest n_obj where substrate_recall <= 0.40

## HARD_PASS (cell-level, per seed)
- cardinality_ok = 84
- arms_must_differ PASS
- META_RULE_AM PASS at every point
- All 4 quadrants populated by >=1 point each:
    - saturate: recall >= 0.90
    - strong: 0.60 <= recall < 0.90
    - cliff: 0.10 < recall <= 0.40
    - floor: recall <= 0.10
- frac_strong_lift >= 0.30 (>=30% of points show substrate - static >= 0.30)
- pareto_lift_subst_static >= 0.20

## HARD_FAIL
- arms_must_differ FAIL
- cardinality breach
- METARULE_AM breach
- ALL_SATURATE (all 84 points saturate -- discriminator did not survive scale)
- ALL_FLOOR (all 84 points floor -- cell broken)

## MIDDLE_BAND (HONEST-DOWNWARD default)
- Partial phase-fill: <4 quadrants populated, or frac_lift < 0.30, or pareto_lift < 0.20.
- Cell still characterizes substrate behavior; reports cliff_curve even when not all quadrants land.

## Headline targets
- Map cliff_curve: for each (N_DIM, grid), what is the smallest n_obj at which substrate_recall drops below 0.40?
- Pareto-AUC lift: how much does the substrate beat static across the full load sweep?

## Hardening
- META_RULE_AC (CRLB Python pre-validation): DONE above
- META_RULE_AE (smoke-gate discipline): smoke 4-corner with PASS criteria above
- META_RULE_AF (arms-must-differ SHA-256): enforced
- META_RULE_AG (atomic metrics write): .tmp + os.replace
- META_RULE_AH (L1-L4 main guard sentinels): import-crash sentinel + per-point try/except + outer-crash guard + atomic write
- META_RULE_AM (no by-construction-trivial regime): assert SUBSTRATE > RANDOM per point
- META_RULE_AN (config_version completeness): ANCHOR, N_DIMS, sweep axes, seeds, bands, hardening
- META_RULE_H (CARDINALITY_OK): EXPECTED_N_UNITS_SMOKE=4 / FULL=84 declared; HARD_FAIL_CARDINALITY_BREACH if observed != expected
- DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke runs at all 3 N_DIM levels (same as full)
- HONEST-DOWNWARD: MIDDLE_BAND when phase-fill incomplete (not HARD_PASS-inflated)
- Pareto-AUC discriminator (chain-grade lesson)
- ASCII-only, no emojis, self-contained

## Dispatch plan
1. Self-test seed_7 (local; ~1s) -- confirm mechanism wired
2. Smoke seed_7 (local; ~30-90s) -- 4 corners verify phase-fill structure
3. After smoke HARD_PASS: 3 FULL seed cells -> `remote_cpu_queue` with `--timeout` per formula

## Timeout formula (per-experiment, REQUIRED by queue_add.py)
Smoke wall (measured) -> full estimate:
- smoke runs 4 points * 20 scenes
- full runs 84 points * 20 scenes
- scaling per N_DIM: O(N_DIM) for binding ops; smoke spans all 3 N_DIMs
- timeout_s = ceil(1.5 * smoke_wall_s * (84/4) * 1.3) = ceil(40.95 * smoke_wall_s)
- If smoke_wall ~30s -> timeout ~1230s. Use ceiling 3600s for safety; PROT-019 not applicable (N_DIM<4096).

## Files
- `experiments/_parietal_phase_diagram_v2_base.py` (shared engine)
- `experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v2_seed_7.py`
- `experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v2_seed_13.py`
- `experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v2_seed_19.py`
