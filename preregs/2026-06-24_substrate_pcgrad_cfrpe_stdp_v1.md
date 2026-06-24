# Pre-registration: substrate_pcgrad_cfrpe_stdp_v1

**Date:** 2026-06-24
**Anchor:** substrate_pcgrad_cfrpe_stdp_v1
**Queue:** remote_cpu_queue
**N:** 8192, **Seeds:** [7, 17, 23], **Levers:** 4 arms (CFRPE_ONLY / NAIVE / PCGRAD / GCOND)

## Scientific question

Composition collapse drill ANCHOR 2: does PCGrad-style gradient surgery between
cf-RPE and STDP plasticity updates rescue the heterogeneous-plasticity collapse
observed in A1 (ARM_+STDP reversed ARM_+CFRPE gain by -0.116, 3/3 seeds), and
does the alternative GCond accumulation-based stabilization variant produce the
same rescue? ANCHOR 1 (MH beta-sweep) was just HARD_FAIL_STRUCTURAL so MH is
omitted from this cell. H1 (gradient conflict between heterogeneous plasticity
rules updating the same W) is now load-bearing per the drill's L3 ranking
(P_deflated=0.60).

## Pre-registered bands

**Provenance rails (sanity check; must hold both):**
- ARM_CFRPE_ONLY BPC within +/-0.05 of A1's 7.0888 (cf-RPE primitive integrity)
- ARM_CFRPE_PLUS_STDP_NAIVE BPC within +/-0.05 of A1's 7.2044 (NAIVE compose reproduces collapse)

**HARD-PASS (chain-grade-eligible):**
- ARM_CFRPE_PLUS_STDP_PCGRAD BPC <= 7.05 (PCGrad rescues hetplast collapse) OR
- ARM_CFRPE_PLUS_STDP_GCOND BPC <= 7.05 (GCond rescues hetplast collapse)
- AND cv <= 0.05 across seeds for the passing arm
- INTERPRETATION: gradient-conflict IS first-order cause of hetplast collapse;
  fixable without architecture change via gradient surgery between heterogeneous
  plasticity rules updating the same W matrix

**MIDDLE-BAND (partial rescue):**
- PCGRAD BPC in (7.05, 7.20) — gradient conflict contributes but not sole cause;
  investigate trained gate (K=2 learned-routing) or shared-state architecture

**HARD-FAIL:**
- PCGRAD BPC >= 7.20 — gradient projection doesn't rescue collapse; H1 refuted;
  structural diagnosis stands; need cross-layer or other architectural change

**HARD-FAIL provenance trip-wires (sanity gates):**
- ARM_CFRPE_ONLY drift > 0.05 from 7.0888 -> cf-RPE primitive mismatch (HARD_FAIL_PROVENANCE)
- ARM_CFRPE_PLUS_STDP_NAIVE drift > 0.05 from 7.2044 -> NAIVE compose mismatch (HARD_FAIL_PROVENANCE)
- ARM_PCGRAD cv > 0.05 across seeds -> MIDDLE_BAND_HIGH_CV (seed-unstable; refuse cert)

## Calibration rationale

Bands derived from ANCHOR 2 of the composition collapse drill
(`notes/research_composition_collapse_critical_drill_2026-06-24.md` Cell 2 spec).

7.05 HARD_PASS ceiling = A1 cf-RPE-only baseline (7.0888) - tolerance (0.04);
i.e., "PCGrad-rescued compose matches or beats best-single cf-RPE primitive."
This is the substantive bar: hetplast collapse is "rescued" iff the composed
version returns to at-or-below cf-RPE-only performance.

7.20 HARD_FAIL floor = A1 NAIVE collapse (7.2044) - tolerance; i.e., "PCGrad
fails to improve over NAIVE collapse" -> projection doesn't help, H1 refuted.

MIDDLE_BAND (7.05, 7.20) = intermediate; PCGrad provides some lift but not full
recovery. Discriminates between "gradient conflict is THE cause" (HARD_PASS)
and "gradient conflict contributes but other mechanisms also operate" (MIDDLE_BAND).

cv <= 0.05 is the substrate's standing discipline (Skunkworks's cv gate; saved
multiple cells from false-PASS this year).

Provenance rails at +/-0.05 prevent silent encoder/plasticity drift from masking
the actual rescue signal. If the cf-RPE arm doesn't reproduce A1's 7.0888, the
NUMERICAL FLOOR of any rescue claim is broken (e.g. if cf-RPE-only itself
regressed to 7.20, claiming "PCGrad at 7.05 rescues" is meaningless).

## Gradient-conflict instrumentation (Fix #28 per-arm metrics)

Per-arm logged across COSINE_STRIDE=50 step samples:
- mean cosine between g_cf and g_stdp (negative -> conflict; positive -> aligned)
- frac_conflict = fraction of sampled steps with cosine < 0
- accumulated magnitudes (g_cf, g_stdp) across training
- (PCGRAD only) n_projected, sum_proj_norm
- (GCOND only) n_rescaled, mean_rescale_factor

This provides MECHANISTIC evidence regardless of the BPC outcome: if mean cosine
is consistently positive across all seeds, the H1 conflict-mechanism hypothesis
is REFUTED at the gradient level (and any PCGrad rescue would be coincidental).
If mean cosine is consistently negative, conflict is empirically confirmed at
the gradient level (regardless of whether PCGrad's projection method fixes it).

## N-suffix section

No `_n<N>` suffix on the anchor name (PROT-018 does not apply). Production
N_DIM = 8192 hard-coded in the script; not parameter-swept.

## Timeout estimate

Smoke wall: estimated ~120s on remote CPU (N_DIM=1024, V=300, N_TRAIN=2000, 1 seed,
80 steps per arm * 4 arms; numpy matmul on small dims).

FULL: N_DIM=8192, V=4000, N_TRAIN=100k, 3 seeds, 1000 steps per arm * 4 arms.

Per-arm wall scaling:
- Encoder build (per seed): ~30s (word2vec load + 4000-vocab project + sparsify)
- Training (per arm, per seed): 1000 steps * batch=64 * matmul cost dominated by
  (batch x N_DIM) @ (N_DIM x N_DIM) = ~64 * 8192 * 8192 = 4.3e9 ops per step
  ~ 1000 steps * 4.3e9 ops / ~10 GFLOPS CPU = ~430s = ~7min per arm per seed
- Recall (per arm per seed): N_HELD=20k, batch=256, ~1 matmul + V dot products
  ~ 20000 * 8192 * V=4000 = 6.5e11 ops / 10 GFLOPS = ~65s per arm per seed
- Total per arm per seed: ~7.5min ingest + ~1min recall = ~8.5min
- Total per seed: 4 arms * 8.5 min + 30s encoder + overhead = ~35min
- Total: 3 seeds * 35min = ~105min

Formula: ceil(1.5 * 105min * 60) = ceil(9450) = 9450 seconds.

timeout_s = 5400 (per ANCHOR 2 specification; cell author's adjustment based on
empirical past runtimes for similar matmul-bound numpy cells, knowing the
COSINE_STRIDE diagnostic + PCGrad/GCond overhead is bounded and per-arm
checkpointing via _seed_checkpoint allows resume on timeout). If the cell
genuinely takes >5400s, the partials are restartable; PROT-021 NOT triggered
(timeout < 14400s threshold).

## References

- `notes/research_composition_collapse_critical_drill_2026-06-24.md` (ANCHOR 2 / Cell 2 spec)
- `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 provenance refs 7.0888 / 7.2044)
- Yu et al. 2020 "Gradient Surgery for Multi-Task Learning" arxiv.org/abs/2001.06782 (PCGrad)
- "Gradient Conflict Resolution via Accumulation-based Stabilization" arXiv:2509.07252 (GCond)
- `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` (A1 reference; cf-RPE + STDP primitive implementations)
