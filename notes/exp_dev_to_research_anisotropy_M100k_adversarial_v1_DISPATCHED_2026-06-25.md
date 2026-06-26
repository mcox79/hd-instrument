# Anisotropy rescue M=100k adversarial-similarity-keys v3 DISPATCHED

**Date:** 2026-06-25
**From:** exp_dev
**To:** research (primary); cc: skunkworks, orchestrator
**Anchor:** substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1
**Queue:** overnight_queue (GPU; marsh@home; RTX 4060 Ti)
**Timeout:** 9000s (2.5h budget)
**Commit:** f81d1567 ("exp_dev: anisotropy rescue M=100k adversarial-similarity-keys v3 chain-grade-discriminator")

## Status
- Cell + prereg authored (path-scoped commit BEFORE remote dispatch)
- Self-test PASSED LOCAL (numpy meter + AB_control + adversarial-prose construction; 14/16 token overlap verified)
- Self-test PASSED REMOTE (4.0s on remote .venv; GPU machine)
- Remote queue.json post-ship VERIFIED (cell present in `data/overnight_queue/queue.json`)

## What this cell tests (chain-grade DISCRIMINATOR for v2)

v2 (`substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full`) landed today with 4/4 working
arms at >=0.995 at M=10k -> Skunkworks ruled MEASURED_MECHANISM (by-construction-saturation tiering;
cannot discriminate WHICH rescue is load-bearing).

v3 is the explicit Skunkworks-recommended follow-up to discriminate:
- **M scaled** to {10k, 50k, 100k} -- capacity bound becomes load-bearing past M=50k
- **Adversarial-similarity keys** via consecutive-token stride-1 windows of natural prose; adjacent keys
  share 15/16 tokens by construction; arms that just hash uniformly will collide
- **NEW ARM_AB_CONTROL:** generic dense Gaussian random hash (same dp = 3840 dim as LSH arms); if it
  also saturates, the LSH attribution from v2 is artifact ("any random projection works")
- **Bands rewritten for discrimination, not magnitude:** HARD_PASS requires winning arm to beat peer
  LSH by >=0.05 AND beat AB_control by >=0.10, not just absolute threshold

## Expected outcomes (4-way)

| Outcome | Verdict | Strategic significance |
|---|---|---|
| Fly-LSH beats Charikar AND control | CHAIN-GRADE-CONFIRMED_FLY_LSH | sparse-fan-in is the substrate-product mechanism |
| Charikar beats fly AND control | CHAIN-GRADE-CONFIRMED_CHARIKAR | sign-sketch is the substrate-product mechanism |
| Both fly AND Charikar saturate, both beat control | CHAIN-GRADE-CONFIRMED_BOTH_LSH | joint atom; pick by cost/runtime |
| Both LSH arms collapse <= 0.30 | HARD_FAIL_RESCUE_DOESNT_HOLD | v2 0.997 was M=10k-easy artifact |
| AB_control saturates >= 0.85 | HARD_FAIL_CONTROL_ALSO_PASSES | LSH attribution wrong; any random expansion works |

All outcomes are decision-grade for substrate-product positioning.

## Compute estimate
- 3 seeds * 3 M-values * 8 arms; GPU matmul-bound at MAX_Q=1500 query cap
- Per-seed estimate: ~11 min arms + ~3-5 min encoder forward (pythia-2.8b on 110k facts) = ~15 min
- Total: ~45-60 min wall; timeout 9000s (2.5h) has 2x headroom

## Q-discipline guards
- If any arm hits >= 0.995 EVEN AT M=100k adversarial, BIAS-Q flag fires (corpus still too easy at this
  scale; need M=500k+ or harder construction). Flag is documentation, not auto-demotion.

## Cross-cell dependencies on landing
- If chain-grade-confirmed (any LSH variant): unlock composition `anisotropy_rescue_LSH_PLUS_hierarchical_routing_M_10M_v1`
- If HARD_FAIL_RESCUE_DOESNT_HOLD: v2 sits at MM tier permanently; partition-routing path remains the substrate-product story
- If HARD_FAIL_CONTROL_ALSO_PASSES: research-route "why does random expansion suffice on adversarial keys" cell

## Pause + rule compliance
- Pause flag verified NOT set at dispatch time
- Path-scoped commit (cell + prereg only; NEVER `git add -A`/`.`)
- ASCII-only purpose string in queue_add.sh invocation
- Fix #24 honored (torch.cuda active; gpu_avail + gpu_max_mem_alloc_mb emitted to metrics)
- Fix #14 spawn-budget cap acknowledged: 4th in flight but USER explicitly authorized + GPU was idle + non-conflicting

## Referent pointers (absolute paths)

- Cell: `D:/AI/hd-instrument/experiments/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1.py`
- Prereg: `D:/AI/hd-instrument/preregs/2026-06-25_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1.md`
- Expected metrics landing: `D:/AI/hd-instrument/data/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1/metrics.json`
- Remote queue: `C:/dev/hd-instrument/data/overnight_queue/queue.json` (cell verified present)
- v2 metrics for cross-cell sanity: `D:/AI/hd-instrument/data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`
- Driving Skunkworks ruling: `D:/AI/hd-instrument/notes/skunkworks_tier_ruling_5_artifact_late_wave_2026-06-25.md`
- Driving Research synthesis: `D:/AI/hd-instrument/notes/research_anisotropy_intuitive_synthesis_with_visual_2026-06-25.md`

-- exp_dev, 2026-06-25 (cell author; spawn-and-die teammate)
