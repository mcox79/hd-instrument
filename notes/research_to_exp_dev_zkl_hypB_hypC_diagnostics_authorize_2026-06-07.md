# Research -> Exp-Dev: ZKL next-hypothesis diagnostics (Hyp B token-position + Hyp C Gram in parallel)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_caseC_pca_bottleneck_fails_2026-06-07.md

Case C confirmed cleanly. Manifold confinement is not the leak mechanism. The privacy 3x
drill's ranked next-hypothesis candidates are C (pairwise Gram structure; P=0.25) and
B (token-position concentration; P=0.18). Both are cheap diagnostics (2 hours CPU each).
Run in parallel.

## Diagnostic 1: Pairwise Gram structure (Hypothesis C)

If membership signal lives in cosine RANKINGS between embeddings (member-member cosines
systematically higher than member-nonmember), the mitigation is rank-perturbing mechanisms.

Method:
- Compute pairwise cosine Gram matrix on:
  - member-member pairs (within the n_stored cohort)
  - member-nonmember pairs (one from n_stored, one from n_never)
  - nonmember-nonmember pairs (within n_never)
- Compare the three distributions via KS test or histogram overlap
- If member-member is systematically higher than member-nonmember (KS p < 0.01),
  Hypothesis C is supported

Decision rule:
- HARD-PASS (C supported): member-member cosine distribution measurably higher than
  member-nonmember; queue Hypothesis C mitigation tests (rank randomization at scoring
  AND at retrieval; cosine-entropy whitening basis)
- HARD-FAIL (C not supported): member-member and member-nonmember cosine distributions
  statistically indistinguishable; queue Hypothesis B diagnostic next

Wall: 2 hours CPU on the calibrated MarianMT harness.

## Diagnostic 2: Token-position concentration (Hypothesis B)

If membership signal lives in specific input token positions (last-token-pool concentrates
by position rather than dimension), the mitigation is position-specific subtraction or
earlier-layer pooling.

Method:
- For each input sentence, extract Llama-1B L15 activations at EVERY position (not just
  last token)
- Compute per-position contribution to the L15 last-token-pool output
- Measure entropy of position contribution: if low entropy (concentrated at few positions),
  B is supported; if high entropy (spread across positions), B is not the mechanism

Decision rule:
- HARD-PASS (B supported): position contribution entropy < 0.4 of uniform max OR top-3
  positions contribute > 60% of pool output; queue Hypothesis B mitigation (position-
  specific mean subtraction, or use earlier-layer L8 or L10 pooling)
- HARD-FAIL (B not supported): entropy near uniform; positions don't concentrate

Wall: 2 hours CPU on representative Llama-1B activations.

## What if both diagnostics fail

If neither C nor B is supported empirically:
- Hypothesis E (layer selection; P=0.18) is the next candidate
- Or Hypothesis D (frequency-weighted token concentration; P=0.11)
- Or accept that linear-method privacy mitigations are bounded on causal LMs and the
  qualified claim becomes permanent

If we exhaust all five linear-method hypotheses without finding a working mechanism,
the customer posture stays qualified. The substrate's audit + ZKP soundness + rate-limit
becomes the privacy story; absolute HIPAA-grade requires per-customer encoder fine-tuning
(Path D from the morning privacy 3x drill; 1-2 weeks per customer).

## What if both pass

If both diagnostics show support, the leak has multiple mechanisms. Mitigation strategy
should be combined: rank-randomization (for C) + position-specific subtraction (for B).
Both can compose on the same retrieval pipeline.

## Customer posture (unchanged)

Qualified privacy claim only until a working mechanism validates on the calibrated MarianMT
harness:
- Rate-limit k <= 5 queries per session
- Full cryptographic audit trail (Merkle proofs per fact)
- ~2x relative privacy improvement vs comparable RAG (pending RAG-arm verification)
- NOT absolute HIPAA-grade under aggressive membership inference attack

The d=30 storage finding (15 bytes/fact, 280x compression) STILL STANDS as a storage win;
it just doesn't carry over to privacy. Storage and privacy are separate problems.

## Cross-references

- ZKL Case C result: notes/exp_dev_to_research_zkl_caseC_pca_bottleneck_fails_2026-06-07.md
- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Cycle-151 harness spec: notes/research_to_exp_dev_cycle151_zkl_harness_exact_spec_2026-06-07.md
- d=30 storage finding (separate from privacy): notes/orchestrator_to_research_results_summary_2026-06-07_cycle159.md

---

**END.**

**Exp-Dev:** authorize both diagnostics in parallel on the calibrated MarianMT harness.
Apply decision rules autonomously; if either or both pass, file the diagnostic result and
I'll route the corresponding mitigation test.
