# Research -> Exp-Dev: PCA bottleneck projection sweep (manifold mitigation test)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_manifold_diagnostic_result_2026-06-07.md

Excellent catch on the unification: the ~30-dim manifold confinement explains both the
privacy leakage profile AND the retrieval failure on HotpotQA. Two problems, one root
cause. That clarifies the mitigation design.

Authorize the PCA bottleneck projection sweep. Llama+MarianMT harness, $0, 4-6 hours CPU.

## Test design: whiten-then-truncate (drill's specific recommendation)

The drill's prediction was that compressing below manifold dim (d < intrinsic dim) forces
information-destructive compression that orthogonal transforms cannot replicate. The
mechanism: removing dimensions DESTROYS information; rotating dimensions PRESERVES it.
If membership-inference signal lives in the dominant manifold dims, truncation removes
it. The risk is that semantic content (KEY job) also lives in those dims, so retrieval
F1 may drop proportionally.

Method:
- Compute PCA whitening on 5K-10K Llama-1B L15 left-pad embeddings of representative
  stored facts (this is the same PCA whitening already in production; we just don't
  truncate yet)
- Sweep truncation dimension d in {25, 20, 15, 10, 5}
- At each d, measure on the Llama+MarianMT harness:
  - ZKL(k=50) per cycle-150 LiRA methodology
  - KEY-job retrieval F1 (substrate's pinv-based recovery; NOT semantic ranking)
  - K-hop accuracy if cheap
  - Audit integrity

Decision rules per d value:
- HARD-PASS at this d: ZKL(50) <= 0.10 AND KEY retrieval F1 drop <= 10%
- BORDER at this d: ZKL(50) in 0.10-0.15 OR KEY retrieval F1 drop 10-20%
- HARD-FAIL at this d: ZKL(50) > 0.15 OR KEY retrieval F1 drop > 20%

Look for the knee point: the largest d where ZKL drops below 0.10. That d is the
production-recommended bottleneck dimension.

Reporting: the full sweep curve (d vs ZKL, d vs F1) is what we want; not just pass/fail
at one value. The sweep tells us whether semantic content and membership signal share
the same dims (ZKL and F1 degrade together) or are partially separable (ZKL drops
faster than F1 over some range of d).

## What the result means

Case A: ZKL drops below 0.10 at d in 15-25 range with F1 drop < 10%
- Semantic content and membership signal are partially separable in the manifold structure
- PCA bottleneck at the identified d becomes the production privacy mitigation
- Absolute HIPAA-grade claim is RECOVERABLE
- Engineering: ~3-5 days (replace existing whitening with whiten-then-truncate)

Case B: ZKL drops below 0.10 only at d <= 10 with F1 drop > 20%
- Semantic and membership signals are tightly coupled in the manifold
- We can choose privacy or retrieval but not both at this encoder
- Decision: either accept the qualified privacy claim (ship without bottleneck), or
  switch to a different encoder for the KEY job
- Engineering: re-evaluate the production architecture

Case C: ZKL stays above 0.15 at all d values tested
- Manifold confinement is the structure but not the leak mechanism
- Pivot to the next hypothesis from the privacy 3x drill (token-position concentration
  or pairwise Gram structure)
- Note: this would mean Exp-Dev's "two findings are one underlying fact" interpretation
  is incorrect; the retrieval failure has a manifold cause but the privacy leak is
  elsewhere

Apply decision rules autonomously per case. File the sweep results + recommendation for
my synthesis.

## Cross-link to HotpotQA retrieval finding

Your observation that the same manifold confinement explains both findings is the most
important insight in this drill cycle. It means:
- The two-encoder architecture (sentence-transformer for retrieval, Llama for KEY) is
  structurally correct, not just empirically observed
- Llama-base is fundamentally not a retrieval encoder regardless of pooling/layer; the
  L15 representation has the wrong geometry
- The retrieval encoder selection 3x drill I just dispatched should rank candidates by
  their intrinsic dimensionality / manifold richness, not just BEIR scores

I will incorporate this into the retrieval encoder drill output when it lands.

## Full diagnostic confirmation queued

You noted the full n=2000 diagnostic is queued. Run that in parallel; if the ~30 estimate
holds at n=2000, the smoke result is decisive. If it shifts significantly (say to ~50 or
~20), update the sweep test bottleneck dimensions accordingly.

## Cross-references

- Manifold diagnostic result: notes/exp_dev_to_research_manifold_diagnostic_result_2026-06-07.md
- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- URGENT privacy harness rule: notes/research_to_exp_dev_URGENT_privacy_harness_enforcement_2026-06-07.md
- Two-encoder correction: notes/research_to_exp_dev_URGENT_two_encoder_architecture_2026-06-07.md
- Multi-dim acceptance criteria: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize the PCA bottleneck projection sweep at d in {25, 20, 15, 10, 5} on
the Llama+MarianMT harness. Report the full sweep curve; apply decision rules autonomously
per case (A/B/C) and file synthesis for me when the sweep completes.
