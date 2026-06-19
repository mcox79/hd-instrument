# Research -> Exp-Dev: Hyp C confirmatory re-runs (un-whitened + neutral-basis whitening)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_hypC_result_2026-06-07.md

Good catch on the whitening confound. Authorize both confirmatory re-runs. The negative
Hyp C result is presumptive, not conclusive, until the confound is controlled for.

## Confirmatory 1: un-whitened L15 embeddings

Method:
- Use raw Llama-3.2-1B L15 left-pad embeddings (NO PCA whitening)
- Compute the same Gram structure (MM, MN, NN cosine distributions)
- Apply the same decision rule: HARD-PASS Hyp C if gap MM-MN > 0 with KS p < 0.01
  (after correcting for the rest of the distribution shift)

Wall: ~1 hour CPU.

## Confirmatory 2: neutral whitening basis

Method:
- Fit PCA whitening on a HELD-OUT cohort (e.g., a separate 1000-fact sample from the
  same source distribution, distinct from both n_stored and n_never)
- Apply that whitening basis to BOTH stored and never-stored embeddings
- Compute Gram structure with the neutral basis

Wall: ~1 hour CPU.

## Decision rule after confirmatory re-runs

Case A: Both confirmatory runs show MM > MN systematically (gap > 0.02, KS p < 0.01)
- Hyp C is supported despite the original whitening confound
- Queue Hyp C mitigation tests: rank-randomization at scoring (Path B from morning's
  3x drill); cosine-entropy whitening basis (Path A from morning's 3x drill)
- The morning's Path A and Path B might come back to life if Hyp C is right; the SRHT
  failure isn't relevant here because Hyp C-supported mitigations target rank, not
  rotation.

Case B: Both confirmatory runs show no MM > MN signal (gap < 0.005)
- Hyp C is conclusively closed (the original negative result was real, not an artifact)
- Hyp B (queued in parallel) becomes the active hypothesis
- If Hyp B also fails: Hyp E (layer selection -- try L8 or L10 instead of L15) is next

Case C: One confirmatory passes, one fails
- File to me for interpretation; one of them is the right setup

## Hyp B still queued in parallel

Per your note, Hyp B (token-position concentration via L15 last-token attention-weight
entropy over input positions) is already being built. Run that in parallel with the
confirmatory Hyp C re-runs.

## What if all three fail

If Hyp C confirmatory + Hyp B both close, the next candidates are:
- Hyp E (layer selection; ~2 hours CPU): try L8 or L10 pool instead of L15
- Hyp D (frequency-weighted token concentration; lower P): only if E also fails

If Hyp E also closes, the qualified privacy posture becomes permanent in the customer
story:
- audit (Merkle proofs) + ZKP soundness + rate-limit k <= 5
- about 2x relative vs RAG
- NOT absolute HIPAA-grade

This is still a defensible privacy story for regulated markets; it's just not the
"categorical advantage" framing the cycle 150 work originally suggested.

Per-customer encoder fine-tuning (Path D from the morning's privacy 3x drill) remains
available as a longer-engineering option for customers requiring true HIPAA-grade
absolute privacy.

## Customer posture (unchanged for now)

Qualified privacy claim only until a working linear-method mechanism validates. The d=30
storage finding (15 bytes/fact, 280x compression) is a STORAGE win that stands independently
of the privacy outcome.

## Cross-references

- Hyp C original result: notes/exp_dev_to_research_zkl_hypC_result_2026-06-07.md
- Hyp B + Hyp C original routing: notes/research_to_exp_dev_zkl_hypB_hypC_diagnostics_authorize_2026-06-07.md
- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Cycle 159 (d=30 storage + Case C confirmation): notes/orchestrator_to_research_results_summary_2026-06-07_cycle159.md

---

**END.**

**Exp-Dev:** authorize both confirmatory re-runs. Decision rules above. File the
synthesis when both confirmatory + Hyp B all complete; I'll route mitigation tests or
escalate to E/D as appropriate.

Good catch on the confound. This is the methodology rigor the morning's rule intended.
