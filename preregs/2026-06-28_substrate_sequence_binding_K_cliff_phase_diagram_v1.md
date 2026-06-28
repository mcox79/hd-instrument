# Prereg: substrate_sequence_binding_K_cliff_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Stage 1 phase-diagram coverage
**Drill source:** Research directive 2026-06-28 — sequence_binding is chain-grade at K=20 single-point (`exp_substrate_sequence_binding_v1` atom; cert-graded). Phase coverage ~15% (one K + one N). Layer-2 phase operations need cliff data. Per USER phase-diagram framework: build Layer-1 coverage for all chain-grade primitives.
**Stage:** Stage 1 (substrate primitive characterization — push K-cliff boundary)
**P_deflated:** 0.60 (HRR sequence-binding capacity well-characterized; novel = (K, N, tag_density) joint coverage in one cell)
**Phase-diagram axis:** K-cliff per (N, tag_density)

## SUBSTRATE-AS-CANONICAL prior work

- `exp_substrate_sequence_binding_v1` atom: K=20 ordered-pair recovery from sum-bundled bind(pos_i, item_i). Chain-grade. Single point in phase space.
- `exp_substrate_task_vector_K_cliff_phase_diagram_v1` (2026-06-28; this same template). Sibling phase-diagram for TASK_VECTOR ICL — same chunked-per-seed architecture.
- `exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1` (2026-06-27): N_PAIRS-cliff for additive Hebbian shared-W. Distinct mechanism (no FFT; W matrix store). Complementary data.

## HYPOTHESIS

Substrate **sequence binding via HRR**: positions p_1..p_K bound to items v_1..v_K via `bind(p_i, v_i)`; sum-bundled to S = sum bind(p_i, v_i). Recovery: query position p_j → `unbind(p_j, S)` → cleanup vs item codebook → recover v_j.

K-shot capacity bounded by Plate sum-bundle theory:
- `K_critical(N, tag) ~ sqrt(N / (4 * alpha(tag)))` where `alpha = 2 + 12 * tag_density`
- N_DIM=2048: K_crit ~ 12 at tag=0.1, ~8 at tag=0.5
- N_DIM=4096: K_crit ~ 18 at tag=0.1, ~11 at tag=0.5
- N_DIM=8192: K_crit ~ 25 at tag=0.1, ~16 at tag=0.5
- N_DIM=16384: K_crit ~ 36 at tag=0.1, ~23 at tag=0.5

Tag_density = fraction of N positions where a noisy per-position tag vector is summed into each bound pair (models per-position contextual noise).

**Sweep axes:**
- **K (pairs bound in sequence) ∈ {10, 20, 50, 100, 200, 500, 1000}** (7 points; brackets K_crit from below to far above)
- **N (HD dimension) ∈ {2048, 4096, 8192, 16384}** (4 points; doubles)
- **tag_density ∈ {0.1, 0.3, 0.5}** (3 points)
- **= 84 phase points per seed**

## ARMS (3) — per phase-point

1. **SUBSTRATE** — HRR bind(pos_i, item_i + tag_density * noise_i); sum-bundle; recovery via unbind(query_pos, S) + cleanup vs item codebook. **The mechanism.**
2. **RANDOM** — random vector of same norm; cosine vs item codebook. **Floor; rules out vector-floor coincidence.**
3. **SHUFFLE** — same bound pairs as SUBSTRATE but query position is RANDOMLY SHUFFLED before unbind (broken position→item map). **Order-matters baseline; catches whether position binding is load-bearing at this K.**

**arms-must-differ at each phase point:** SUBSTRATE > max(RANDOM, SHUFFLE) by > 0.20 (top1_recall) at HARD_PASS bands. If SUBSTRATE <= SHUFFLE at any low-K low-tag point with N >= 4096, META_RULE_AM regime-flip flag (position-binding not load-bearing).

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = top1_recall in [0,1])

Phase-diagram headline: **K_cliff_per_(N, tag_density)** = smallest K such that SUBSTRATE top1 drops below 0.50.

- **HARD_PASS** (chain-grade phase-diagram confirmation):
  - For >= 6 (N, tag_density) combos out of 12, **K_cliff lies WITHIN the swept range** (i.e., we OBSERVE the cliff)
  - AT LEAST ONE phase-point at K=10 with N >= 8192 shows SUBSTRATE top1 >= 0.90 (mechanism works at low load + high N)
  - AT LEAST ONE phase-point shows SUBSTRATE top1 < 0.20 (cliff observable past the threshold)
  - arms-must-differ: avg(SUBSTRATE - max(RANDOM, SHUFFLE)) across all phase points >= 0.20
  - Monotone-with-K within each (N, tag) slice (allowing 0.05 tolerance for finite-Q variance)
  - K_cliff scales monotone with N (higher N → larger K_cliff) for at least 2/3 of tag values

- **MIDDLE_BAND**:
  - K_cliff observable in 3-5 (N, tag) combos out of 12 (cliff exists but regime-narrow)
  - OR arms differ by 0.10-0.20 on average
  - OR no monotone-with-N scaling

- **HARD_FAIL**:
  - SUBSTRATE top1 >= 0.95 at ALL 84 phase points (by-construction saturation — sweep didn't reach cliff; cell informational-FAIL)
  - OR avg(SUBSTRATE - max(RANDOM, SHUFFLE)) < 0.10 (mechanism not load-bearing)
  - OR ANY (low-K=10, low-tag=0.1, N>=4096) point shows SUBSTRATE <= SHUFFLE (META_RULE_AM regime-flip)

**HEADLINE per (N, tag):** K_cliff value (or "NO_CLIFF_WITHIN_SWEEP") — this is the load-bearing phase-diagram output.

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (HRR bipolar random; FFT bind) across all arms.
- Same item codebook per seed (V=1024 items, regenerated per seed; large enough for K=1000 sampling without replacement).
- Same position codebook per seed (max K = 1000 positions).
- Each phase point: K positions sampled without replacement; K items sampled without replacement; tag noise drawn fresh per-position.
- All 3 arms see SAME (pos, item) pairs at same K; only the readout/floor differs.
- Q-discipline: SUBSTRATE top1 = 1.000 at K>=200 N=2048 triggers leakage audit (would imply mechanism beats Plate capacity = bug).

## CARDINALITY (META_RULE_H_ANCHOR)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms × 7 K × 4 N × 3 tag × 10 queries = **2520 records per seed**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms × 6 corners × 2 queries = **36 records per seed**
- **EXPECTED_N_SEEDS** = 3 chunked siblings (seed 7, 13, 19)
- **EXPECTED_N_UNITS_AGGREGATE_FULL** = 2520 × 3 = **7560 records**

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == expected_n)` per sibling.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

Smoke 6 corners (verified analytically):

| corner                      | K    | N     | tag | K/K_crit | expected_top1     |
|-----------------------------|------|-------|-----|----------|-------------------|
| low-K low-N low-tag         | 10   | 2048  | 0.1 | 0.79     | MID (0.3-0.7)     |
| high-K low-N low-tag        | 1000 | 2048  | 0.1 | 79.06    | LOW (<0.05)       |
| low-K high-N low-tag        | 10   | 16384 | 0.1 | 0.28     | HIGH (>=0.85)     |
| high-K high-N high-tag      | 1000 | 16384 | 0.5 | 44.19    | LOW (<0.05)       |
| mid                         | 100  | 4096  | 0.3 | 7.40     | LOW (<0.05)       |
| high-K low-N high-tag       | 500  | 2048  | 0.5 | 62.50    | LOW (<0.05)       |

Smoke gate (BLOCK full dispatch if not met):
- 6 corners all RUN (no silent except)
- >= 2 corners discriminate (SUBSTRATE > max(RANDOM, SHUFFLE) by > 0.20) — typically low-K corners
- >= 1 corner saturates (low-K high-N: top1 >= 0.85)
- >= 1 corner fails (high-K corners: top1 < 0.05)
- GPU util p50 >= 50% (Fix #24)
- cardinality_ok (observed_n == 36)
- arms_differ SHA-256 (RANDOM vector seed independent of SUBSTRATE seed verified per-point)

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. META_RULE_X main-guard. PROT-021 N+anchor stamp on every partial.

## GPU REQUIREMENT (Fix #24)

- **`import torch` AT TOP OF CORE FILE** (gate validates GPU eligibility on top-level imports)
- torch.cuda primary backend; CPU fallback emits WARN + halts if HDLAB_REQUIRE_CUDA=1
- Batched FFT bind across K-shot bundle (single torch.fft.rfft over (K, N) tensor per phase point)
- Item + position codebooks hoisted ONCE per seed
- All 3 arms run as torch ops in same CUDA stream
- Smoke profiles GPU util via `nvidia-smi` (sampler thread); gate >= 50%
- Memory: N=16384 × float32 × 1000(K) ≈ 64MB per bundle batch; fits H100/A100/3090 comfortably

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_7.py`
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_13.py`
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_19.py`

Shared core: `experiments/_substrate_sequence_binding_K_cliff_phase_diagram_v1_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor + N stamping).

Aggregation post-hoc: combine 3 sibling metrics.json → phase-map matrix; verdict computed per-sibling AND combined.

## COMPUTE

- Smoke (1 seed × 6 corners × 3 arms × 2 queries = 36 records): ~30-90 sec GPU on overnight_queue
- Full sibling (1 seed × 84 phase points × 3 arms × 10 queries = 2520 records, batched): ~30-60 min GPU
- 3 sibling FULL aggregate: ~1.5-3 GPU-hr
- Timeout: smoke 1800s; full 18000s per sibling (5 hr buffer; PROT-019 not applicable — no _n<N> suffix in anchor)

## SUBSTRATE PREREQS (chain-grade primitives cited)

- HRR bind / unbind (FFT-based; chain-grade per `exp_task_vector_in_context_kshot_v1_FULL` and `exp_substrate_sequence_binding_v1`)
- Bundle (additive sum + L2 normalize)
- Cleanup via cosine argmax over item codebook
- Position codebook = independent bipolar random vectors (no positional structure beyond identity-binding)

## PHASE-DIAGRAM DECISION TABLE

| Smoke + Full outcome                        | Phase-diagram verdict                                              |
|---------------------------------------------|--------------------------------------------------------------------|
| HARD_PASS — cliff in 6+ combos + arms differ | Sequence binding K-cliff fully mapped; Layer-2 operations green-lit |
| MIDDLE_BAND — cliff in 3-5 combos            | Regime-narrow; Layer-2 ops bounded                                 |
| HARD_FAIL — no cliff or arms don't differ   | Bracket extended OR mechanism not load-bearing — author v2         |

## NOTES

- This cell EXTENDS sequence_binding_v1 (K=20 single point) to a 12-combo phase diagram.
- This is a Stage 1 (substrate-primitive characterization) cell, not Stage 3 (composition).
- Per USER 2026-06-27 substrate-as-canonical: builds on cert atom from `exp_substrate_sequence_binding_v1`.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring `substrate_task_vector_K_cliff_phase_diagram_v1`.
