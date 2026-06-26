# Prereg: substrate_anisotropy_polarimetric_multi_probe_retrieval_v1

**Date:** 2026-06-25
**Author:** exp_dev (USER-directed; main-thread authoring per Fix #27)
**Cell:** experiments/exp_substrate_anisotropy_polarimetric_multi_probe_retrieval_v1.py
**Anchor:** substrate_anisotropy_polarimetric_multi_probe_retrieval_v1
**Routing:** remote_cpu_queue (pure numpy; small matrices throughout; USER explicit "remote CPU idle; use it")
**Driver:** USER 2026-06-25 cross-domain insight: brain assumes 50B parallel granule cells; we have one GPU. Materials scientists / optics use multiple SMALL probe inputs that interact differently with cone-aligned items, then INFER structure from the response pattern (X-ray diffraction, polarimetry, Lorentz electron microscopy, Fourier ptychography). This is hardware-friendly because probes + responses are SMALL.

## Why this cell exists (the cross-domain reframe)

Three GPU-expansion cells (v1 + v2_batched + v3) hit OOM at the brain-scale (4096x) regime. The CPU-path v2 sweep is running but the expansion approach inherits the same fundamental cost: build a d_p-sized representation per item.

USER's reframe: instead of EXPANDING into a 50B-dim space, send K=10 different SMALL "probe" vectors per retrieval. Each probe interacts differently with cone-aligned items via a structured projection. Combine the K probe-response patterns to uniquely identify each item.

This is mathematically equivalent (per query) to a low-rank decomposition of the would-be expansion, but pays cost K*d*M rather than d_p*M. At K=10, d=768, M=10k: 76M ops per arm vs 31B ops at d_p=3.15M. Three orders of magnitude cheaper. Hardware-friendly even on laptop.

## Mechanism (substrate-native reformulation)

For each candidate key item K_i:
- Apply K=10 probe vectors p_1..p_K to K_i: per-probe scalar response r_ki = <p_k, K_i>
- Stack into response vector R_i = (r_1i, ..., r_Ki) in R^K
- At retrieval, do the same to the cue: Q = (q_1, ..., q_K)
- Predicted match: argmax_i <Q, R_i>  (or weighted, or via L1-min reconstruction)

The K probes form a small "interrogation basis". Each probe sees the cone differently. Items that look identical along the cone axis still differ along OTHER probe axes, so the K-dim response signature disambiguates them.

## Strategic significance (USER reframe)

If polarimetric works at substrate scale:
- Anisotropy "solved" via probe-and-response model (NOT expansion-based)
- Hardware-friendly (small matrices throughout; K=10 probes vs d_p=3.15M expansion)
- Brain-aligned to cortical attention (multi-head probes)
- Computationally cheap

If polarimetric HARD_FAILs:
- Probe-based methods don't work for substrate; need to either accept partition routing bypass OR find totally different mechanism
- Still informative: closes off the cross-domain hypothesis

Either outcome is decision-grade.

## Arms (8 — FAIR-TEST design; USER's "include baselines that catch alternative explanations")

The fair-test design is load-bearing. Three alternative explanations could yield false-positive "polarimetric works":
1. "Multi-probe is just averaging noise" -- controlled by ARM_SINGLE_PROBE_AVERAGED_K10
2. "Any K random probes work; structure doesn't matter" -- controlled by ARM_AB_CONTROL_RANDOM_K_PROBES and ARM_POLARIMETRIC_K10_RANDOM_UNIT
3. "Polarimetric is just rebranded expansion at small d_p" -- controlled by ARM_FLY_LSH_5x cross-cell sanity rail

The 8 arms:

1. **ARM_RAW** -- no-rescue baseline; single dot-product on anisotropic keys; verifies anisotropy collapse (target ~0.02 to match prior anisotropy cells at adversarial regime)
2. **ARM_SINGLE_PROBE_DENSE** -- standard single-probe cleanup (substrate's current default at adversarial regime); target ~0.18-0.24 per v2_batched M=10k partial slice
3. **ARM_SINGLE_PROBE_AVERAGED_K10** -- average 10 queries from same probe distribution (e.g., 10 noise-perturbed cues averaged); controls for "polarimetric just averages noise" -- if this matches polarimetric, the lift is just averaging
4. **ARM_AB_CONTROL_RANDOM_K_PROBES** -- K=10 random Gaussian probes (no structure); controls for "any K probes work" alternative explanation
5. **ARM_POLARIMETRIC_K10_RANDOM_UNIT** -- K=10 random unit vector probes; tests if randomness alone helps when sampled uniformly on sphere
6. **ARM_POLARIMETRIC_K10_PCA_AXES** -- K=10 probes aligned with top-K PCA axes of stored items (interrogates actual cone structure; brain-aligned to cortical attention learning the data subspace)
7. **ARM_POLARIMETRIC_K10_LEARNED** -- K=10 probes trained via contrastive loss to maximize per-probe discrimination (strongest version; analogous to learned attention heads)
8. **ARM_FLY_LSH_5x** -- reproduces v2 small-expansion baseline at this regime (cross-cell sanity rail; expansion-based reference point)

## Pre-reg bands (PROSPECTIVE, LOCKED at module init via assert)

**HARD_PASS_CHAIN_GRADE_POLARIMETRIC_RESCUES** (the headline outcome):
- ARM_POLARIMETRIC_K10_LEARNED >= 0.85 at M=10k AND
- beats ARM_AB_CONTROL_RANDOM_K_PROBES by >= 0.10 AND
- beats ARM_SINGLE_PROBE_AVERAGED_K10 by >= 0.10 AND
- beats ARM_FLY_LSH_5x by >= 0.10 AND
- monotonic: K=1 (ARM_SINGLE_PROBE_DENSE) < K=10 (multi-probe contribution real) AND
- cv <= 0.05 across 3 seeds

**HARD_PASS_PCA_AXIS_PROBES_RESCUE** (brain-aligned version):
- ARM_POLARIMETRIC_K10_PCA_AXES >= 0.85 AND beats ALL controls (AB_CONTROL, AVERAGED, FLY_LSH) by >= 0.10
- Same cv + monotonic gates

**HARD_PASS_PARTIAL_RANDOM_K_HELPS** (informative even if not chain-grade-attributable to learned/PCA):
- ARM_AB_CONTROL_RANDOM_K_PROBES >= 0.85 (any K probes help; not polarimetric-specific; informative for cross-domain framing)

**HARD_FAIL_POLARIMETRIC_DOESNT_HELP**:
- ARM_POLARIMETRIC_K10_LEARNED <= 0.30 at M=10k (mechanism doesn't transport; cross-domain reframe falsified at substrate scale)

**HARD_FAIL_AVERAGED_K10_DOMINATES** (Q-discipline failsafe):
- ARM_SINGLE_PROBE_AVERAGED_K10 >= ARM_POLARIMETRIC_K10_LEARNED at M=10k (polarimetric is just averaging; mechanism story collapses; honest demote)

**MIDDLE_BAND**: any partial signal not hitting HP and not falling into HF -- numbers measured but discriminator inconclusive

**Module-init assert chain** (CONFIG_VERSION echoes in metrics):
```
assert 0.0 < BAND_HF_RESCUE < BAND_HP_CHAIN_GRADE < BAND_Q_SATURATION < 1.0
assert 0.0 < BAND_HP_BEAT_PEER == 0.10 < 1.0
assert 0 < K_PROBES == 10
```

## Q-discipline guards (load-bearing for the fair test)

- Any arm at 0.995+ flagged saturation (corpus-too-easy artifact)
- **Q-discipline for SINGLE_PROBE_AVERAGED_K10**: if this matches POLARIMETRIC, the "polarimetric structure" claim is reduced to "averaging helps" -- HONEST DEMOTE to MM tier with explicit attribution note
- **Q-discipline for AB_CONTROL_RANDOM_K_PROBES**: if random K probes match polarimetric, the "structure matters" claim is reduced to "K probes help" -- HONEST DEMOTE
- All by-construction-saturation tiering deferred to Skunkworks per Fix #28

## Config

- N_DIM = PROJ_DIM = 768 (substrate base; matches Pythia residual dim)
- d_input = 768 (Pythia residual dim)
- M in {2k, 10k, 50k} (CPU-feasible; mirrors recent anisotropy cells)
- K_PROBES = 10 (fixed; USER directive)
- 3 seeds [11, 13, 19] (apples-to-apples with anisotropy cells)
- Adversarial-similarity keys (consecutive-token stride-1 windows; matches v2_batched + v3 expansion sweep)
- Substrate-only at inference; numpy; ASCII; per-arm metrics
- ENCODER = EleutherAI/pythia-2.8b (full); pythia-160m (smoke)

## CPU runtime budget

Per-seed encoder hoist (pythia-2.8b on CPU): ~5-8 min
Per-seed per-arm at M=10k:
- ARM_RAW: ~1s
- ARM_SINGLE_PROBE_DENSE: ~1s
- ARM_SINGLE_PROBE_AVERAGED_K10: ~10s (10x cue noise samples)
- ARM_AB_CONTROL_RANDOM_K_PROBES: ~5s (K=10 random probes; small matrices)
- ARM_POLARIMETRIC_K10_RANDOM_UNIT: ~5s
- ARM_POLARIMETRIC_K10_PCA_AXES: ~30s (PCA on stored keys)
- ARM_POLARIMETRIC_K10_LEARNED: ~3-5 min (contrastive train; small probe set)
- ARM_FLY_LSH_5x: ~30s

Per-seed wall: ~10-15 min. Three seeds plus three M-points: ~2-3h.
Per-experiment timeout: 10800s (3h) with per-seed checkpoint resume.

## META disciplines

- **META_M6**: ARM_RAW measured in-cell at adversarial regime (NOT copied from prior cells)
- **META_M7**: smoke matches full along ALL capacity-sensitive dims (PROJ_DIM, K_PROBES, K_FANIN, adversarial-window structure); only M and SEEDS reduce
- **META_PROSPECTIVE_BANDS_FRESH_SEEDS**: bands locked at module init via assert chain
- **Q-discipline**: any arm >= 0.995 flagged
- **ASCII-only**; no unicode in scripts
- **PROT-021** satisfied (per-seed checkpoint resume; run_cfg passed to aggregate_partials)
- **Fix #28**: per-arm metrics surfaced; verdict_msg has all 8 arm numbers (no cross-arm narrative without metrics.json check)

## Routing

- **remote_cpu_queue** (marsh@home; Windows; reads origin/main; pure-CPU runner)
- **NO PROT-020 gate** (no torch imports for inference; encoder is setup-time only)
- **PROT-021** satisfied
- **Timeout: 10800s** (3h budget)

## Self-test guarantees (PASS before queue_add)

- (a) per-arm builders run on tiny synthetic (M=50, d=64) without errors
- (b) K_PROBES dimensions correct for each arm (random / unit / PCA / learned)
- (c) PCA arm: top-K PCA axes computed correctly (eigvals descending)
- (d) AB_CONTROL: K random Gaussian probes with no structure (sanity)
- (e) Module-init band assertions hold
- (f) compute_verdict synthetic paths exercised: HP_LEARNED, HP_PCA, HF_DOESNT_HELP, HF_AVERAGED_DOMINATES, MB
- (g) **Ground-truth recall**: end-to-end mini polarimetric (PCA arm) at M=50, d=64, K=10 achieves >= 0.80 recall on noise-perturbed identity reconstruction
- (h) Fairness check: AB_CONTROL on isotropic toy data does not exceed POLARIMETRIC_LEARNED by > 0.05 (controls are honest, not crippled)

## Reference cells (cross-cell sanity rails)

- `exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched` (adversarial-keys construction)
- `exp_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path` (CPU-path numpy patterns; FLY_LSH 5x as sanity arm 8)
- `exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full` (calibrated meter)
- `exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1` (encoder + contrastive train pipeline; reused for ARM_POLARIMETRIC_K10_LEARNED probe training)
- `dense_KV_whitening_revival_v1_gpu` (HARD_FAIL; whitening doesn't add rank)
- `research_anisotropy_intuitive_synthesis_with_visual_2026-06-25` (full context)

## Post-landing cross-cell sanity rails

- ARM_FLY_LSH_5x at M=10k should match v2_batched M=10k slice fly numbers (~0.19) within 0.05
- ARM_RAW at adversarial-keys M=10k: expect very low (~0.02; matches v2_batched M=10k slice raw=0.021)
- ARM_SINGLE_PROBE_DENSE at M=10k should match v2_batched M=10k partial single-probe numbers
- If POLARIMETRIC_LEARNED matches POLARIMETRIC_RANDOM_UNIT within 0.10 -> structure attribution falsified -> demote
- If POLARIMETRIC_PCA_AXES beats POLARIMETRIC_LEARNED -> data-structure attribution stronger than learned-attention attribution -> note in atomization

-- exp_dev, 2026-06-25 (cell author; spawn-and-die teammate; main-thread authoring per Fix #27 due to spawn cap)
