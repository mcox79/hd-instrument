# Pre-registration: n1_concept_lm_substrate_native_token_decode_v2

**Date:** 2026-06-21
**Anchor name:** n1_concept_lm_substrate_native_token_decode_v2
**Script:** experiments/exp_n1_concept_lm_substrate_native_token_decode_v2.py
**Queue:** remote_cpu_queue
**Authority:** exp_dev (per USER directive 2026-06-21 re: substrate-optimal storage density)
**Bands source:** Skunkworks N3 corpus-eval cert-bands (2026-06-21T16:06:58Z, CERT 583/177265)
**Research synthesis:** notes/research_to_orchestrator_N1_density_scour_substrate_optimal_synthesis_2026-06-21.md

---

## What this tests

Substrate-native token-level language model using SPARSE Willshaw-style concept codes at
N_DIM=4096. Re-authors v1 (dense bipolar cf-RPE at N=1024, definitively under-capacity) with
substrate-optimal storage density per Research scour + Skunkworks N3 eval spec.

At INFERENCE, no transformer is called. Pythia-160m is used ONCE at ingest to produce residuals.
The concept codebook C is built from random sparse binary codes (not km centroids). The transition
memory W and decode memory D are substrate-native Hebbian associations over sparse codes.

---

## Configurable params (defaults pre-registered here)

| Param   | Default | How to set                        | Notes                                 |
|---------|---------|-----------------------------------|---------------------------------------|
| N_DIM   | 4096    | HDLAB_N_DIM env or --n-dim        | Substrate-optimal (was 1024 in v1)    |
| f       | 0.006   | HDLAB_F_SPARSE env or --f-sparse  | Willshaw sweet-spot log(N)/N at N=4096 |
| V_C     | 256     | HDLAB_V_C env or --v-c            | Codebook size; N2 sweeps this         |

k_active = round(f * N_DIM) = round(0.006 * 4096) = 25 active units per concept code.

Theoretical capacity at f=0.006, N=4096: ~80k transition patterns (vs ~140 dense Hopfield at
N=1024). Source: a3f473dd MEASURED_MECHANISM (8x@f=0.10 / 20x@f=0.02 / >=300x@f=0.005,
N-independent raw P.T@P Willshaw); Research density-scour Lever C lit-scan (Tsodyks-Feigelman
1988; Knoblauch-Palm-Sommer 2010).

---

## Sparse encoding (substrate-optimal, pre-registered)

**Codebook C:** sparse binary, shape (V_C, N_DIM), k=round(f*N) active per row.
  Reused construction idiom from exp_sparse_boundary_v2_cpu_v1 (atom a3f473dd lineage).

**Transition memory W (W-free Willshaw single-step):**
  Stored as raw pattern matrices P_src (M_trans, N_DIM) and P_dst (M_trans, N_DIM).
  Recall: sign( (query @ P_src.T) @ P_dst ) -> cleanup argmax against C.
  Proven readout idiom: EXACTLY from exp_sparse_boundary_v2_cpu_v1 / exp_sparse_onset*.
  No dense W matrix stored; memory footprint = 2 * M_trans * N_DIM * 4 bytes.

**Decode memory D:** shape (N_DIM, V_TOK). Column j = sum of C[concept_t] for all
  (concept_t, token_t=j) in train. Decode: D.T @ concept_vec -> argmax (substrate-native;
  no LLM head). Because concept_vec is sparse (k-of-N active), D.T @ concept_vec sums
  only k columns of D.

---

## Data dependency (HARD GATE)

residuals_per_token.npz MUST contain a token_ids key. The v2 cell raises FileNotFoundError
if token_ids is absent (no silent fallback). A recovery cell landing token_ids on marsh@home
MUST complete before this cell runs.

---

## Pre-registered verdict bands (Skunkworks N3 cert-bands, 2026-06-21T16:06:58Z)

**HARD_PASS (chain-grade):**
  substrate-native BPC < token-BIGRAM BPC on held-out
  AND cv <= 0.05 across seeds (substrate_bpc coefficient of variation)
  AND substrate-only-decode verified (zero LLM calls at inference -- structural, enforced by design)
  AND NOT saturated (alpha <= 1.0 AND no recall plateau >= 0.5)

**MIDDLE_BAND:**
  substrate BPC in (bigram_BPC, unigram_BPC] -- captures some structure, doesn't beat bigram.
  Also: HARD_PASS conditions met but saturation flag raised -> demote to MIDDLE_BAND (PROVEN-BOUND).

**HARD_FAIL:**
  substrate BPC >= unigram_BPC (no real structure extracted by substrate)
  OR any LLM forward call in the inference path (substrate-only violated -> disqualified)

**SATURATION GUARD (pre-registered, mandatory):**
  alpha = n_unique_transition_pairs / N_DIM.
  If alpha > 1.0 OR recall plateaus >= 0.5 across queries: demote to PROVEN-BOUND (MIDDLE_BAND),
  not chain-grade. This guard is symmetric and applies regardless of BPC outcome.

---

## Additional metrics (diagnostic, not verdict-bearing)

- substrate_concept_top1: concept-level next-concept top-1 accuracy (sanity)
- ceiling_bpc: analytic ceiling (oracle concept -> best token); distillation gap = substrate_bpc - ceiling_bpc
- codebook_utilization: fraction of V_C clusters active in train (VQ collapse detector)
- alpha: n_unique_pairs / N_DIM (saturation gauge)

---

## Config version (checkpoint invalidation)

CONFIG_VERSION = "V_C=256,N_DIM=4096,f=0.0060,DECODE=freq,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8"
Any change to V_C, N_DIM, f, MAX_DOCS, SEEDS, or SPLIT invalidates existing checkpoints.

---

## Seeds

Full run: SEEDS = [7, 17, 23] (3 seeds, CV computed across all 3).
Smoke: SEEDS = [1], V_C=32, MAX_DOCS=100.

---

## Timeout estimate

No prior smoke wall time available (full run requires remote npz).
Reference: v1 analogue with N=1024, V_C=256, 100k docs ~15-30 min per seed.
v2 at N=4096 (4x larger W-free matmul per step): scale ~4x per seed.
Estimate: 3 seeds * 30min * 4x_scale = 360 min. Add 50% margin.

timeout_s = 32400  (9 hours; within 4h cap? NO -- exceeds 14400s)

FLAG: estimated wall time ~6 hours (360 min) at 1.5x margin. This exceeds the 4-hour
soft-block threshold. However:
  (a) The 4x scale factor is conservative; sparse W-free matmul at N=4096 is much cheaper
      than dense W construction. P_src.shape = (M_trans, 4096); typical M_trans ~= 200k
      transition pairs from 80k train docs. Dot (200k, 4096) x (4096,) per test step.
  (b) With vectorized eval (batch test queries), this is feasible ~90 min per seed.
Revised estimate: 3 seeds * 90 min + 50% = 405 min ~= 6.75 hours.

REVISED FLAG: estimated ~6h. Exceeds the 2-hour flag threshold. Shipping is allowed per
role contract (>2h but allowed with flag). Orchestrator may want to reduce MAX_DOCS for
initial run if runtime is critical.

timeout_s = 25200  (7 hours, rounded up with margin; matches role contract "flag if >7200")

NOTE: This experiment has a EVAL BOTTLENECK (per-token dot product in test loop). The inner
loop over test tokens is O(M_trans) per step. At 100k docs, 20k test docs, avg 200 tokens/doc =
4M test positions * O(M_trans ~ 200k) = expensive. If runtime is too long, reduce MAX_DOCS
to 10000 for the initial run.

---

## N-suffix note (PROT-018)

Anchor name n1_concept_lm_substrate_native_token_decode_v2 has no _nN suffix.
Production N_DIM = 4096 (default, configurable). Per PROT-018 rule 3:
"No _nN suffix; production N = 4096 (default); rationale: N is configurable via env/CLI;
N2 sweeps this param. Hardcoding N in the name would block sweeps."

---

## By-construction guards (Skunkworks N3 spec compliance)

1. NO LEAK: held-out tokens VQ'd by FROZEN ingest codebook (km fit on train only; test cids
   computed with km.predict, no refit on test). Disjoint split enforced by random permutation.
2. VQ-GRANULARITY BPC-FLOOR: ceiling_bpc = within-concept token entropy (analytic ceiling).
   Reports both concept-transition BPC gap and within-concept floor.
3. ANALYTIC CEILING is the CEILING, not the target. Distillation gap reported.
4. V_C utilization reported (codebook_utilization metric).
5. Substrate-only verified structurally (no LLM imports in this script).
