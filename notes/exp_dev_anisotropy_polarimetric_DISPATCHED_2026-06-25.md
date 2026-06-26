# exp_dev: substrate_anisotropy_polarimetric_multi_probe_retrieval_v1 DISPATCHED

**Date:** 2026-06-25
**Author:** exp_dev
**Anchor:** substrate_anisotropy_polarimetric_multi_probe_retrieval_v1
**Queue:** remote_cpu_queue (marsh@home; Windows; reads origin/main)
**Cell:** experiments/exp_substrate_anisotropy_polarimetric_multi_probe_retrieval_v1.py
**Prereg:** preregs/2026-06-25_substrate_anisotropy_polarimetric_multi_probe_retrieval_v1.md
**Commit:** f7609149
**Timeout:** 10800s (3h)

## Status

- DISPATCHED + REMOTE VERIFIED in remote_cpu_queue/queue.json
- Remote --self-test PASSED in 5.6s on remote .venv
- Queue depth 1 (was 0; idle pre-dispatch)

## What this cell tests (USER cross-domain reframe 2026-06-25)

Brain assumes 50B parallel granule cells; we have one GPU. Materials scientists /
optics use multiple SMALL probe inputs that interact differently with cone-aligned
items, then INFER structure from response pattern (X-ray diffraction, polarimetry,
Fourier ptychography). Hardware-friendly: probes + responses are SMALL.

Three GPU expansion cells (v1, v2_batched, v3) OOMed at brain-scale 4096x. This cell
sidesteps the expansion-cost trap with K=10 small probe vectors. Pays K*d*M cost
(76M ops at K=10, d=768, M=10k) vs d_p*M for expansion (31B ops at d_p=3.15M) -- three
orders of magnitude cheaper. Laptop-friendly even at M=50k.

## 8-arm FAIR-TEST design (USER explicit "include baselines that catch alternative explanations")

1. ARM_RAW                              -- single-probe collapse baseline (target ~0.02)
2. ARM_SINGLE_PROBE_DENSE               -- K=1 anchor (target ~0.18-0.24)
3. ARM_SINGLE_PROBE_AVERAGED_K10        -- controls "polarimetric = averaging noise"
4. ARM_AB_CONTROL_RANDOM_K_PROBES       -- controls "any K probes work"
5. ARM_POLARIMETRIC_K10_RANDOM_UNIT     -- controls "randomness alone"
6. ARM_POLARIMETRIC_K10_PCA_AXES        -- data-structure-aware (brain-aligned)
7. ARM_POLARIMETRIC_K10_LEARNED         -- contrastive-trained (strongest)
8. ARM_FLY_LSH_5x                       -- cross-cell sanity rail vs v2_batched

## Pre-reg bands (LOCKED via module-init assert chain)

- HP_LEARNED: pol_learned >= 0.85 AND beats AB_K, AVG_K10, FLY each by >= 0.10 AND
  monotonic K=1 < K=10 AND cv <= 0.05
- HP_PCA: pol_pca_axes >= 0.85 AND beats all controls by >= 0.10
- HP_PARTIAL_RANDOM_K: AB_CONTROL_K >= 0.85 (informative; "any K probes help")
- HF_DOESNT_HELP: pol_learned <= 0.30 (cross-domain reframe falsified)
- HF_AVERAGED_DOMINATES: avg_K10 >= pol_learned (mechanism collapses to averaging)

## Smoke evidence (local; pre-dispatch)

- Self-test: 5 verdict paths exercised + true-anisotropy-collapse smoke
  (raw=0.037 on near-duplicate keys) + polarimetric_identity=1.000 +
  learned-probe unit-norm post-train
- Smoke at M=400/1000 with pythia-160m runs all 8 arms end-to-end
- HF_AVG_DOMINATES verdict path FIRES correctly at smoke regime (pythia-160m + small M
  is too easy for the fair-test discriminator to land HP) -- proving the assertion
  machinery works as designed

## Cross-cell sanity rails to verify post-landing

- ARM_FLY_LSH_5x at M=10k should match v2_batched M=10k slice (~0.19) within 0.05
- ARM_RAW at adversarial-keys M=10k: ~0.02 (matches v2_batched slice raw=0.021)
- ARM_SINGLE_PROBE_DENSE at M=10k should match v2_batched single-probe baseline
- If POLARIMETRIC_LEARNED matches POLARIMETRIC_RANDOM_UNIT within 0.10 -> structure
  attribution falsified -> demote (per Q-discipline)
- If POLARIMETRIC_PCA_AXES beats POLARIMETRIC_LEARNED -> data-structure attribution
  stronger than learned-attention attribution -> note in atomization

## Strategic significance

Either outcome decision-grade:
- HP_LEARNED or HP_PCA: anisotropy "solved" via probe-and-response model (NOT
  expansion-based); hardware-friendly; brain-aligned to cortical attention
- HF_DOESNT_HELP or HF_AVERAGED_DOMINATES: cross-domain reframe doesn't transport;
  closes off another mechanism + locks substrate-product on partition routing +
  learned projection paths

## Config

- K_PROBES=10 (USER directive)
- M sweep: [2k, 10k, 50k] (CPU-feasible; mirrors recent anisotropy cells)
- 3 seeds [11, 13, 19]
- ENCODER=pythia-2.8b (full); pythia-160m (smoke)
- Adversarial-similarity keys (consecutive-token stride-1 windows; window=16, shift=1)
- Pure numpy at inference (no torch; encoder is setup-time hidden-state extractor)
- META_M7 capacity-sensitive dims identical across smoke/full

## Disciplines

- ASCII-only
- Pre-reg bands LOCKED via module-init assert chain
- Self-test PASSED on local + remote venvs before queue_add
- Per-seed checkpoint resume (PROT-021 run_cfg passed to aggregate_partials)
- Fix #28: per-arm metrics surfaced in verdict_msg + metrics.json detail block
- Path-scoped commit (only the 2 new files; no `git add .`)
- REMOTE VERIFY post-dispatch: confirmed in remote_cpu_queue/queue.json

## Waiting on

- Remote CPU runner to pick up and execute (~2-3h wall per the prereg runtime budget)
- Skunkworks landed-VET post-landing for cert-tiering
- Research synthesis of polarimetric outcome into anisotropy positioning

-- exp_dev, 2026-06-25
