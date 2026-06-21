# Prereg: n2_context_depth_hd_binding_v1

**Filed:** 2026-06-21  
**Anchor:** n2_context_depth_hd_binding_v1  
**Script:** experiments/exp_n2_context_depth_hd_binding_v1.py  
**Queue:** remote_cpu_queue  
**Dependency:** token_ids present in data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz (same as N1)

## Hypothesis

HD permutation-binding provides a DISTRIBUTED order-K context representation that generalizes
across contexts (vs count-based k-gram which sparsifies at high K). Deeper K (K>1) should
improve concept prediction (more structure captured) and partially -- but not fully -- improve
token-BPC (floor-masked by within-concept VQ noise, per Skunkworks 2026-06-21 PoC).

K=1 reproduces N1 single-step recall (built-in control / correctness anchor).

## Config

- N_DIM = 4096, f = 0.006, V_C = 256 (matches N1 exactly)
- DEPTH_SET = [1, 2, 3]
- SEEDS = [7, 17, 23] (same as N1)
- MAX_DOCS = 100000 (same as N1)
- DECODE: count-proportional batched_token_logprob with LAM_BACKOFF=0.1 (N1-identical)
- Baselines: token-unigram, token-bigram-Markov (Jelinek-Mercer INTERP_B=0.3), analytic ceiling
- CONFIG_VERSION: DEPTH=1-2-3,V_C=256,N_DIM=4096,f=0.0060,DECODE=countprop_interp,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8

## HD-binding formula

ctx_vec(t) = L2_normalize( sum_{j=0..K-1} roll(C[c_{t-j}], j) )

where roll(v, j) = np.roll(v, j) (cyclic shift by j positions = position encoding for lag j).
K=1: ctx_vec = L2_normalize(C[c_t]) -- identical to N1 source code (argmax-invariant under L2 scaling).

## Pre-registered bands (HARD -- no ex-post adjustment)

### HARD_PASS (chain-grade)
All of:
- substrate-BPC (best K in {1,2,3}) < token-BIGRAM BPC (expected ~3.84 from N1)
- depth gain: best_K sub_bpc beats K=1 sub_bpc by >= 0.10 BPC (clear signal vs noise)
- CV across seeds (BPC) <= 0.05
- substrate-only-decode (structural: no LLM calls at inference -- enforced by script design)

### MIDDLE_BAND
- depth helps: best_K sub_bpc < K=1 sub_bpc by >= 0.02 BPC (depth provides signal)
- BUT does not beat bigram OR depth_gain < 0.10 BPC (clears noise threshold but not clear margin)
- Note: within-concept VQ floor may absorb most of the concept-prediction gain (Skunkworks finding)

### HARD_FAIL
- No K improves over K=1 by >= 0.02 BPC (depth provides no real benefit)
- OR substrate BPC >= unigram BPC for all K (no structure captured)

## Saturation guard

Same as N1: alpha = n_unique_concept_pairs / N_DIM.
If alpha > 1.0 OR recall plateau >= 0.5 across seeds: demote to PROVEN-BOUND (not chain-grade).

## Separate concept-gain reporting (floor-absorption diagnostic)

Per Skunkworks 2026-06-21 finding: the within-concept VQ floor absorbs part of the
concept-prediction gain from deeper context. Reported separately:
- depth_token_gain_kK = substrate_bpc_k1 - substrate_bpc_kK (bits saved in token-BPC)
- depth_concept_top1_gain_kK = concept_top1_kK - concept_top1_k1 (concept accuracy gain)
- floor_absorption_approx_kK = concept_gain - token_gain (>= 0 if floor absorbs)

## Middle-band outcome plan (envelope-expansion)

If MIDDLE_BAND (depth helps but doesn't beat bigram):
- Report depth_token_gain and depth_concept_top1_gain separately.
- If concept gain is substantial (>= 0.05) but token gain is small: interpret as floor-masked;
  route to N3 which co-optimizes depth + codebook granularity C (lowers VQ floor).
- If both gains are small (< 0.02): re-route to Research for 2x revival (alternative binding
  strategies, SimVQ alignment-rescue, or structured VQ).

If HARD_FAIL (no depth benefit):
- Route to Research for 2x revival: (a) whether Pythia-160m residuals carry measurable higher-
  order concept structure beyond bigram, (b) whether the VQ-floor fully masks depth gain at C=256,
  (c) alternative HD-binding strategies (XOR, circular convolution, product codes).

## Runtime estimate

Per-K cost: context construction O(K * M * N) + W build O(M * N^2 / N) = O(M * N) once precomputed.
At M~40k transitions, N=4096: W build ~1-2 min per K; eval ~2-3 min per K.
3 seeds x 3 K values = ~27-45 min total on remote_cpu. Similar to N1 (which runs ~15 min/seed).

## K=1 correctness anchor

K=1 context vector = L2_normalize(C[c_t]).
W-free recall: L2_normalize(C[c_t]) @ W @ C.T argmax.
Since L2 scaling is argmax-invariant on the output (W is linear, scales output uniformly),
this is equivalent to N1's C[c_t] @ W @ C.T argmax.
Therefore K=1 should reproduce N1 concept_top1 ~0.507 and token-BPC ~5.00.
The _instrumentation_selftest() asserts this on a synthetic case.
