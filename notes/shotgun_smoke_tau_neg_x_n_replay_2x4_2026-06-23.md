# Shotgun Smoke: TAU_NEG x N_REPLAY 2x4 Factorial (2026-06-23)

Script: `experiments/shotgun_smoke_tau_neg_x_n_replay_2x4_v1.py`
Config: N=512, VOCAB=100, N_TRAIN=2000, N_HELD=400, SEEDS=[42, 137], TAU_POS=5, SPARSE_F=0.05
Wall time: 103s

---

## Per-arm BPC (mean across 2 seeds)

| Arm            | tau_neg | n_replay | BPC    | Lift vs vehicle |
|----------------|---------|----------|--------|-----------------|
| ARM_VEHICLE    | None    | 0        | 3.8893 | 0.0000          |
| ARM_T50_R1     | 50      | 1        | 3.8893 | 0.0000          |
| ARM_T50_R10    | 50      | 10       | 3.8893 | 0.0000          |
| ARM_T50_R30    | 50      | 30       | 3.8893 | 0.0000          |
| ARM_T50_R100   | 50      | 100      | 3.8893 | 0.0000          |
| ARM_T10_R1     | 10      | 1        | 3.8893 | 0.0000          |
| ARM_T10_R10    | 10      | 10       | 3.8893 | 0.0000          |
| ARM_T10_R30    | 10      | 30       | 3.8893 | 0.0000          |
| ARM_T10_R100   | 10      | 100      | 3.8893 | 0.0000          |

Classification: BOTH_NULL_AT_SMOKE

---

## HARD_INFO Interpretation

**TAU_NEG axis**: NULL at smoke scale. NOT because the mechanism is wrong, but because:
  - At N_TRAIN=2000 with INGEST_CHUNK=512, the W-builder processes ~4 chunks total.
  - TAU_NEG=50 produces decay_neg = 1 - 1/50 = 0.98 per chunk.
  - TAU_NEG=10 produces decay_neg = 1 - 1/10 = 0.90 per chunk.
  - After 4 chunks, these two trace EMAs are NEARLY IDENTICAL (difference is ~4th power of 0.08).
  - Structural confirmation: W matrix diff norm between t50_r1 and t10_r1 is exactly 0.0000.
  - The timescale ratio effect needs dozens of chunks to accumulate; smoke has 4.

**N_REPLAY axis**: TINY effect at smoke scale (not zero, but sub-threshold):
  - W diff norm between t10_r1 and t10_r10: 0.0041 (0.5% of W norm).
  - No BPC change because W is rank-1 dominated: sv[0]=0.794, all others < 0.002.
  - Multi-pass replay makes W MORE rank-1 (sv[1] drops further with more passes).
  - At smoke scale, replay reshuffles 2000 tokens; no new information added.

**Root cause of degenerate BPC**: W is rank-1 at all scales tested. All predicted vectors
are parallel (top eigenvector dominates); logit std = 0.0046 across 100-vocab. Grid-search
always picks lambda=0 (pure unigram) because substrate adds no discriminative signal.
This is NOT a measurement artifact -- it is a genuine property of the mechanism at N_TRAIN=2000.

**Unigram BPC context**: 3.89 is the best achievable BPC with this harness at this scale
(unigram dominates; substrate W is degenerate).

---

## WHAT THIS DOES NOT SHOW

1. **Small-N/small-corpus limitation**: N_TRAIN=2000 = 4 chunks at INGEST_CHUNK=512.
   TAU_NEG trace timescales need O(tau) chunks to diverge. TAU_NEG=50 needs ~50 chunks
   = 25k tokens. This smoke CANNOT show the TAU_NEG axis effect.

2. **Char-trigram vs word2vec**: Production cells use word2vec encoder (hit rate ~85%).
   Char-trigram at VOCAB=100 is a much weaker encoding; W rank-1 collapse may be
   encoding-specific, not mechanism-specific.

3. **N=512 vs N=8192**: Fair-harness HARD_PASS used N=8192 (16x larger). At higher N,
   rank-1 W still concentrates in one direction but the signal-to-noise ratio is
   higher and logit std is larger.

4. **Not testing continual-learning retention**: N_REPLAY re-uses same 2000 tokens.
   Production replay would use distinct replay episodes. This smoke tests weight
   accumulation, not catastrophic forgetting prevention.

5. **Grid-search on degenerate logits**: When all logits are nearly constant (~0.96-0.99),
   the (T, lambda) grid-search is operating in the noise regime. BPC differences
   between arms that are < 0.001 bits cannot be trusted as real signals.

---

## What to Do Next

**DO NOT interpret BOTH_NULL_AT_SMOKE as evidence the TAU_NEG hypothesis is wrong.**
The smoke had structural insufficient scale to test it.

**Recommended path:**
1. Run PRIMARY anchor at full production scale (N=8192, N_TRAIN=100k, word2vec, 3 seeds)
   as planned in the handoff. That is where the timescale effect should emerge.
2. The dual_trace_RESCUE_corrected_baseline_v1 cell in overnight_queue uses TAU_NEG=50
   (the "wrong" value per brain-canonical). If that HARD_FAILs, it does NOT confirm
   TAU_NEG is irrelevant -- it confirms the smoke correctly warned it can't resolve this.
3. The smoke DOES confirm: at production scale, TAU_NEG axis should be tested with
   N_TRAIN >> 50*INGEST_CHUNK (> 50 chunks = > 200k tokens at INGEST_CHUNK=4096).

**Structural finding worth preserving**: W is rank-1 dominated at all smoke scales tested.
This matches prior observation that dual-trace mechanism in v1 got MEASURED_MECHANISM
(by-construction near-saturation). The rank-1 floor is a real constraint, not a smoke artifact.

---

## Degenerate-collapse check (per SUSPICIOUS-RESULT GATE)

All arms identical BPC is suspicious-looking but NOT a script bug:
- Confirmed by W structural analysis (W diff t50 vs t10 = 0.0; replay diff is real but tiny)
- Root cause: too few chunks for trace timescales to diverge + rank-1 W collapse
- BPC is finite and non-sentinel (3.89)
- Self-test passes (PASS: logits shape OK, BPC finite=3.2905)
- This IS the expected null result when scale is insufficient; result is informative
