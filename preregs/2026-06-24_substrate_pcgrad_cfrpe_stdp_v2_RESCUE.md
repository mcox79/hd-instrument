# Pre-registration: substrate_pcgrad_cfrpe_stdp_v2_RESCUE

**Date:** 2026-06-24
**Anchor:** substrate_pcgrad_cfrpe_stdp_v2_RESCUE
**Queue:** remote_cpu_queue
**Precursor:** `substrate_pcgrad_cfrpe_stdp_v1` TIMED OUT at 5400s without producing metrics
**N_DIM:** 4096 (scope-reduced from 8192), **N_TRAIN:** 50_000 (from 100_000), **Seeds:** [7, 17, 23]
**Arms:** 4 (CFRPE_ONLY / NAIVE / PCGRAD / GCOND)

## Scientific question

Same as v1: does PCGrad-style gradient surgery between cf-RPE and STDP
plasticity updates rescue the heterogeneous-plasticity collapse observed in A1
(ARM_+STDP reversed ARM_+CFRPE gain by -0.116, 3/3 seeds), and does the
alternative GCond accumulation-based stabilization variant produce the same
rescue?

ANCHOR 1 (MH beta-sweep) HARD_FAIL_STRUCTURAL. H1 (gradient conflict between
heterogeneous plasticity rules updating the same W) is load-bearing.

## v1 timed-out post-mortem (cell-author re-read)

v1's own prereg estimated 105min = 6300s full runtime; cell author shipped at
timeout_s=5400 (BELOW own estimate). v1 imports `_seed_checkpoint` so partial
seeds COULD have survived, but `data/exp_substrate_pcgrad_cfrpe_stdp_v1/` is
empty -- the timeout fired before any seed completed.

Root cause: under-estimated CPU matmul throughput. (B=64, D=8192) @ (D, D)
matmul is 4.3 GFLOPS per step; 1000 steps per arm at 5 GFLOPS sustained =
860s/arm; 4 arms x 3 seeds = 10320s base + encoder + recall = ~3h. v1's 5400s
budget was ~half the realistic need.

## v2_RESCUE scope reduction (Option A from dispatch spec)

Choice: **Option A (scope reduction)** over **Option B (longer timeout)** or
**Option C (drop instrumentation)**.

Rationale:
- Option B would need ~14400s+ for full v1 scope; exceeds PROT-021 threshold
  cleanly, but commits 4+ hours of remote CPU to a single test. v2_RESCUE at
  1/8 cost lets the rescue land in ~1.5-2h on remote.
- Option C rejected: gradient-cosine instrumentation cost is bounded
  (COSINE_STRIDE=50 = 20 samples per arm), <1% of per-step wall.

Scope reduction is well-grounded for an intra-cell discriminator:
- PCGRAD vs NAIVE is the load-bearing measurement
- Matmul dynamics scale uniformly with D, N_STEPS
- Step-count PRESERVED at 1000 (PCGrad/GCond projection-convergence
  opportunity depends on training duration, not corpus size)

Changes from v1:
- N_DIM: 8192 -> 4096 (matmul cost ~1/4)
- N_TRAIN: 100_000 -> 50_000 (token pool 1/2; per-step sampling cost unchanged)
- N_HELD: 20_000 -> 10_000 (recall cost ~1/2)
- N_STEPS: 1000 (UNCHANGED -- projection-convergence bound)
- Provenance rails to A1's 7.0888 / 7.2044: DISABLED (calibrations were at v1
  scope; absolute BPC at reduced scope cannot be expected to match)
- All other configs unchanged: 3 seeds, 4 arms, word2vec sparse-bipolar f=0.05,
  cf-RPE LR=0.5, STDP weight=0.5, TEMP/LAMBDA grids, COSINE_STRIDE=50

## Pre-registered bands (per USER spec; identical to v1)

**HARD-PASS (chain-grade-eligible):**
- ARM_CFRPE_PLUS_STDP_PCGRAD BPC <= 7.05 (PCGrad rescues hetplast collapse) OR
- ARM_CFRPE_PLUS_STDP_GCOND BPC <= 7.05 (GCond rescues hetplast collapse)
- AND cv <= 0.05 across seeds for the passing arm
- INTERPRETATION: gradient-conflict IS first-order cause of hetplast collapse;
  fixable without architecture change via gradient surgery between heterogeneous
  plasticity rules updating the same W matrix

**MIDDLE-BAND (partial rescue):**
- PCGRAD BPC in (7.05, 7.20) -- gradient conflict contributes but not sole cause;
  investigate trained gate (K=2 learned-routing) or shared-state architecture

**HARD-FAIL:**
- PCGRAD BPC >= 7.20 -- gradient projection doesn't rescue collapse; H1 refuted;
  structural diagnosis stands; need cross-layer or other architectural change

**Caveat noted in honest_scope:** absolute bands 7.05 / 7.20 are calibrated to
v1 scope (N_DIM=8192 / N_TRAIN=100k). At v2_RESCUE scope, baseline BPC for ALL
arms may shift uniformly upward (less data + less capacity). Cell surfaces
BOTH absolute per-arm BPC AND relative lift PCGRAD-vs-NAIVE so cert-owner can
tier with full per-arm visibility. The INTRA-CELL discriminator (PCGRAD-vs-NAIVE
delta sign + magnitude) is the load-bearing finding regardless of absolute
floors.

**cv gate (unchanged):** PCGRAD cv > 0.05 across seeds -> MIDDLE_BAND_HIGH_CV
(seed-unstable; refuse cert).

## Gradient-conflict instrumentation (Fix #28 per-arm metrics)

Per-arm logged across COSINE_STRIDE=50 step samples (unchanged from v1):
- mean cosine between g_cf and g_stdp (negative -> conflict; positive -> aligned)
- frac_conflict = fraction of sampled steps with cosine < 0
- accumulated magnitudes (g_cf, g_stdp) across training
- (PCGRAD only) n_projected, sum_proj_norm
- (GCOND only) n_rescaled, mean_rescale_factor

This provides MECHANISTIC evidence regardless of BPC outcome: if mean cosine is
consistently positive across all seeds, the H1 conflict-mechanism hypothesis is
REFUTED at the gradient level (and any PCGrad rescue would be coincidental).
If mean cosine is consistently negative, conflict is empirically confirmed at
the gradient level (regardless of whether PCGrad's projection method fixes it).

## N-suffix section

No `_n<N>` suffix on the anchor name (PROT-018 does not apply). Production
N_DIM = 4096 hard-coded in the script; not parameter-swept.

## Timeout estimate

Smoke wall: 31s for 4 arms x 1 seed at N_DIM=1024, N_STEPS=80, V=300,
N_TRAIN=2000, N_HELD=400 on local laptop CPU.

Per-arm smoke wall ~7-8s. Scaling to v2_RESCUE full on remote CPU:
- D ratio: 4096/1024 = 4 -> matmul cost x 16 (cf-RPE dominates)
- N_STEPS ratio: 1000/80 = 12.5
- Per-arm full: 8s x 16 x 12.5 = ~1600s/arm on LAPTOP
- Remote CPU is typically 2-3x faster than this laptop for matmul-heavy numpy
  -> per-arm on remote ~600-800s
- 4 arms x 3 seeds = 12 arm-seeds: ~7200-9600s train
- Plus per-seed encoder load (word2vec, ~30s/seed = 90s) + recall (N_HELD=10k,
  V=4000, D=4096 -> ~40s/arm-seed = 480s) + sweep overhead ~120s
- Total estimate: ~8000-10000s

Formula: ceil(1.5 * 9600) = 14400s pushes PROT-021. Choose **timeout_s=10800**
(3h) -- gives ~30% safety on midpoint estimate, well below PROT-021 14400s
floor, _seed_checkpoint allows per-seed resume on timeout (so even a partial
2-seed completion is recoverable).

## References

- `experiments/exp_substrate_pcgrad_cfrpe_stdp_v1.py` (timed-out precursor at 5400s)
- `preregs/2026-06-24_substrate_pcgrad_cfrpe_stdp_v1.md` (v1 prereg)
- `notes/research_composition_collapse_critical_drill_2026-06-24.md` (ANCHOR 2 / Cell 2 spec)
- `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 reference)
- Yu et al. 2020 "Gradient Surgery for Multi-Task Learning" arxiv.org/abs/2001.06782 (PCGrad)
- "Gradient Conflict Resolution via Accumulation-based Stabilization" arXiv:2509.07252 (GCond)
