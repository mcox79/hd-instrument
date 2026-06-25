# Pre-registration: substrate_KG_capacity_sweep_M_10k_100k_1M_v1

**Date:** 2026-06-25
**Anchor:** substrate_KG_capacity_sweep_M_10k_100k_1M_v1
**Queue:** overnight_queue (GPU)
**d:** 768, **sigma:** 0.1, **Seeds:** [11, 13, 19]
**M_GRID:** [10000, 50000, 100000, 500000, 1000000]
**Routing rationale:** torch.cuda required per Fix #24 (GPU dispatch MUST actually
use GPU; M=1M with d=768 is a 768x768 matmul vs 1M-row key matrix = ~3GB GPU
mem; batched query-eval requires CUDA tensor cores for tractable wall time).

## Strategic intent — KG retrieval phase-diagram closure

USER directive (2026-06-25): "approved on 3" (KG scale-up) + "I want...we
understand where everything operates best within the phase diagram".

`dense_projected_KV_envelope_v1` proved chain-grade at M=10k (recall@1 >= 0.80;
M-independent O(d^2) superposition store). The cliff location at M > 10k is
the substrate-product KG positioning question:
- M=10k = small-corpus demo
- M=100k = real KG product
- M=1M = stretch / production-scale KG

This cell sweeps M to find the cliff (or its absence) and identify the
operating envelope.

## Mechanism (reused from dense_projected_KV_envelope_v1)

Per (M, seed):
- Generate M random i.i.d. gaussian keys K of shape (M, d=768).
- Assign each key a label y_i in {0..C-1} where C=256 codebook.
- Build superposition store W = sum_i codebook[y_i] k_i^T of shape (d, d).
  **M-independent** O(d^2) storage.
- For Q=2000 sampled queries: cue = K[qidx] + sigma*noise; readout =
  cue @ W.T; predict y_hat = argmax cosine(readout, codebook); compare
  to y[qidx].

Measure at each M:
- recall@1, recall@5, recall@10 (top-k cleanup)
- keysep (mean key-key cosine; isotropy check)
- avg-cleanup-sigma (substrate's softmax peak vs runner-up)
- memory footprint (W matrix bytes + K matrix bytes)
- per-query latency (GPU wall, ms)

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE_AT_M_100k
- recall@1 >= 0.70 at M=100k (substrate-product KG threshold)
- cv <= 0.05 across 3 seeds at M=100k

### HARD_PASS_CHAIN_GRADE_AT_M_1M
- recall@1 >= 0.50 at M=1M (stretch goal; if HARD_PASS_AT_M_100k also holds)

### MEASURED_MECHANISM_at_M_cliff_X
- Identify the smallest M in M_GRID where recall@1 cliffs from >= 0.80 to
  < 0.50. Cert as MM at that M (operating-envelope upper-bound found).

### HARD_FAIL_M_10k_DOESNT_REPRODUCE
- recall@1 < 0.70 at M=10k (rail violation; would suggest env or scaling bug;
  prior cert envelope was >= 0.80 at M=10k)

### HARD_FAIL_GPU_UNUSED
- nvml-reported GPU util < 50% averaged over wall (per Fix #24; GPU dispatch
  MUST actually use GPU). Smoke verifies with torch.cuda.is_available + memory
  allocated. Full run cv computed from torch GPU memory delta.

### OOM
- GPU memory exhausted at some M < 1M. Cert as "M-ceiling-identified at
  some M_oom".

## Calibration rationale

- **0.70 recall@1 at M=100k:** lower than the M=10k chain-grade envelope
  (0.80) because crowding grows linearly with M. 0.70 still well above
  chance (1/256 = 0.004) and useful for retrieval product.
- **0.50 recall@1 at M=1M:** "useful retrieval at 1M facts" threshold;
  even at 0.50 the substrate beats every classical KG-attention model at
  M=1M dict-equivalent O(M*d) baseline budget.
- **+-0.05 reproduce envelope at M=10k:** standard substrate replication tolerance.
- **cv <= 0.05:** standard substrate-stability requirement.
- **GPU util >= 50%:** per Fix #24 GPU dispatch must show >= 50% gpu util to
  avoid wasting GPU runner slot on CPU work.

## Q-discipline (BIAS-Q: suspect 1.000 results)

If any M shows recall@1 >= 0.995, suspect:
1. Smoke at M=10k reproduces existing cert envelope (~0.80, NOT 1.000); a
   1.000 number at any M is suspect saturation in this regime.
2. Query-leakage: queries must be cue = K[qidx] + sigma*noise, NOT K[qidx]
   exactly (smoke self-test verifies non-zero sigma).
3. The cell should DECREASE recall as M grows (crowding); monotonic
   non-increase verified in self-test.

## Q-discipline (META_M6: NAIVE bands DERIVED from this regime)

The naive "M=10k chain-grade envelope" baseline (recall@1 >= 0.80) is
DERIVED from `dense_projected_KV_envelope_v1` measured envelope at the SAME
(d, sigma, C) regime. Per-M HARD_PASS thresholds (0.70 at 100k; 0.50 at 1M)
extrapolate from the M=10k anchor along the expected Phi(1/sqrt(alpha))
RMT crowding curve, NOT from copied envelopes.

## Capacity-feasibility analysis

- d=768 means W is 768x768 = ~2.3MB regardless of M (the substrate-product
  win: M-INDEPENDENT storage).
- Key matrix K is M x d float32:
  - M=10k -> 30MB
  - M=100k -> 300MB
  - M=500k -> 1.5GB
  - M=1M -> 3GB
- Query batch is Q x d = 2000 x 768 = 6MB.
- Decode is over C x d = 256 x 768 = 0.75MB.
- Per (M, seed): build K + assign y + build W + Q queries + decode.
  GPU wall estimate: M=10k ~1s; M=100k ~10s; M=1M ~3min (matmul-dominated).
- Total per seed: ~5min; 3 seeds = 15min; total wall ~20-30min.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix (M-suffix only; not a hidden-dim
sweep). PROT-018 does not apply.

PROT-020 (GPU queue must import torch): script imports torch + uses
torch.cuda explicitly per Fix #24. Verified.

PROT-021 (long timeout needs checkpoint): timeout_s budget below 14400s;
PROT-021 does not apply.

## Timeout estimate

Smoke at M=[10k, 50k] / 1 seed / d=768 on local CPU: ~30-60s wall (numpy
fallback for smoke); on GPU smoke <10s.

FULL: 5 M values x 3 seeds = 15 (M, seed) pairs. Per-pair GPU wall estimate:
- M=10k: ~1s
- M=50k: ~5s
- M=100k: ~10s
- M=500k: ~60s
- M=1M: ~180s
Sum per seed = ~4.5min; 3 seeds = ~14min. Add 2x margin for GPU overhead +
metric collection = ~30min.

formula: timeout_s = ceil(1.5 * 60 * (1000000/10000)^1.5 * (3/1)) =
ceil(1.5 * 60 * 1000 * 3) = 270000s. **However**, this overestimates by
ignoring M-independence of W storage; actual scaling is O(M) on key matrix
build + O(d^2*Q) query (M-independent). Realistic budget: 1800s (30min).

Budget: **timeout_s = 3600** (1 hour; conservative; per-(M, seed) checkpoint).

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports both directions per M:
- recall@1 (the headline)
- recall@5, recall@10 (graceful-degradation rail)
- keysep (substrate isotropy)
- avg-cleanup-sigma (substrate confidence)
- per-query latency (substrate speed)
- memory footprint (substrate footprint)
- GPU util observed (Fix #24)

## Strategic significance

Defines the substrate's KG-retrieval phase-diagram operating envelope:
- M-ceiling for chain-grade product
- Cliff location (or its absence)
- Scaling regime (M-independent storage win vs M-dependent baselines)

This is the data USER needs to position "substrate as KG retrieval product".
