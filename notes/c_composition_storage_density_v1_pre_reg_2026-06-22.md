# Pre-reg: c_composition_storage_density_v1

**Date:** 2026-06-22
**Anchor:** `c_composition_storage_density_v1`
**Cell file:** `experiments/exp_c_composition_storage_density_v1.py`
**Author:** exp_dev (autonomous spawn under Director routing)
**Cert-owner:** skunkworks (landed-VET)
**P:** 0.40 (novel-synthesis cap; deflated because 4-mechanism orthogonality is theoretically uncertain)

## Why this cell exists

USER 2026-06-22 storage-density question: substrate is ~15x denser than LLMs at single-mechanism
chain-grade (n8 ConceptNet 100k facts). Brain-drills + cell-pipelines surfaced 4+ capacity-lifting
mechanisms ONE BY ONE. No cell has combined them. This cell measures the compound effect.

## Mechanisms composed

1. **Baseline (Arm 1):** plain multi-value Hebbian (= n8 mechanism unchanged)
2. **+ Modular K-macrocolumn (Arm 2):** K=8 content-routed; sqrt(K) capacity claim
3. **+ Whitening (Arm 3):** ZCA decorrelation on encoded keys before Hebbian write
4. **+ kWTA-sparse (Arm 4):** sparse readout (k=20-of-256 winner-take-all on the recall scores)
5. **+ ALL COMBINED (Arm 5):** modular + whitening + kWTA stacked

## Cell design

Pure synthetic-bipolar KG (no encoder; no Pythia; structural test only):
- `M_grid = [1000, 10000, 50000, 100000]` triples (smoke uses M=[500, 2000])
- `N_DIM = 4096` (matches n8 baseline)
- `V_C = 1024` (entity codebook size; ~50k synthetic entities sampled per M)
- multi-value (each (s, p) -> 1-10 objects)
- 5 arms x 3 seeds at each M
- Metrics: `setrecall_all`, `setrecall_1to1`, `refuse_ood`, `eff_rank`, `wall_s`

## Pre-reg HARD bands

Define `M_fail(arm) = smallest M where setrecall_all < 0.95 for that arm`. Baseline (Arm 1) fail
boundary is the reference. Compound lift `L = M_fail(Arm 5) / M_fail(Arm 1)`.

- **HARD_PASS** (chain-grade): `L >= 5.0` AND substrate-only-decode preserved (n_llm == 0)
  AND `cv <= 0.10` across seeds AND Arm 1 reproduces n8's chain-grade pattern at M=10k
  (sanity check: Arm 1 setrecall@10k >= 0.95).
- **HARD_FAIL:** `L <= 1.5` (compound mechanisms don't compose; either independent mechanisms
  break each other OR mechanisms aren't actually orthogonal as theorized).
- **MIDDLE_BAND:** `1.5 < L < 5.0` — partial compounding; characterize which mechanism-pair is
  the load-bearing combo (look at single-mechanism arms' individual lifts).

## Discriminator regime (Fix #16)

Arm 1 (baseline) MUST hit n8's chain-grade pattern at M=10k. If Arm 1 setrecall@10k < 0.90,
the harness is broken — HARD_HALT and surface to Director.

## By-construction-saturation guard

At small M (M=1000), ALL arms saturate (setrecall ~= 1.0). The discriminator regime is large M
where some arms fail and others don't. Report curve so the discriminator regime is visible.

## Substrate-only-decode gate

- `_LLM_CALL_COUNTER = [0]` at module top (pure numpy, by construction)
- assert `n_llm_calls_at_inference == 0` in metrics

## Per-Fix discipline (autonomous-arc 7+ fixes)

- Fix #1 (1 ScheduleWakeup): N/A — exp_dev does not schedule wakeups
- Fix #3 (per-seed runtime measured): smoke locally measures per-seed wall at M=10k before full dispatch
- Fix #5 (run_mode check first): cell honors `HDLAB_EXP_NAME` suffix `_smoke` (TODO #6 pattern)
- Fix #6 (zero-D-overlap fallback): N/A (no LM decode in this cell)
- Fix #7 (status-line on long waits): pipeline-agent pattern (not applicable to direct dispatch)
- Fix #16 (discriminator regime): Arm 1 baseline at M=10k must reproduce n8 pattern
- Fix #17 (wall measurement): single-seed at M=10k all 5 arms BEFORE dispatching M=100k full

## Wall budget

Per-seed estimate (synthetic-bipolar; no encoder forward):
- Arm 1 Hebbian outer-product loop at M=100k, N_DIM=4096: ~100k * 67ms = ~7 min (vectorized BLAS via chunked matmul)
- Arm 2 modular K=8: ~7 min (per-shard dim ~1448; total params identical)
- Arm 3 whitening: +30s for ZCA fit on key matrix
- Arm 4 kWTA readout: negligible
- Arm 5 (combined): ~8 min (dominant: modular + whitening fit)

5 arms x 3 seeds x ~7 min/cell = ~105 min per M. M_grid covers 4 points, BUT smaller M are much
cheaper: total ~120-150 min wall on remote_cpu_queue (3 hours conservatively).

**Wall budget:** 10800s (3 hr) per queue_add timeout per autonomous-arc TODO #8 (encoding-dominant
cells get 2-3x default 3600s).

## v2 deferred

`M=500k` and `M=1M` deferred to v2. If v1 HARD_PASS, v2 pushes the upper bound to find the
new compound failure boundary. If v1 MIDDLE_BAND or HARD_FAIL, v2 unnecessary — revival drill
identifies which mechanism-pair composes vs competes.

## Information value (regardless of outcome)

- HARD_PASS: substrate's path to LLM-class storage density (10M-100M facts per 10-50GB) is
  chain-grade-substantiated; storage-density program proceeds to v2.
- HARD_FAIL: rules out simple-compounding hypothesis; routes 2x revival to Research with the
  observed mechanism-pair conflict.
- MIDDLE_BAND: characterizes which mechanism subset compounds; routes specific 2x-pair drills.

## Atom-ID candidate

`storage::T3/EXP_c_composition_storage_density_v1`

## Cites

- n8 ConceptNet ingest (`exp_n8_conceptnet_ingest_eval_v1.py`) — multi-value Hebbian baseline
- m1 modular macrocolumn (`exp_m1_modular_macrocolumn_W_v1.py`) — K-shard architecture
- n10 whitening (`exp_n10_whitening_projection_revival_v1.py`) — ZCA primitive
- n4 kWTA-VQ (`exp_n4_kwta_soft_decode_v1.py`) — sparse readout primitive
- `hdlab/whitening.py` — canonical ZCA implementation

## Asks

- **skunkworks:** SCHEMA-VET this pre-reg + landed-VET on data arrival; ratify or adjust
  inline disposition; A5-gated Store write if chain-grade
- **research (Director):** route 2x revival on negative; cross-check pre-reg direction
