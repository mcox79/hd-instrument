# Prereg: substrate_task_vector_K_cliff_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) M3 concern #4 confirmation
**Drill source:** USER directive 2026-06-28 — confirm task_vector HRR ICL is genuine chain-grade vs by-construction-saturation; today's `online_conv_oneshot_taskvec_hippo_v1` redispatch_rerun HARD_FAILed at top1=1.000 saturated TV_ONLY arm.
**Stage:** Stage 3 (compositional understanding — substrate K-shot regime)
**P_deflated:** 0.55 (capacity-driven cliff is well-characterized in HRR theory; novel here = phase-diagram coverage with overlap axis)
**M3 milestone:** Concern #4 — online conversational learning. If TASK_VECTOR un-saturated at K >= some X (the K-cliff), primitive is genuinely chain-grade; if cliff at K=10 or below regardless of (V,overlap), primitive is regime-narrow.

## HYPOTHESIS

Substrate `TASK_VECTOR = sum_i bind(input_i, perm(input_i))` followed by `unbind(query_input, TV)` + cleanup recovers `perm(query_input)` (top1) with K-shot capacity bounded by Plate-class capacity `K_critical ~ N_DIM / (4 * V_tasks)` (rough).
- **N_DIM=8192:** predicted K-cliff at V=10 ~ K=205; V=50 ~ K=41; V=200 ~ K=10.
- **Phase axis 1: K (shots) in {1, 3, 5, 10, 20, 50, 100}.**
- **Phase axis 2: N_tasks (entity-vocab size) in {10, 50, 200}.**
- **Phase axis 3: task_overlap in {0.0, 0.3, 0.6}** (fraction of K context pairs shared across tasks within a seed; secondary — tests whether task-vector interference compounds with task-similarity).
- **Expected:** Monotone DROP in top1 as K grows past K_critical; ORACLE arm stays at 1.0; RANDOM arm at chance (1/V).

## ARMS (3) — per phase-point

1. **TASK_VECTOR** — K legitimate (input_i, perm(input_i)) binds bundled; query is a presented input. The mechanism.
2. **RANDOM_VECTOR** — K (input_i, random_entity) binds (input_i was presented but output is wrong); query is presented input. Floor; rules out generic-bundle lift.
3. **ORACLE** — perfect permutation table query (no HRR involved; reads perm[query_input] directly). Saturation comparator at 1.0.

**arms-must-differ at each phase point:** TASK_VECTOR > RANDOM_VECTOR by > 0.20 (top1_recall) at HARD_PASS bands; if TASK_VECTOR <= RANDOM_VECTOR at any low-K low-V point, META_RULE_AM flag (substrate has regime where task-vector mechanism isn't load-bearing).

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = top1_recall in [0,1])

Phase-diagram metric: **K_cliff_per_(N_tasks, overlap)** = smallest K such that TASK_VECTOR top1 drops below 0.40 (loose cleanup floor).

- **HARD_PASS** (chain-grade confirmation):
  - For at least one (N_tasks, overlap) combo, **K_cliff lies WITHIN the swept range** (i.e., we OBSERVE the cliff) — proves non-saturation.
  - AT LEAST ONE phase-point at K=1 with V<=50 shows TASK_VECTOR top1 >= 0.95 (proves mechanism works at low load).
  - AT LEAST ONE phase-point shows TASK_VECTOR top1 < 0.40 (proves cliff is observable).
  - arms-must-differ: avg(TASK_VECTOR - RANDOM_VECTOR) across all phase points >= 0.20.
  - Monotone-with-K within each (V, overlap) slice (allowing 0.02 tolerance).

- **MIDDLE_BAND**:
  - K_cliff observable in 1-2 (V, overlap) combos out of 9 (cliff exists but regime-narrow).
  - OR arms differ by 0.10-0.20 on average.

- **HARD_FAIL** (saturation-trivial OR un-mechanistic):
  - TASK_VECTOR top1 >= 0.95 at ALL 63 phase points (no cliff observable — by-construction saturation; M3 concern #4 NOT confirmed; primitive's chain-grade was K=5 boundary artifact).
  - OR avg(TASK_VECTOR - RANDOM_VECTOR) < 0.10 (mechanism not load-bearing).
  - OR ANY (low-K, low-V) point shows TASK_VECTOR <= RANDOM_VECTOR (META_RULE_AM regime-flip).

**IMPORTANT FINDING ANNOTATION:** verdict_msg MUST cite the smallest cliff-K observed across all (V, overlap), as "K_cliff_min=X at V=Y overlap=Z". This is the headline number for M3 concern #4 resolution.

## FAIRNESS GATES

- Same N_DIM=8192 across all arms + phase points.
- Same encoder (HRR bipolar random, FFT bind).
- Same entity codebook per seed (regenerated per seed).
- Each phase point draws K context pairs fresh; query is one of the K presented inputs.
- task_overlap: shared INDICES across the N_tasks within a seed (pool shared at overlap fraction).
- Q-discipline: TASK_VECTOR top1 = 1.000 at K>=50 V>=50 triggers leakage audit (would imply mechanism beats Plate capacity = bug).
- META_RULE_AM check: if RANDOM_VECTOR > TASK_VECTOR at any (K, V, overlap), flag as regime-flip evidence.

## CARDINALITY (META_RULE_H)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms * 7 K * 3 V * 3 overlap * N_QUERIES = 189 phase-points * Q
  - With N_QUERIES = 10 per (arm, K, V, overlap) → 1890 results per seed.
- **EXPECTED_N_UNITS_SMOKE** = 3 arms * 5 corner-points * 2 queries = 30 results (smoke gate: 5 corner points all run; 1 seed only).
- **EXPECTED_N_UNITS_PER_SIBLING_FULL** = 1890 (one seed per sibling chunk).
- **EXPECTED_N_SEEDS_CHUNKED** = 3 (seed 7, 13, 19; one sibling file each).

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == 1890)` per sibling full; `cardinality_ok = (observed_n == 30)` for smoke.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

- Smoke at **full N_DIM=8192** (not toy N=512) — substrate saturation tolerance scales with N.
- Smoke includes 5 corner points spanning low-K low-V (saturation regime) to high-K high-V (cliff regime).
- If smoke shows TASK_VECTOR >= 0.95 at ALL 5 corners, **smoke fails** (discriminator didn't fire) — full dispatch BLOCKED per USER 2026-06-26 rule.
- Required smoke evidence: at LEAST 1 corner point with TASK_VECTOR < 0.95 (cliff observable in smoke).

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `_seed_checkpoint.py`.

## GPU REQUIREMENT (Fix #24)

- torch.cuda primary backend (CPU fallback emits WARN line + halts if env requires GPU).
- Batched FFT bind across K-shot bundle (single torch.fft.rfft over (K, N_DIM) tensor).
- Encoder hoisted ONCE per seed (entity codebook generated and cached).
- Smoke profiles GPU util via `nvidia-smi` parse from runner; gate >= 50%.
- N_DIM=8192 (memory: 8192*float32*1000=32MB per bundle batch; fits comfortably).

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_7.py`
- `exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_13.py`
- `exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_19.py`

Each sibling: 1 seed × 63 phase points × 3 arms × 10 queries = 1890 result records.
Aggregation step (post hoc): combine 3 sibling metrics.json files into phase-map matrix; verdict computed per-sibling AND combined.

## COMPUTE

- Smoke (1 seed × 5 corners × 3 arms × 2 queries = 30 results): ~30-60 sec GPU on overnight_queue.
- Full sibling (1 seed × 1890 results, batched): ~15-30 min GPU on overnight_queue.
- 3 sibling full dispatch: ~1-1.5 GPU-hr aggregate.
- Timeout per sibling: 18000s (5 hr buffer).

## SUBSTRATE PREREQS (cite chain-grade primitives)

- HRR bind / unbind (chain-grade; cell `exp_task_vector_in_context_kshot_v1_FULL` 2026-06-27 — K=5 top1=1.000)
- Bundle (additive sum + normalize; same cell)
- Cleanup via cosine argmax over entity codebook (same)

## M3 CONCERN #4 RESOLUTION DECISION TABLE

| Smoke + Full outcome | M3 concern #4 verdict |
|---|---|
| HARD_PASS — cliff observable + arms differ | TASK_VECTOR is genuine chain-grade primitive (regime-wide) |
| MIDDLE_BAND — cliff in 1-2 combos | Primitive is regime-narrow; usable for ICL but with bounded K |
| HARD_FAIL — no cliff anywhere OR arms don't differ | Online conv #4 NOT supported by TV mechanism — needs alternate (hippo/explicit-write) |

## NOTES

- Today's `online_conv_oneshot_taskvec_hippo_v1` HARD_FAIL had TV_ONLY=1.000 — that was a confounding K=1 single-shot test that hit floor. This cell extends to K=100 in 3 dimensions to PROVE OR REFUTE saturation-triviality.
- This is a Stage 3 cell (compositional understanding), not Stage 4 (language).
- Per USER 2026-06-27 substrate-as-canonical: cell builds on cert atom from `exp_task_vector_in_context_kshot_v1_FULL` (K=5 chain-grade) — see substrate registry query.
