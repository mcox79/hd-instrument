# Pre-registration: Titans-style surprise-gated pool writes

Date: 2026-05-18
Status: Pre-registered, not yet run
Experiment file: [exp_surprise_gated_pool_charlm.py](../experiments/exp_surprise_gated_pool_charlm.py)

## Hypothesis (H)

A surprise-gated pool write policy — only commit `(context, target_byte)` to
the pool when per-token prediction loss `bits = -log2 P(target | ctx)` exceeds
a threshold — will improve test bpc on our 38KB byte-level corpus relative to
the unconditional-write baseline (combined+modReLU, 2.4994).

## Cited mechanism / paper

Behrouz, Zhong et al. *Titans: Learning to Memorize at Test Time*,
arXiv 2501.00663 (Jan 2025). Titans uses a surprise gate — gradient norm of
prediction loss — to write to a fast/episodic neural long-term memory. Scales
to 2M context, beats transformer baselines on long-context benchmarks.

## Operational definition (Carnap)

At training time, for each batch element `b`:
1. Compute `q = modReLU(W @ ctx_b)`, then `P_W = softmax(beta * sim(byte_atoms, q))`.
2. Compute per-token loss `bits_b = -log2 P_W[target_b]`.
3. Apply gate decision per strategy:
   - `fixed`: write if `bits_b > tau` for tau in {3.0, 4.0, 5.0}
   - `adaptive`: write if `bits_b > running_mean(bits) * c` for c in {1.0, 1.5}
   - `topk_frac`: write top-`k` fraction of batch by bits, k in {0.25, 0.10}
   - `none` (baseline): write all batch elements
4. Pool write rule is otherwise identical to baseline: epoch-1 only, ring buffer of 1024.

**Faithfulness check against Titans:** Titans uses gradient norm as surprise;
we use loss in bits. These correlate strongly but not identically. We are
testing the *surprise-gated write* principle, not the exact Titans gradient
mechanism. The tracker entry should note this.

**What our implementation is NOT:** Titans' full system includes a
*neural long-term memory* (small MLP trained at test time) and a *persistent
memory* gating module — we have neither. We are testing only the surprise-gate
write rule applied to our existing pool.

## Falsification criterion (machine-readable)

H is rejected if, for the best of all 7 non-baseline variants:
- 5-seed mean `test_bpc` is within [2.4944, 2.5044] (i.e., effect within
  ±0.005 of baseline, in the noise of GPU FP-precision drift we already measured)

H is supported (BF₁₀ ≥ 6 informal) if, for the best variant:
- 5-seed mean `test_bpc` ≤ 2.485 (≥0.014 bpc improvement, ~2x the FP-noise floor)

H is "weak win" (BF₁₀ ≈ 3, candidate not promoted) if best 5-seed mean is
between 2.485 and 2.494.

Single-seed result will be treated as exploratory only; promotion requires
the 5-seed protocol.

## Pre-mortem (top 3 failure causes if it doesn't help)

1. **Pool is already small enough that selectivity doesn't matter.** Our pool
   is only 1024 items from ~39K training bytes; the ring buffer naturally
   filters out very early items by overwriting. The surprise gate may
   redundantly do what the ring-buffer is doing.
2. **Surprise-by-loss correlates with "hard for current W", not "informative
   for future predictions".** Hard bytes might be the noisy/rare ones whose
   contexts don't generalize. Selecting them could *hurt* pool retrieval
   quality. This is the Titans-vs-our-setup mismatch concern.
3. **The pool head contribution (alpha=0.3) is already small enough that even
   a 2x improvement in pool quality moves test bpc by less than our noise floor.**
   Without recomputing alpha, the gate may be invisible.

If H fails for reason 3, the follow-up experiment is alpha sweep
(0.1, 0.3, 0.5, 0.7) at the best gate setting.

## Parameter-matched non-biological control

The baseline `none` strategy IS the parameter-matched non-bio control:
identical architecture, identical update, only the write rule differs.

Additional check: if `topk_frac=0.10` wins but `fixed_tau` does not, that
suggests the gain is from *pool compression* (less interference, fewer entries
to softmax over) rather than from *selecting informative items*. The
`topk_frac` strategy gives a 10x smaller effective pool. A confounded result
requires a pool-size control: run baseline with `pool_size=100` to disambiguate.

## Falsification of "this is just regularization"

If the surprise gate appears to help, run the same gate with the pool
*disabled at test time* (only W readout). If the gain persists, the gate is
implicitly regularizing W training (e.g., by changing the effective per-byte
training distribution). If the gain disappears, the gain is genuinely pool-quality.

This is not in the current experiment file; it is a follow-up planned in
advance per playbook item 5.

## Expected wall time

7 variants × ~50s each × 15 epochs (N=4096, single seed) ≈ 6 minutes total
for single-seed sweep. 5-seed promotion run (best variant) ≈ 4 minutes.
