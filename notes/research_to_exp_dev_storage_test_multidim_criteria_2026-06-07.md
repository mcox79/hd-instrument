# Research -> Exp-Dev: Storage tests need multi-dimensional pass criteria, not just retrieval

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** research_to_exp_dev_storage_efficiency_test_program_2026-06-07.md (supplement)

User flagged: do not choose storage settings that improve compression at the cost of other
substrate properties. Need to understand the safe operating regimes.

The pass criteria I shipped in the test program were narrow (retrieval accuracy drop <= 3%
only). They miss the broader question of what each reduction technique costs us across the
full set of substrate properties. Replacing those criteria with the multi-dimensional set
below before you run the cells.

## Properties to measure on every storage-reduction cell

For each cell (sparse-W, 4-bit quant, lower N, source PCA, content-addressable keys,
hybrid sparse-key, pruning), report all of:

### Retrieval
- Top-1 retrieval accuracy on stored facts (target: >= 95% of baseline)
- Top-k recall at k=10 (target: >= 95% of baseline)
- Cosine similarity distribution on retrieval (mean and tail)

### Reasoning
- K-hop accuracy at K=5, K=12 (production target)
- K-hop end-to-end answer quality
- Per-hop confidence calibration (does confidence still predict correctness?)

### Hallucination resistance
- KF-1 AUC on the 6 attack types from the adversarial envelope
- False positive rate on never-stored queries (target: <= 1% at cosine threshold 0.9)
- ZKL leakage on standard attack at k=50 (target: should not WORSEN; ideally improve)

### Adversarial robustness
- Sparse concentration attack: K_max retention vs baseline
- Random distractor attack at B=10: cosine SNR vs baseline
- Coherent distractor attack at c_d=0.48: K_max vs baseline

### Audit integrity
- Merkle proof verification rate (target: 100% of stored facts verify correctly)
- HMAC key deletion still produces verifiable anonymization (target: yes)
- Bitemporal as_of() reconstruction accuracy (target: >= 99%)

### Performance
- Write throughput at production N (writes/sec)
- Retrieval latency p50, p95, p99
- Memory cost reduction factor (the compression ratio you're after)

## Pass / fail / qualify rules per cell

A cell HARD-PASSES if:
- Memory reduction factor matches target AND
- Retrieval, K-hop, KF-1, adversarial, and audit properties all >= 95% of baseline AND
- ZKL leakage does not worsen vs baseline

A cell QUALIFIES (gray zone; flag to me for decision) if:
- Memory reduction factor matches target AND
- ANY substrate property in the 90-95% range
- OR memory reduction is lower than target but no property is degraded

A cell HARD-FAILS if:
- Memory reduction misses target with no property compensation OR
- ANY substrate property drops below 90% of baseline OR
- ZKL leakage measurably worsens OR
- Audit integrity is not 100%

## Why the audit and ZKL properties must not be degraded

The product story is "substrate uses more bits per fact than LLM but provides individual
addressability, cryptographic audit, and privacy guarantees LLMs cannot match." If a
storage reduction degrades audit integrity or privacy properties, the bytes we save are
not bytes worth saving -- the customer value vanishes with the audit.

The cost vs benefit must be calculated on the full property surface, not on memory alone.

## Operating regime mapping (deliverable per cell)

In addition to HP/MID/HF, report each cell's SAFE OPERATING REGIME:

- "Compression factor R is achievable up to fact-density M/N = X without degrading
  property Y below threshold Z"
- Sweep at least 3 settings per cell (low, medium, aggressive compression) and report
  the property scores at each
- Identify the knee point where each property starts to degrade

This gives us the picture of what's achievable safely, not just whether the most
aggressive setting works.

## Specific reductions

For sparse-W: sweep weight-keep ratios in {0.01, 0.05, 0.1, 0.2}, measure all properties
above at each.

For 4-bit quant: report 4-bit alongside 8-bit and 2-bit; pick whichever level passes the
property set.

For lower-N: report N in {16384, 32768, 65536}; identify the lowest N that retains all
properties.

For source vector PCA: report compression at {2x, 4x, 8x}.

For pruning: report pruning rate {10%, 25%, 50%} and the property scores on retained
facts at each.

## How this changes the test program

The original test program's decision rules still apply for v1 ship decisions. But each
cell's verdict carries more information now -- not just one pass/fail bit, but a regime
map. Build the v1 stack from the SAFE operating settings, not the maximum-compression
ones.

## Cross-references

- Storage test program (original): notes/research_to_exp_dev_storage_efficiency_test_program_2026-06-07.md
- Storage 3x drill: notes/research_drill_storage_efficiency_per_fact_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** apply the multi-dimensional criteria to every storage-reduction cell. Sweep
multiple compression levels per cell. Report each cell's safe operating regime, not just
pass/fail. This is more work per cell (probably 2-3x the original budget) but avoids
silent quality regressions.

**User:** test program updated to measure all substrate properties, not just retrieval. We
won't ship a setting that saves bytes at the cost of audit, K-hop, or hallucination
resistance. Each cell will report its safe operating regime.
