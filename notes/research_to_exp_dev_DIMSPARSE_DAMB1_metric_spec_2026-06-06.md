# Research -> Exp-Dev: DIMSPARSE construction spec = Option (iii) + DAMB1 unified M_50 metric

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~15:15
**Re:** exp_dev_to_research_DIMSPARSE_parked_construction_2026-06-06.md
**Subject:** Option (iii) for DIMSPARSE: real keys + sparse-coded values + dim-expanded keys. M_50 metric. N_ENC=10000 (uncensored). Same M_50 metric applies to DAMB1.

---

## Construction = Option (iii) -- real keys + sparse VK binding

You correctly identified that Slot-14 dim-expansion (real-encoder sign-lift) and Slot-3 sparse-pattern (synthetic auto-assoc bipolar) live on DIFFERENT substrate types. The right compound test for PRODUCTION substrate is real keys + sparse VALUES.

### Architecture

- **Keys:** real encoder output (Pythia-160m residuals; matches G8 architecture for direct comparability)
- **Values:** bipolar VQ codes (V_c=4096 codes; k-of-D active for sparse arms)
- **Substrate:** standard W = sum_i k_i v_i^T (or W = Vs^T keys/n if W-free)

### Four arms (N=4096 + N=16384; N_ENC=10000)

- (a) baseline: real keys + dense values (k=D active)
- (b) expand-keys: dim-expanded real keys (phi(x)=sign(Rx) at D=1024 or larger) + dense values
- (c) sparse-values: real keys + sparse bipolar values (f=0.20 active, matches Slot 3 alpha)
- (d) compound: expanded keys + sparse values

### Metric: M_50 (key-collision-aware)

For each arm:
1. Sweep M from low to high (insert M random KV pairs)
2. For each M, query with flip-corrupted key (FLIP=0.05); measure retrieval recall (does retrieved value match stored)
3. Find M_50 = M at which retrieval recall first drops below 0.5

Compare M_50 across arms.

### Why this is the right compound test

- **Keys hit dim-expansion mechanism** (encoder anisotropy attack)
- **Values hit sparse-pattern mechanism** (linear-noise regime attack per Tsodyks-Feigelman)
- They attack DIFFERENT bottlenecks in same retrieval pipeline
- If multiplicative compound holds, ~45x for production substrate

### Why NOT Options (i) or (ii)

- (i) Synthetic + larger N is just a scale-up; not a real compound test
- (ii) Sparsifying real KEYS loses info (encoder embeddings are dense by design); not the original sparse mechanism

## Censoring fix

N_ENC=10000 for expanded arms (5000 was too low; both b and d hit ceiling). If still censored at 10000 for d_both, report as ">=M_50_seen" and we know compound is at least the floor.

## Pre-reg thresholds (DIMSPARSE)

- HP: (d) M_50 >= 0.80 * (b_M_50)*(c_M_50)/(a_M_50) -- multiplicative within 20%
- MID: (d) > max(b,c) but < 0.80 of product
- HF: (d) approximately = max(b,c)

(I'm framing the compound as ratios to baseline. The product test is "(d)/(a) >= 0.80 * [(b)/(a)] * [(c)/(a)]" which simplifies to the formula above.)

## DAMB1 metric (parallel question -- same M_50 framework)

For DAMB1 substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1:
- Same M_50 metric (key-collision-aware)
- Sweep N_sub in {384, 768, 1536, 3072, 6144}
- For each N_sub, measure M_50(synthetic) and M_50(real)
- Plot ratio M_50(real)/M_50(synthetic) vs N_sub
- HP for H1 (N-dependent noise): ratio decays SUB-LINEARLY with N
- HP for H2 (Hadamard saturation): ratio decays LINEARLY with N
- Disambiguation cell -- routes which rescue path to invest in (DAMB3 SRHT for H2; DAMB4 PCA for H1)

This consolidates: DIMSPARSE + DAMB1 + G9-FIX all use the SAME M_50 metric. One implementation; reused across cells.

## Note: this might MERGE with Slot G16 too

Slot G16 (substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1) is about whether expansion subsumes whitening. The compound question (dim-expansion + sparse) is independent. So G16 stays separate, but the M_50 metric works for both.

---

**END.**

**Exp-Dev:** DIMSPARSE = Option (iii) real keys + sparse VK binding. M_50 metric (key-collision-aware). N_ENC=10000. ~45 min CPU per arm. Same M_50 metric for DAMB1 (and G9-FIX which I already specified at 12:10). Apologies for the earlier under-spec; this is a non-trivial substrate-architecture question and you caught the issue correctly.

**User:** DIMSPARSE construction needed clarification. The compound test is now defined as real-encoder KEYS + sparse-bipolar VALUES with dim-expanded keys for the expansion arms. Tests whether the two mechanisms (encoder anisotropy attack via expansion + linear-noise regime via sparse) compound multiplicatively. If yes, causal-LM substrate gets ~45x compound. If no, each axis is independent ~7x. Same metric (M_50 key-collision-aware) reused for DAMB1 + G9-FIX.
