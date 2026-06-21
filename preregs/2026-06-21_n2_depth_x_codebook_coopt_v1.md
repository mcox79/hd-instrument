# Prereg: n2_depth_x_codebook_coopt_v1

**Filed:** 2026-06-21
**Anchor:** n2_depth_x_codebook_coopt_v1
**Script:** experiments/exp_n2_depth_x_codebook_coopt_v1.py
**Queue:** remote_cpu_queue (residuals_per_token.npz lives on marsh@home)
**Dependency:** token_ids present in data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz (same as N1/v1)

## Motivation

n2_context_depth_hd_binding_v1 swept K in {1,2,3} at FIXED V_C=256. Result:
  - concept_top1: 0.507 (K=1) -> 0.527 (K=2)  [depth helped concept prediction]
  - token-BPC:    5.00 (K=1) -> 5.05 (K=2)    [depth did NOT help token-BPC]

Skunkworks diagnosis: the within-concept VQ floor (ceiling_bpc ~2.70 at V_C=256) ABSORBED
the concept-prediction gain. Floor lowers with finer V_C. Conclusion: depth gain only shows
in token-BPC if the floor is ALSO lowered. This cell co-optimizes K x V_C.

## Hypothesis

V_C and K are COUPLED levers:
  - V_C finer -> lower within-concept VQ floor (ceiling_bpc falls) -> depth gain can reach token-BPC
  - K deeper -> better concept prediction (captures higher-order structure)
  - Together: depth_token_gain at V_C=1024 > depth_token_gain at V_C=256 (~0)

## Config

- N_DIM = 4096, f = 0.006 (matches N1/v1 exactly)
- V_C_GRID = [256, 1024] (FULL; 6 configs total)
- DEPTH_SET = [1, 2, 3]
- SEEDS = [7, 17, 23] (same as N1/v1)
- MAX_DOCS = 100000 (same as N1/v1)
- DECODE: count-proportional batched_token_logprob + LAM_BACKOFF=0.1 (N1/v1-identical)
- Baselines: token-unigram, token-bigram-Markov (Jelinek-Mercer INTERP_B=0.3), analytic ceiling
- CONFIG_VERSION: VC_GRID=256-1024,DEPTH=1-2-3,N_DIM=4096,f=0.0060,DECODE=countprop_interp,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8

## Scientific questions (stated in verdict)

(a) Does finer V_C (1024 vs 256) LOWER the floor (ceiling_bpc) AND substrate token-BPC?
    [codebook lever alone -- V_C=1024,K=1 vs V_C=256,K=1]
(b) Does depth's concept-prediction gain SHOW in token-BPC at the LOWER floor (V_C=1024)?
    i.e. depth_token_gain at V_C=1024 > depth_token_gain at V_C=256 (~0)?
    [co-optimization payoff]
(c) Does ANY (V_C, K) beat the token-bigram baseline (~3.84)?

## K=1/V_C=256 correctness anchor

K=1/V_C=256 must reproduce ~5.00 token-BPC (consistent with N1/v1 result at same N_DIM/f/docs).
Any value outside [4.80, 5.20] should trigger a re-check.

## Pre-registered bands (HARD -- no ex-post adjustment)

### HARD_PASS (chain-grade, ALL of):
- some (V_C, K) substrate_bpc < bigram_bpc (expected ~3.84)
- clear depth_token_gain >= 0.10 bits at V_C=1024 (best K vs K=1 at same V_C)
- CV across seeds (BPC) <= 0.05
- substrate-only-decode (no LLM at inference -- enforced by script design)
- NOT demoted by saturation flag (alpha < 1.0)

### MIDDLE_BAND (either of):
- V_C lever works: substrate_bpc[V_C=1024,K=1] < substrate_bpc[V_C=256,K=1] by >= 0.05 bits
  (finer codebook alone lowers token-BPC -- the floor hypothesis)
- OR depth_token_gain >= 0.05 bits at V_C=1024 (co-optimization payoff visible, even if not
  beating bigram)
- Saturation-demote from HARD_PASS also lands here.

### HARD_FAIL:
- No (V_C, K) improves on the V_C=256 / K=1 anchor (~5.00) by > 0.05 bpc
  AND depth stays floor-masked (depth_token_gain < 0.05 bits) at ALL V_C tested.
- NOTE: per Skunkworks, the substrate may not beat bigram even at V_C=1024; the cell
  is designed to measure the TREND. Report findings regardless of HARD_PASS/FAIL.

## Saturation guard

Same as N1/v1: alpha = n_unique_concept_pairs / N_DIM.
If alpha > 1.0 for any (V_C, K): PROVEN-BOUND flag (not chain-grade). Coded in script.

## Middle-band outcome plan

If MIDDLE_BAND (V_C lever works OR depth shows at finer V_C):
  - If Q(a) is YES but Q(b) is NO: V_C helps floor but depth still masked even at V_C=1024.
    Route to N3: even finer V_C (2048+) OR alternative depth mechanism.
  - If Q(a) is NO but Q(b) is YES: depth shows without floor reduction. Unexpected -- route
    to Research for mechanism diagnosis.
  - If both Q(a) and Q(b) are YES but Q(c) NO: co-optimization works but substrate doesn't
    beat bigram. Quantify how close; route to N3 with larger V_C or alternative decode.

If HARD_FAIL (no improvement):
  - Route to Research for 2x revival: (a) do Pythia-160m residuals carry measurable order-2+
    concept structure? (b) is the VQ-floor fully dominant even at V_C=1024? (c) HD-binding
    alternatives (XOR, circular convolution, product codes, SimVQ alignment).

## Depth gains metric definitions

Per-(V_C, K) vs K=1 AT SAME V_C:
  depth_token_gain_vc<V>_k<K>  = substrate_bpc_vc<V>_k1 - substrate_bpc_vc<V>_k<K>
  depth_concept_gain_vc<V>_k<K> = substrate_concept_top1_vc<V>_k<K> - substrate_concept_top1_vc<V>_k1
  floor_absorption_vc<V>_k<K>   = concept_gain - token_gain  (>=0 if floor absorbs depth gain)

All reported in metrics.json per seed + mean.

## RAM estimate (V_C=1024 check)

VQ fitting (V_C=1024): MiniBatchKMeans with 1024 clusters on ~80k float32 vecs of dim 768 (Pythia).
  Cluster centers: 1024 * 768 * 4 bytes = 3.1 MB -- negligible.
W matrix (N_DIM x N_DIM = 4096^2 float32): 64 MB -- same as v1, independent of V_C.
P_src/P_dst (M_trans x N_DIM): at M_trans ~80k-400k tokens, 80k*4096*4=1.25 GB peak (brief).
  This was handled in v1; v2 uses the same approach (concatenate, build W, delete P_src/P_dst).
No V_C-dependent memory blowup in the W path.
concept_tok_counts dict at V_C=1024: 1024 * V_TOK * 8 bytes ~ 1024 * 50257 * 8 = 400 MB.
  This IS larger than V_C=256 (100 MB). Peak OK for remote_cpu_queue (~16GB RAM on marsh@home).

## Timeout estimate

Smoke not runnable on laptop (NPZ on marsh@home only).
Reference: v1 cell (3 seeds x 3 K at single V_C) ran ~27-45 min estimated.
This cell: 3 seeds x 2 V_C x 3 K = 18 config-seed combos vs v1's 9.
VQ fit cost doubles (2 V_C per seed). Estimate 2x v1 runtime = ~60-90 min per seed x 3 seeds.
Total: 180-270 min. Using 1.5x margin: ceil(270 * 60 * 1.5) = 24300s.
Rounded up to nearest 300s: timeout_s = 24300.

Formula inputs:
  smoke_wall_s: not available (no local NPZ); using v1 estimate 45 min/seed as anchor.
  FULL_seeds = 3, v1_seeds = 3
  Scale factor: 2 V_C x same N per seed = ~2x (extra VQ fit + second V_C inner loop)
  scaling_exp = 1.0 (linear sweep, no matrix ops beyond W build)
  timeout_s = ceil(1.5 * 45*60 * 2 * 3) = ceil(24300) = 24300

NOTE: runtime > 7200s (2h) flag -- this is a long run. Remote_cpu_queue at BELOWNORMAL priority;
desktop remains usable. Monitor for timeout.

## N-suffix binding note

Anchor name n2_depth_x_codebook_coopt_v1 does NOT contain an _nNUMBER suffix.
Production N_DIM = 4096 (embedded as module constant, not suffix).
Per PROT-018 rule 3b: N_DIM=4096 explicitly stated here as the no-suffix production value.

## Commit verification

Script: experiments/exp_n2_depth_x_codebook_coopt_v1.py
Prereg: preregs/2026-06-21_n2_depth_x_codebook_coopt_v1.md
Self-test: EXIT 0 (8/8 tests pass, confirmed 2026-06-21)
AST constants: all module-level (real code, not docstring), confirmed by ast.parse walk
