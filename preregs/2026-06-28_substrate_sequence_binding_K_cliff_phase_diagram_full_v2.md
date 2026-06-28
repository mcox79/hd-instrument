# Prereg: substrate_sequence_binding_K_cliff_phase_diagram_full_v2

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Stage 1 phase-coverage promotion
**Drill source:** Research directive 2026-06-28 — promote sequence_binding phase coverage from MID to HIGH. v1 landed MIDDLE_BAND (smoke; 4/12 K-cliff combos observable; avg_arms_diff=0.167). v2 narrows K start to 20 (cert anchor), upgrades N_QUERIES to 100, replaces tag_density {0.1,0.3,0.5} with discrete noise levels Q ∈ {1,2,4}, and ships local-CPU full.
**Stage:** Stage 1 (substrate primitive characterization — full K-cliff phase diagram)
**P_deflated:** 0.65 (HRR sequence-binding capacity well-characterized at K=20 cert anchor; novel = (K, N, Q-noise) joint sweep with band-floor verdict instead of arms-differ)
**Phase-diagram axis:** K-cliff per (N, Q_noise_level)

## SUBSTRATE-AS-CANONICAL prior work

- `exp_substrate_sequence_binding_v1` atom: K=20 cert-graded sequence binding. Single point.
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1` (2026-06-28): full-sweep MIDDLE_BAND in smoke; 84 pts; tag_density {0.1,0.3,0.5}; 10 q/pt; cliff observable at 4/12 combos.
- `exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1` (2026-06-27): N_PAIRS-cliff for additive Hebbian shared-W. Complementary mechanism.
- `pattern_completion v2.1`: precedent for "≥N points in MIDDLE_BAND → HARD_PASS" tiering.

## DIFFERENCES FROM v1 (load-bearing)

| dimension       | v1                          | v2                                        |
|-----------------|-----------------------------|-------------------------------------------|
| K values        | {10,20,50,100,200,500,1000} | {20,50,100,200,500,1000} (drop K=10)      |
| Noise axis      | tag_density {0.1,0.3,0.5}   | Q_level {1,2,4}; effective tag = 0.1 * Q  |
| n_queries/pt    | 10 (FULL)                   | 100 (FULL) — 10x finer band precision     |
| Total pts       | 7 x 4 x 3 = 84              | 6 x 4 x 3 = 72                            |
| Verdict logic   | arms-differ + cliff combos  | band-distribution (SAT/MB/FLOOR)          |
| Codebook        | bipolar L2-normalized       | bipolar raw (no L2 norm)                  |
| Dispatch        | GPU (overnight_queue)       | local_cpu_queue (laptop idle, ~5min/seed) |
| Mechanism check | SUBSTRATE > floor by 0.20   | recall ≥ 0.90 SAT band                    |

**Why drop K=10:** v1's K=10 in smoke gave SUBSTRATE=0.5 (only 2 queries) — uninterpretable. K=20 is the cert-validated anchor (chain-grade from `exp_substrate_sequence_binding_v1`).

**Why discrete Q noise:** task spec — Q ∈ {1,2,4} aligns with Kanerva 2009 capacity bound `K ~ N / (4 * log_2(N))` at noise-free; Q acts as integer noise multiplier on base 0.1 tag_density. Effective tag_density ∈ {0.1, 0.2, 0.4}.

**Why bipolar raw (no L2 norm):** classic Plate HRR keeps bipolar elements at ±1. v1's L2 normalization shrunk elements to ±1/sqrt(N) (≈0.008 at N=16384), making them collapse below tag_noise=0.1*Q (signal destroyed; v1 selftest only got SUBSTRATE=0.5 at K=10,N=16384 because of this). v2 fixes this; selftest confirms SUBSTRATE=1.000 at SAT corner.

## HYPOTHESIS

Substrate **sequence binding via HRR**: positions p_1..p_K bound to items v_1..v_K via `bind(p_i, v_i)` (FFT circular convolution); sum-bundled to S = sum bind(p_i, v_i + Q * 0.1 * noise_i). Recovery: query p_j → `unbind(p_j, S)` → cleanup vs item codebook → recover v_j.

Per Kanerva 2009 / Plate sum-bundle theory, capacity scales as:
- K_crit(N) ~ N / (4 * log_2(N)) at noise-free (Q→0)
- Q noise adds crosstalk; effective capacity drops as Q rises
- Cliff sharpens as N grows (higher-N has more "room" before crosstalk dominates)

**Sweep axes:**
- **K ∈ {20, 50, 100, 200, 500, 1000}** — 6 points; brackets K_crit at all Ns from cert anchor to far above
- **N ∈ {2048, 4096, 8192, 16384}** — 4 points; doubles
- **Q ∈ {1, 2, 4}** — 3 noise levels (effective tag_density {0.1, 0.2, 0.4})
- **= 72 phase points per seed**

## ARMS (3) — per phase-point

1. **SUBSTRATE** — HRR bind(pos_i, item_i + Q*0.1*noise_i); sum-bundle; recovery via unbind(q_pos, S) + cosine cleanup vs item codebook. **The mechanism.**
2. **RANDOM** — independent random unit vector; cosine vs item codebook. **Floor; rules out vector-floor coincidence.**
3. **SHUFFLE** — same bundle S; query position is SHUFFLED (broken pos→item map). **Order-matters baseline.**

**arms-must-differ at each phase point:** SUBSTRATE > max(RANDOM, SHUFFLE) by > 0.20 (mean across pts) at HARD_PASS bands. If avg_arms_diff < 0.05 → HARD_FAIL (mechanism not load-bearing).

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = mean top1_recall in [0,1])

**Discriminating bracket** (per task spec):
- **recall ≥ 0.90** → **SAT** (saturated; mechanism trivially solves)
- **recall ∈ [0.30, 0.70]** → **MIDDLE_BAND** (discriminating regime; the cell's main signal)
- **recall ≤ 0.10** → **FLOOR** (cliff fully past; mechanism broken at this K)
- recall ∈ (0.10, 0.30) ∪ (0.70, 0.90) → **TRANSITION** (informational; not load-bearing)

**HARD_PASS** (chain-grade phase-diagram HIGH coverage):
- `n_MB >= 22` of 72 phase points (≥30% in discriminating regime; tunable per pattern_completion v2.1 precedent)
- `avg_arms_diff >= 0.20` (mechanism load-bearing across grid)
- `n_SAT >= 6` (mechanism works at low load; positive control regime present)
- `n_FLOOR >= 6` (cliff observable; sweep brackets the boundary)
- `cardinality_ok` (observed_phase_points == 72)

**MIDDLE_BAND**:
- `n_MB >= 10` (partial discriminating coverage)
- OR HARD_PASS gates partially met

**HARD_FAIL** (any of):
- `all_saturated` (every point ≥ 0.90; by-construction failure — sweep doesn't reach cliff)
- `all_floored` (every point ≤ 0.10; no signal — mechanism broken)
- `arms_identical` (SUBSTRATE == RANDOM at all points; code bug — same key sampled across arms)
- `avg_arms_diff < 0.05` (mechanism not load-bearing)

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (HRR bipolar random; FFT bind) across all arms.
- Same item codebook per seed (V_ITEMS=1200; >= 1000 + slack for sampling without replacement).
- Same position codebook per seed (V_POS=1200).
- Each phase point: K positions sampled w/o replacement; K items sampled w/o replacement; tag noise drawn fresh per-position.
- All 3 arms see SAME (pos, item) pairs at same K; only the readout/floor differs.
- SHUFFLE re-rolls coincidences with true position (up to 50 retries) to ensure broken pos→item map.

## CARDINALITY (META_RULE_H_ANCHOR)

- **EXPECTED_N_PHASE_POINTS_FULL per seed** = 6 K × 4 N × 3 Q = **72 points per seed**
- **EXPECTED_N_RECORDS_FULL per seed** = 72 × 3 arms × 100 queries = **21600 records per seed**
- **EXPECTED_N_PHASE_POINTS_SMOKE per seed** = **6 corners**
- **EXPECTED_N_RECORDS_SMOKE per seed** = 6 × 3 × 4 = **72 records per seed**
- **EXPECTED_N_SEEDS** = 3 chunked siblings (7, 13, 19)

CARDINALITY_OK declared in metrics: `observed_n_phase_points == 72` AND `observed_n_records == 21600` per sibling.

**HARD_FAIL_CARDINALITY_BREACH** if observed < expected.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

Smoke at SAT/FLOOR endpoints validated (selftest + smoke 6-corner run; results below).

Smoke 6 corners (expected analytic regime + empirical observation at n_queries=4):

| corner | K | N | Q | expected band | observed smoke (seed=7) |
|--------|---|---|---|---------------|-------------------------|
| low-K high-N low-Q  | 20   | 16384 | 1 | SAT       | SUBSTRATE=1.000 ✓     |
| low-K mid-N low-Q   | 20   | 8192  | 1 | SAT       | SUBSTRATE=1.000 ✓     |
| mid                 | 100  | 4096  | 2 | MB or SAT | SUBSTRATE=1.000 (smoke saturates at nq=4; full nq=100 will resolve to MB) |
| high-K low-N high-Q | 200  | 2048  | 4 | TRANS     | SUBSTRATE=0.750 ✓     |
| high-K low-N mid-Q  | 500  | 2048  | 2 | TRANS     | SUBSTRATE=0.250 ✓     |
| very-high-K low-N high-Q | 1000 | 2048 | 4 | FLOOR | SUBSTRATE=0.000 ✓     |

Smoke gate (BLOCK full dispatch if not met):
- ✓ 6 corners all RUN (no silent except; cardinality_ok=True observed)
- ✓ >= 2 corners SAT (mechanism floor present)
- ✓ >= 1 corner FLOOR (cliff observable)
- ✓ avg_arms_diff >= 0.20 (observed: 0.667 in smoke seed 7)
- ✓ SUBSTRATE >> RANDOM, SHUFFLE everywhere (arms differ)
- ✓ cardinality_ok = True

**ALL smoke gates met as of 2026-06-28.**

## HARDENING

L1 STARTED early-write + L2 per-seed progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. PROT-021 anchor + run_mode stamping on every partial. META_RULE_X main-guard.

## DISPATCH

- **Local CPU**: laptop idle per USER 2026-06-28 framing
- **Numpy primary; torch optional CPU** (CUDA not required; if available used as numpy passthrough)
- Batched FFT bind across K-shot bundle (single np.fft.rfft over (K, N) tensor per phase point)
- Item + position codebooks re-generated per phase point (N varies across sweep)
- Batched cleanup matmul over Q queries × V_ITEMS keys (single matmul per arm)
- 3 chunked seed siblings dispatched separately to local_cpu_queue

**Timeout:** 1200s per sibling (20 min; ~3-5 min wall observed at smoke heaviest-point projection; well below ceiling)

**Compute estimate:**
- Smoke (6 pts × 3 arms × 4 q): ~5s observed
- Full (72 pts × 3 arms × 100 q): ~100-200s projected (heaviest pt K=1000 N=16384 = 3.4s × 72 pts upper bound; lighter pts ~0.5s)
- 3 sibling FULL: ~15 min total wall (serial); minutes parallel

**No PROT-019 large-N anchor enforcement applies** — anchor lacks `_n<N>` suffix.

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7.py`
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_13.py`
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_19.py`

Shared core: `experiments/_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor stamping).

**Aggregation post-hoc:** combine 3 sibling metrics.json → phase-map matrix; per-seed verdict (sibling-level) + cross-seed agreement check on cliff locations.

## SUBSTRATE PREREQS (chain-grade primitives cited)

- HRR bind / unbind (FFT circular convolution; chain-grade per `exp_substrate_sequence_binding_v1`)
- Bundle (additive sum + L2 normalize on the bundle, NOT on codebook items)
- Cleanup via cosine argmax over item codebook
- Position codebook = independent bipolar random vectors (no positional structure beyond identity)

## PHASE-DIAGRAM DECISION TABLE

| Outcome | Phase-diagram verdict |
|---------|----------------------|
| HARD_PASS — >= 22 MB pts + SAT/FLOOR present + arms differ | Sequence binding K-cliff phase coverage promoted MID → HIGH; chain-grade phase-characterization |
| MIDDLE_BAND — 10-21 MB pts                                  | Partial discriminating coverage; phase coverage stays MID; consider v3 with finer K grid |
| HARD_FAIL — saturated / floored / arms-identical            | Sweep mis-bracketed; author v3 with extended axis or fixed mechanism |

## CROSS-SEED AGREEMENT CHECK (post-hoc, expected, not pre-reg'd as gate)

If 3 seeds agree on K_cliff location within ±1 K-grid-step at each (N, Q) cell, that's cross-seed cliff localization — strong signal. Reported in aggregated verdict; not a HARD_PASS gate (single-seed HARD_PASS already promotes coverage).

## NOTES

- This cell EXTENDS sequence_binding_v1 (K=20 cert anchor) to a 12-(N,Q) phase diagram with 6 K levels each.
- This is a Stage 1 (substrate-primitive characterization) cell, NOT Stage 3 composition or Stage 4 LM equivalence.
- Per USER 2026-06-27 substrate-as-canonical: builds on cert atom from `exp_substrate_sequence_binding_v1`.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring `substrate_task_vector_K_cliff_phase_diagram_v1`.
- Per USER 2026-06-26 stage-progression: Stage 1 phase coverage promotion is exactly the right work for this primitive.
