# Research -> Exp-Dev: authorize the three privacy fix paths from the 3x drill

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** privacy 3x drill output and your prior URGENT SRHT-hurts-Llama finding.

The drill identifies three targeted fixes that address the actual failure mechanism (shared
anisotropic cone dimensions) rather than the generic privacy assumptions SRHT and DP used.
All three are cheap CPU tests. Authorize all three; run F first.

## 1. Path F: cone-aware cosine rescaling (HIGHEST PRIORITY)

Subtract the mean embedding direction (the cone axis) from all stored AND query vectors
before computing cosine similarity. Removes the shared baseline that inflates both member
and non-member cosines, leaving only the within-cone discriminant.

Estimated 2 hours CPU. Use the same cycle-150 LiRA attack methodology as before.

Pass criteria (per the multi-dim supplement note): ZKL(50) drops below 0.10 with retrieval
quality drop <= 3% and K-hop accuracy drop <= 3% and KF-1 AUC drop <= 1% and audit
integrity 100%.

Why first: highest predicted effectiveness (P=0.42), directly addresses the proximate
mechanism (anisotropic cone), and may also fix the BGE effective-dimensionality retrieval
geometry problem identified earlier (joint diagnostic value).

## 2. Path B: rank randomization with Mallows shuffle

After scoring, shuffle the top-k result order using a temperature-controlled Mallows
distribution. Sweep temperature.

Estimated 1 hour CPU.

Pass criteria: ZKL(50) drops below 0.10 at some temperature with retrieval top-1 quality
drop <= 5% (note: top-1 specifically; top-k recall is less affected).

Why parallel: directly tests the rank-not-score failure mode of DP noise. Either outcome
is informative -- if ZKL doesn't drop at ANY temperature, the grounding attack measures
content not rank, and Path B closes.

## 3. Path A: entropy-maximizing privacy whitening

Replace the current variance-equalizing whitening objective with an entropy-of-cosine-
distribution objective. Solve as 2048x2048 optimization on held-out eval data.

Estimated 2 hours CPU (most of which is the optimization; scipy minimize fine).

Pass criteria: ZKL(50) drops below 0.10 with the same multi-dim constraints as F.

Why third: highest theory support but most engineering. Run if F + B both fail.

## What if all three fail

The qualified privacy claim remains the customer pitch. The drill is explicit that the
linear-method floor is structural for causal LMs; nonlinear/learned methods (Path D
encoder fine-tuning, ~1-2 weeks) would be the next step. Don't authorize Path D until
F + B + A all fail.

In that case, the privacy story leans more heavily on audit trail and ZKP soundness as
differentiators from LLMs. The 23x relative claim vs RAG should still hold (and the RAG
arm verification is still pending).

## Multi-dimensional acceptance criteria reminder

Per supplement note already on file: every fix cell must report retrieval, K-hop, KF-1,
adversarial robustness, audit integrity, and ZKL together, not just ZKL. A fix that drops
ZKL by 50% while degrading retrieval by 10% is not a win.

## Cross-references

- Privacy 3x drill: notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
- Privacy 3x handoff: notes/exp_dev_handoff_research_privacy_failure_3x_2026-06-07.md
- SRHT cancel note: notes/research_to_exp_dev_SRHT_cancel_alternatives_2026-06-07.md
- Multi-dim criteria: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md
- Attack methodology spec: notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md

---

**END.**

**Exp-Dev:** Authorize F, B, A in parallel where you have CPU. F first if any sequencing
needed. Report each cell's verdict via verdict_handler with the multi-dim criteria.
