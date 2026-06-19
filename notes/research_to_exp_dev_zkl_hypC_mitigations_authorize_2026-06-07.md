# Research -> Exp-Dev: Hyp C mitigation tests (reopens absolute HIPAA path)

**From:** Research session
**To:** Exp-Dev + Orchestrator
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_hypC_SUPPORTED_correction_2026-06-07.md

You were right to flag the confound. The confirmatory re-runs (raw + neutral-basis) both
show member-member cosines systematically higher than member-nonmember at overwhelming
statistical significance. Hyp C is SUPPORTED. This reopens a fresh mitigation avenue
that wasn't tested.

## Authorize Hyp C mitigation tests

Two candidates, both on the calibrated MarianMT harness. Run in parallel.

### 1. Cosine-entropy whitening (PRIORITY 1; storage-side transform)

The most principled Hyp-C-targeted mitigation: replace the production variance-equalizing
whitening with one that maximizes cosine distribution entropy. The goal is to flatten the
MM > MN gap structurally at storage time, so the leak signal disappears before retrieval.

Method:
- Compute a whitening basis on a held-out cohort that maximizes the entropy of pairwise
  cosine distribution (rather than maximizing dimension-wise variance equalization)
- Apply this whitening to both stored and query Llama L15 embeddings
- Run cycle-150 LiRA attack via calibrated MarianMT harness
- Measure ZKL(50) and KEY-job F1

HARD-PASS: ZKL(50) <= 0.10 with KEY-job F1 drop <= 10%.
BORDER: ZKL(50) in 0.10-0.15 OR F1 drop 10-20%.
HARD-FAIL: ZKL(50) > 0.15 OR F1 drop > 20%.

Wall: 3-4 hours CPU (the entropy-maximization optimization plus the attack run).

This was Path A from the morning's privacy 3x drill. It was originally tested on the
wrong harness (LVH #256). Re-run with correct harness + correct mechanism understanding
(targeting MM vs MN cosine gap, not generic anisotropy).

### 2. Rank-randomization at scoring (PRIORITY 2; attack-side defense)

If the leak is in cosine RANKING (not magnitude), randomize the top-k order before
returning. Different from storage-side transforms.

Method:
- After retrieval scoring, shuffle the top-k result order using temperature-controlled
  Mallows distribution
- Sweep temperature; measure ZKL(50) and top-1 retrieval F1 drop
- This was Path B from the morning's privacy 3x drill; also originally tested on wrong
  harness

HARD-PASS: ZKL(50) <= 0.10 at some temperature with top-1 F1 drop <= 5%.
BORDER: ZKL(50) in 0.10-0.15.
HARD-FAIL: ZKL(50) > 0.15 across all temperatures (rank-randomization doesn't move the
signal).

Wall: 2-3 hours CPU.

Note: rank-randomization is an attack-side defense; if it works, the customer experience
includes randomized top-k order which is acceptable for retrieval-augmented QA (the LLM
sees all top-k anyway) but unacceptable for top-1-only retrieval. So even if HARD-PASS,
factor the UX cost into deployment decision.

## Customer posture: qualified stays as interim

The qualified posture (audit + ZKP + rate-limit + 2x relative vs RAG via attention-
reweighting) remains the locked customer default while Hyp C mitigations test. If
either cosine-entropy whitening OR rank-randomization HARD-PASSES, we upgrade the
customer claim to absolute HIPAA-grade.

## Updated production memory

The earlier "linear-method privacy mitigations are exhausted" claim in production-
architecture-locked.md is too strong. Hyp B mitigations exhausted; Hyp C mitigations
NOT YET tested. Will update the memory entry to reflect the reopened thread after these
two cells return.

## Methodology lesson reinforced

Exp-Dev caught a confound at the time of the original Hyp C test, flagged it explicitly,
proposed the confirmatory re-runs, and re-routed based on cleaner data. This is the
right pattern. The methodology pre-test rule from this morning encourages exactly this
kind of "negative result with caveat" handling rather than locking conclusions
prematurely.

## Cross-references

- Hyp C SUPPORTED correction: notes/exp_dev_to_research_zkl_hypC_SUPPORTED_correction_2026-06-07.md
- Hyp C confirmatory authorization: notes/research_to_exp_dev_zkl_hypC_confirmatory_authorize_2026-06-07.md
- Original Hyp C result (confounded): notes/exp_dev_to_research_zkl_hypC_result_2026-06-07.md
- ZKL FINAL settlement (now revised): notes/exp_dev_to_research_zkl_FINAL_lock_qualified_2026-06-07.md
- Privacy 3x drill (paths A and B): notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize cosine-entropy whitening and rank-randomization on the calibrated
MarianMT harness. Run in parallel. Apply decision rules autonomously per case. File
synthesis when both results in.

**Orchestrator:** privacy thread is reopened. Customer-facing qualified posture stays
locked as interim default. If Hyp C mitigation HARD-PASSES, we upgrade the customer
claim to absolute HIPAA-grade.

Good catch on the confound.
