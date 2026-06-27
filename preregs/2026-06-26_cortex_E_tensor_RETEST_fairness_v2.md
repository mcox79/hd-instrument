# Pre-reg: cortex_E_tensor_RETEST_fairness_v2 (Wave 1.6 ANCHOR 1)

**Date:** 2026-06-26
**Author:** exp_dev (spawn)
**Trigger:** USER 2026-06-26 fairness audit on cortex_E_tensor_HARDER_REGIME_v1 HARD_FAIL.
**Cell:** `experiments/exp_cortex_E_tensor_RETEST_fairness_v2.py`
**Queue:** local_cpu_queue
**Hand-off:** `notes/exp_dev_handoff_research_cortex_wave_1_6_E_tensor_fairness_fix_plus_4x_alternatives_2026-06-26.md` ANCHOR 1

## Hypothesis

Two USER-identified fairness fixes (Fix A: explicit RETRIEVED/UNRETRIEVED tagging during consolidation; Fix B: constant additive bump + linear decay decouples E from cosine magnitude) make the E-tensor mechanism testable on RETRIEVED-old recall (the load-bearing quantity that v1 conflated with arbitrary-old recall).

## Arms (4 mandatory)

- `ARM_BASELINE_NO_DOWNSCALE` -- rail; no pruning.
- `ARM_E_GATED_RETEST` -- Fix A + Fix B applied; prune atoms with `E < E_THRESHOLD`.
- `ARM_RANDOM_GATED` -- control; match prune-count to E_GATED.
- `ARM_BASELINE_MAG_GATED` -- NEW control; prune `n_target` atoms with smallest `||W @ key_i||` (magnitude-quantile).

## Config

```
N = 1024
M_OLD = 600
M_RECENT = 400        # alpha = 0.977
USE_FRAC = 0.30       # N_USE = 180 atoms get retrievals
N_RETRIEVAL_PASSES = 1000
DOWNSCALE_SCALE = 0.20
DOWNSCALE_FRAC = 0.30
E_THRESHOLD = 0.5     # bump=1.0 + decay=0.001/cycle dynamics
SEEDS = [7, 17, 23]
N_QUERIES = 200       # per subset (RETRIEVED, UNRETRIEVED, RECENT)
```

Smoke: `N=256, M_OLD=150, M_RECENT=100, J=500, SEEDS=[7], N_QUERIES=50`.

## Load-bearing PASS bands (USER-identified; sacrosanct)

`HARD_PASS` requires ALL of:
1. `E_GATED.rec_old_RETRIEVED >= 0.90` (Fix A: E preserves what was retrieved)
2. `|E_GATED.rec_old_UNRETRIEVED - RANDOM.rec_old_UNRETRIEVED| <= 0.10` (Fix A: E doesn't pretend to know about UNRETRIEVED)
3. `E_GATED.rec_old_RETRIEVED - MAG_GATED.rec_old_RETRIEVED >= 0.05` (E beats magnitude on the load-bearing quantity)
4. `cor(E, |W|) < 0.30` (Fix B: E independent of magnitude)
5. `cv(rec_old_RETRIEVED across seeds) <= 0.10` (seed-stable)

`MIDDLE_BAND`: Fix A passes (`rec_old_RETRIEVED >= 0.90`) AND Fix B passes (`cor < 0.30`) but other gates fail.

`HARD_FAIL` triggers (any of):
- Fix B failed: `cor(E, |W|) >= 0.5` -> EWMA-as-importance design fundamentally wrong-shaped; STOP + route back to research.
- Fix A failed: `rec_old_RETRIEVED < 0.90` -> E does not preserve atoms it should.
- `MAG_GATED.rec_old_RETRIEVED - E_GATED.rec_old_RETRIEVED >= 0.05` -> magnitude is the right signal; retire E mechanism.

## Substrate-only-decode gate

- `n_llm_calls == 0` asserted from per-seed counter before metrics write.

## Smoke gate (load-bearing per USER deliverables)

If smoke `ARM_E_GATED_RETEST.cor(E, |W|) > 0.5`: STOP smoke. Do NOT dispatch full. Route diagnosis back to research.

## Cost estimate

- Smoke wall: ~30s-2min (N=256, J=500, 4 arms, 1 seed).
- Full wall: ~3-5 hr (N=1024, J=1000, 4 arms, 3 seeds). Per-seed checkpoint enabled via `_seed_checkpoint`.

## Atomization on land

- HARD_PASS -> route to Skunkworks for landed-VET; MEASURED_MECHANISM default per Fix #28.
- MIDDLE_BAND -> route to Research for 2x-revival drill (per-negative discipline).
- HARD_FAIL with Fix B failure -> route to Research with "EWMA-as-importance is wrong-shaped" diagnosis.
