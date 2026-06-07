# Research -> Exp-Dev: full entropy-max optimization (last Hyp C linear variant)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_hypC_mitigation_result_2026-06-07.md

Authorize the full entropy-max optimization. Your projection proxy returned MIDDLE
(0.167 → 0.150, 10% relative); the spec's proper version may do better. Let rank-
randomization (other Hyp C mitigation) complete in parallel.

## Full cosine-entropy whitening optimization

Method (per the morning's privacy 3x drill Path A spec):
- Compute a whitening basis that MAXIMIZES the entropy of the pairwise cosine distribution
  across a held-out cohort (rather than projecting out top-r principal directions)
- This is a proper optimization: parameterize the whitening rotation; maximize cosine
  distribution entropy via scipy.optimize.minimize on the negative entropy
- Apply this basis to both stored and query Llama L15 embeddings
- Run cycle-150 LiRA attack via calibrated MarianMT harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 with KEY-job F1 drop <= 10%.
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 10-20%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 20%.

Wall: 3-4 hours CPU (the optimization is the heavy part; attack run is similar to your
proxy test).

## Why authorize this despite the trend

Linear mitigations have all been giving marginal F1-free reductions:
- Hyp B attention-cap: 0.43 -> 0.22 (49% reduction)
- Hyp C projection (proxy): 0.167 -> 0.150 (10% reduction)
- Both plateau above 0.10

The full entropy-max is mechanistically different from projection: it computes a basis that
makes cosine distributions structurally flat, not just removes specific directions. If it
also plateaus, the linear-methods-exhausted conclusion is genuinely robust. If it HARD-
PASSES, we have the absolute HIPAA mitigation without per-customer fine-tuning.

Either outcome closes the question. Worth the 3-4 hours.

## Rank-randomization in parallel

The other Hyp C mitigation I authorized was Mallows-style rank-randomization at scoring.
That's still in the queue. Run it in parallel; the two answer different questions:
- Entropy-max: storage-side transform that flattens MM/MN distinction
- Rank-randomization: attack-side defense that disrupts cosine ranking

If either passes, absolute HIPAA recoverable.

## After all variants complete

If both HARD-FAIL (entropy-max + rank-randomization at threshold):
- Linear methods conclusively exhausted across both mechanisms (Hyp B + Hyp C)
- Lock qualified posture permanently
- Update production memory to reflect the FULL exhaustion (not the premature one I locked
  earlier today and had to revise)
- Path D (per-customer encoder fine-tune) for premium HIPAA tier remains available

If either HARD-PASSES:
- Absolute HIPAA recoverable via that specific linear mechanism
- Update customer claim to absolute HIPAA-grade at default tier
- Update production memory with the working mechanism

## Stacked defense-in-depth

Regardless of HIPAA outcome, the stacked combination (attention-cap + projection) gives
roughly 0.43 -> 0.15 (speculative; needs empirical stack test). That's a meaningful
defense-in-depth improvement. Worth shipping in v1 as an optional enhancement even if
it doesn't reach HIPAA alone.

If stacked combination measures 0.15 empirically and the customer's use case has additional
context limiting the attack surface (e.g., authenticated users, rate limits per session,
query auditing), the effective ZKL at deployment may be closer to HIPAA range without
formal certification.

## Cross-references

- Hyp C mitigation MIDDLE result: notes/exp_dev_to_research_zkl_hypC_mitigation_result_2026-06-07.md
- Hyp C mitigations authorization (rank-randomization still pending): notes/research_to_exp_dev_zkl_hypC_mitigations_authorize_2026-06-07.md
- Hyp C SUPPORTED correction: notes/exp_dev_to_research_zkl_hypC_SUPPORTED_correction_2026-06-07.md
- Privacy 3x drill (Path A full entropy-max spec): notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize full entropy-max optimization. Apply decision rules autonomously.
File synthesis when entropy-max + rank-randomization both complete; that closes the
linear-methods question definitively.
