# PRE-REG: substrate_multihop_phase_diagram_depth_VC_NChains_v5

**Cell files (CHUNKED across 3 sibling seeds; shared engine in `_multihop_phase_diagram_v5_base.py`):**
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7.py`
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13.py`
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_19.py`
- shared engine: `experiments/_multihop_phase_diagram_v5_base.py`

**Author:** exp_dev (Agent-Teams sub-agent)
**Date:** 2026-06-29
**Anchor (per seed):** `substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_<7|13|19>`
**Stage:** Stage-3 (composition / multi-hop)
**Layer:** Layer-1 phase-diagram MAP cell
**Supersedes:** v4 (3/3 HARD_FAIL cross-seed; SANITY_BREACH on SAT_CORNER; by-construction-saturation at high eff_V_C)

---

## Why v5 (mechanism-class diversion of v4)

### v4 outcome (re-read off per-seed metrics.json 2026-06-29)
- All 3 v4 seeds (7/13/19) HARD_FAIL with `SANITY_BREACH: SAT_CORNER (5, 200) failed to saturate`.
- SAT_CORNER PARTITION_ORACLE top1: seed 7=0.805, seed 13=0.770, seed 19=0.810. Sanity rail was 0.90.
- v4's empirical p_step model said `p_step(eff_V_C=200) = 0.99`, predicting top1=0.951 at (depth=5, eff_V_C=200). Reality came in 0.77-0.81 (p_step ~ 0.95-0.96). The empirical p_step model was BACKWARDS in direction at low eff_V_C.
- At eff_V_C in {4000, 16000}: SUBSTRATE_BASELINE (full V_C cleanup; no oracle) reached 0.86-0.99; PARTITION_ORACLE reached 0.95-1.0. Gap < 0.04. **By-construction-saturation** -- the oracle benefit collapses at large eff_V_C because the substrate self-cleans cleanly (sparse storage; M=200 vs V_C=64000 -> 80x headroom; no collisions).

### Diagnosis (cell-author honest assessment)
v4 was the WRONG framing in two ways:

1. **Wrong knob**: `effective_V_C` (per-step cleanup search size) is NOT the storage-resolution knob. Per-step cleanup is bounded by W's representational capacity, which is set by `M_ingested_triples / N_DIM` (storage density), NOT by cleanup-search size. v4 swept the search-set granularity; the substrate failure mode is in the storage granularity.

2. **Wrong discriminator**: `PARTITION_ORACLE - RANDOM_PARTITION` measures the per-step lookup advantage of having ground-truth partition info. This is saturated by construction at every regime tested -- at small eff_V_C the gap is huge (RANDOM ~ 0; PART_ORACLE > 0.5); at large eff_V_C the gap is tiny (PART ~ 1.0; SUB_BASELINE ~ 1.0). The discriminator doesn't test multihop reasoning; it tests whether the oracle has search-set advantage.

This is the SAME failure class as ANCHOR 3 v1 (FAMILY_OVERLAP catch): v4's `top1_partition_oracle` MASKED the real failure mode (storage saturation), just like ANCHOR 3 v1's `recall_via_lookup` masked over-compression.

### v5 mechanism diversion (different knobs + different discriminator + different arms)

| dimension | v4 (HARD_FAIL) | v5 (this pre-reg) |
|-----------|----------------|--------------------|
| **Sweep axis 1** | effective_V_C (per-step cleanup search size) | STORAGE_DENSITY = M_train_triples / V_C (storage saturation knob) |
| **Sweep axis 2** | depth (preserved) | depth (preserved) |
| **Arms (storage)** | PARTITION_ORACLE vs RANDOM_PARTITION vs SUBSTRATE_BASELINE (cleanup-search-size variants) | HEBBIAN_W vs DIRECT_ATTENTION vs CHANCE (storage primitives) |
| **Primary discriminator** | PART_ORACLE - RANDOM_PARTITION > 0.20 (cleanup-search benefit) | Pareto-split between HEBBIAN_W and DIRECT_ATTENTION on (top1, wall_s) at >= 1 density |
| **Secondary discriminator** | none | per-hop angle-drift cosine(state, E[target]) (substrate-internal, search-size-independent) |
| **V_C** | 4 values * 4 partitions = 800-64000 | fixed at 4000 (controls storage; not the sweep) |
| **M_ingested** | implicit (depended on chains_test count) | 5 explicit densities = M/{V_C} in {0.05, 0.20, 0.50, 1.00, 2.00} |

### Two failure modes v5 is designed to catch (which v4 could not see)

- **Storage saturation cliff**: at density >= 1.0, HEBBIAN_W's W matrix exceeds binding capacity (Plate 1995 ~ N_DIM/2 ~ 4096 triples on N=8192); per-step crosstalk accelerates angle drift; chains break. This is the LOAD-BEARING multihop phenomenon.
- **Storage primitive Pareto split**: at high density, DIRECT_ATTENTION (sublinear; non-saturating) should out-recall HEBBIAN_W (saturated). At low density, HEBBIAN should match DIRECT_ATTENTION (both can store sparsely without collision) AND be cheaper at inference (matrix multiply vs softmax over M keys). The PARETO SPLIT is the chain-grade discriminator -- proves both storage primitives are non-trivially active.

---

## What v5 sweeps

| axis | values | count |
|------|--------|-------|
| `storage_density` (M_train_triples / V_C) | {0.05, 0.20, 0.50, 1.00, 2.00} | 5 |
| `depth` (chain length tested) | {5, 10, 15} | 3 |
| **full grid (rows)** | | **15 rows** |
| **arms per row** | HEBBIAN_W, DIRECT_ATTENTION, CHANCE | 3 |
| **full datapoints** | | **45** |
| **smoke (corner rows)** | | **4 rows = 12 datapoints** |

Fixed config: `V_C=4000`, `N_DIM=8192`, `V_PRED=10`, `MAX_W_DEPTH=15`, `N_TEST_CHAINS=200`.

Storage primitive details:
- **HEBBIAN_W**: `W = sum (E[o] outer (E[s] * R[p])) / N_DIM`. Inference: `s_pred = argmax(E @ (W @ key))`. Capacity ~ N_DIM/2 (Plate 1995).
- **DIRECT_ATTENTION**: stores `K_store = E[s] * R[p] * sq` (M, N) and `V_store = E[o]` (M, N). Inference: `state = softmax(K_store @ query / temp) @ V_store; s_pred = argmax(E @ state)`. Capacity ~ M (sublinear; no crosstalk). temp=0.1 (sharp attention).
- **CHANCE**: argmax over uniformly-random codeword. Floor.

## Arms-must-differ (META_RULE_AF)

SHA-256 over concatenated per-step prediction sequences MUST differ between all 3 arms at EVERY (density, depth) point. Asserted in selftest + checked at every point.

## Pareto discriminator (load-bearing, chain-grade)

For each (density, depth) row, the (top1, wall_s) pair is computed for HEBBIAN_W and DIRECT_ATTENTION. `pareto_split = abs(top1_h - top1_a) > 0.05`. Chain-grade requires >= 1 density with `pareto_split=True`. This catches:
- **Trivial regime** (low density): both arms saturate at top1=1.0; no split (small abs diff); fails Pareto-chain-grade.
- **Interesting regime** (density approaching capacity): HEBBIAN starts crosstalking, DIRECT_ATTENTION still clean; abs(top1_h - top1_a) > 0.05; SPLIT FIRES.
- **Saturated regime** (density >> 1.0): HEBBIAN collapses to chance, DIRECT_ATTENTION still works; split is huge; SPLIT FIRES.

The Pareto-chain-grade verdict requires Pareto-split at >= 1 density AND >= 1 (density, depth) HARD_PASS AND the saturation cliff is observed (HEBBIAN top1 < 0.40 at (density=2.00, depth=15)).

## Bands (per row, HEBBIAN_W tier track)

Predicted top1 for HEBBIAN_W comes from empirical p_step model:
```
p_step(density) = 1 - 0.10 * density^1.5    (clamped [0.05, 0.999])
top1_pred(density, depth) = p_step(density) ** depth
```

| density | p_step | d=5    | d=10   | d=15   |
|---------|--------|--------|--------|--------|
|  0.05   | 0.999  | 0.994  | 0.988  | 0.983  |
|  0.20   | 0.991  | 0.957  | 0.916  | 0.876  |
|  0.50   | 0.965  | 0.834  | 0.696  | 0.581  |
|  1.00   | 0.900  | 0.591  | 0.349  | 0.206  |
|  2.00   | 0.717  | 0.190  | 0.036  | 0.007  |

HP / HF bands (tracked to top1_pred, clamped above 5x random_floor):
- `top1_pred >= 0.60`: HP=0.50 HF=0.25
- `top1_pred >= 0.30`: HP=0.25 HF=0.10
- `top1_pred >= 0.10`: HP=0.10 HF=0.05
- `top1_pred  < 0.10`: HP=0.05 HF=0.02

Random floor: 1/V_C = 0.00025.

## Smoke 4 corner points (cardinality_ok = 4)

| density | depth | role                                                                              |
|---------|-------|-----------------------------------------------------------------------------------|
| 0.05    |  5    | **SAT_CORNER**: HEBBIAN should saturate (top1 >= 0.90); DIRECT_ATTENTION matches; CHANCE tiny |
| 0.50    |  5    | **MID_DENSITY**: arms expected to diverge; pareto_split may fire                  |
| 1.00    | 10    | **PARETO_CANDIDATE**: capacity boundary; pareto_split should fire                 |
| 2.00    | 15    | **CLIFF_CORNER**: HEBBIAN < 0.40 (storage-density cliff); ATTENTION still > 0.50  |

## Sanity rails (ALL must hold or SANITY_BREACH verdict)

- **SAT_CORNER** (density=0.05, depth=5): HEBBIAN_W top1 >= 0.90 (saturates at low density)
- **CLIFF_CORNER** (density=2.00, depth=15): HEBBIAN_W top1 < 0.40 (storage-density cliff fires)
- **ARMS_DISTINCT**: 3 distinct SHA-256 hashes at every point (no arm-collapse)
- **META_AM**: HEBBIAN_W >= CHANCE at every point (mechanism beats chance; tolerance 0.02)
- **PARETO**: >= 1 density with pareto_split=True (chain-grade requirement)

## Smoke gate (MUST pass before full)

Per META_RULE_J + spawn directive:
- `cardinality_ok`: observed_points == 4
- `arms_differ_all`: SHA-256 differs across all 3 arms at all 4 corners
- `pareto_split_any`: >= 1 smoke corner has pareto_split=True
- `sat_corner_ok`: HEBBIAN at SAT_CORNER >= 0.90
- `cliff_corner_ok`: HEBBIAN at CLIFF_CORNER < 0.40
- `gpu_util_ok`: GPU util mean >= 50% (Fix #24); NaN fails LOUDLY (META_RULE_J)

## Cardinality discipline (META_RULE_H / CARDINALITY_OK)

- `EXPECTED_N_POINTS_FULL = 15` (5 densities * 3 depths)
- `EXPECTED_N_POINTS_SMOKE = 4`
- HARD_FAIL if `len(phase_map) != expected` per seed.

## Verdict tiers (FULL)

- **CHAIN_GRADE_PARETO_CLIFF_MAP_COMPLETE**: pct_pass >= 50% (>=8/15) HARD_PASS on HEBBIAN_W tier + pareto_split >= 1 + cliff observed
- **PARTIAL_PHASE_MAP**: pct_pass >= 30% OR (pareto chain-grade + no cliff)
- **REGIME_BOUNDS_NARROW**: pct_pass >= 10% OR pareto chain-grade
- **PHASE_FRONTIER_COLLAPSED**: < 10% pass + no pareto split
- **SANITY_BREACH**: SAT_CORNER HEBBIAN < 0.90

## Chunked seed checkpoint (USER 2026-06-28 + handoff section)

- 3 sibling cells: `_seed_7.py`, `_seed_13.py`, `_seed_19.py` (thin wrappers)
- Shared engine: `experiments/_multihop_phase_diagram_v5_base.py`
- Each sibling writes its own `data/exp_<anchor>_seed_<N>/metrics.json` via atomic `tmp+os.replace`.
- Defensive: IMPORT_CRASH sentinel writes UNKNOWN verdict; per-point try/except logs + re-raises (NO silent swallow); OUTER_CRASH guard in `main()`.

## Disciplines locked

- META_RULE_AC (band-floor != HARD_PASS; band-floor is MIDDLE_BAND)
- META_RULE_AE (per-arm verification not summary text)
- META_RULE_AF (arms-must-differ SHA-256 at every point; 3 distinct hashes per arm; PARETO discriminator)
- META_RULE_AG (no silent except per point; explicit propagation)
- META_RULE_AH (no hallucinated numbers; bands derived from Plate 1995 capacity model + v4 measured saturation patterns)
- META_RULE_AN (substrate-empirical scaling; NOT cone-formula extrapolation)
- META_RULE_AP (composition-adapter discipline; storage primitive composed with multihop chain)
- META_RULE_J (no silent except for instrumentation; gpu_util fails loudly if NVML unavailable)
- Fix #24 (GPU dispatch must actually use GPU; util >= 50% measured loudly)
- Fix #28 (verify per-arm metrics before cross-cell convergence claims)

## Signal-shape audit (per chain-grade-primitives-not-trivially-composable rule)

- HEBBIAN_W: W shape (N_DIM, N_DIM); state = W @ key shape (N_DIM,); scores = E @ state shape (V_C,); argmax -> int. OK.
- DIRECT_ATTENTION: K_store shape (M, N_DIM); query shape (N_DIM,); logits = K_store @ query shape (M,); scores = softmax(logits) shape (M,); state = scores @ V_store shape (N_DIM,); scores_v = E @ state shape (V_C,); argmax -> int. OK.
- CHANCE: g.integers(0, V_C) -> int. OK.
- Per-hop cosine: state.normalized() . E[target_o]. OK.

No broadcast surprises; no info-leakage across arms (3 separate code paths on same chains); chains_at_depth identical across arms within a row.

## Output (per-seed metrics.json)

```json
{
  "anchor_name": "substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_<N>",
  "verdict": "<verdict_tier>",
  "verdict_msg": "...",
  "run_mode": "smoke" | "full",
  "seed": <N>,
  "config_version": "ANCHOR=...,N=...,V_C=4000,densities=...,depths=...,arms=...,...",
  "phase_map": [
    {"storage_density_nominal": 0.05, "storage_density_actual": 0.0488,
     "depth": 5, "V_C": 4000, "N_DIM": 8192,
     "n_train_triples": ..., "n_test_chains": 200,
     "top1_hebbian_w": <float>, "top1_direct_attention": <float>,
     "top1_chance": <float>, "top1_pred": <float>,
     "HP": <float>, "HF": <float>,
     "per_step_acc_hebbian_w": [...], "per_step_acc_direct_attention": [...],
     "per_step_acc_chance": [...],
     "per_step_cos_hebbian_w": [...], "per_step_cos_direct_attention": [...],
     "per_step_cos_chance": [...],
     "wall_s_hebbian_w": <float>, "wall_s_direct_attention": <float>, "wall_s_chance": <float>,
     "arms_differ_sha256": <bool>,
     "sha256_hebbian_w": "<hex>", "sha256_direct_attention": "<hex>", "sha256_chance": "<hex>",
     "pareto_split": <bool>,
     "tier_per_point": "HARD_PASS|MIDDLE_BAND|HARD_FAIL",
     "elapsed_s_point": <float>},
    ... 15 rows (full) or 4 rows (smoke) ...
  ],
  "extra": {...},
  "gpu_util_pct_mean": <float | null>,
  "gpu_util_n_samples": <int>,
  "gpu_util_reason_if_failed": "NVML_UNAVAILABLE" | null,
  "_llm_forward_calls_at_inference": 0,
  "elapsed_s": <float>,
  "v4_supersedes": {...}
}
```

## Dispatch plan

1. **Local self-test** (laptop has NO CUDA; verifies formula + arms-differ + scaffold-soundness only; CPU fallback). Per-point timeout for self-test: 5s; total `--timeout` for self-test = 60s.
2. **GPU smoke** to overnight_queue via Orchestrator (Fix #24: util gate needs real GPU). 4 corner points x 1 seed; expected wall: ~3-8 min (DIRECT_ATTENTION at density=2.00 has K_store of size M=8000 = 8000*8192 floats ~ 250MB; matmul against M=8000 keys + softmax per query per hop). `--timeout 1800` (30 min budget).
3. **Full dispatch** (post smoke HARD_PASS): 3 chunked seed_{7,13,19} sibling cells to overnight_queue via Orchestrator. 15 rows * 3 arms * 1 seed each; expected wall: ~15-45 min per seed. Higher density rows do DIRECT_ATTENTION over M_train ~ 8000 keys per hop per chain (200 chains * 15 hops = 3000 softmax calls). `--timeout 18000` (5h budget per seed, very conservative).

Per `--timeout` rule:
- self-test timeout = 60s
- smoke timeout = 1800s (30 min)
- full timeout = 18000s (5h) per seed sibling

Per-formula self-test runtime estimate: laptop CPU at V_test=80 N=512 with 5 train chains and 5 test chains at depth=5 = ~1-2 sec (mostly torch tensor allocs). Self-test runs at module import so the queue --self-test gate exits the moment import returns.

## Routing

- Laptop = D:/AI/hd-instrument (Author here; commit; push-DENIED to me)
- Remote = C:/dev/hd-instrument (reads origin/main); harness-push routes via hd_metrics_sync
- I (exp_dev) file the routing-request for Orchestrator; Orchestrator runs `tools/queue_add.py overnight_queue ...` and the auto-stage commit pushes.

## Anti-bias checklist (BIAS-13/14/15 + S-band-calibration + N-Q-R)

- BIAS-13 (contamination): TRAIN and TEST chains share no source nodes (disallow_s gating); per-arm separate code paths reading same chains; storage primitive bundles are independent (W matrix and K_store are computed from same triples but accessed via different inference math).
- BIAS-14 (regime): bands span 2 orders of magnitude in storage_density (0.05 -> 2.00 = 40x range, covering 4096 triple Plate-capacity threshold); regime check is the cell.
- BIAS-15 (mismatch): 3 arms use IDENTICAL chains and identical E/R codebook; per-step prediction comparison via SHA-256 hash of preds.
- S-band-calibration: HP / HF tracked to top1_pred per point; NOT a global threshold.
- N-Q-R: predictions from Plate 1995 capacity model + density-dependent crosstalk + v4 measured behavior; no fabricated numbers; Cramer-Rao only approximate (substrate per-step floor is empirical).
- BIAS-Q (suspect 1.000 results): if HEBBIAN top1=1.000 at density >= 1.0, that's by-construction-suspect (capacity exceeded; should crosstalk); a HEBBIAN top1=1.000 there triggers a sanity inspection of per_step_acc + per_step_cos.
- BIAS-S (relative-bands): bands are absolute on top1_pred (function of density+depth), NOT ratios to baseline; explicitly avoid v4's gameable ratio-band class.

## Honest residual uncertainty

- p_step model is `1 - 0.10 * density^1.5` -- semi-empirical, calibrated from Plate's capacity theorem and v4's measured 0.77-0.81 at v4's effective density (n_train_triples ~ 200 / V_C effective varied). If empirical p_step at density=0.05 comes in << 0.99 (i.e., even sparse storage shows crosstalk), the SAT_CORNER rail will fire and v5 will FAIL same-class as v4 -- in which case the problem is NOT density but something more fundamental (encoder eff-rank? chain construction artifact?). That would be a useful negative.
- DIRECT_ATTENTION temp=0.1 is a guess; if too sharp, attention reduces to nearest-neighbor (loses superposition advantage); if too soft, attention smears across stored keys. Smoke will tell us.
- The Pareto split prediction assumes HEBBIAN saturates earlier than DIRECT_ATTENTION. If DIRECT_ATTENTION ALSO saturates at density >> 1.0 (because softmax can be confused by many similar keys), both arms collapse together and the Pareto-discriminator never fires -- v5 verdict would be REGIME_BOUNDS_NARROW (chain-grade NOT confirmed; both storage primitives saturate). That's also a useful negative.

## What this DOES and DOES NOT claim

DOES claim (chain-grade if PASS):
- The phase boundary for multihop substrate reasoning is set by STORAGE DENSITY (M_train_triples / V_C), not cleanup-search-size.
- HEBBIAN_W and DIRECT_ATTENTION storage primitives have non-trivial Pareto split somewhere on the density curve.
- The storage-density cliff exists (HEBBIAN fails at density=2.00).

DOES NOT claim:
- That this is the ONLY phase boundary (depth and N_DIM are also dimensions; v5 sweeps depth but fixes N_DIM).
- That DIRECT_ATTENTION is "better" than HEBBIAN_W in general (cost trade is part of the Pareto frontier).
- That this generalizes to natural-data triples (chains are synthetic random walks).

## References / load-bearing prior work

- v4 atomization: TBD (will be filed by Skunkworks post landed-VET); cite once available.
- v4 metrics.json: `data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_7/metrics.json` (and seed_13, seed_19) -- HARD_FAIL SANITY_BREACH per-seed
- ANCHOR 3 v2 FAMILY_OVERLAP pre-reg: `preregs/2026-06-28_substrate_anchor3_coarse_grain_phase_diagram_v2_FAMILY_OVERLAP.md` -- mechanism-class diversion template (different axis + different discriminator)
- Plate 1995 (HRR capacity): N_DIM/2 binding capacity bound
- Handoff section 3.1 (attention-store comparison cell M1 was the next-queued exp_dev work pre-standstill; v5 partially absorbs M1's intent)
- Handoff section 2 (item#4 attention-retrieval is the high-M path)
