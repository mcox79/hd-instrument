# Pre-registration: wave14ya_erase_kerdock_v4

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14ya_erase_kerdock_v4.py](../experiments/exp_wave14ya_erase_kerdock_v4.py)
Priority source: follow-up to [wave14y_erase_kerdock_v3](../experiments/exp_wave14y_erase_kerdock_v3.py)
verdict `KERDOCK_V3_EXTENDS_TO_4N` (envelope at M ≤ 4N validated)
Author: experiment_dev session, pipeline tick 12

## Why

v3 validated Mirage protection through M_stored=4N=16384 using a 4-coset
MM codebook. The envelope question is now: does the structured-codebook
story have an upper bound, or does it extend indefinitely?

v4 extends to **8 cosets** = 8N=32768 codewords using the same MM
construction. b values: {0, 1, α, α², α³, α⁴, α⁵, α⁶} ∈ GF(2^t).
All C(8,2)=28 pairwise differences are nonzero distinct elements of
GF(2^t), so all 28 cross-coset XOR quadratics are bent — Welch bound
preserved everywhere.

Tests M_stored ∈ {4096, 8192, 16384, 24576, 32768} = {N, 2N, 4N, 6N, 8N}.

At M=8N, the substrate is **8x over-capacity**: 32768 (v, k) pairs
stored in an N×N matrix of rank ≤ N=4096. This is the regime where
Kerdock's *cross-talk bound* holds (by construction) but the substrate's
*storage capacity* is overdrawn. Kept reads may degrade even if erase
remains clean.

## Hypothesis

At N=4096 with the 8-coset MM codebook, 5 seeds:

- Erase-side multi-probe (argmax_leak, rank, norm_ratio, paraphrase_leak)
  passes at every M_stored up to 8N — Welch bound carries the structured-
  keys story this far.
- Kept_preservation may degrade as M_stored approaches 8N because W
  can't hold that many facts; verdict captures the cliff.

## Multi-probe success criteria (per M_stored)

Same five as v1/v2/v3 at α=1.0:
1. argmax_leak < 0.05
2. mean_rank > M_stored × 0.3
3. norm_ratio < 0.15
4. paraphrase_leak_h8 < 0.05
5. kept_preservation > 0.95

PASS at a given M = all five hold. Verdict captures the largest M_stored
at which Kerdock arm passes; for v4 the interesting envelope question
is "where does kept_preservation start to drop?"

## Kill criterion

Kerdock arm fails at M_stored=4N: regresses from v3's pass. Would
suggest v3 was a borderline result; audit.

## Verdict labels (5)

- `KERDOCK_V4_EXTENDS_TO_8N` — Kerdock passes all 5 probes at every M
  including 8N=32768
- `KERDOCK_V4_DECAYS_AT_<M>` — Kerdock fails at some M > 2N; envelope
  sized
- `KERDOCK_V4_REGRESSES_BELOW_V3` — Kerdock fails at M ≤ 4N (regression
  vs v3)
- `KERDOCK_V4_CORRELATED_PASSES` — control arm unexpectedly passes
- `KERDOCK_V4_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

Same construction-correctness checks as v3:
1. Codebook cross-coset max IP = 1/sqrt(N) (Welch bound, MM-exact)
2. Within-coset IPs near zero
3. Snap-to-codebook identity

For 8 cosets at smoke N=1024 (k=10, t=5): GF(2^5) has 31 nonzero
elements, so 8 distinct b values fit comfortably.

## Pre-mortem (3 failure causes)

1. **Memory at M=8N**: codebook is 8N × N = 32768 × 4096 floats =
   512 MB. Plus W = 4096² = 64 MB and per-call probe tensors.
   Should fit on workstation GPU (likely 8+ GB) but borderline.
   Mitigation: smoke at N=1024 (8N = 8192 × 1024 = 32 MB) tests
   the construction path; memory issue would only emerge at full mode.
   If full mode OOMs, retry with M_stored capped at 6N or seed count
   reduced.

2. **Kept_preservation cliff before erase fails**: at M = 8N, W
   can't actually store 32K facts. Each kept read W·k_j is the linear
   combination of v's weighted by cross-talk. As M grows, this noise
   dominates. The kept_preservation criterion (> 0.95) may fail well
   before the erase-side probes do. Verdict naturally captures this
   as DECAYS_AT_<M>.

3. **Runtime at M=8N**: matmul cost scales linearly with M. At 8N, the
   sims = (n_erase, N) @ values^T = (n_erase, M) = 30 × 32768 = 1M
   sims, each 4096-dim inner product. Per probe set: ~3 G ops. Times
   30 erases × 60 paraphrase queries (3 hamming × 20 each) × 5 seeds
   × 5 M_stored = ~9 T ops. Plus snap (8N codebook). Estimated runtime
   8-15 min on GPU; just inside the target.

## Operational definition

Reuses v3's codebook construction and probe machinery; the only
substantive change is `make_kerdock_8coset_codebook` which extends
b_values to 8 distinct GF(2^t) elements.

## Cited mechanism / sources

Same as v3.

## Expected runtime

- Smoke (N=1024, M_stored={1024, 4096, 8192} = {N, 4N, 8N}, 1 seed):
  ~5-10 s
- Full (N=4096, M_stored={4096, 8192, 16384, 24576, 32768}, 5 seeds):
  estimated 8-15 min on GPU

## What product decision this enables

- `EXTENDS_TO_8N` → Bet 2 envelope confirmed at 8x over-capacity;
  structured-keys story is essentially unbounded by codebook density.
  Strategy can claim "GDPR-grade erase scales beyond the substrate's
  storage capacity bound by ~8x."
- `DECAYS_AT_<M>` → envelope precisely sized; cap_map row updates.
- `REGRESSES_BELOW_V3` → audit; v3's verdict was borderline.
