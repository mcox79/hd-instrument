# Prereg: substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1

**Date:** 2026-06-25
**Author:** exp_dev (USER-directed)
**Cell:** experiments/exp_substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1.py
**Anchor:** substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1
**Routing:** overnight_queue (GPU; Fix #24 active torch.cuda)
**Driver:** USER 2026-06-25: "if you have a cone - why can't you project the origin into the 'middle' of that cone and blow out all the parts to a bigger space?" + "Why can't you expand the cone to be 360 degrees (just fan it out in 3d)?"

## Strategic significance

USER's geometric intuition is exactly the cerebellar mechanism (sparse fan-in expansion creating new axes from the cone). v2 (`exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full`) used **5x expansion** (768 -> 3840 dims), got chain-grade-candidate at M=10k (Bfly=0.997). But brain operates at MUCH larger expansion ratios:
- Cerebellar mossy fiber -> granule cell: **~7M x** expansion (7000 mossy -> 50B granule)
- Fly olfactory PN -> KC: **~40x** expansion (50 PN -> 2000 KC)
- v2 substrate: **5x** expansion

Hypothesis: rescue mechanism strength scales with expansion ratio. If 5x gave 0.997 saturation at M=10k easy regime, then at M=100k harder regime where v3 cell was dispatched (Drill 2 URGENT 1), 5x may not be enough. Brain-scale expansion ratios may be necessary.

The complementary question (USER pose): "why can't you expand the cone to 360 degrees" — the geometric answer is that adding more random projections (sparse fan-in) creates new axes orthogonal-on-average to the cone-dominant direction; with sufficient expansion ratio the cone fans out into a hypersphere shell. This cell measures that ratio.

## Mechanism

Apply identical fly-LSH sparse-fan-in mechanism (K=5 sparse connections per item, WTA top-2% activation) at progressively larger expansion ratios. Use Pythia-2.8b encoder (same as v2 full) + contrastive projection train (same as v2). M=10000 (matched to v2 M_max for cross-cell comparison).

Sparse representation makes high expansion memory-feasible: at expansion 4096x, d_p = 3.15M dims, but each item only has K=5 nonzero values in the sparse-fan-in matrix S (and fly-LSH tags have FLY_TOPK=20 nonzero entries per item).

## Arms (6)

- **ARM_RAW** (baseline; no expansion; reproduces v2 raw 0.018)
- **ARM_FLY_LSH_5x** (matches v2 fly_lsh = 0.997; baseline reproduce sanity)
- **ARM_FLY_LSH_64x** (~12x more expansion; toward fly-olfactory regime)
- **ARM_FLY_LSH_512x** (close to fly-olfactory 40x effective; mid-range brain)
- **ARM_FLY_LSH_4096x** (closer to brain-scale; ~3.15M dim sparse expansion)
- **ARM_AB_CONTROL_4096x** (generic random Gaussian dense fan-in at same expansion; control for "any random projection at this expansion works")

NB: 5x reproduces v2 baseline (chain-grade-candidate); the expansion sweep upgrades the same mechanism through brain-scale regimes.

## Pre-reg bands (LOCKED at module init via assert)

- **HARD_PASS_FLY_LSH_RESCUES_AT_BRAIN_EXPANSION**: ARM_FLY_LSH_4096x >= 0.85 AT M=10000 AND beats ARM_AB_CONTROL_4096x by >= 0.10 AND monotonic-or-saturated in expansion (5x <= 64x <= 512x <= 4096x with no big-drop reversion)
- **HARD_PASS_PARTIAL_EXPANSION_HELPS**: monotonic lift visible (5x < 64x < 512x < 4096x within tolerance 0.02) but absolute plateau below 0.85
- **HARD_FAIL_EXPANSION_DOESNT_HELP**: ARM_FLY_LSH_4096x <= ARM_FLY_LSH_5x + 0.02 (expansion ratio not the limiting factor at this regime)
- **HARD_FAIL_OOM_AT_EXPANSION_X**: GPU memory exhausted at some expansion level (no metrics for that level; cell partial)
- **MIDDLE_BAND_CONTROL_ALSO_HELPS**: ARM_AB_CONTROL_4096x within 0.10 of ARM_FLY_LSH_4096x ("any random projection at brain-scale rescues"; mechanism not specifically fly-LSH)

## Config

- N_DIM = 768 (Pythia projection base; matches v2)
- expansion_factors = [5, 64, 512, 4096]
- d_p = N_DIM * expansion_factor in {3840, 49152, 393216, 3145728}
- K_FANIN = 5 (cerebellar regime; same as v2)
- KWTA_FRAC = 0.02 (WTA top-2% activation per item; slightly sparser than v2 0.10 to keep memory bounded at 4096x)
- FLY_TOPK = max(20, int(0.005 * d_p)) (0.5% of d_p as nonzero tags; matches v2 at small d_p)
- FLY_NONZERO = 0.05 (sparsity of random projection matrix entries)
- M = 10000 (matched to v2)
- Seeds [11, 13, 19] (cross-cell consistent)
- Substrate-only; ASCII; per-arm + per-expansion metrics
- Fix #24: active torch.cuda; smoke logs GPU utilization

## GPU memory budget

At expansion 4096x (d_p = 3.15M), critical matrices:
- Sparse-fan-in matrix S: dense (d_p, d) = (3.15M, 768) = 9.6GB at FP32 — TOO LARGE for dense storage
- Solution: store S as sparse COO/CSR (5 nonzero per row; total 15.7M nonzeros = 188MB)
- Forward: Ks_expanded = Ks @ S.t() — use torch.sparse matmul; output (M=10k, d_p=3.15M) = 126GB DENSE — TOO LARGE
- Solution: kWTA top-frac=0.02 keeps only 62k nonzero per row -> output sparse (M, d_p) with 6.2e8 nnz = 7.4GB FP32 - feasible but tight
- Alternative: chunk M into batches of 500 -> peak intermediate (500, 3.15M) = 6.3GB; manageable
- fly-LSH tags: int8, (M=10k, d_p=3.15M) = 31GB; INFEASIBLE. Solution: tags also sparse — only FLY_TOPK=int(0.005*3.15M)=15750 nonzero per row, store as index lists (10k * 15750 * 4 bytes int32 = 630MB)
- Tag-overlap matmul: dense (M, M) = 400MB FP32 — fine

**Critical:** ARM_FLY_LSH_4096x must use SPARSE representations end-to-end. The implementation does:
- Sparse S stored as torch COO tensor
- Ks @ S.t() done as sparse-dense matmul, then kWTA-sparsified per row
- Tags stored as topk-indices (no full d_p int8 tensor materialized)
- All arm logic verified at smoke before full

If 4096x OOMs, cell falls back to 2048x for that arm and verdict notes "HARD_FAIL_OOM_AT_4096x; 2048x measured as partial".

## META disciplines

- META_M6: baseline ARM_RAW measured in-cell (not copied from v2)
- META_M7: smoke matches full on PROJ_DIM, K_FANIN, KWTA_FRAC, expansion_factors (capacity-sensitive); only M + SEEDS reduce
- META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands locked at module init via assert
- Q-discipline: any arm >= 0.995 flagged as suspect saturation
- Fix #24: GPU smoke must hit >= 50% util on at least one matmul
- ASCII-only; no unicode in scripts

## Routing

- overnight_queue (GPU; RTX 4060 Ti 16GB)
- Timeout: 14400s (4h; 3 seeds * 4 expansion levels + AB_CONTROL + smoke overhead; conservative budget given memory pressure at 4096x)
- PROT-019 N/A (anchor has no _n<N> suffix; expansion_factor is on d_p, not N)
- PROT-020 satisfied (torch imported actively)
- PROT-021 satisfied (imports _seed_checkpoint via same template as v2)

## Reference cells

- exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full (v2 chain-grade-candidate at 5x)
- exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 (encoder + contrastive train pipeline)
- exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched (v3 batched-matmul reference)
- Drill 2 URGENT 1 (Research 2026-06-25): anisotropy M=100k adversarial-similarity in flight
