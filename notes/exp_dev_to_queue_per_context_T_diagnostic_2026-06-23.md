# exp_dev routing note: substrate_per_context_T_diagnostic_v1

**Filed:** 2026-06-23
**From:** exp_dev
**Action:** QUEUED to local_cpu_queue

---

queue=local_cpu_queue name=substrate_per_context_T_diagnostic_v1 script=experiments/exp_substrate_per_context_T_diagnostic_v1.py prereg=preregs/2026-06-23_substrate_per_context_T_diagnostic_v1.md timeout=2700

---

## Root cause analysis of discrepancy (pre-ship diagnosis)

### Shotgun P8 LIVE (83% entropy-variance delta)
- Dense random Gaussian encoder (not char-trigram)
- N_DIM=2048, N_TRAIN=5000 (small scale)
- Metric measured: variance of OUTPUT entropy distributions (not BPC)
- Per-token T calibrated to 50% max entropy via binary search
- Result: var(per-token output entropy) >> var(global-T output entropy): 83% increase
- This ONLY proves the mechanism computes something different per context
- It does NOT measure whether BPC improves

### Production cell HARD_FAIL (-0.32 to -0.37 bits vs unigram)
- Sparse-bipolar encoder f=0.05 (not dense random)
- N_DIM=8192, N_TRAIN=100k (production scale)
- Metric measured: BPC (lower = better)
- ARM_GLOBAL_T chose best_T=0.01 best_lambda=0.0 on dev
- best_lambda=0.0 means substrate contribution was ZERO -- unigram-only was best
- Per-context arms used fixed lambda=0.3, mixing 30% of a substrate signal that was BELOW unigram
- Result: any substrate mixing (lambda>0) makes BPC worse; per-context T compounds this

### Key insight: lambda=0 discovery
The production cell's ARM_GLOBAL_T picking best_lambda=0.0 is diagnostic:
- It means substrate (at T=0.01, sparse-bipolar, N_DIM=8192, N_TRAIN=100k) was NOT better than unigram
- The fair_harness baseline of BPC=7.3065 was at N_DIM=4096 -- a DIFFERENT config
- Production cell ran at N_DIM=8192 with SAME N_TRAIN=100k; substrate may be below unigram here
- Per-context arms were penalized by forced lambda=0.3 ON TOP of a below-unigram substrate signal

### Hypotheses (ranked by evidence)

H4 (codebook interaction): MODERATE prior
- Sparse-bipolar top-k quantization loses the smooth gradient information that entropy calibration needs
- The T_std values in production are tiny (0.000002-0.000007) -- the per-context T is near-constant
- This suggests sparse-bipolar logits are so quantized that entropy/margin vary little across contexts
- Dense encoder (shotgun) has smooth continuous logits with much more per-context entropy variance

H2 (lambda confound): HIGH prior
- Production global arm chose lambda=0.0 (substrate worse than unigram)
- Per-context arms forced lambda=0.3 (some substrate mixing)
- lambda mixing a below-unigram signal always hurts BPC, regardless of T routing
- This is not per-context T failing -- it's substrate signal quality failing

H3 (scale dependence): LOW-MODERATE prior
- N_DIM=8192 is 4x larger than fair_harness optimum (4096); substrate at 8192 may be over-specified
- N_TRAIN=100k with dense char-trigram matrix [8192x8192] may dilute per-bigram signal

H1 (implementation bug): LOW prior
- Production T_std=0.000002-0.000007 is suspiciously small -- T_vec is barely varying
- But entropy computation logic is identical to shotgun; shotgun had T_std=0.013 (orders of magnitude larger)
- Root cause of low T_std may be that sparse-bipolar logits have low entropy variance (H4)

## What diagnostic cell resolves

- ARM_GLOBAL_T_DENSE vs ARM_UNIGRAM: confirms whether dense encoder is above unigram at N=4096
- ARM_PER_CONTEXT_T_DENSE vs ARM_GLOBAL_T_DENSE: tests H1/H4 (is per-context T beneficial with dense?)
- ARM_PER_CONTEXT_T_SPARSE vs ARM_GLOBAL_T_SPARSE: tests H4 directly (does sparse ruin per-context T?)
- Lambda=0.0 option in per-context arms: tests H2 (does forcing lambda=0.0 recover the benefit?)
- Method B (50pct-target binary search) vs Method A (entropy formula): tests H1 directly

## Smoke results (N_DIM=256, N_TRAIN=2k, 1 seed)

BPC uni=5.1621
ARM_GLOBAL_T_DENSE: bpc=5.1057, lift_vs_unigram=+0.056 (DENSE SUBSTRATE ABOVE UNIGRAM = good)
ARM_PER_CONTEXT_T_DENSE: bpc=5.1621 (best of A/B), pc_lift=-0.056 (worse than global at smoke)
ARM_GLOBAL_T_SPARSE: bpc=5.2299 (WORSE than unigram -- sparse below unigram at N=256)
ARM_PER_CONTEXT_T_SPARSE: bpc=5.1621 (best of A/B), pc_lift=+0.068 (better than sparse global)

Smoke verdict: SPARSE_ONLY_BENEFIT (unexpected at smoke scale)
Note: N_DIM=256 smoke is very noisy; the H4/H2 diagnostic needs full N=4096 run.
T_std for dense methods: 0.036 (method A), 0.050 (method B) -- both show real per-context variation
T_std for sparse methods: 0.012 (method A), 0.178 (method B) -- methods differ significantly
This is already informative: sparse-bipolar entropy calibration shows different T distribution than dense.
