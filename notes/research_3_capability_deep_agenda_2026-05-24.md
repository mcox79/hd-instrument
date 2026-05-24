# Research analysis: 3-capability deep agenda

**Filed:** 2026-05-24 by orchestrator (verbatim from user analysis).
**USER EXPLICIT DIRECTIVE:** "The single highest-leverage move across all three capabilities is running the existing-data analyses before the next compute round. The substrate may be telling us more than we've read yet."

---

## Capability 1 — Multi-hop reasoning

### Existing data analyses (zero-compute, HIGHEST LEVERAGE per user)
1. **Per-hop accuracy decay curve shape.** Fit existing multi-hop accuracy(depth) data to: exponential a*exp(-bd), power-law a*d^-b, sigmoid a/(1+exp(b(d-c))). Best fit = mechanism hint.
2. **Cross-talk magnitude vs depth.** Does cross-talk grow as sqrt(d) (random-walk in HD-space) or linearly in d (additive interference)?
3. **Multi-hop accuracy vs M_stored.** Does multi-hop accuracy degrade as M grows (capacity-bound) or remain flat (depth-bound)?

### Pass 1 — broad research (unbiased)
- List-decoding literature on iterated codeword recall
- Free probability — multiplicative free convolution for chained operations
- AMP / VAMP iterative inference depth bounds

### Pass 2 — substrate drills
- Cap 10 / Cap 12 row review + KILLER probe re-examination
- Bet R / Bet C interaction at depth >= 4

### New experimental directions
- Multi-hop with mid-hop renormalization
- Hop-wise resonator network (already partially explored as exp_connectivity_resonator)

---

## Capability 2 — Multi-task retention

### Existing data analyses (zero-compute, HIGHEST LEVERAGE per user)
1. **Bet B retention vs phase-A bundle norm.** Histogram of retention across phase-A regimes; does retention bimodal-split at norm thresholds?
2. **Retention vs task-pair representational distance.** Correlate retention with <v_taskA, v_taskB> or mean cosine.
3. **Allen-Cahn t^(1/2) fit.** DONE 2026-05-24 — REJECTED (slope=0.069 outside [0.3, 0.7]).

### Pass 1 — broad research (unbiased)
- PAC-Bayes KL accumulation (R-PRIME-1)
- Replica-symmetric ansatz on substrate retention landscape
- Renyi-DP composition theorems

### Pass 2 — substrate drills
- MoE M_c falsifier (R-PRIME-2)
- Task-pair geometry (R-PRIME-3)

### New experimental directions
- K-sweep at fixed M_total (R-PRIME-2 ship)
- Task-pair geometry sweep
- HiPPO-basis retention fit (R-PRIME-5)

---

## Capability 3 — GPT-quality generation

### Existing data analyses (zero-compute, HIGHEST LEVERAGE per user)
1. **Existing perplexity at tested (N, K, M).** Fit perplexity surface to AGS-scaling form.
2. **Generation vs token frequency.** Does substrate handle rare tokens differently from frequent ones? Per-token perplexity histogram by frequency rank.
3. **Bet D analyzer pass on K=32 / K=64.** PENDING.

### Pass 1 — broad research (unbiased)
- AGS-scaling refinement (Allocation, Generality, Scale)
- Compression-as-prediction bounds (Solomonoff, Kolmogorov complexity)

### Pass 2 — substrate drills
- Bet D K=32 / K=64 analyzer
- Bet C M-N capacity envelope at N=65536

### New experimental directions
- Bet D sweep with structured-key allocation (Kerdock)
- K-cluster-conditional generation
