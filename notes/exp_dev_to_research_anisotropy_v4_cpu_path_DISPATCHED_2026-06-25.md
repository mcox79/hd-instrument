# Anisotropy expansion sweep v4 CPU-PATH DISPATCHED to remote_cpu_queue

**Date:** 2026-06-25
**From:** exp_dev
**To:** research (primary); cc: skunkworks, orchestrator
**Anchor:** substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path
**Queue:** remote_cpu_queue (marsh@home; pure-numpy CPU runner; no GPU memory cap)
**Timeout:** 10800s (3h budget)
**Commit:** 1520bd60 ("exp_dev: anisotropy expansion sweep v2 CPU-PATH (route around 3x GPU OOM streak)")

## Status

- Cell + prereg authored
- Self-test PASSED LOCAL (.venv): sparse-fanin builder + sparse-matvec bit-equivalent vs dense (np.allclose atol=1e-5) + tag-overlap argmax + bands + memory budget assert + 4 verdict paths (HP_BRAIN/HP_CTRL/HF_CTRL/HF_NOLIFT) + ground-truth mini fly-LSH recall = 1.000 at M=50/d=64/expansion=8
- Smoke PASSED LOCAL (CPU; pythia-160m; M=400; expansions [8, 64]; encoder elapsed 429s = ~7 min; total ~10 min wall):
  - ARM_RAW = 0.035 (matches v2_batched M=10k adversarial raw=0.021 ballpark; anisotropy + adversarial = near-chance)
  - ARM_FLY_LSH_8x = 0.623 (baseline; sparse-fan-in lifts 18x over raw)
  - ARM_FLY_LSH_64x = 0.720 (12x more expansion -> +10pp lift; MONOTONIC 8x->64x ok=True)
  - ARM_AB_CONTROL_64x = 0.720 (TIES with fly at smoke regime; preview signal AB_CONTROL may match fly at full)
  - Verdict: MIDDLE_BAND_INCONCLUSIVE (correct for smoke; full needs all 4 expansions for verdict)
- Self-test PASSED REMOTE: 3.2s on remote .venv (verified during gate ship)
- Remote queue VERIFIED: present in `data/remote_cpu_queue/queue.json` on marsh@home (1 pending)

## Why this cell exists (USER 2026-06-25)

Three GPU OOMs in a row blocked the brain-scale expansion test:
- v1 GPU expansion sweep (anchor `substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1`): OOM at 64x / 512x / 4096x / AB_CONTROL_4096x. Only FLY_5x landed (=0.999 saturation; no discriminator).
- v2_batched M=100k adversarial (anchor `substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched`): OOM during batched matmul on 8GB GPU.
- v3 expansion sweep (same lineage): OOM.

USER: "remote cpu and gpu still idle" -- use the CPU capacity. CPU has no per-process memory cap (vs 8GB GPU); pure-numpy with sparse representations stays under 12GB RAM at 4096x expansion.

## What this cell answers

This is the FINAL anisotropy discrimination test. Five outcomes, all decision-grade:

| Outcome | Verdict | Strategic significance |
|---|---|---|
| FLY_4096x >= 0.85 AND beats AB_CONTROL by >= 0.10 AND monotonic | HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES | cerebellar mechanism transports at brain-scale; USER intuition validated; Tier 4 path opens |
| BOTH FLY_4096x AND AB_CONTROL_4096x >= 0.85 AND both beat raw by >= 0.50 | HARD_PASS_CONTROL_ALSO_HELPS | expansion IS the mechanism (NOT LSH-specific); still a real primitive |
| AB_CONTROL > FLY by >= 0.05 at 4096x | HARD_FAIL_CONTROL_DOMINATES | fly-LSH NOT the mechanism; 3rd cell-confirmation; close anisotropy as bypass-only |
| FLY_4096x <= FLY_8x + 0.02 | HARD_FAIL_EXPANSION_DOESNT_HELP | expansion ratio not the limit; cerebellar mechanism doesn't transport |
| monotonic but FLY_4096x < 0.85 | MIDDLE_BAND_PARTIAL_LIFT | mechanism real but insufficient at this corpus regime |

All five outcomes lock substrate-product positioning. No outcome is "uninformative".

## Critical changes from v1 (load-bearing)

1. **No torch / no torch.cuda anywhere** -- pure numpy compute path; no GPU memory cap. CPU runner has no PROT-020 torch gate.
2. **M reduced 10k -> 2k** for CPU feasibility (reduce DATA not MECHANISM).
3. **Expansion grid changed [5, 64, 512, 4096] -> [8, 64, 512, 4096]** for cleaner octave-step monotonicity.
4. **Sparse representation throughout**: COO arrays for S (rows+cols+vals); topk-indices for tags; inverted-index hash for tag-overlap retrieval (avoids any dense (M, d_p) materialization).
5. **Per-arm CPU RAM budget asserted at module init**: max < MEM_BUDGET_GB = 12 (laptop CPU has ~16GB; remote CPU has more). Module FAIL-FASTS at import time if config drifts.
6. **Same adversarial-similarity keys** as v2_batched (consecutive-token stride-1 windows of natural prose; adjacent keys share 15/16 tokens by construction).
7. **AB_CONTROL_4096x retained** -- the LSH-vs-generic discriminator. Chunked Gaussian + running-topk merge (CPU port via numpy argpartition).

## Cross-cell sanity rails (post-landing)

- ARM_FLY_LSH_8x at M=2k adversarial vs v2 5x M=10k easy keys: similar mechanism, similar regime; expect roughly comparable top-1 with adversarial-key gap being informative.
- ARM_RAW at M=2k adversarial should match v2_batched M=10k slice raw=0.021 ballpark (both are anisotropic + adversarial = near-chance retrieval).
- AB_CONTROL_4096x vs ARM_FLY_LSH_4096x: the discriminator. Margin or sign determines outcome triage.

## Compute estimate (CPU; remote runner)

- Per-seed encoder hoist (pythia-2.8b CPU, mean-pooled last hidden state across ~3500 docs): ~5-8 min
- Per-seed ARM_RAW: ~1s
- Per-seed ARM_FLY_LSH_8x: ~30s (dp=6144; sparse matvec + inverted-index tag-overlap fast at small dp)
- Per-seed ARM_FLY_LSH_64x: ~3-5 min
- Per-seed ARM_FLY_LSH_512x: ~15-25 min
- Per-seed ARM_FLY_LSH_4096x: ~60-90 min (dominated by 2-pass chunked sparse matvec over dp=3.15M)
- Per-seed ARM_AB_CONTROL_4096x: ~30-50 min (chunked Gaussian + running-topk merge)
- Per-seed wall: ~2-3h
- 3 seeds with per-seed checkpoint resume (PROT-021): each seed atomically saved
- Timeout 10800s (3h) per shipped slice with checkpoint-resume safety net for retries

## Pause + rule compliance

- Pause flag verified NOT set at dispatch time
- Path-scoped commit (cell + prereg + this note only; NEVER `git add -A`)
- ASCII-only purpose string in queue_add.sh invocation
- No torch (pure numpy); CPU runner has no PROT-020 torch routing gate
- PROT-021 satisfied (imports `_seed_checkpoint`; run_cfg passed to `aggregate_partials`)
- PROT-019 N/A (anchor has no `_n<N>` suffix; expansion_factor is on d_p not N)
- Spawn-budget check: 0 in flight (no exp_dev spawns active); USER explicit-directed
- Non-conflicting with local_cpu_queue cells (different runner)
- Non-conflicting with GPU (overnight_queue) cells (different machine + queue)

## Q-discipline guards

- Any arm >= 0.995 fires [Q-DISCIPLINE: suspect saturation] note. Documentation only; not auto-demotion.
- At M=2k adversarial-similarity, sustained >= 0.995 would suggest corpus still too easy at this scale (need M=10k+ on CPU or harder construction).

## Referent pointers (absolute paths)

- Cell: `D:/AI/hd-instrument/experiments/exp_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path.py`
- Prereg: `D:/AI/hd-instrument/preregs/2026-06-25_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path.md`
- Expected metrics landing: `D:/AI/hd-instrument/data/exp_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path/metrics.json`
- Remote queue: `C:/dev/hd-instrument/data/remote_cpu_queue/queue.json` (cell verified present)
- v1 GPU OOM evidence: `D:/AI/hd-instrument/data/exp_substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1/metrics.json` (FLY_5x=0.999; 64x/512x/4096x/AB_CONTROL_4096x all OOM)
- v2 4arm chain-grade-candidate at 5x: `D:/AI/hd-instrument/data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` (Skunkworks ruled MM by-construction-saturation)
- Anisotropy synthesis: `D:/AI/hd-instrument/notes/research_anisotropy_intuitive_synthesis_with_visual_2026-06-25.md`

-- exp_dev, 2026-06-25 (cell author; spawn-and-die teammate)
