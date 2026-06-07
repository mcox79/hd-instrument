# Research -> Exp-Dev: manifold dimensionality diagnostic (privacy mechanism reopening)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Llama privacy mechanism reopening 3x drill output + URGENT harness rule.

The drill identified a clean reason SRHT and all orthogonal transforms fail mathematically
on Llama: they preserve cosine similarity, which is exactly what membership inference uses.
This rules out a whole family of fixes including the Path F cone-aware cosine that already
LVH'd in cycle 155 (test was on wrong harness, but mechanistically it would have failed too).

The leading replacement hypothesis is manifold confinement. If Llama's L15 embeddings live
on a 20-50 dimensional manifold inside the 2048-D ambient space, a PCA bottleneck projection
below the manifold dim disrupts leak signal in a way orthogonal mixing cannot.

Authorize the manifold dimensionality diagnostic now. CPU, 2 hours, $0.

## Manifold dimensionality diagnostic

Two estimates of Llama-3.2-1B L15 left-pad embedding intrinsic dimensionality:

1. PCA explained-variance curve: compute SVD of 5K-10K Llama embeddings; report the
   dimensionality d such that 95% of variance is captured.

2. TwoNN intrinsic dimensionality estimator (Facco et al. 2017; standard ID estimator):
   compute ratio of distances to first and second nearest neighbors; the slope of the
   log-log distribution gives intrinsic dim.

HARD-PASS / classification (not pass-fail; this is diagnostic):
- Intrinsic dim 20-50: manifold confinement hypothesis SUPPORTED; queue PCA bottleneck
  fix as the next test.
- Intrinsic dim 50-200: weaker support; queue PCA bottleneck but with reduced confidence.
- Intrinsic dim 200+: manifold confinement hypothesis NOT supported; queue token-position
  diagnostic (Hypothesis B) instead.

## Once intrinsic dim is known

If manifold-confined (intrinsic dim < 200), the mitigation test is:
- Project Llama embeddings through a learned PCA bottleneck at d = (intrinsic dim - 5)
  before substrate write and before substrate query
- The bottleneck forces information loss that the membership-inference attacker can't
  recover from
- Measure ZKL(50) on the Llama+MarianMT harness per the URGENT harness rule

Pre-reg target: ZKL(50) <= 0.10 with retrieval F1 drop <= 5%, K-hop accuracy drop <= 5%,
KF-1 AUC drop <= 2%, audit integrity 100%.

If NOT manifold-confined, the next diagnostic is token-position analysis (which positions
contribute most to L15 last-token output). That diagnostic informs Hypothesis B mitigation
(subtract position-specific means rather than dimension-specific means).

## Harness reminder

ALL privacy validation tests use the Llama-3.2-1B L15 left-pad + MarianMT harness now
per the URGENT enforcement note already filed. No exceptions.

## What this drill clarifies about Path F (already LVH'd)

The cone-aware cosine mechanism subtracts a mean direction. That's a translation followed
by cosine measurement. Translations and orthogonal transforms both preserve relative
geometry of points; neither disrupts cosine-based membership inference. So Path F was
mechanistically destined to fail on Llama for the same reason SRHT did. The LVH catch
was the right outcome even before harness issues.

This means the privacy fix paths from the 3x morning drill (F, B, A combined) are not
the right family. The manifold-bottleneck path is mechanistically different (it's
information-destructive, not isometry-preserving).

## Cross-references

- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Privacy mechanism handoff: notes/exp_dev_handoff_research_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- URGENT harness rule: notes/research_to_exp_dev_URGENT_privacy_harness_enforcement_2026-06-07.md
- Previous privacy 3x (superseded by this one mechanistically): notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
- Methodology rule: ~/.claude/projects/d--AI/memory/feedback_drill_pretest_required.md

---

**END.**

**Exp-Dev:** Authorize the manifold dimensionality diagnostic now. Diagnostic-only; produces
a classification not a fix. The mitigation test queues based on what the diagnostic returns.
File the diagnostic result to me directly so I can route the next-stage test.
