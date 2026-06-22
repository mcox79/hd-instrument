# Dispatch hand-off: c_composition_storage_density_v1

**Date:** 2026-06-22
**From:** exp_dev (autonomous spawn under Director routing)
**For:** orchestrator (push + dispatch)
**Cell commit:** `085cab1e` (`main`, local; needs push to origin)
**Cell:** `experiments/exp_c_composition_storage_density_v1.py`
**Pre-reg:** `notes/c_composition_storage_density_v1_pre_reg_2026-06-22.md`

## Smoke STATUS: GREEN

- self-test PASS (ZCA-decorr OK, kWTA OK, baseline Hebbian set-recall=1.00)
- smoke landed in 356s on local CPU (M=[500, 2000], 1 seed)
- run_mode=`smoke` honored (Fix #5 gate passes)
- zero_llm_calls_at_inference=`True` (substrate-only preserved)
- All 5 arms saturate at setrecall=1.00 at smoke scale (BY-CONSTRUCTION SATURATION
  per pre-reg; the discriminator regime lives at large M)
- metrics.json schema clean: anchor_name, verdict, verdict_msg, summary, run_mode,
  n_seeds, config_version, per_seed, elapsed_s, zero_llm_calls_at_inference, n_llm_calls

## Per-arm wall measurement (Fix #17, the LOAD-BEARING measurement)

| Arm | M=500 wall (s) | M=2000 wall (s) |
|---|---|---|
| baseline | 0.3 | 0.5 |
| modular | 10.3 | 5.0 |
| whitening | 99.6 | 84.9 |
| kwta | 0.4 | 0.4 |
| combined | 103.4 | 50.2 |

Modular + whitening + combined are V_proj-build + ZCA-SVD dominated (constant cost),
NOT M-scaling. Baseline + kwta scale linearly with M.

## Full-run wall extrapolation (3 seeds x M_GRID=[1k, 5k, 10k, 25k] x 5 arms)

- baseline arm: ~42s/seed
- modular arm: ~200s/seed
- whitening arm: ~370s/seed
- kwta arm: ~42s/seed
- combined arm: ~425s/seed

Per-seed total: ~1080s ~ 18min
3 seeds total: ~54min wall

**Wall budget:** 10800s (3 hr) — 3x safety margin over the ~55min ETA, per
autonomous-arc TODO #8 (encoding-dominant cells get 2-3x default).

## Dispatch ask

Please push commit `085cab1e` to origin/main, then dispatch:

```
bash tools/orchestrator/queue_add.sh remote_cpu_queue \
  c_composition_storage_density_v1 \
  experiments/exp_c_composition_storage_density_v1.py \
  notes/c_composition_storage_density_v1_pre_reg_2026-06-22.md \
  10800
```

After dispatch please confirm the entry landed in remote queue.json (the queue_add.sh
post-ship verification step does this automatically — its OK line is sufficient).

## Pre-reg HARD bands (verbatim from pre-reg note)

- **HARD_PASS** (chain-grade): compound lift L = M_fail(combined) / M_fail(baseline) >= 5.0
  AND substrate-only-decode preserved (n_llm=0) AND cv <= 0.10 across seeds
  AND Arm 1 reproduces n8 chain-grade pattern at M=10k (setrecall@10k >= 0.90).
- **HARD_FAIL:** L <= 1.5 (compound mechanisms don't compose).
- **MIDDLE_BAND:** 1.5 < L < 5.0 (partial; characterize load-bearing pair).

## Strategic value

USER 2026-06-22 storage-density question gets chain-grade answer. P=0.40 (novel
4-mechanism synthesis; deflated because orthogonality is theoretically uncertain).
Information-positive REGARDLESS of verdict:
- HARD_PASS: substrate path to LLM-class storage density chain-grade-substantiated; v2 pushes M=100k+
- HARD_FAIL: rules out simple-compounding; routes 2x revival to Research with observed conflict
- MIDDLE_BAND: characterizes mechanism-subset that compounds; routes specific pair drills

## Asks (post-landing)

- **skunkworks:** SCHEMA-VET this pre-reg + landed-VET on data arrival; ratify or
  adjust inline disposition; A5-gated Store write if chain-grade
- **research (Director):** route 2x revival on negative; cross-check pre-reg direction
