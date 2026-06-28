# PRE-REG: substrate_multihop_phase_diagram_depth_VC_NChains_v1

**Cell file:** `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py`
**Author:** exp_dev (Agent-Teams sub-agent spawned by research lead)
**Date:** 2026-06-28
**Anchor:** `substrate_multihop_phase_diagram_depth_VC_NChains_v1`
**Stage:** Stage-3 (composition/higher-functions per stage-progression rule; multi-hop is composition + retrieval)
**Layer:** Layer-1 phase-diagram MAP cell per USER strategic directive (substrate-product portfolio; map first, then ship Layer-2 phase operations)

## Why

Multi-hop reasoning is chain-grade at depth-15 0.808 (single-point banked atom; V_C=200, N_chains=200, N_DIM=8192).
Phase coverage is ~30% — we don't know:
- Depth-cliff (does it hold beyond 15?)
- V_C-cliff (does it survive at 1000 / 5000 / 16000?)
- N_chains interaction (load × V_eff product effect)

Layer-2 phase operations (USER vision) need cliff data to know **when to switch procedures** between operating points.

This cell maps the (depth × V_C × N_chains) cube so the substrate-product knows where multi-hop works, where it breaks, and where the cliffs are.

## Sweep axes

- `depth ∈ {5, 8, 10, 12, 15}` (5 points)
- `V_C ∈ {200, 1000, 5000, 16000}` (4 points; covers Barrier 1 regime + harder)
- `N_chains ∈ {50, 200}` (2 points)
- **Full grid: 5 × 4 × 2 = 40 points**
- **Smoke grid: 4 corner points** (low-low, low-high, high-low, high-high of {depth, V_C}; N_chains pinned to extremes)

## Smoke corner points

| depth | V_C  | N_chains | p_step_pred | top1_pred | rand_floor | role |
|-------|------|----------|-------------|-----------|------------|------|
|   5   |  200 |    50    |   0.9965    |  0.9824   |  0.005000  | saturation sanity (must SATURATE: top1 > 0.95) |
|   5   |16000 |    50    |   0.7528    |  0.2417   |  0.000063  | discriminator (must show SUBSTRATE-RANDOM > 0.20) |
|  15   |  200 |   200    |   0.9859    |  0.8082   |  0.005000  | discriminator (must show SUBSTRATE-RANDOM > 0.20; reproduces v1 anchor 0.808) |
|  15   |16000 |   200    |   0.3211    |  0.0000   |  0.000063  | regime-fail sanity (must FAIL: top1 < 0.10) |

## Arms (per phase point)

1. **SUBSTRATE** — partition-routed oracle cleanup per-step (verbatim v1 mechanism); W built at max_depth=15 over E_VC, ingest_hebbian_gpu; oracle reduces per-step search to V_C / N_PARTITIONS = 20.
2. **RANDOM** — random-pick floor: uniformly sample target object from V_C codebook (must be ~ 1/V_C across all points).

**Arms-must-differ** (META_RULE_AF): SHA-256 of per-step prediction sequences must differ between SUBSTRATE and RANDOM at EVERY (depth, V_C, N_chains) point.

## GPU requirement (Fix #24 non-negotiable)

- `torch.cuda` primary device (asserted at module init for FULL run mode)
- Batched ingest_hebbian (1000-binding outer-product blocks; matmul per batch not per chain)
- E codebook + R predicates + W matrices hoisted ONCE per (V_C, N_chains) pair; reused across depths
- Per-step retrieval via batched `E_parts @ state` (GPU matmul)
- Smoke profiles GPU util via `torch.cuda.utilization()` sampled mid-run; must be >= 50% across measurement window
- **N_DIM = 8192** (production scale; per USER 2026-06-22 + Fix #24)

## Model (substrate-empirical, META_RULE_AN 3.7x cone-formula)

```
p_step_anchor = 0.808^(1/15) = 0.98590   # from v1 chain-grade anchor V_C=200, N_chains=200, N=8192
log(p_step) = log(p_step_anchor) * (V_C * N_chains) / (V_C_anchor * N_chains_anchor)
top1_pred = p_step ** depth
random_floor = 1.0 / V_C
```

## Phase-point HARD_PASS / HARD_FAIL bands (40 points; per-point)

Bands track prediction (weaker pred -> weaker thresholds; all HP/HF clamped above 5x random floor):

```
top1_pred >= 0.60:  HP=0.50  HF=0.25
top1_pred >= 0.30:  HP=0.25  HF=0.10
top1_pred >= 0.10:  HP=0.10  HF=0.05
top1_pred  < 0.10:  HP=0.05  HF=0.02
```

(Full 40-row table in cell module-level constant `PHASE_BANDS`.)

## Verdict tiers

- **CHAIN_GRADE_PHASE_MAP_COMPLETE**: >= 50% (20/40) phase points HARD_PASS + cliffs identified
- **PARTIAL_PHASE_MAP_SHALLOW**: 30-49% HARD_PASS; cliffs visible at moderate V_C
- **REGIME_BOUNDS_NARROW**: 10-29% HARD_PASS; substrate works only at small V_C
- **PHASE_FRONTIER_COLLAPSED**: <10% HARD_PASS; cliffs at all depths
- **SANITY_BREACH**: corner point (5, 200, 50) fails to saturate -> setup broken

## Sanity rails (corners; ALL must hold or SANITY_BREACH verdict)

- Saturation corner (5, 200, 50): top1 >= 0.95 (must saturate at easy regime)
- Cross-cell rail (15, 200, 200): top1 in [0.75, 0.86] (must reproduce v1 anchor 0.808 +/- 0.05)
- Regime-fail corner (15, 16000, 200): top1 < 0.10 (must fail at hard regime; serves as null check)
- Arms-differ corner: SHA-256(substrate_preds) != SHA-256(random_preds) at ALL 4 corners

## Smoke gate (MUST pass before full)

Per META_RULE_J (no silent except) + spawn directive:
- `cardinality_ok`: observed_points == 4 (all 4 corners ran; no silent drops)
- `arm_discriminator_fires`: >= 2 corners have SUBSTRATE - RANDOM > 0.20
- `saturation_observed`: >= 1 corner has top1 > 0.95 (corner 1)
- `regime_fail_observed`: >= 1 corner has top1 < 0.10 (corner 4)
- `gpu_util_ok`: >= 50% mean GPU util in smoke window
- `arms_differ_sha256`: SHA-256 differs at all 4 corners
- `no_silent_exceptions`: zero except: blocks; all per-point runs either complete or HALT explicitly

## CRLB feasibility (computed in code BEFORE writing pre-reg, per "compute formulas in code" rule)

```
feasible_arm_discriminable_points / 40 = 26/40 = 65%
saturation_observed_predicted = 1 (5, 200, 50)
regime_fail_predicted        = 1 (15, 16000, 200)
discrim_observed_predicted   = 26 of 40 (top1_pred > 5x random_floor AND top1_pred > 0.05)
```

This is a HEALTHY phase diagram: ~half discriminate, ~quarter saturate, ~quarter collapse — phase boundaries are crisp.

## Cardinality discipline (META_RULE_H / CARDINALITY_OK)

- EXPECTED_N_POINTS_FULL = 40
- EXPECTED_N_POINTS_SMOKE = 4
- HARD_FAIL if `len(phase_map) != expected` (silent drops = phantom regime)

## Disciplines locked

- META_RULE_AC (band-floor != HARD_PASS; band-floor is MIDDLE_BAND)
- META_RULE_AE (per-arm verification not summary text)
- META_RULE_AF (arms-must-differ SHA-256 at every point)
- META_RULE_AG (no silent except per point)
- META_RULE_AH (no hallucinated numbers; all values MEASURED@<path>)
- META_RULE_AN (substrate-empirical 3.7x cone scaling)
- Fix #24 (GPU dispatch must actually use GPU; util >= 50%)
- Fix #28 (verify per-arm metrics before cross-cell convergence claims)

## Output

`data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1/metrics.json` with:

```
{
  "anchor_name": "substrate_multihop_phase_diagram_depth_VC_NChains_v1",
  "verdict": "<verdict_tier>",
  "verdict_msg": "...",
  "phase_map": [
    {"depth": 5, "V_C": 200, "N_chains": 50,
     "top1_substrate": <float>, "top1_random": <float>,
     "top1_pred": <float>, "HP": <float>, "HF": <float>,
     "verdict_tier_per_point": "HARD_PASS|MIDDLE_BAND|HARD_FAIL",
     "saturated": <bool>, "arms_differ_sha256": <bool>,
     "elapsed_s_point": <float>},
    ... 40 rows ...
  ],
  "smoke_gate": {"cardinality_ok": true, "arm_discrim_fires": <int>, ...},
  "gpu_util_pct_mean": <float>,
  "per_seed": [...],
  ...
}
```

## Dispatch plan

1. **Local CPU self-test** (laptop has NO CUDA; verifies formula + arms-differ + scaffold-soundness only). Per-point timeout for self-test: 5s.
2. **GPU smoke** to remote_gpu via Orchestrator (Fix #24: util gate needs real GPU). 4 corner points. Timeout: 600s (10 min).
3. **Full dispatch** to overnight_queue via Orchestrator. 40 points × 1 seed. Timeout: 18000s (5h; budget ~7min/point).

Per `--timeout` rule: full timeout = 18000s; smoke timeout = 600s; self-test timeout = 60s.

## Routing

- Laptop = D:/AI/hd-instrument (Author here; commit; push-DENIED to me)
- Remote = C:/dev/hd-instrument (reads origin/main); harness-push routes via hd_metrics_sync
- I file the routing-request for Orchestrator; Orchestrator dispatches via queue_add.sh

## Anti-bias checklist (BIAS-13/14/15 + S-band-calibration)

- BIAS-13 (contamination): chains are freshly generated per seed; no leakage between Ws.
- BIAS-14 (regime): bands span 4 orders-of-magnitude in random_floor (1/200 to 1/16000); regime checks ARE the cell.
- BIAS-15 (mismatch): SUBSTRATE arm uses identical chains as RANDOM arm at each point; per-step prediction comparison.
- S-band-calibration: HP / HF tracked to top1_pred per point; not a single global threshold.

## Honest CRLB note

The "CRLB" here is approximate; substrate per-step floor is empirical not Cramer-Rao tight. I refer to it as "predicted floor" rather than CRLB-tight to avoid over-claim. The 65%-discriminative result is the load-bearing prediction; refine if smoke contradicts.
