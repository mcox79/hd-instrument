# c_composition v1 HARD_FAIL-at-smoke = discriminator-invalid; v2 queued via hdi_orchestrator → GPU

**Date:** 2026-06-22
**Cell:** `experiments/exp_c_composition_storage_density_v1.py` (committed; NOT dispatched full)
**Smoke metrics:** `data/exp_c_composition_storage_density_v1/metrics.json` (HARD_FAIL; run_mode=smoke; n_seeds=1; elapsed 355.7s)

## v1 result

- L = combined/baseline = **1.00** (HARD bar ≥ 1.5×)
- M_fail per arm: **2001 for all 5 arms** (= no arm failed at the test cap of M=2000)
- cv = 0.000
- HARD_FAIL band hit because L < 1.5

## Why this is discriminator-invalid (not real mechanism failure)

Per Fix #16 discriminator-regime check: M_fail=2001 ACROSS ALL ARMS means **baseline single-mechanism handled M=2000 just fine**. There's no failure for compound mechanisms to lift over. The compound-effect signal is by-construction-zero in this regime — same architectural pattern as g1's by-construction-saturation (novelty at metric-cap) and m1's INCONCLUSIVE-sqrt(K) (K=1 anchor doesn't fail in tested N range).

The smoke needs to push M MUCH higher (10k, 50k, 100k) until baseline starts failing. Then compound arms can demonstrate the lift OR fail to compound — either result is information-positive.

## What this does NOT contradict

Existing chain-grade composition evidence stands:
- `EXP_substrate_capacity_composition_b2xb4_v1_n2048` HARD_PASS: 240× multiplicative composition (sparse × K)
- `EXP_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` HARD_PASS: 600K patterns total (sparse × K=10 × D=5 multiplicative), independence_recall=1.00, LOWER BOUND because sparse hit grid ceiling

The storage-density question is answered at chain-grade by these atoms. v1 attempted to RE-VERIFY at modern primitives (modular + whitening + sparse) but the smoke regime didn't reach the discriminating M. v2 fixes that.

## v2 design (queued via hdi_orchestrator → GPU per Fix #22+#23)

- Same architecture (5 arms: baseline / +modular K=8 / +whitening / +kwta / +combined-all)
- M_grid = [1k, 10k, 50k, 100k, 250k, 500k] — sweeps through Hebbian capacity (substrate's measured single-key ~327; multi-value-adjusted ~10k)
- HARD_PASS chain-grade: at M where BASELINE fails (setrecall < 0.50), COMBINED achieves setrecall ≥ 0.80 AND ratio ≥ 3.0×
- Routed via hdi_orchestrator (cell-author + smoke + Fix #17 on remote_cpu via SSH; full dispatch to overnight_queue GPU)
- First cell explicitly under the new Fix #22+#23 routing discipline

## Disposition

v1 = HONEST_NEGATIVE-at-smoke (discriminator-invalid regime). v1 cell stays on disk as cert-trail; v2 supersedes.

## Composes with

- by-construction-saturation tiering META (the underlying rule)
- headroom-to-fail discriminator META (g1b sibling; same lesson for capacity sweeps)
- existing chain-grade composition atoms at N=2048 (the storage-density question is already answered at chain-grade for the sparse × K × D mechanism family; v2 verifies for modern modular + whitening + kwta)

— Research (Director); v1 dispositioned; v2 queued; cert-trail durable artifact
