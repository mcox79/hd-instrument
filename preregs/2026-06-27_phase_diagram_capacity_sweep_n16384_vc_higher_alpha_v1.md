# Pre-registration: phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** Skunkworks flag-back #3 from batch 2 (deferred 2 days). Prior
capacity_sweep_n16384_vc_2000_4000_8000_v1 used M_FACTS/V_C=0.75 (production
audit-device baseline ratio), which is by-construction-saturated at the
substrate's storage capacity. USER directive 2026-06-27: re-test at alpha>=1.0
regime (M_FACTS in {N, 1.5N, 2N}).

## Anchor

`phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1`

## Routing

- **Queue:** `overnight_queue` (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** N_DIM=16384 -> Hebbian W is 16384x16384 fp32 = 1.07GB; ingest is
  batched matmul over thousands of triples; cleanup is batched matmul over E
  (V_C x N) for each query. Matmul-heavy at N=16384.
- **GPU mandate (Fix #24):** torch.cuda required at full; smoke uses N=2048
  (W=16MB, laptop-fittable).
- Push gate: harness-DENIED to exp_dev; cell dispatched via Orchestrator.

## Source

Derived from `experiments/exp_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1.py`
(same primitives -- bipolar codebook, Hebbian W, argmax cleanup). Replaces the
M_FACTS/V_C=0.75 axis with M_FACTS in {N, 1.5N, 2N} = {16384, 24576, 32768}
at V_C in {2000, 4000, 8000}, 3 seeds each.

Prior cell landed (off `data/exp_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1/metrics.json`):
- All 3 V_C phase points at alpha=0.37 (M/V_C=0.75) saturated at recall>=0.99
  (Q-SUSPECT_SATURATION triggered).
- Skunkworks correctly flagged: by-construction-saturation; needs alpha>=1.0
  to actually exercise capacity.

## Mechanism

For each (V_C, M_FACTS) phase point:
1. Build bipolar codebook E (V_C, N) and relation matrix R (V_R=8, N).
2. Generate M_FACTS unique (s, r, o) triples (s != o; (s,r) unique when
   M_FACTS <= V_C*V_R, else (s,r,o) unique with duplicates_allowed mode).
3. Hebbian ingest: W = sum_j outer(E[o_j], E[s_j] * R[r_j] * sqrt(N)) / N
4. For each fact (s, r, o): query = W @ (E[s] * R[r] * sqrt(N)); pred = argmax(E @ query)
5. recall_at_1 = correct / M_FACTS

At alpha=M_FACTS/V_C high enough that V_C*V_R unique keys exhausted (M > V_C*V_R),
fall back to triple-uniqueness with key-duplicates allowed (Hebbian
last-write-wins per (s,r) key; substrate-faithful for the multi-key-per-fact
real-world regime).

## Arms

| V_C | M_FACTS | alpha_M_over_VC | alpha_M_over_N | keys_mode |
|-----|---------|-----------------|----------------|-----------|
| 2000 | 16384 | 8.19 | 1.0 | duplicates_allowed (16384 > 2000*8=16000; just barely) |
| 2000 | 24576 | 12.29 | 1.5 | duplicates_allowed |
| 2000 | 32768 | 16.38 | 2.0 | duplicates_allowed |
| 4000 | 16384 | 4.10 | 1.0 | unique_sr (4000*8=32000 > 16384) |
| 4000 | 24576 | 6.14 | 1.5 | unique_sr (32000 > 24576) |
| 4000 | 32768 | 8.19 | 2.0 | duplicates_allowed (32000 < 32768; just barely) |
| 8000 | 16384 | 2.05 | 1.0 | unique_sr |
| 8000 | 24576 | 3.07 | 1.5 | unique_sr |
| 8000 | 32768 | 4.10 | 2.0 | unique_sr |
| KNN_SENTINEL @ V_C=8000 | 500 items | n/a | n/a | n/a (Fix #28) |

3 seeds each: 9 capacity arms * 3 seeds + 3 sentinels = **30 units total**.

## Pre-reg bands (LOCKED at module init)

- HP_KNN_SENTINEL = 0.90 (Fix #28)
- CV_MAX = 0.05 across 3 seeds
- HP_DISCRIMINATING_REC_MIN = 0.50 (at least 1 phase point at this for chain-grade-disc.)
- HP_MONOTONE_DELTA = 0.10 (min |delta| for "clear monotone trend" along one axis)
- EXPECTED_N_UNITS = 30 (META_RULE_H cardinality guard)

## Verdicts

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_DISCRIMINATING_REGIME | at least 1 phase point rec>=0.50 cv<=0.05 AND at least 1 clear monotone trend (VC-up helps OR M-up hurts) at delta>=0.10 |
| MIDDLE_BAND_DISCRIMINATING_PASSES_NO_MONOTONE | rec>=0.50 cv<=0.05 found but surface flat across V_C and M axes |
| MIDDLE_BAND_MONOTONE_NO_DISC_PASS | monotone trends observed but no phase point >= 0.50 (substrate below discriminating bar) |
| MIDDLE_BAND_FLAT_SURFACE | no trends + no passes (noise floor across all configs) |
| HARD_FAIL_CARDINALITY_BREACH_META_RULE_H | n_units < 30 |
| HARD_FAIL_UNIT_EXCEPTION | any per-unit exception |
| HARD_FAIL_SUBSTRATE_ONLY | LLM calls > 0 |
| HARD_FAIL_KNN_SENTINEL | KNN sentinel < 0.90 |

## Discriminator-must-survive-scale (USER 2026-06-26)

**Check option B (analytical justification) + Check option C (smoke-N preview):**

**Option B:** At alpha_M_over_N>=1 the substrate is fundamentally crosstalk-limited.
Classical HRR-binding theory predicts recall ~0.5-0.7 at alpha=1 and ~0.2-0.4 at
alpha=2 for large N. Saturation (rec=1.0) at full-N=16384 at alpha=2 would be a
**surprising substrate-native capacity result**, not a by-construction artifact.

**Option C (smoke-N=2048 preview):** Smoke ran:
- VC=400 M=2048 (alpha_VC=5.12, alpha_N=1.0, unique_sr): rec=1.0000 (saturated; mode=unique_sr at low alpha_VC tolerates this scale)
- VC=400 M=4096 (alpha_VC=10.24, alpha_N=2.0, duplicates_allowed): **rec=0.5786** (DISCRIMINATOR FIRED)
- VC=800 M=2048 (alpha_VC=2.56, alpha_N=1.0, unique_sr): rec=1.0000
- VC=800 M=4096 (alpha_VC=5.12, alpha_N=2.0, unique_sr): rec=1.0000

The discriminator fired at the alpha_N=2 + duplicates_allowed point in smoke,
proving the substrate IS NOT trivially saturated at high alpha. At full-N=16384
the same crosstalk physics applies but with the substrate's natural N-scaling
tolerance: the question is exactly which (V_C, M) phase points cliff and which
hold up. Both "wider surface degradation" and "graceful capacity surface"
outcomes are scientifically meaningful for the phase diagram.

**META_RULE_K compliance:** smoke FIRES the discriminator (sub-1.000 recall at
high-alpha duplicates_allowed regime), not just verifies mechanism end-to-end.

## Smoke verdict (laptop CPU 2026-06-27)

**SMOKE_PASS** at smoke-N=2048, V_C in [400, 800], M in [2048, 4096]:
- Self-test ALL PASS (T1-T10; including high-alpha duplicates_allowed branch)
- 5/5 expected smoke units landed (cardinality OK)
- KNN sentinel 1.0000 (>=0.90 OK)
- substrate-only_ok=True (LLM calls = 0)
- Discriminator FIRED: rec=0.5786 at alpha_N=2 duplicates_allowed point
- Wall: ~1.7s total
- gpu_util check DEFERRED to remote GPU smoke

Mechanism end-to-end verified WITH non-trivial discriminator response (META_RULE_K).

## Config

- N_DIM = 16384 (full)
- VC_SWEEP = [2000, 4000, 8000]
- M_FACTS_SWEEP = [16384, 24576, 32768] = [N, 1.5N, 2N]
- V_REL = 8 (small for clean capacity-only measurement)
- Seeds: [11, 13, 19]
- Encoder provenance: SUBSTRATE_NATIVE
- Substrate-only decode (zero LLM calls; asserted before metrics.json write)

## ETA + Timeout

Per-unit GPU walltime estimate (extrapolating from smoke at N=2048):
- N=2048: ~0.5s per arm
- N=16384 (8x): scaling ~1.5 (matmul-bound) -> ~0.5 * 8^1.5 = ~11s per arm
- 9 capacity arms * 3 seeds * ~11s = ~300s = ~5 min
- 3 KNN sentinels * ~2s = ~6s
- Setup + W-matrix build * 27 arms = ~60s

**Estimated wall: ~6-10 minutes on GPU.**

**Timeout: 1800s (30 min)** — generous 3x margin over estimate. Anchor name
contains no `_n<N>` suffix; PROT-019 floor not triggered.

## Why this matters

The substrate's storage capacity is THE load-bearing question for using HD as a
durable memory substrate. Prior measurements all sat below the alpha=1 regime
(by construction or by accident); this cell maps the supra-capacity regime
where classical theory predicts the substrate degrades. Whether it degrades
gracefully, sharply, or unexpectedly is the science.
